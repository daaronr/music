---
name: sampled-band-audio
description: Render and revise realistic sampled small-band music as a finished MP3, including acoustic rhythm sections, exposed horns, audible upright bass, stem mixing and technical audio QA. Use for instrumental score or MIDI recordings, not spoken narration.
---

# Sampled band audio

Deliver a playable recording, not just MIDI, code or directions. Preserve earlier mixes and the written score when the request changes only playback. Use the user's assigned working folder; do not inspect competing attempts.

Choose the best suitable installed instruments before downloading. Prefer recorded acoustic multisamples with velocity/articulation choices to a generic GM fallback. State the actual source and engine used. An iReal chord chart or MIDI arrangement does not require using iReal audio. Do not imply that a programmed performance is a live band or that Logic's full DSP was used by a simpler sampler.

Keep each instrument as a separate uncompressed floating-point stem. Validate a short representative render before processing the entire tune: source-pitch convention, range, articulation, note-off behavior, missing samples, frame count and non-silence. Use the instrument's actual sample mappings. For Apple EXS rendering, read [apple-sampler.md](references/apple-sampler.md) only when applicable.

Make a musical performance before mixing: phrase-shaped timing, note lengths, articulations and dynamics; preserve counterpoint and rests. Do not expect random velocity changes, reverb or mastering to fix a rigid MIDI performance.

When the bass lacks presence or sounds like a click, read [upright-bass.md](references/upright-bass.md). First distinguish level, sample choice, truncated decay and masking. Do not solve every bass issue by adding sub-bass or making the pluck brighter.

Balance the band in context. Keep piano and drums supportive, and avoid making both solo voices permanently dominant. Use modest stereo placement and room ambience; keep bass centered. Treat RMS targets as diagnostics, not equivalent perceived loudness across instruments. Recheck balance after mastering.

Render a lossless master and a high-quality MP3. Read [delivery-qa.md](references/delivery-qa.md) for checks and use `scripts/master_mp3.py` when FFmpeg/FFprobe are available. Validate any musical tuning or balance concerns separately. Do not claim to have listened if only numerical checks were possible.

Deliver the full MP3, an excerpt if useful, and concise production notes identifying the changed voices, sound sources, form/timing and remaining limitations. Share portable MIDI when requested, but distinguish its instruments on other machines from the sounds in the MP3. Do not redistribute proprietary raw sample libraries.
