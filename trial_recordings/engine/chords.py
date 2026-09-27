"""Chord charts for the rhythm section: parse an irealbook:// link into bars of
chords, and give each chord quality its chord tones, passing-tone scale and a
four-note rootless piano voicing (semitones above the root).

The entries for Halation's chord qualities are exactly the values its
recording used (claude_halation/src/musiclib.py CHORD_TYPES and
src/audio/perform.py VOICING_PCS); the rest extend the same logic.
"""
from __future__ import annotations

import re
import urllib.parse
from dataclasses import dataclass

LYD = {0, 2, 4, 6, 7, 9, 11}
ION = {0, 2, 4, 5, 7, 9, 11}
DOR = {0, 2, 3, 5, 7, 9, 10}
LYD_DOM = {0, 2, 4, 6, 7, 9, 10}

# iReal quality -> (chord tones, scale, voicing)
QUALITY = {
    "^7#11": ({0, 4, 7, 11}, LYD, [4, 11, 2, 6]),           # Halation maj7#11
    "^9#11": ({0, 4, 7, 11}, LYD, [4, 11, 2, 6]),
    "^7#5": ({0, 4, 8, 11}, {0, 2, 4, 6, 8, 9, 11}, [4, 8, 11, 2]),   # Halation maj7#5
    "^9": ({0, 4, 7, 11}, ION, [4, 7, 11, 2]),
    "^7": ({0, 4, 7, 11}, ION, [4, 7, 11, 2]),
    "69": ({0, 4, 7, 9}, ION, [4, 9, 2, 7]),
    "6": ({0, 4, 7, 9}, ION, [4, 9, 2, 7]),
    "7b9sus": ({0, 5, 7, 10, 1}, {0, 1, 3, 5, 7, 8, 10}, [5, 10, 1, 7]),   # Halation 7sus(b9)
    "7alt": ({0, 4, 10}, {0, 1, 3, 4, 6, 8, 10}, [4, 10, 3, 8]),          # Halation 7alt
    "-9": ({0, 3, 7, 10, 2}, DOR, [3, 7, 10, 2]),                          # Halation m9
    "-7": ({0, 3, 7, 10}, {0, 2, 3, 5, 7, 8, 9, 10}, [3, 7, 10, 2]),       # Halation m7
    "-11": ({0, 3, 7, 10}, DOR, [3, 10, 2, 5]),
    "13sus": ({0, 5, 7, 10}, {0, 2, 5, 7, 9, 10}, [5, 10, 2, 9]),         # Halation 13sus
    "7": ({0, 4, 7, 10}, {0, 1, 2, 3, 4, 6, 7, 8, 9, 10}, [4, 9, 10, 2]),  # Halation 7
    "13": ({0, 4, 7, 10}, {0, 1, 2, 3, 4, 6, 7, 8, 9, 10}, [4, 9, 10, 2]),
    "7b9": ({0, 4, 7, 10, 1}, {0, 1, 3, 4, 5, 7, 8, 10}, [4, 9, 10, 1]),   # Halation 7(b9)
    "h7": ({0, 3, 6, 10}, {0, 1, 2, 3, 5, 6, 8, 10}, [3, 6, 10, 5]),       # Halation m7b5
    "-7b5": ({0, 3, 6, 10}, {0, 1, 2, 3, 5, 6, 8, 10}, [3, 6, 10, 5]),
    "-^7": ({0, 3, 7, 11}, {0, 2, 3, 5, 7, 9, 11}, [3, 7, 11, 2]),         # Halation m(maj7)
    "9#11": ({0, 4, 7, 10, 2}, LYD_DOM, [4, 10, 2, 6]),                    # Halation 9(#11)
    "7#11": ({0, 4, 7, 10}, LYD_DOM, [4, 10, 6, 9]),                       # Halation 7(#11)
    "13#11": ({0, 4, 7, 10}, LYD_DOM, [4, 10, 6, 9]),
}

NOTE_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


@dataclass
class Chord:
    root_pc: int
    quality: str
    name: str
    tick: int = 0

    def text(self):
        return self.name

    @property
    def tones(self):
        return QUALITY[self.quality][0]

    @property
    def scale(self):
        return QUALITY[self.quality][1]

    @property
    def voicing(self):
        return QUALITY[self.quality][2]


CHORD_RE = re.compile(r"^([A-G])(b|#)?([^/]*)(/.*)?$")


def parse_chord(tok: str) -> Chord:
    m = CHORD_RE.match(tok)
    if not m:
        raise ValueError(f"bad chord {tok!r}")
    pc = (NOTE_PC[m.group(1)] + {None: 0, "b": -1, "#": 1}[m.group(2)]) % 12
    q = m.group(3)
    if q not in QUALITY:
        raise ValueError(f"no rhythm-section recipe for quality {q!r} ({tok})")
    return Chord(pc, q, tok)


def parse_ireal(url: str, n_bars: int = 32) -> list[list[Chord]]:
    """Bars of chords from an irealbook:// link (first n_bars bars of the chart)."""
    body = urllib.parse.unquote(url.split("://", 1)[1])
    prog = body.split("=")[5]
    prog = re.sub(r"<[^>]*>", "", prog)          # staff text
    prog = re.sub(r"\*[A-Za-z]", "", prog)        # section marks
    prog = re.sub(r"T\d\d", "", prog)             # time signatures
    prog = re.sub(r"N\d", "", prog)               # endings
    bars, prev = [], None
    for cell in re.split(r"[|\[\]{}Z]", prog):
        cell = cell.replace("Y", "").replace("Q", "").replace("S", "")
        toks = [t for t in re.split(r"[ ,]+", cell.strip()) if t and t not in ("s", "l", "p", "n")]
        if not cell.strip():
            continue
        if toks == ["x"]:
            bars.append(list(prev))
        elif toks:
            bars.append([parse_chord(t.lstrip("sl")) for t in toks])
            prev = bars[-1]
        if len(bars) == n_bars:
            break
    assert len(bars) == n_bars, len(bars)
    return bars
