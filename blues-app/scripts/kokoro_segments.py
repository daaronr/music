#!/usr/bin/env python3
"""Render speech segments with Kokoro (mlx-audio), loading the model once.

usage: kokoro_segments.py TEXTS_JSON OUTPUT_DIR [VOICE] [SPEED]
Writes speech_000.wav, speech_001.wav, ... Voices: bm_george (older British man,
the default), am_onyx, bm_lewis, am_santa, af_heart, ...
Run with the Kokoro venv from ~/githubs/claude_code_misc_work/brass_playing_next_step.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from mlx_audio.tts.generate import generate_audio


def main() -> int:
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    texts = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    out = Path(sys.argv[2])
    voice = sys.argv[3] if len(sys.argv) > 3 else "am_santa"
    speed = float(sys.argv[4]) if len(sys.argv) > 4 else 0.92
    out.mkdir(parents=True, exist_ok=True)
    for i, text in enumerate(texts):
        prefix = f"speech_{i:03d}"
        generate_audio(
            text=text.strip(),
            model="mlx-community/Kokoro-82M-bf16",
            voice=voice,
            speed=speed,
            lang_code="b" if voice.startswith("b") else "a",
            output_path=str(out),
            file_prefix=prefix,
            audio_format="wav",
            join_audio=True,
            verbose=False,
        )
        if not (out / f"{prefix}.wav").is_file():
            raise RuntimeError(f"Kokoro failed on segment {i}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
