"""Chords and melody of "The Glory of the Pumpkin" (from David's MuseScore file), plus voicing."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import numpy as np

W = Path(__file__).resolve().parents[1] / "work"
PC = dict(C=0, Db=1, D=2, Eb=3, E=4, F=5, Gb=6, G=7, Ab=8, A=9, Bb=10, B=11, **{"C#": 1, "F#": 6, "G#": 8})
QUAL = {"maj": [0, 4, 7], "": [0, 4, 7], "maj7": [0, 4, 7, 11], "maj9": [0, 4, 7, 11, 14], "7": [0, 4, 7, 10],
        "7b9": [0, 4, 7, 10, 13], "-7": [0, 3, 7, 10], "-9": [0, 3, 7, 10, 14], "dim7": [0, 3, 6, 9],
        "dim": [0, 3, 6], "+7": [0, 4, 8, 10], "6": [0, 4, 7, 9], "sus7": [0, 5, 7, 10], "sus": [0, 5, 7],
        "add9": [0, 4, 7, 14], "7sus": [0, 5, 7, 10]}
C_MAJOR = {0, 2, 4, 5, 7, 9, 11}


def parse(name):
    root = name[:2] if len(name) > 1 and name[1] in "b#" else name[:1]
    return PC[root], QUAL[name[len(root):]]


def chord_pcs(name, scale=False):
    r, iv = parse(name)
    tones = {(r + i) % 12 for i in iv}
    if not scale:
        return tones
    out = set(C_MAJOR)
    for tpc in tones:                       # an altered chord tone replaces its scale neighbour
        if tpc not in C_MAJOR:
            for nb in ((tpc - 1) % 12, (tpc + 1) % 12):
                if nb in out and nb not in tones:
                    out.discard(nb)
                    break
            out.add(tpc)
    return out


@lru_cache(maxsize=None)
def _score():
    return json.load(open(W / "score.json"))


def bar_starts():
    s, b = [], 0.0
    for m in _score():
        s.append(b)
        b += m["length"]
    return s, b


# Where the MuseScore chart differs from what the video's accompaniment plays and the voice
# sings, follow the performance (chroma check in check_chords.py).  score beat -> chord.
CHORD_FIX = {
    29.0: "G7",     # G+7 under "fellow!"; accompaniment plays G7
    35.0: "C6",     # C#dim under "head" (sung C natural)
    37.0: "G7",     # D-7 under "cook came around"; accompaniment holds G
    41.0: "G7", 43.0: "G7", 44.0: "G7",   # G7b9 / D-7 / G7 -> G7 for the whole bar
    45.0: "C",      # Csus7 under "winner" (sung E, clashes with the sus4)
    51.0: "D-7",    # Csus under "true, he was" (sung E); accompaniment plays Dm7
    59.0: "D7",     # D7b9
    67.0: "A-7",    # A7 under "Jack is in the" (sung C natural)
    69.0: "D-7",    # Dmaj7 under "lantern"; accompaniment plays Dm
    91.0: "G7",     # G7b9 under "pumpkin is the"
}


def score_chords():
    starts, total = bar_starts()
    ev = []
    for bi, m in enumerate(_score()):
        for pos, name in m["chords"]:
            b = starts[bi] + pos
            ev.append((b, CHORD_FIX.get(b, name)))
    ev.sort()
    out = []
    for k, (b, name) in enumerate(ev):
        e = ev[k + 1][0] if k + 1 < len(ev) else total + 4
        out.append((b, e, name))
    return out


def score_melody():
    starts, _ = bar_starts()
    out = []
    for bi, m in enumerate(_score()):
        for n in m["notes"]:
            out.append((starts[bi] + n["pos"], starts[bi] + n["pos"] + n["dur"], n["pitch"]))
    return out


def chords_between(b0, b1):
    """Score chords clipped to [b0, b1)."""
    out = []
    for s, e, name in score_chords():
        s2, e2 = max(s, b0), min(e, b1)
        if e2 > s2:
            out.append((s2, e2, name))
    return out


def voice(name, prev=None, lo=55, hi=79, n=4):
    """Close voicing of the chord in [lo, hi], nearest to the previous voicing."""
    r, iv = parse(name)
    pcs = [(r + i) % 12 for i in iv]
    if len(pcs) > n:                         # drop the fifth first
        fifth = (r + 7) % 12
        if fifth in pcs and len(pcs) > n:
            pcs.remove(fifth)
        pcs = pcs[:n]
    best, bestc = None, 1e9
    for base in range(lo, lo + 12):
        notes = []
        for p in pcs:
            k = base + ((p - base) % 12)
            notes.append(k)
        notes = sorted(notes)
        if notes[-1] > hi:
            continue
        cost = 0 if prev is None else sum(min(abs(a - b) for b in prev) for a in notes)
        cost += 0.15 * abs(np.mean(notes) - (lo + hi) / 2)
        if cost < bestc:
            best, bestc = notes, cost
    return best


def root_midi(name, lo=28):
    r, _ = parse(name)
    return lo + ((r - lo) % 12)
