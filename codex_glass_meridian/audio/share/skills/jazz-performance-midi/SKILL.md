---
name: jazz-performance-midi
description: Turn a written jazz head and ensemble solo into expressive performance MIDI or timed note events, with phrase-aware swing, coordinated counterpoint, articulation and dynamics. Use for jazz playback phrasing; it does not compose or change the written music unless asked.
---

# Jazz performance MIDI

Preserve the user's pitches, form, rests, instrument entrances and harmonic timing. Distinguish sounding pitch from written transposition; a recording-only instrument substitution does not authorize changing the score. Work in the assigned folder and preserve earlier versions.

Parse the score into sounding-pitch events with explicit time units. Read MusicXML divisions, ties, voices, rests, repeats and instrument transposition rather than assuming a particular export structure. Compare emitted pitch sequences, section lengths and entrances with the score. Treat the guitar's conventional octave transposition explicitly.

Build phrases from musical gestures and rests, including gestures that cross barlines. Shape note lengths, articulation and dynamics around those phrases. Keep the spaces between contrapuntal entries. For two simultaneous lead voices, let foreground and support change with the line; do not simply maximize both tracks.

For a medium or up-tempo post-bop request, read [phrasing.md](references/phrasing.md). Use it as interpretive guidance, not a universal timing recipe. Respect requests for a different swing tradition or a literal rendering.

Keep quarter-note anchors and section downbeats aligned across the band. Check imported backing count-ins independently: a MIDI export and an audio export from the same app may have different lead-ins. Rephrase the backing when changing the groove; straightening only the horns can leave the rhythm section dragging against them.

Export portable MIDI and/or an event list with time, duration, MIDI pitch, velocity and channel/instrument identity. Record tempo, count-in, section boundaries, seed if used, and any recording-only substitutions. Timing randomness should be reproducible and subordinate to phrase design. Report pitch/form checks separately from any listening assessment.
