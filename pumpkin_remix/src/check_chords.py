"""Do the MuseScore chords match what the video's accompaniment plays?

For each score half-bar, compare the accompaniment ("other" stem) chroma with the score chord
and with the best-fitting simple chord.
"""
import json
import sys
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).parent))
from harmony import chord_pcs, score_chords  # noqa: E402

W = Path(__file__).resolve().parents[1] / "work"
bm = json.load(open(W / "stems" / "beat_map.json"))
grid, gt = np.array(bm["grid"]), np.array(bm["t"])
x, sr = sf.read(str(W / "stems" / "other.wav"), dtype="float32")
y = librosa.resample(x.mean(axis=1), orig_sr=sr, target_sr=22050)
C = librosa.feature.chroma_cqt(y=y, sr=22050, hop_length=512, fmin=librosa.note_to_hz("C2"), tuning=-0.08)
ft = librosa.frames_to_time(np.arange(C.shape[1]), sr=22050, hop_length=512)
names = "C Db D Eb E F F# G Ab A Bb B".split()
TEMPL = {}
for r in range(12):
    for q, iv in [("", [0, 4, 7]), ("m", [0, 3, 7]), ("7", [0, 4, 7, 10]), ("m7", [0, 3, 7, 10]),
                  ("maj7", [0, 4, 7, 11]), ("dim7", [0, 3, 6, 9]), ("6", [0, 4, 7, 9])]:
        v = np.zeros(12)
        v[[(r + i) % 12 for i in iv]] = 1
        TEMPL[names[r] + q] = v


def corr(a, b):
    return float(np.corrcoef(a, b)[0, 1])


for s, e, name in score_chords():
    if s < 1 or s >= 97:
        continue
    t0, t1 = np.interp(s, grid, gt), np.interp(min(e, 97), grid, gt)
    sel = (ft >= t0) & (ft < t1)
    if sel.sum() < 3:
        continue
    v = C[:, sel].mean(axis=1)
    sc = np.zeros(12)
    sc[list(chord_pcs(name))] = 1
    best = max(TEMPL, key=lambda k: corr(TEMPL[k], v))
    flag = "" if corr(sc, v) > 0.5 else "   <-- check"
    print(f"beat {s:5.1f}-{e:5.1f} score {name:7s} fit {corr(sc, v):+.2f}   best {best:6s} {corr(TEMPL[best], v):+.2f}{flag}")
