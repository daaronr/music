---
name: music-sample-libraries
description: "Local sampled instruments usable for offline audio rendering on this Mac, and their gotchas"
metadata:
  node_type: memory
  type: reference
  originSessionId: 1d04035d-fdad-427c-8f61-4a8e11210c09
  modified: 2026-09-26T22:49:40.104Z
---

- Apple GarageBand/Logic EXS instruments: `/Library/Application Support/Logic/Sampler Instruments/` (Steinway Grand Piano 2, Upright Jazz Bass, Alto Sax, orchestral Trumpets (a section, not solo), SoCal drum kit). Samples in `.../Logic/EXS Factory Samples/` and `.../GarageBand/Instrument Library/Sampler/Sampler Files/`.
- AVAudioUnitSampler cannot load the "consolidated" ones (Steinway, drums): parse the .exs yourself. Zone start/end are frame offsets into one big 16-bit big-endian CAF; stop each zone at the next zone's start. Parser: `claude_halation/src/audio/exs.py`.
- EXS zone fine-tune is added to the pitch (it corrects the sample). Upright Jazz Bass is mapped an octave up (send sounding + 12). SoCal kit: ride bow key 99, hi-hat foot key 33, snare 38, kick 36.
- No jazz drum loops, brushes or tenor sax are installed.
- Solo trumpet: University of Iowa MIS samples (free for any use), downloaded and cut into notes by `claude_halation/src/audio/fetch_trumpet.sh` + `prepare_trumpet.py` into `claude_halation/build/samples/`.
- MuseScore 3 CLI: MusicXML import drops `7alt`/`13sus`/`m(maj7)` chord names and ignores `-S` style files. Patch `<Harmony><name>` and `<Style>` in the imported .mscx instead (see `claude_halation/src/build.py`).

Related: [[music-audio-realism]]
