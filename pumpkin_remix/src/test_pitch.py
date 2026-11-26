"""Check sampled/synth instruments play the right pitch, and the vocal's tuning offset."""
import json
from pathlib import Path

import librosa
import numpy as np

import inst
from dsp import SR

for name, fn, m in [("strings", lambda m: inst.strings().note(m, 1.0, 100), 64),
                    ("brass", lambda m: inst.brass().note(m, 0.4, 110), 67),
                    ("piano", lambda m: inst.piano().note(m, 0.8, 100), 60),
                    ("guitar", lambda m: inst.guitar().note(m, 0.6, 100), 64),
                    ("bass", lambda m: inst.bass_synth(m, 0.5), 36),
                    ("supersaw", lambda m: inst.supersaw(m, 0.6), 60),
                    ("808", lambda m: inst.k808(m, 0.8), 36)]:
    a = fn(m).mean(axis=1)
    f0, v, _ = librosa.pyin(a, fmin=30, fmax=1200, sr=SR, frame_length=4096)
    est = np.nanmedian(librosa.hz_to_midi(f0[v])) if v.any() else np.nan
    print(f"{name:9s} asked {m} got {est:6.2f}")

W = Path(__file__).resolve().parents[1] / "work"
y, sr = librosa.load(W / "vocal_grid.wav", sr=22050, mono=True)
f0, v, _ = librosa.pyin(y, fmin=70, fmax=600, sr=sr, frame_length=2048)
mi = librosa.hz_to_midi(f0[v])
dev = mi - np.round(mi)
print(f"vocal: median cents off nearest semitone {100*np.median(dev):+.1f}, mean {100*np.mean(dev):+.1f}")
