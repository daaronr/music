"""Is the hook intelligible in the processed vocal itself (no mix)?  Whisper, no lyric prompt."""
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import whisper

W = Path(__file__).resolve().parents[1] / "work"
meta = json.load(open(W / "vocal_grid.json"))
LEAD, SB = meta["lead"], meta["sb"]
model = whisper.load_model("medium")
src = {"orig_stem": (W / "stems" / "vocals.wav", None), "grid": (W / "vocal_grid.wav", 1),
       "soft": (W / "vocal_soft.wav", 1)}
phr = {"jack": (64.9, 69.2, 57.4, 62.0), "pumpkin_pie": (88.9, 96.0, 79.0, 87.0)}
for pname, (b0, b1, o0, o1) in phr.items():
    for sname, (path, grid) in src.items():
        x, sr = sf.read(str(path), dtype="float32")
        x = x.mean(axis=1)
        a, b = ((LEAD + b0 * SB), (LEAD + b1 * SB)) if grid else (o0, o1)
        seg = x[int(a * sr):int(b * sr)]
        import librosa
        seg = librosa.resample(seg, orig_sr=sr, target_sr=16000).astype(np.float32)
        r = model.transcribe(seg, language="en", fp16=False, condition_on_previous_text=False)
        print(f"{pname:12s} {sname:10s} -> {r['text'].strip()}")
