"""Segment the vocal f0 track into notes: onset, duration, median pitch."""
import sys
from pathlib import Path
import numpy as np
import librosa

d = Path(sys.argv[1])
z = np.load(d / "vocal_f0.npz")
t, midi, voiced = z["t"], z["midi"], z["voiced"]
y, sr = librosa.load(d / "vocals.wav", sr=22050, mono=True)
on_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=256)
onsets = librosa.onset.onset_detect(onset_envelope=on_env, sr=sr, hop_length=256, units="time", backtrack=False)

notes = []
cur = None
for i in range(len(t)):
    m = midi[i] if voiced[i] else np.nan
    if np.isnan(m):
        if cur and t[i] - cur["last"] > 0.06:
            notes.append(cur)
            cur = None
        continue
    if cur is None:
        cur = dict(start=t[i], last=t[i], p=[m])
    elif abs(m - np.median(cur["p"][-6:])) > 0.8:
        notes.append(cur)
        cur = dict(start=t[i], last=t[i], p=[m])
    else:
        cur["last"] = t[i]
        cur["p"].append(m)
if cur:
    notes.append(cur)
notes = [n for n in notes if n["last"] - n["start"] >= 0.07]
out = []
for n in notes:
    out.append((n["start"], n["last"] - n["start"], float(np.median(n["p"]))))
np.save(d / "vocal_notes.npy", np.array(out))
np.save(d / "vocal_onsets.npy", onsets)
for s, du, p in out:
    print(f"{s:7.2f} {du:5.2f} {p:5.1f} {librosa.midi_to_note(round(p))}")
print("onsets:", np.round(onsets, 2).tolist())
