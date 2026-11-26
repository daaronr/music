"""Flow checks: silent gaps, energy per bar (so drops land), vocal presence at key cue points."""
import json
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
W = ROOT / "work"
tl = json.load(open(W / "timeline.json"))
x, sr = sf.read(str(ROOT / "output" / "Glory_of_the_Pumpkin_Disco_Trap_Remix.wav"), dtype="float32")
v, _ = sf.read(str(W / "mix_stems" / "vocals.wav"), dtype="float32")
T0, BAR = tl["T0"], tl["bar"]
beat = BAR / 4
m = np.abs(x).max(axis=1)

# silent gaps (> 250 ms below -50 dBFS) before the final tail
win = int(0.05 * sr)
blocks = m[: len(m) // win * win].reshape(-1, win).max(axis=1)
quiet = blocks < 10 ** (-50 / 20)
runs, start = [], None
for i, q in enumerate(quiet):
    if q and start is None:
        start = i
    if not q and start is not None:
        if (i - start) * 0.05 > 0.25:
            runs.append((start * 0.05, i * 0.05))
        start = None
print("silent gaps:", [(round(a, 2), round(b, 2)) for a, b in runs if b < tl["sections"]["end"] - 4] or "none")

# energy per bar (RMS dB)
rms = []
for k in range(96):
    a = int((T0 + k * BAR) * sr)
    seg = x[a:a + int(BAR * sr)]
    rms.append(20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9))
print("bar RMS dB (8 per row):")
for k in range(0, 96, 8):
    print(f"  bars {k:2d}-{k+7:2d}: " + " ".join(f"{r:5.1f}" for r in rms[k:k + 8]))


def vlevel(t, dur=0.35):
    a = int(t * sr)
    return 20 * np.log10(np.sqrt(np.mean(v[a:a + int(dur * sr)] ** 2)) + 1e-9)


cues = {"'Oh a' pickup (bar 7 beat 3)": T0 + 7 * BAR + 2 * beat, "'lone' (bar 8)": T0 + 8 * BAR,
        "'PIE' at drop (bar 32)": T0 + 32 * BAR, "'So he' (bar 47 beat 3)": T0 + 47 * BAR + 2 * beat,
        "'raised' (bar 48)": T0 + 48 * BAR, "'For the' (bar 71 beat 3)": T0 + 71 * BAR + 2 * beat,
        "'glo-' (bar 72)": T0 + 72 * BAR, "final 'pie' (bar 86)": T0 + 86 * BAR}
print("vocal level at cue points (dB, stem):")
for k, t in cues.items():
    print(f"  {k:28s} {vlevel(t):6.1f}   (100 ms before: {vlevel(t - 0.45, 0.3):6.1f})")
print(f"peak {20*np.log10(m.max()):.2f} dBFS, DC {x.mean():+.5f}")
