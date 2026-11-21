#!/usr/bin/env python3
"""Sanity checks on the written music: chord fit, ranges, clashes between the two solo lines.

It only flags things for a human (or me) to look at; chromatic passing notes are normal.
"""
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import engine as E  # noqa: E402
import music_head as H  # noqa: E402
import music_solo as S  # noqa: E402

SCALE = {  # pitch classes above the root that count as "inside"
    "maj7": {0, 2, 4, 6, 7, 9, 11},
    "maj7#11": {0, 2, 4, 6, 7, 9, 11},
    "m7": {0, 2, 3, 5, 7, 9, 10},
    "7": {0, 2, 4, 7, 9, 10},
    "7#11": {0, 2, 4, 6, 7, 9, 10},
    "7b9": {0, 1, 3, 4, 6, 7, 8, 10},
    "7sus": {0, 2, 5, 7, 9, 10},
    "7alt": {0, 1, 3, 4, 6, 8, 10},
}
ROLE = ["1", "b9", "9", "b3", "3", "4", "#11", "5", "b13", "13", "b7", "7"]
NAMES = ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]


def timeline(bars):
    """-> list of (bar, onset in bar, duration, midi or None, tied_in)"""
    out = []
    for bi, evs in enumerate(bars):
        pos = F(0)
        for e in evs:
            out.append((bi, pos, e.dur, E.midi(e.pitches[0]) if e.pitches else None, e.tied_in))
            pos += e.dur
    return out


def chord_at(changes, bi, pos):
    cur = changes[bi][0]
    for c in changes[bi]:
        if c[0] <= pos:
            cur = c
    return cur


def fit(name, bars, changes, lo, hi):
    print(f"\n=== {name}: chord fit (flagging outside notes) and range {lo}-{hi}")
    tl = timeline(bars)
    notes = [t for t in tl if t[3] is not None]
    print(f"    range used: {min(n[3] for n in notes)}-{max(n[3] for n in notes)} (midi)")
    for bi, pos, dur, m, tied in tl:
        if m is None:
            continue
        if not lo <= m <= hi:
            print(f"  bar {bi+1}: OUT OF RANGE midi {m}")
        _, root, qual = chord_at(changes, bi, pos)
        rpc = (E.STEP_PC[root[0]] + root[1]) % 12
        rel = (m - rpc) % 12
        if rel not in SCALE[qual] and not tied:
            strong = (pos * 4) % 1 == 0
            long_ = dur >= F(1, 4)
            tag = "LONG " if long_ else ("beat " if strong else "pass ")
            print(f"  bar {bi+1:2d} @{float(pos*4)+1:4.2f} {tag} {NAMES[m % 12]:2s} = {ROLE[rel]:3s} "
                  f"of {E.root_name(root)}{qual}")


def clashes(a, b):
    print("\n=== trumpet vs guitar: seconds/unisons sounding together")
    ta, tb = timeline(a), timeline(b)
    for bi, pa, da, ma, _ in ta:
        if ma is None:
            continue
        for bj, pb, db, mb, _ in tb:
            if bj != bi or mb is None:
                continue
            start, end = max(pa, pb), min(pa + da, pb + db)
            if end <= start:
                continue
            iv = abs(ma - mb)
            if iv % 12 in (1, 11) or iv == 0 or (iv % 12 == 2 and iv < 12):
                kind = {0: "unison", 1: "m2", 2: "M2"}.get(iv, "m9/M7")
                print(f"  bar {bi+1:2d} @{float(start*4)+1:4.2f} for {float((end-start)*4):4.2f} beats: "
                      f"tpt {NAMES[ma%12]}{ma//12-1} / gtr {NAMES[mb%12]}{mb//12-1}  {kind}")


def main():
    ch1 = E.parse_changes(H.CHANGES)
    fit("HEAD", E.parse_part(H.HEAD), ch1, 58, 82)
    tpt, gtr = E.parse_part(S.TRUMPET), E.parse_part(S.GUITAR)
    assert len(tpt) == len(gtr) == 64, (len(tpt), len(gtr))
    ch2 = ch1 + ch1
    fit("TRUMPET solo (concert)", tpt, ch2, 52, 82)   # concert E3-Bb5
    fit("GUITAR solo (sounding)", gtr, ch2, 40, 77)    # E2-F5
    clashes(tpt, gtr)
    for name, bars in (("trumpet", tpt), ("guitar", gtr)):
        rest = sum(e.dur for evs in bars for e in evs if e.is_rest)
        print(f"\n{name}: resting {float(rest):.1f} of 64 bars")


if __name__ == "__main__":
    main()
