"""Whisper (no lyric prompt) on short passages of the finished mix."""
import json
from pathlib import Path

import librosa
import numpy as np
import whisper

ROOT = Path(__file__).resolve().parents[1]
tl = json.load(open(ROOT / "work" / "timeline.json"))
T0, BAR = tl["T0"], tl["bar"]
y, _ = librosa.load(ROOT / "output" / "Glory_of_the_Pumpkin_Disco_Trap_Remix.wav", sr=16000, mono=True)
model = whisper.load_model("medium")
for name, b0, b1 in [("build into drop", 29, 33.5), ("drop A loop", 35.8, 40.5), ("final line", 83, 88)]:
    seg = y[int((T0 + b0 * BAR) * 16000):int((T0 + b1 * BAR) * 16000)].astype(np.float32)
    r = model.transcribe(seg, language="en", fp16=False, condition_on_previous_text=False)
    print(f"{name:16s} bars {b0}-{b1}: {r['text'].strip()}")
