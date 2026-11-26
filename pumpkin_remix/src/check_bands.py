"""Band energy (dB, relative to the full mix total) of each mix stem, plus K-weighted loudness."""
from pathlib import Path

import librosa
import numpy as np
import pyloudnorm as pyln
import soundfile as sf

W = Path(__file__).resolve().parents[1] / "work"
BANDS = [(20, 60), (60, 250), (250, 2000), (2000, 6000), (6000, 20000)]
res = {}
for k in ["low", "music", "drums", "vocals", "fx"]:
    x, sr = sf.read(str(W / "mix_stems" / f"{k}.wav"), dtype="float32")
    x = x * 2
    sp = np.abs(librosa.stft(x.mean(axis=1), n_fft=8192, hop_length=4096)) ** 2
    f = librosa.fft_frequencies(sr=sr, n_fft=8192)
    res[k] = [sp[(f >= a) & (f < b)].sum() for a, b in BANDS]
    res[k].append(pyln.Meter(sr).integrated_loudness(x.astype(np.float64)))
tot = sum(sum(v[:5]) for v in res.values())
print("stem     " + "  ".join(f"{a}-{b}".rjust(10) for a, b in BANDS) + "     LUFS")
for k, v in res.items():
    print(f"{k:8s} " + "  ".join(f"{10*np.log10(e/tot+1e-12):10.1f}" for e in v[:5]) + f"  {v[5]:7.1f}")
