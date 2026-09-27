"""Small jazz-chart DSL -> MusicXML writer (MusicXML 3.1, tested with MuseScore 3.6).

Measure strings are whitespace-separated tokens. All pitches are CONCERT pitch;
transposing parts are produced at write time.

  C5/q.            note: pitch + duration (w h. h q. q 8. 8 16)
  r/8              rest
  C4+E4/q          chord / double stop (pitches joined with '+')
  C5/q~            tie into the next note (next note must repeat the pitch)
  (C5/8  D5/8)     slur start '(' prefix, slur stop ')' suffix
  C5/8!acc!fall    articulations: acc stac ten marc fall doit scoop ferm
  3{C5/8 D5/8 E5/8}  triplet group; inner durations are scaled by 2/3
  @mf @f ...       dynamics (pp p mp mf f ff)
  @cresc @dim @endw  hairpin start / stop
  @txt=Some_text   expression text (underscores become spaces)
  @ann=Some_text   analysis annotation; only printed when annotations are on
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from xml.sax.saxutils import escape

DIV = 12  # divisions per quarter note
BAR = 4 * DIV

DUR = {"w": 48, "h.": 36, "h": 24, "q.": 18, "q": 12, "8.": 9, "8": 6, "16": 3}
TYPE = {"w": ("whole", 0), "h.": ("half", 1), "h": ("half", 0), "q.": ("quarter", 1),
        "q": ("quarter", 0), "8.": ("eighth", 1), "8": ("eighth", 0), "16": ("16th", 0)}
STEPS = "CDEFGAB"
NAT = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
ACC = {"": 0, "#": 1, "##": 2, "b": -1, "bb": -2}
ARTS = {"acc", "stac", "ten", "marc", "fall", "doit", "scoop", "ferm"}
AWKWARD = {("B", 1), ("E", 1), ("C", -1), ("F", -1)}
DYN = {"pp", "p", "mp", "mf", "f", "ff"}

NOTE_RE = re.compile(
    r"^(\()?((?:[A-G](?:##|#|bb|b)?-?\d)(?:\+[A-G](?:##|#|bb|b)?-?\d)*|r)"
    r"/(w|h\.|h|q\.|q|8\.|8|16)(~)?(\))?((?:![a-z]+)*)(~)?$")
PITCH_RE = re.compile(r"^([A-G])(##|#|bb|b)?(-?\d)$")


# ---------------------------------------------------------------- pitches

@dataclass(frozen=True)
class Pitch:
    step: str
    alter: int
    octave: int

    @property
    def midi(self) -> int:
        return 12 * (self.octave + 1) + NAT[self.step] + self.alter

    @property
    def pc(self) -> int:
        return self.midi % 12

    def name(self) -> str:
        acc = {0: "", 1: "#", 2: "##", -1: "b", -2: "bb"}[self.alter]
        return f"{self.step}{acc}{self.octave}"

    def transpose(self, dia: int, chrom: int, simplify: bool = False) -> "Pitch":
        idx = STEPS.index(self.step) + dia
        octave = self.octave + idx // 7
        step = STEPS[idx % 7]
        target = self.midi + chrom
        alter = target - (12 * (octave + 1) + NAT[step])
        p = Pitch(step, alter, octave)
        return p.simplified() if simplify else p

    def simplified(self) -> "Pitch":
        """Respell double accidentals and B#/E#/Cb/Fb for easier reading."""
        if abs(self.alter) <= 1 and (self.step, self.alter) not in AWKWARD:
            return self
        m = self.midi
        for alter in ((0, 1, -1) if self.alter > 0 else (0, -1, 1)):
            for step in STEPS:
                if (m - NAT[step] - alter) % 12 == 0 and (step, alter) not in AWKWARD:
                    return Pitch(step, alter, (m - NAT[step] - alter) // 12 - 1)
        return self


def parse_pitch(s: str) -> Pitch:
    m = PITCH_RE.match(s)
    if not m:
        raise ValueError(f"bad pitch {s!r}")
    return Pitch(m.group(1), ACC[m.group(2) or ""], int(m.group(3)))


# ---------------------------------------------------------------- chord symbols

# suffix -> (MusicXML kind, display text, [(degree, alter, type)])
KINDS = {
    "maj7#11": ("major-seventh", "maj7#11", [(11, 1, "add")]),
    "maj9#11": ("major-ninth", "maj9#11", [(11, 1, "add")]),
    "maj7#5": ("major-seventh", "maj7#5", [(5, 1, "alter")]),
    "maj9": ("major-ninth", "maj9", []),
    "maj7": ("major-seventh", "maj7", []),
    "m(maj7)": ("major-minor", "m(maj7)", []),
    "m7b5": ("half-diminished", "m7b5", []),
    "m11": ("minor-11th", "m11", []),
    "m9": ("minor-ninth", "m9", []),
    "m7": ("minor-seventh", "m7", []),
    "13#11": ("dominant-13th", "13#11", [(11, 1, "add")]),
    "9#11": ("dominant-ninth", "9#11", [(11, 1, "add")]),
    "7#11": ("dominant", "7#11", [(11, 1, "add")]),
    "7alt": ("other", "7alt", []),   # MuseScore drops the text if kind is "dominant"
    "13": ("dominant-13th", "13", []),
    "7sus4": ("suspended-fourth", "7sus4", [(7, -1, "add")]),
    "7": ("dominant", "7", []),
    "": ("major", "", []),
}
CHORD_RE = re.compile(r"^([A-G])(#|b)?(.*?)(?:/([A-G])(#|b)?)?$")


@dataclass
class ChordSym:
    root: Pitch            # octave ignored
    suffix: str
    bass: Pitch | None = None

    @staticmethod
    def parse(s: str) -> "ChordSym":
        m = CHORD_RE.match(s)
        if not m or m.group(3) not in KINDS:
            raise ValueError(f"unknown chord symbol {s!r}")
        root = Pitch(m.group(1), ACC[m.group(2) or ""], 4)
        bass = Pitch(m.group(4), ACC[m.group(5) or ""], 3) if m.group(4) else None
        return ChordSym(root, m.group(3), bass)

    def transpose(self, dia: int, chrom: int) -> "ChordSym":
        r = self.root.transpose(dia, chrom, simplify=True)
        b = self.bass.transpose(dia, chrom, simplify=True) if self.bass else None
        return ChordSym(r, self.suffix, b)

    def text(self) -> str:
        acc = {0: "", 1: "#", -1: "b"}
        s = self.root.step + acc[self.root.alter] + self.suffix
        if self.bass:
            s += "/" + self.bass.step + acc[self.bass.alter]
        return s

    def xml(self, offset: int = 0) -> str:
        kind, text, degrees = KINDS[self.suffix]
        out = ["<harmony print-frame=\"no\">",
               f"<root><root-step>{self.root.step}</root-step>"
               + (f"<root-alter>{self.root.alter}</root-alter>" if self.root.alter else "")
               + "</root>",
               f"<kind text=\"{escape(text)}\">{kind}</kind>"]
        if self.bass:
            out.append(f"<bass><bass-step>{self.bass.step}</bass-step>"
                       + (f"<bass-alter>{self.bass.alter}</bass-alter>" if self.bass.alter else "")
                       + "</bass>")
        for value, alter, dtype in degrees:
            out.append(f"<degree><degree-value>{value}</degree-value><degree-alter>{alter}"
                       f"</degree-alter><degree-type>{dtype}</degree-type></degree>")
        if offset:
            out.append(f"<offset>{offset}</offset>")
        out.append("</harmony>")
        return "".join(out)


# ---------------------------------------------------------------- events

@dataclass
class Event:
    pitches: list            # [] for a rest
    dur: int                 # ticks
    ntype: str
    dots: int
    tuplet: str | None = None       # None / "start" / "mid" / "stop"
    tie_start: bool = False
    tie_stop: bool = False
    slur_start: bool = False
    slur_stop: bool = False
    arts: list = field(default_factory=list)
    dirs: list = field(default_factory=list)   # (kind, value) before the note
    start: int = 0


@dataclass
class Measure:
    events: list
    chords: list = field(default_factory=list)   # [(tick, ChordSym)]
    rehearsal: str | None = None
    new_system: bool = False
    new_page: bool = False
    barline: str | None = None   # "light-light" / "light-heavy"
    texts: list = field(default_factory=list)    # [(tick, text, placement)]
    implicit: bool = False       # excluded from bar numbering (intro bars)


def _event_from_token(tok: str, scale: float) -> Event:
    m = NOTE_RE.match(tok)
    if not m:
        raise ValueError(f"bad token {tok!r}")
    slur_open, pstr, d, tie, slur_close, arts, tie_after = m.groups()
    tie = tie or tie_after
    pitches = [] if pstr == "r" else [parse_pitch(p) for p in pstr.split("+")]
    ntype, dots = TYPE[d]
    dur = DUR[d] * scale
    if abs(dur - round(dur)) > 1e-9:
        raise ValueError(f"duration of {tok!r} is not representable")
    art_list = [a for a in arts.split("!") if a]
    for a in art_list:
        if a not in ARTS:
            raise ValueError(f"unknown articulation {a!r} in {tok!r}")
    return Event(pitches, int(round(dur)), ntype, dots, tie_start=bool(tie),
                 slur_start=bool(slur_open), slur_stop=bool(slur_close), arts=art_list)


def parse_measure(text: str, where: str = "") -> list:
    tokens = re.findall(r"3\{|\}|[^\s{}]+", text)
    events, pending_dirs = [], []
    in_tuplet, tuplet_events = False, []
    for tok in tokens:
        if tok == "3{":
            in_tuplet, tuplet_events = True, []
            continue
        if tok == "}":
            if not tuplet_events:
                raise ValueError(f"empty tuplet in {where}")
            tuplet_events[0].tuplet = "start"
            tuplet_events[-1].tuplet = "stop"
            for ev in tuplet_events[1:-1]:
                ev.tuplet = "mid"
            in_tuplet = False
            continue
        if tok.startswith("@"):
            body = tok[1:]
            if body in DYN:
                pending_dirs.append(("dyn", body))
            elif body in ("cresc", "dim", "endw"):
                pending_dirs.append(("wedge", body))
            elif body.startswith("txt="):
                pending_dirs.append(("txt", body[4:].replace("_", " ")))
            elif body.startswith("ann="):
                pending_dirs.append(("ann", body[4:].replace("_", " ")))
            else:
                raise ValueError(f"unknown direction {tok!r} in {where}")
            continue
        ev = _event_from_token(tok, 2 / 3 if in_tuplet else 1)
        ev.dirs, pending_dirs = pending_dirs, []
        events.append(ev)
        if in_tuplet:
            tuplet_events.append(ev)
    if pending_dirs:  # trailing directions attach to a zero-length anchor at bar end
        raise ValueError(f"directions after the last note in {where}")
    t = 0
    for ev in events:
        ev.start = t
        t += ev.dur
    if t != BAR:
        raise ValueError(f"measure {where} has {t / DIV} beats: {text}")
    return events


def parse_chords(text: str | None) -> list:
    """'Ebmaj7#11' -> one chord on beat 1; 'F#m11 F7#11' -> beats 1 and 3;
    explicit placement: 'Cm7@1 F7@4'."""
    if not text:
        return []
    items = text.split()
    out = []
    if all("@" in it for it in items):
        for it in items:
            sym, beat = it.split("@")
            out.append((int(round((float(beat) - 1) * DIV)), ChordSym.parse(sym)))
        return out
    step = BAR // len(items)
    return [(i * step, ChordSym.parse(sym)) for i, sym in enumerate(items)]


def link_ties(measures: list) -> None:
    """Mark the tie-stop on the note that follows each tie-start."""
    flat = [ev for m in measures for ev in m.events]
    for a, b in zip(flat, flat[1:]):
        if a.tie_start:
            if not b.pitches or [p.midi for p in a.pitches] != [p.midi for p in b.pitches]:
                raise ValueError(f"tie from {[p.name() for p in a.pitches]} does not "
                                 f"reach the same pitch")
            b.tie_stop = True
