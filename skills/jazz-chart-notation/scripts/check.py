"""Harmonic and range checks: flag every note that is outside the chord's scale.

The scales are the chord-scale choices the tune implies. Flags are not errors -
side-slips and chromatic approach notes are deliberate - but every flag should
be one we meant.
"""

from __future__ import annotations

from notation import BAR, DIV, Measure

SCALES = {
    "maj7#11": {0, 2, 4, 6, 7, 9, 11},        # lydian
    "maj9#11": {0, 2, 4, 6, 7, 9, 11},
    "maj9": {0, 2, 4, 5, 6, 7, 9, 11},        # ionian or lydian
    "maj7": {0, 2, 4, 5, 6, 7, 9, 11},
    "maj7#5": {0, 2, 4, 6, 8, 9, 11},         # lydian augmented
    "7alt": {0, 1, 3, 4, 6, 8, 10},           # altered
    "m9": {0, 2, 3, 5, 7, 9, 10},             # dorian
    "m11": {0, 2, 3, 5, 7, 9, 10},
    "m7": {0, 2, 3, 5, 7, 9, 10},
    "13#11": {0, 2, 4, 6, 7, 9, 10},          # lydian dominant
    "7#11": {0, 2, 4, 6, 7, 9, 10},
    "9#11": {0, 2, 4, 6, 7, 9, 10},
    "m7b5": {0, 2, 3, 5, 6, 8, 10},           # locrian natural 2
}
RANGES = {"trumpet": (54, 84), "guitar": (40, 81)}   # concert MIDI: F#3-C6, E2-A5


def chord_at(m: Measure, tick: int):
    current = None
    for t, ch in m.chords:
        if t <= tick:
            current = ch
    return current


def check(measures, label: str, instrument: str = "trumpet", bar_offset: int = 0,
          verbose: bool = True) -> int:
    lo, hi = RANGES[instrument]
    flags = 0
    for i, m in enumerate(measures):
        for ev in m.events:
            if not ev.pitches or ev.tie_stop:
                continue
            ch = chord_at(m, ev.start)
            for p in ev.pitches:
                if not lo <= p.midi <= hi:
                    print(f"  RANGE {label} bar {i + 1 + bar_offset}: {p.name()}")
                    flags += 1
                if ch is None or ch.suffix not in SCALES:
                    continue
                interval = (p.pc - ch.root.pc) % 12
                if interval not in SCALES[ch.suffix]:
                    beat = ev.start / DIV + 1
                    strong = ev.start % DIV == 0 or ev.dur >= DIV
                    flags += 1
                    if verbose:
                        print(f"  {'STRONG' if strong else 'weak  '} {label} bar "
                              f"{i + 1 + bar_offset} beat {beat:g}: {p.name()} over "
                              f"{ch.text()} (interval {interval})")
    return flags


def _timeline(measures):
    """[(start, end, [midi...])] in absolute ticks; tied notes merged."""
    out = []
    for i, m in enumerate(measures):
        for ev in m.events:
            if not ev.pitches:
                continue
            start, end = i * BAR + ev.start, i * BAR + ev.start + ev.dur
            if ev.tie_stop and out and out[-1][1] == start:
                out[-1] = (out[-1][0], end, out[-1][2])
            else:
                out.append((start, end, [p.midi for p in ev.pitches]))
    return out


NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]


def counterpoint(upper, lower, bar_offset=0):
    """Flag unisons and minor-2nd / minor-9th rubs between the two players.

    Checked wherever either player attacks a note while the other sounds.
    """
    a, b = _timeline(upper), _timeline(lower)
    flags = []
    for (s1, e1, m1) in a:
        for (s2, e2, m2) in b:
            start = max(s1, s2)
            if start >= min(e1, e2):
                continue
            for x in m1:
                for y in m2:
                    d = abs(x - y)
                    kind = "unison" if d == 0 else "m2/m9" if d % 12 == 1 else None
                    if kind:
                        bar = start // BAR + 1 + bar_offset
                        beat = (start % BAR) / DIV + 1
                        flags.append((bar, beat, kind, f"{NAMES[x % 12]}{x // 12 - 1}",
                                      f"{NAMES[y % 12]}{y // 12 - 1}"))
    for f in sorted(set(flags)):
        print(f"  {f[2]:7s} bar {f[0]} beat {f[1]:g}: tpt {f[3]} / gtr {f[4]}")
    return len(set(flags))


def span(measures):
    notes = [p.midi for m in measures for ev in m.events for p in ev.pitches]
    return min(notes), max(notes)
