"""How tightly does a warped vocal sit on the grid?

Detects vocal onsets and measures each one's distance to the nearest half-score-beat
(= one beat at 128 BPM).  Prints median and 80th-percentile absolute deviation in ms,
weighted toward strong onsets.
"""
import json
import sys
from pathlib import Path

import librosa
import numpy as np

wav = sys.argv[1]
meta = json.load(open(Path(wav).with_suffix(".json"))) if Path(wav).with_suffix(".json").exists() else None
lead, sb = (meta["lead"], meta["sb"]) if meta else (3.0, 0.9375)
y, sr = librosa.load(wav, sr=22050, mono=True)
env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=128)
on = librosa.onset.onset_detect(onset_envelope=env, sr=sr, hop_length=128, units="frames", backtrack=False)
t = librosa.frames_to_time(on, sr=sr, hop_length=128)
s = env[on]
keep = (t > lead - 0.3) & (t < lead + 93 * sb + 0.3) & (s > np.percentile(s, 40))
t, s = t[keep], s[keep]
step = sb / 2
dev = (t - lead) / step
dev = (dev - np.round(dev)) * step * 1000
a = np.abs(dev)
print(f"{Path(wav).name}: n={len(a)} median |dev| {np.median(a):.0f} ms, p80 {np.percentile(a, 80):.0f} ms, "
      f"mean signed {np.mean(dev):+.0f} ms")
