"""Cut the Iowa MIS trumpet runs into single notes, verify each pitch, and
cache them as one .npz (mono float32, level-matched per dynamic layer)."""
from __future__ import annotations

from pathlib import Path

import numpy as np

from pitch import estimate_midi
from samples import CACHE, SR, read_aiff

SRC = CACHE / "iowa_trumpet"
OUT = CACHE / "trumpet_notes.npz"
FILES = {  # file -> first MIDI note of the chromatic run
    "Trumpet.novib.mf.E3B3.aiff": 52, "Trumpet.novib.mf.C4B4.aiff": 60,
    "Trumpet.novib.mf.C5B5.aiff": 72, "Trumpet.novib.mf.C6D6.aiff": 84,
    "Trumpet.novib.ff.E3B3.aiff": 52, "Trumpet.novib.ff.C4B4.aiff": 60,
    "Trumpet.novib.ff.C5B5.aiff": 72, "Trumpet.novib.ff.C6Eb6.aiff": 84,
}
NAMES = {"E3B3": 8, "C4B4": 12, "C5B5": 12, "C6D6": 3, "C6Eb6": 4}


def segments(x: np.ndarray, expected: int):
    mono = x[:, 0]
    win = 441
    n = len(mono) // win
    rms = np.sqrt((mono[:n * win].reshape(n, win) ** 2).mean(axis=1) + 1e-12)
    db = 20 * np.log10(rms)
    for thresh in (40, 35, 45, 30, 50):
        active = db > db.max() - thresh
        runs, start = [], None
        for i, a in enumerate(active):
            if a and start is None:
                start = i
            if not a and start is not None:
                runs.append([start, i])
                start = None
        if start is not None:
            runs.append([start, n])
        merged = []
        for r in runs:                       # bridge dropouts shorter than 0.25 s
            if merged and r[0] - merged[-1][1] < 25:
                merged[-1][1] = r[1]
            else:
                merged.append(r)
        merged = [r for r in merged if r[1] - r[0] > 40]     # notes are > 0.4 s
        if len(merged) == expected:
            return [(a * win, b * win) for a, b in merged]
    raise SystemExit(f"could not find {expected} notes (got {len(merged)})")


def main():
    store = {}
    for fname, first in FILES.items():
        x = read_aiff(SRC / fname)
        dyn = fname.split(".")[2]
        rng = fname.split(".")[3]
        segs = segments(x, NAMES[rng])
        for k, (a, b) in enumerate(segs):
            midi = first + k
            a = max(0, a - int(0.004 * SR))
            note = x[a:b + int(0.25 * SR), 0].copy()
            # onset: first sample above 5% of the note's peak
            peak = np.abs(note).max()
            on = int(np.argmax(np.abs(note) > 0.05 * peak))
            note = note[max(0, on - int(0.002 * SR)):]
            mid = note[int(0.4 * SR):int(0.4 * SR) + 8192]
            est = estimate_midi(mid)
            ok = abs(est - midi) < 0.5
            steady = np.sqrt(np.mean(note[int(0.2 * SR):int(0.8 * SR)] ** 2))
            print(f"{dyn} {midi:>3} est {est:6.2f} {'ok ' if ok else 'BAD'} len {len(note) / SR:5.2f}s "
                  f"rms {20 * np.log10(steady):6.1f} dB")
            if not ok:
                raise SystemExit("pitch mismatch")
            store[f"{dyn}_{midi}"] = note.astype(np.float32)
            store[f"{dyn}_{midi}_rms"] = np.float32(steady)
            store[f"{dyn}_{midi}_tune"] = np.float32(est - midi)
    np.savez_compressed(OUT, **store)
    print("saved", OUT)


if __name__ == "__main__":
    main()
