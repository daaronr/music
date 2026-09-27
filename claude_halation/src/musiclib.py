"""Small toolkit for writing jazz lead sheets and duo solos as text, checking
them, and emitting MusicXML that MuseScore 3 imports cleanly.

Text notation (one file per instrument line), whitespace separated tokens:

    C#5/8      note C#5, eighth.  Durations: 1 2 4 8 16 32, dots allowed (4. 8.)
    Bb4        note with the previous duration (durations are sticky)
    r/4        rest
    <D4 A4>/4  simultaneous notes (double stop)
    ~          suffix: tie to the next note (same pitch)   e.g. G4/2~
    @...       suffix flags: > accent, ^ marcato, . staccato, - tenuto,
               f fall, d doit, s scoop, g ghost, F fermata, b breath mark after
    { ... }    triplet group (3 in the time of 2)
    g:Eb5      grace note before the next note
    ( )        slur start / slur stop (standalone tokens, before/after notes)
    !mf        dynamic attached to the next note
    !cresc !dim !end   hairpin start / stop at the next note
    "text"     staff text above the next note ("_text" puts it below)
    |          bar line (bars are validated to 4/4)
    %          comment to end of line
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from fractions import Fraction
from xml.sax.saxutils import escape

DIV = 24                     # divisions per quarter note
BAR = 4 * DIV                # 4/4 only
STEPS = "CDEFGAB"
STEP_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

# ---------------------------------------------------------------- pitches


@dataclass(frozen=True)
class Pitch:
    step: str
    alter: int
    octave: int

    @property
    def midi(self) -> int:
        return 12 * (self.octave + 1) + STEP_PC[self.step] + self.alter

    @property
    def pc(self) -> int:
        return self.midi % 12

    def name(self) -> str:
        acc = {-2: "bb", -1: "b", 0: "", 1: "#", 2: "##"}[self.alter]
        return f"{self.step}{acc}{self.octave}"

    def transpose(self, steps: int, semis: int) -> "Pitch":
        idx = STEPS.index(self.step) + steps
        octave = self.octave + idx // 7
        step = STEPS[idx % 7]
        natural = 12 * (octave + 1) + STEP_PC[step]
        alter = self.midi + semis - natural
        if abs(alter) > 2:
            raise ValueError(f"cannot spell {self.name()} moved {steps}/{semis}")
        return Pitch(step, alter, octave)


PITCH_RE = re.compile(r"^([A-G])(##|bb|#|b|n)?(-?\d)$")


def parse_pitch(text: str) -> Pitch:
    m = PITCH_RE.match(text)
    if not m:
        raise ValueError(f"bad pitch {text!r}")
    acc = m.group(2) or ""
    alter = {"": 0, "n": 0, "#": 1, "##": 2, "b": -1, "bb": -2}[acc]
    return Pitch(m.group(1), alter, int(m.group(3)))


# ---------------------------------------------------------------- chords

ROOT_RE = re.compile(r"^([A-G])(b|#)?(.*)$")

# suffix -> (chord tones, tensions, scale) as semitone sets above the root.
CHORD_TYPES = {
    "maj7#11":   ({0, 4, 7, 11}, {2, 6, 9}, {0, 2, 4, 6, 7, 9, 11}),
    "maj7#5":    ({0, 4, 8, 11}, {2, 6, 9}, {0, 2, 4, 6, 8, 9, 11}),
    "7sus(b9)":  ({0, 5, 7, 10, 1}, {3, 8}, {0, 1, 3, 5, 7, 8, 10}),
    "7alt":      ({0, 4, 10}, {1, 3, 6, 8}, {0, 1, 3, 4, 6, 8, 10}),
    "m9":        ({0, 3, 7, 10, 2}, {5, 9}, {0, 2, 3, 5, 7, 9, 10}),
    "13sus":     ({0, 5, 7, 10}, {2, 9}, {0, 2, 5, 7, 9, 10}),
    "m7":        ({0, 3, 7, 10}, {2, 5}, {0, 2, 3, 5, 7, 8, 9, 10}),
    "7":         ({0, 4, 7, 10}, {2, 9, 1, 3, 8, 6}, {0, 1, 2, 3, 4, 6, 7, 8, 9, 10}),
    "7(b9)":     ({0, 4, 7, 10, 1}, {3, 8}, {0, 1, 3, 4, 5, 7, 8, 10}),
    "m7b5":      ({0, 3, 6, 10}, {2, 5, 8}, {0, 1, 2, 3, 5, 6, 8, 10}),
    "m(maj7)":   ({0, 3, 7, 11}, {2, 5, 9}, {0, 2, 3, 5, 7, 9, 11}),
    "9(#11)":    ({0, 4, 7, 10, 2}, {6, 9}, {0, 2, 4, 6, 7, 9, 10}),
    "7(#11)":    ({0, 4, 7, 10}, {2, 6, 9}, {0, 2, 4, 6, 7, 9, 10}),
}

INTERVAL_NAMES = {0: "1", 1: "b9", 2: "9", 3: "b3/#9", 4: "3", 5: "11", 6: "#11/b5",
                  7: "5", 8: "b13/#5", 9: "13", 10: "b7", 11: "7"}

# How each suffix is written for MuseScore's chord parser (typed text).
MSCORE_NAME = {"maj7#11": "maj7#11", "maj7#5": "maj7#5", "7sus(b9)": "7sus(b9)",
               "7alt": "7alt", "m9": "m9", "13sus": "13sus", "m7": "m7", "7": "7",
               "7(b9)": "7(b9)", "m7b5": "m7b5", "m(maj7)": "m(maj7)",
               "9(#11)": "9(#11)", "7(#11)": "7(#11)"}

# MusicXML <kind> for the interchange file (MuseScore re-derives some names).
XML_KIND = {"maj7#11": ("major-seventh", "maj7", [(11, 1, "add")]),
            "maj7#5": ("major-seventh", "maj7", [(5, 1, "alter")]),
            "7sus(b9)": ("suspended-fourth", "7sus", [(7, 0, "add"), (9, -1, "add")]),
            "7alt": ("dominant", "7", [(5, 1, "alter"), (9, 1, "add"), (9, -1, "add")]),
            "m9": ("minor-ninth", "m9", []),
            "13sus": ("suspended-fourth", "13sus", [(7, 0, "add"), (9, 0, "add"), (13, 0, "add")]),
            "m7": ("minor-seventh", "m7", []),
            "7": ("dominant", "7", []),
            "7(b9)": ("dominant", "7", [(9, -1, "add")]),
            "m7b5": ("half-diminished", "m7b5", []),
            "m(maj7)": ("major-minor", "m(maj7)", []),
            "9(#11)": ("dominant-ninth", "9", [(11, 1, "add")]),
            "7(#11)": ("dominant", "7", [(11, 1, "add")])}

TPC_BASE = {"F": 13, "C": 14, "G": 15, "D": 16, "A": 17, "E": 18, "B": 19}


@dataclass
class Chord:
    root_step: str
    root_alter: int
    suffix: str
    tick: int              # absolute tick from the start of the piece

    @property
    def root_pc(self) -> int:
        return (STEP_PC[self.root_step] + self.root_alter) % 12

    def root_name(self) -> str:
        return self.root_step + {-1: "b", 0: "", 1: "#"}[self.root_alter]

    def text(self) -> str:
        return self.root_name() + self.suffix

    def tpc(self) -> int:
        return TPC_BASE[self.root_step] + 7 * self.root_alter

    def transposed(self, steps: int, semis: int) -> "Chord":
        p = Pitch(self.root_step, self.root_alter, 4).transpose(steps, semis)
        return Chord(p.step, p.alter, self.suffix, self.tick)

    def classify(self, pc: int) -> tuple[str, str]:
        tones, tens, scale = CHORD_TYPES[self.suffix]
        iv = (pc - self.root_pc) % 12
        if iv in tones:
            kind = "CT"
        elif iv in tens:
            kind = "T"
        elif iv in scale:
            kind = "S"
        else:
            kind = "X"
        return INTERVAL_NAMES[iv], kind


def parse_chord(text: str, tick: int) -> Chord:
    m = ROOT_RE.match(text)
    if not m:
        raise ValueError(f"bad chord {text!r}")
    suffix = m.group(3)
    if suffix not in CHORD_TYPES:
        raise ValueError(f"unknown chord suffix {suffix!r} in {text!r}")
    alter = {None: 0, "b": -1, "#": 1}[m.group(2)]
    return Chord(m.group(1), alter, suffix, tick)


def parse_changes(text: str) -> list[list[Chord]]:
    """One line per bar: 'Fmaj7#11' or 'Cm7 F7' (beats 1 & 3) or 'C@1 D@2.5'."""
    bars: list[list[Chord]] = []
    for raw in text.splitlines():
        line = raw.split("%", 1)[0].strip()
        if not line:
            continue
        if ":" in line.split()[0]:
            line = line.split(":", 1)[1].strip()
        items = line.split()
        base = len(bars) * BAR
        chords = []
        for i, item in enumerate(items):
            if "@" in item:
                name, beat = item.split("@")
                off = int((Fraction(beat) - 1) * DIV)
            else:
                name = item
                off = i * (BAR // len(items))
            chords.append(parse_chord(name, base + off))
        bars.append(chords)
    return bars


# ---------------------------------------------------------------- events

DUR_BASE = {"1": ("whole", 96), "2": ("half", 48), "4": ("quarter", 24),
            "8": ("eighth", 12), "16": ("16th", 6), "32": ("32nd", 3)}
DUR_RE = re.compile(r"^(1|2|4|8|16|32)(\.{0,2})$")


def dur_value(code: str) -> tuple[str, int, int]:
    m = DUR_RE.match(code)
    if not m:
        raise ValueError(f"bad duration {code!r}")
    typ, base = DUR_BASE[m.group(1)]
    dots = len(m.group(2))
    total = base
    add = base
    for _ in range(dots):
        add //= 2
        total += add
    return typ, dots, total


@dataclass
class Event:
    kind: str                       # "note" | "rest"
    pitches: list[Pitch]
    typ: str
    dots: int
    dur: int                        # sounding duration in divisions
    tick: int = 0                   # absolute onset
    tie_start: bool = False
    tie_stop: bool = False
    flags: str = ""
    tuplet: str | None = None       # None | "start" | "mid" | "stop"
    graces: list[Pitch] = field(default_factory=list)
    slur_start: bool = False
    slur_stop: bool = False
    dynamic: str | None = None
    hairpin: str | None = None      # "crescendo" | "diminuendo" | "stop"
    texts: list[tuple[str, str]] = field(default_factory=list)   # (placement, text)
    src: str = ""


TOKEN_RE = re.compile(r'"[^"]*"|\{|\}|<[^>]*>[^\s]*|[^\s{}]+')


def parse_line(text: str, start_tick: int = 0) -> list[list[Event]]:
    """Parse instrument text into bars of events. Validates 4/4 bar lengths."""
    cleaned = "\n".join(l.split("%", 1)[0] for l in text.splitlines())
    tokens = TOKEN_RE.findall(cleaned)
    bars: list[list[Event]] = [[]]
    last_dur = "4"
    in_tuplet = False
    pending: dict = {"graces": [], "slur_start": False, "dynamic": None,
                     "hairpin": None, "texts": []}
    tick = start_tick
    for tok in tokens:
        if tok == "|":
            bars.append([])
            continue
        if tok == "{":
            in_tuplet = True
            tuplet_first = True
            continue
        if tok == "}":
            in_tuplet = False
            evs = [e for e in bars[-1] if e.tuplet]
            evs[-1].tuplet = "stop"
            continue
        if tok == "(":
            pending["slur_start"] = True
            continue
        if tok == ")":
            last = _last_event(bars)
            last.slur_stop = True
            continue
        if tok.startswith('"'):
            body = tok.strip('"')
            place = "above"
            if body.startswith("_"):
                place, body = "below", body[1:]
            pending["texts"].append((place, body))
            continue
        if tok.startswith("!"):
            word = tok[1:]
            if word in ("cresc", "dim"):
                pending["hairpin"] = "crescendo" if word == "cresc" else "diminuendo"
            elif word == "end":
                pending["hairpin"] = "stop"
            else:
                pending["dynamic"] = word
            continue
        if tok.startswith("g:"):
            pending["graces"].append(parse_pitch(tok[2:]))
            continue
        # note / rest / chord token
        tie = tok.endswith("~")
        if tie:
            tok = tok[:-1]
        flags = ""
        if "@" in tok:
            tok, flags = tok.split("@", 1)
        if "/" in tok and not tok.startswith("<"):
            head, dcode = tok.split("/", 1)
        elif tok.startswith("<"):
            close = tok.index(">")
            head, rest = tok[:close + 1], tok[close + 1:]
            dcode = rest[1:] if rest.startswith("/") else ""
        else:
            head, dcode = tok, ""
        if dcode:
            last_dur = dcode
        typ, dots, dur = dur_value(last_dur)
        if in_tuplet:
            dur = dur * 2 // 3
        if head == "r":
            ev = Event("rest", [], typ, dots, dur)
        elif head.startswith("<"):
            ev = Event("note", [parse_pitch(p) for p in head[1:-1].split()], typ, dots, dur)
        else:
            ev = Event("note", [parse_pitch(head)], typ, dots, dur)
        ev.tie_start = tie
        ev.flags = flags
        ev.src = tok
        if in_tuplet:
            ev.tuplet = "start" if tuplet_first else "mid"
            tuplet_first = False
        ev.graces = pending["graces"]
        ev.slur_start = pending["slur_start"]
        ev.dynamic = pending["dynamic"]
        ev.hairpin = pending["hairpin"]
        ev.texts = pending["texts"]
        pending = {"graces": [], "slur_start": False, "dynamic": None,
                   "hairpin": None, "texts": []}
        ev.tick = tick
        tick += ev.dur
        bars[-1].append(ev)
    if not bars[-1]:
        bars.pop()
    # validate bar lengths and tie continuity
    for i, bar in enumerate(bars):
        total = sum(e.dur for e in bar)
        if total != BAR:
            raise ValueError(f"bar {i + 1}: length {total}/{BAR}: "
                             + " ".join(e.src for e in bar))
    flat = [e for bar in bars for e in bar]
    for a, b in zip(flat, flat[1:]):
        if a.tie_start:
            if b.kind != "note" or [p.midi for p in a.pitches] != [p.midi for p in b.pitches]:
                raise ValueError(f"tie from {a.src} at tick {a.tick} to non-matching {b.src}")
            b.tie_stop = True
    return bars


def _last_event(bars):
    for bar in reversed(bars):
        if bar:
            return bar[-1]
    raise ValueError("no event to attach to")


# ---------------------------------------------------------------- analysis

def chord_at(changes: list[list[Chord]], tick: int) -> Chord:
    flat = [c for bar in changes for c in bar]
    cur = flat[0]
    for c in flat:
        if c.tick <= tick:
            cur = c
        else:
            break
    return cur


def analyse(name: str, bars: list[list[Event]], changes: list[list[Chord]],
            offset_bars: int = 0) -> list[str]:
    """Label every note against the chord sounding at its onset."""
    out = []
    for bi, bar in enumerate(bars):
        cells = []
        for e in bar:
            if e.kind == "rest":
                cells.append(f"r{e.dur // 12 if e.dur % 12 == 0 else e.dur}")
                continue
            if e.tie_stop:
                cells.append("~")
                continue
            ch = chord_at(changes, (e.tick - offset_bars * BAR) % (len(changes) * BAR))
            labels = []
            for p in e.pitches:
                iv, kind = ch.classify(p.pc)
                mark = "" if kind in ("CT", "T") else ("·" if kind == "S" else "!!")
                labels.append(f"{p.name()}={iv}{mark}")
            cells.append("+".join(labels))
        ch_names = " ".join(c.text() for c in changes[(bi) % len(changes)])
        out.append(f"{name} {bi + 1 + offset_bars:>3} [{ch_names:<22}] " + "  ".join(cells))
    return out


def sounding_notes(bars, octave_shift=0):
    """List of (start, end, midi) for sustained sounding notes (ties merged)."""
    res = []
    cur = None
    for bar in bars:
        for e in bar:
            if e.kind != "note":
                if cur:
                    res.extend(cur)
                    cur = None
                continue
            if e.tie_stop and cur:
                cur = [(s, e.tick + e.dur, m) for (s, _, m) in cur]
            else:
                if cur:
                    res.extend(cur)
                cur = [(e.tick, e.tick + e.dur, p.midi + 12 * octave_shift) for p in e.pitches]
    if cur:
        res.extend(cur)
    return res
