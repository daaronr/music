"""Baseline for check_mix's per-bar chroma test: same measure on the original video
(vocal stem vs accompaniment stem), per sung half-bar (= one remix bar)."""
import json
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

W = Path(__file__).resolve().parents[1] / "work"
bm = json.load(open(W / "stems" / "beat_map.json"))
grid, gt = np.array(bm["grid"]), np.array(bm["t"])
sr = 22050
c2 = librosa.note_to_hz("C2")


def chroma(name):
    x, s = sf.read(str(W / "stems" / f"{name}.wav"), dtype="float32")
    y = librosa.resample(x.mean(axis=1), orig_sr=s, target_sr=sr)
    return librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=512, fmin=c2), y


cv, yv = chroma("vocals")
co, _ = chroma("other")
ft = librosa.frames_to_time(np.arange(cv.shape[1]), sr=sr, hop_length=512)
cs = []
for b in np.arange(1, 93, 2.0):
    t0, t1 = np.interp(b, grid, gt), np.interp(b + 2, grid, gt)
    sel = (ft >= t0) & (ft < t1)
    if np.sqrt(np.mean(yv[int(t0 * sr):int(t1 * sr)] ** 2)) < 0.01:
        continue
    cs.append(np.corrcoef(cv[:, sel].mean(axis=1), co[:, sel].mean(axis=1))[0, 1])
cs = np.array(cs)
print(f"original video, vocal vs accompaniment per half-bar: median corr {np.median(cs):.2f}, "
      f"share < 0.3: {np.mean(cs < 0.3):.0%} (n={len(cs)})")
