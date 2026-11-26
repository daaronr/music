"""Is the vocal in the same key as the backing?  Best chroma shift per section, and overall."""
import json
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
W = ROOT / "work"
tl = json.load(open(W / "timeline.json"))
sr = 22050


def load(name):
    x, s = sf.read(str(W / "mix_stems" / f"{name}.wav"), dtype="float32")
    return librosa.resample(x.mean(axis=1), orig_sr=s, target_sr=sr)


v = load("vocals")
mu = load("music")
cv = librosa.feature.chroma_cqt(y=v, sr=sr, hop_length=1024, fmin=librosa.note_to_hz("C2"))
cm = librosa.feature.chroma_cqt(y=mu, sr=sr, hop_length=1024, fmin=librosa.note_to_hz("C2"))
ft = librosa.frames_to_time(np.arange(cv.shape[1]), sr=sr, hop_length=1024)
names = list(tl["sections"])
for a, b in zip(names, names[1:]):
    sel = (ft >= tl["sections"][a]) & (ft < tl["sections"][b])
    pv, pm = cv[:, sel].mean(axis=1), cm[:, sel].mean(axis=1)
    cs = [np.corrcoef(np.roll(pv, k), pm)[0, 1] for k in range(12)]
    k = int(np.argmax(cs))
    print(f"{a:12s} corr at shift 0: {cs[0]:+.2f}  best shift {k:+d} ({cs[k]:+.2f})  "
          f"vocal top pcs {np.argsort(pv)[::-1][:4]}  music top pcs {np.argsort(pm)[::-1][:4]}")

# original video: accompaniment ("other") vs vocal, before any processing
o, s = sf.read(str(W / "stems" / "other.wav"), dtype="float32")
vv, _ = sf.read(str(W / "stems" / "vocals.wav"), dtype="float32")
o = librosa.resample(o.mean(axis=1), orig_sr=s, target_sr=sr)
vv = librosa.resample(vv.mean(axis=1), orig_sr=s, target_sr=sr)
po = librosa.feature.chroma_cqt(y=o, sr=sr, hop_length=1024).mean(axis=1)
pv = librosa.feature.chroma_cqt(y=vv, sr=sr, hop_length=1024).mean(axis=1)
cs = [np.corrcoef(np.roll(pv, k), po)[0, 1] for k in range(12)]
print(f"\noriginal video: vocal vs accompaniment corr at 0: {cs[0]:+.2f}, best shift {int(np.argmax(cs))}")
print("accompaniment top pcs", np.argsort(po)[::-1][:5], " vocal top pcs", np.argsort(pv)[::-1][:5])
