"""Robust smooth tempo map from syllable candidates.

Uses all candidate anchors (anchors.py output before rejection is recomputed here),
fits a local-linear curve t(beat) on on-beat syllables, rejects outliers, and reports
offbeat placement (swing ratio).  Writes beat_map.json: audio time of every 1/2 beat.
"""
import json
import sys
from pathlib import Path
import numpy as np

d = Path(sys.argv[1])
cands = json.load(open(d / "anchors_all.json"))
B = np.array([c["beat"] for c in cands])
T = np.array([c["t"] for c in cands])
onb = np.abs(B - np.round(B)) < 1e-6


def loclin(bq, b, t, w, h=3.0):
    out = []
    for q in bq:
        k = w * np.exp(-0.5 * ((b - q) / h) ** 2)
        if k.sum() < 1e-6:
            out.append(np.nan)
            continue
        X = np.stack([np.ones_like(b), b - q], 1)
        W = np.diag(k)
        beta = np.linalg.lstsq(X.T @ W @ X, X.T @ W @ t, rcond=None)[0]
        out.append(beta[0])
    return np.array(out)


w = onb.astype(float)
for it in range(6):
    fit = loclin(B, B[onb | ~onb], T, w)
    res = T - fit
    sd = 1.4826 * np.median(np.abs(res[w > 0]))
    w = (onb & (np.abs(res) < max(2.5 * sd, 0.06))).astype(float)
print(f"on-beat kept {int(w.sum())}/{onb.sum()}  resid sd {sd:.3f}s")

grid = np.arange(0, 97.01, 0.5)
gt = loclin(grid, B, T, w)
# beat durations
bd = np.diff(gt[::2])
print("bpm by bar:", " ".join(f"{60/np.mean(bd[max(0,i-1):i+3]):.0f}" for i in range(1, len(bd), 4)))
# offbeat ratio: where in the beat do offbeat syllables land?
off = ~onb & (np.abs(B - np.floor(B) - 0.5) < 1e-6)
fr = []
for b, t in zip(B[off], T[off]):
    t0 = np.interp(np.floor(b), grid, gt)
    t1 = np.interp(np.floor(b) + 1, grid, gt)
    fr.append((t - t0) / (t1 - t0))
fr = np.array(fr)
print("offbeat position in beat: median", np.round(np.median(fr), 3), "IQR", np.round(np.percentile(fr, [25, 75]), 3))
res_on = (T - np.interp(B, grid, gt))
for c, r, k in zip(cands, res_on, w):
    flag = "" if k else ("  off" if not onb[cands.index(c)] else "  REJ")
    print(f"bar {c['bar']:2d} beat {c['beat']:6.2f} t {c['t']:6.2f} res {r:+.3f} {c['text']}{flag}")
json.dump(dict(grid=grid.tolist(), t=gt.tolist(), offbeat_frac=float(np.median(fr))), open(d / "beat_map.json", "w"))
