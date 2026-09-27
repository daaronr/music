---
name: music-audio-realism
description: "For music demos/recordings, David wants realistic band audio (Band-in-a-Box-like), not cheesy GM/8-bit MIDI"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 1d04035d-fdad-427c-8f61-4a8e11210c09
  modified: 2026-09-26T22:49:34.200Z
---

When asked to render audio for compositions, aim for a realistic band sound (real samples, swing, humanised timing, a generated rhythm section with walking bass, comping and ride-cymbal drums), not General MIDI playback.

**Why:** On 2026-09-26 David asked for an MP3 of the Halation tune "more towards band in a box than cheesy 8 bit midi", with the second soloist changed to saxophone for the recording only.

**How to apply:** Reuse the pipeline in `~/githubs/music/claude_halation/src/audio/` (see [[music-sample-libraries]]); keep score and recording decisions separate when he asks for recording-only changes.
