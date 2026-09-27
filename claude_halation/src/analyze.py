"""Print a bar-by-bar harmonic analysis of the head and the duo solo, plus
range and counterpoint checks.  Usage: python3 analyze.py [head|solo|all]"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

from musiclib import BAR, analyse, parse_changes, parse_line, sounding_notes

SRC = Path(__file__).parent
changes = parse_changes((SRC / "changes.txt").read_text())

RANGES = {"head": (52, 81), "tpt": (52, 84), "gtr": (40, 76)}   # concert MIDI
NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]


def mname(m):
    return f"{NAMES[m % 12]}{m // 12 - 1}"


def range_report(label, bars):
    notes = [p.midi for bar in bars for e in bar if e.kind == "note" for p in e.pitches]
    lo, hi = min(notes), max(notes)
    rlo, rhi = RANGES[label]
    flag = "" if rlo <= lo and hi <= rhi else "   <-- OUT OF RANGE"
    print(f"{label}: range {mname(lo)}..{mname(hi)} ({len(notes)} notes){flag}")


def outside_report(label, bars, offset_bars=0):
    """Notes that are neither chord tones nor tensions, on strong beats or long."""
    from musiclib import chord_at
    issues = []
    for bar in bars:
        for e in bar:
            if e.kind != "note" or e.tie_stop:
                continue
            ch = chord_at(changes, (e.tick - offset_bars * BAR) % (32 * BAR))
            for p in e.pitches:
                iv, kind = ch.classify(p.pc)
                strong = (e.tick % 24 == 0)
                if kind == "X" or (kind == "S" and (strong or e.dur >= 24)):
                    beat = (e.tick % BAR) / 24 + 1
                    issues.append(f"  bar {e.tick // BAR + 1:>2} beat {beat:<4} {p.name():<4} "
                                  f"over {ch.text():<12} = {iv:<7} {kind}  dur={e.dur}")
    print(f"{label}: {len(issues)} notes flagged (X = outside, S = scale note on strong/long)")
    for line in issues:
        print(line)


def counterpoint(tpt_bars, gtr_bars):
    t = sounding_notes(tpt_bars)
    g = sounding_notes(gtr_bars)
    print("\nSimultaneous-interval check (sounding pitch):")
    flagged = Counter()
    for (ts, te, tm) in t:
        for (gs, ge, gm) in g:
            s, e = max(ts, gs), min(te, ge)
            if s >= e:
                continue
            iv = (tm - gm)
            cls = iv % 12
            strong = s % 24 == 0
            overlap = e - s
            tag = None
            if iv < 0:
                tag = "crossing"
            elif cls in (1, 11) and (strong or overlap >= 12):
                tag = "m2/M7"
            elif cls == 0 and overlap >= 12:
                tag = "unison/oct"
            if tag:
                flagged[tag] += 1
                beat = (s % BAR) / 24 + 1
                print(f"  bar {s // BAR + 1:>2} beat {beat:<5} tpt {mname(tm):<4} gtr {mname(gm):<4} "
                      f"iv={iv:>3} {tag} overlap={overlap}")
    print("  totals:", dict(flagged))
    # density per bar
    print("\nActivity per bar (onsets tpt/gtr):")
    row = []
    for bi in range(len(tpt_bars)):
        tn = sum(1 for e in tpt_bars[bi] if e.kind == "note" and not e.tie_stop)
        gn = sum(1 for e in gtr_bars[bi] if e.kind == "note" and not e.tie_stop)
        row.append(f"{bi + 1}:{tn}/{gn}")
    for i in range(0, len(row), 8):
        print("  " + "  ".join(row[i:i + 8]))


def main():
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("head", "all"):
        head = parse_line((SRC / "head.txt").read_text())
        print("\n".join(analyse("head", head, changes)))
        range_report("head", head)
        outside_report("head", head)
    if what in ("solo", "all"):
        tpt = parse_line((SRC / "solo_trumpet.txt").read_text())
        gtr = parse_line((SRC / "solo_guitar.txt").read_text())
        assert len(tpt) == len(gtr) == 64, (len(tpt), len(gtr))
        print("\n".join(analyse("tpt", tpt, changes)))
        print()
        print("\n".join(analyse("gtr", gtr, changes)))
        range_report("tpt", tpt)
        range_report("gtr", gtr)
        outside_report("tpt", tpt)
        outside_report("gtr", gtr)
        counterpoint(tpt, gtr)


if __name__ == "__main__":
    main()
