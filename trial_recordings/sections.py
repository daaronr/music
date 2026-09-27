"""Loudness per section for a rendered mix (bars: intro 0-4, head 4-36, ch1 36-68, ch2 68-100, out 100-)."""
import sys
import wave

import numpy as np

path, tempo = sys.argv[1], float(sys.argv[2])
with wave.open(path) as w:
    x = np.frombuffer(w.readframes(w.getnframes()), "<i2").reshape(-1, 2).astype(np.float32) / 32768
bar = 4 * 60 / tempo
row = []
for name, (a, b) in {"intro": (0, 4), "head": (4, 36), "chorus1": (36, 68), "chorus2": (68, 100),
                     "ch2 climax": (88, 96), "head out": (100, 130)}.items():
    seg = x[int(a * bar * 44100):int(b * bar * 44100)]
    row.append(f"{name} {20 * np.log10(np.sqrt(np.mean(seg ** 2))):.1f}")
print(f"{path.split('/')[-1]:<40} " + " | ".join(row))
