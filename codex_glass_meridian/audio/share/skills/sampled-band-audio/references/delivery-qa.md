# Export and verification

Keep a floating-point premaster and a lossless final master. Avoid hard clipping between stages; floating-point samples over 1.0 still need gain reduction before fixed-point export. Master gently enough to preserve accents. A starting delivery target around −17 LUFS integrated and −1.5 dBTP works for these rehearsal recordings, but follow the user's requirements. Check the encoded MP3 because encoding can raise true peaks.

The included `master_mp3.py` uses two-pass FFmpeg loudnorm, exports a 24-bit WAV and 320 kb/s MP3, fully decodes the MP3, then records its duration, channels, sample rate, loudness and true peak as JSON. It refuses to overwrite outputs unless `--overwrite` is supplied. Required tools: Python 3, FFmpeg and FFprobe on PATH or supplied explicitly. It neither validates the score nor assesses musical quality.

```
python3 scripts/master_mp3.py premaster.wav revised.mp3 --title "Tune - revised mix"
```

Also check:

- Expected form, count-in alignment, ending and effect tails.
- Lead pitch order/ranges, substitution octave, rests and planned dropouts.
- Every requested stem is non-silent; no unplanned long gaps or clipped segments.
- Representative actual rendered pitches—not just the MIDI note numbers. Tuning checks near an expected frequency do not exclude all octave errors, so test sample roots explicitly.
- Bass body, soloist balance and groove through listening if the environment permits it. Otherwise state the scope of technical checks accurately.

Deliver the playable MP3 prominently. Retain the previous version. If the user requested only a sound change, keep the notation files intact. Record the actual sound sources and explain any fallback succinctly. A high bitrate and successful decode do not prove a natural performance.
