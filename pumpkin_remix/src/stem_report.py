"""Per-stem loudness over time and vocal pitch track."""
import sys
from pathlib import Path
import numpy as np
import librosa

d = Path(sys.argv[1])
stems = {}
for name in ["vocals", "drums", "bass", "other"]:
    y, sr = librosa.load(d / f"{name}.wav", sr=22050, mono=True)
    stems[name] = y
    rms = librosa.feature.rms(y=y, frame_length=4096, hop_length=sr)[0]
    db = 20 * np.log10(rms + 1e-9)
    print(f"{name:7s} overall {20*np.log10(np.sqrt(np.mean(y**2))+1e-9):6.1f} dB")
    print("   per s: " + " ".join(f"{v:4.0f}" for v in db[:95]))

v = stems["vocals"]
f0, voiced, prob = librosa.pyin(v, fmin=70, fmax=700, sr=22050, frame_length=2048, hop_length=256)
t = librosa.times_like(f0, sr=22050, hop_length=256)
midi = librosa.hz_to_midi(f0)
np.savez(d / "vocal_f0.npz", t=t, midi=midi, voiced=voiced, prob=prob)
vm = midi[voiced]
print("voiced fraction", voiced.mean(), "median midi", np.nanmedian(vm), "range", np.nanpercentile(vm, [5, 95]))
# coarse pitch outline per 0.5 s
for s in range(0, int(t[-1]), 4):
    seg = []
    for k in range(8):
        lo, hi = s + k * 0.5, s + (k + 1) * 0.5
        m = (t >= lo) & (t < hi) & voiced
        seg.append(f"{np.nanmedian(midi[m]):5.1f}" if m.sum() > 3 else "   - ")
    print(f"{s:4d}s " + " ".join(seg))
