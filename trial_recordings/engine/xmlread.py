"""Read one part of a MusicXML file into bars of musiclib Events (24 ticks per
quarter, 4/4), so every tune goes through the same performance code.

Kept: pitches (sounding: MusicXML pitch + <transpose>), rests, chords, ties,
triplets, accents/staccato/tenuto/marcato, falls, doits, scoops, fermatas,
dynamics and hairpins.  Only 4/4 and a single voice are expected.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from fractions import Fraction

from musiclib import BAR, Event, Pitch

ART = {"accent": ">", "strong-accent": "^", "staccato": ".", "staccatissimo": ".", "tenuto": "-",
       "falloff": "f", "doit": "d", "scoop": "s", "fermata": "F"}
STEP_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def read_part(path: str, part_index: int, measures: list[int]) -> list[list[Event]]:
    root = ET.parse(path).getroot()
    part = root.findall("part")[part_index]
    all_m = part.findall("measure")
    divisions = 1
    chrom = 0
    # attributes are sticky: walk from the start so divisions/transposition are known
    state_at = {}
    for i, m in enumerate(all_m):
        for a in m.findall("attributes"):
            if a.findtext("divisions"):
                divisions = int(a.findtext("divisions"))
            t = a.find("transpose")
            if t is not None:
                chrom = int(t.findtext("chromatic") or 0) + 12 * int(t.findtext("octave-change") or 0)
        state_at[i] = (divisions, chrom)

    bars = []
    for seq, mi in enumerate(measures):
        m = all_m[mi]
        divisions, chrom = state_at[mi]
        scale = Fraction(24, divisions)
        pos = Fraction(0)
        bar: list[Event] = []
        pending = {"dynamic": None, "hairpin": None}
        for el in m:
            if el.tag == "direction":
                for d in el.iter("dynamics"):
                    for c in d:
                        pending["dynamic"] = c.tag
                for w in el.iter("wedge"):
                    typ = w.get("type")
                    pending["hairpin"] = {"crescendo": "crescendo", "diminuendo": "diminuendo"}.get(typ, "stop")
            elif el.tag == "backup":
                pos -= Fraction(int(el.findtext("duration"))) * scale
            elif el.tag == "forward":
                pos += Fraction(int(el.findtext("duration"))) * scale
            elif el.tag == "note":
                if el.find("grace") is not None:
                    continue
                dur = Fraction(int(el.findtext("duration"))) * scale
                is_chord = el.find("chord") is not None
                pitch_el = el.find("pitch")
                pitches = []
                if pitch_el is not None:
                    step = pitch_el.findtext("step")
                    alter = int(float(pitch_el.findtext("alter") or 0))
                    octv = int(pitch_el.findtext("octave"))
                    p = Pitch(step, alter, octv)
                    if chrom:
                        p = Pitch(step, alter, octv).transpose(round(chrom * 7 / 12), chrom)
                    pitches = [p]
                if is_chord and bar and bar[-1].kind == "note" and pitches:
                    bar[-1].pitches.append(pitches[0])
                    continue
                flags = ""
                for n in el.iter():
                    if n.tag in ART:
                        flags += ART[n.tag]
                ties = [t.get("type") for t in el.findall("tie")]
                assert dur.denominator == 1, (path, mi, dur)
                ev = Event("note" if pitches else "rest", pitches, "eighth", 0, int(dur))
                ev.tick = seq * BAR + int(pos)
                ev.tie_start = "start" in ties
                ev.tie_stop = "stop" in ties
                ev.flags = flags
                ev.tuplet = "mid" if el.find("time-modification") is not None else None
                ev.dynamic, ev.hairpin = pending["dynamic"], pending["hairpin"]
                pending = {"dynamic": None, "hairpin": None}
                bar.append(ev)
                pos += dur
        total = sum(e.dur for e in bar)
        if total < BAR:                      # pad an incomplete bar with a rest
            ev = Event("rest", [], "eighth", 0, BAR - total)
            ev.tick = seq * BAR + total
            bar.append(ev)
        assert sum(e.dur for e in bar) == BAR, (path, mi, total)
        bars.append(bar)
    # a tie that points at a rest or a different pitch is dropped
    flat = [e for b in bars for e in b]
    for a, b in zip(flat, flat[1:]):
        if a.tie_start and (b.kind != "note" or [p.midi for p in a.pitches] != [p.midi for p in b.pitches]):
            a.tie_start = False
    return bars


def harmony_roots(path: str, part_index: int, measures: list[int]) -> list[list[int]]:
    """Root pitch classes of the chord symbols in each measure (for cross-checks)."""
    root = ET.parse(path).getroot()
    all_m = root.findall("part")[part_index].findall("measure")
    out = []
    for mi in measures:
        roots = []
        for h in all_m[mi].iter("harmony"):
            r = h.find("root")
            if r is None:
                continue
            roots.append((STEP_PC[r.findtext("root-step")] + int(float(r.findtext("root-alter") or 0))) % 12)
        out.append(roots)
    return out
