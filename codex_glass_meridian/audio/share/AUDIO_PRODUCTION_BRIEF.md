# Instructions for creating the audio

Use this brief with your own composition, in your own assigned working folder. Do not inspect another attempt's music or working files. The attached skills contain production guidance and generic helpers, not another composition.

Create a finished, natural-sounding small-band jazz recording as a high-quality MP3. Render the written head, two-chorus interweaving solo, and head out with an acoustic rhythm section. Preserve the music's pitches, changes, form, rests and thematic development. For the recording only, use trumpet and saxophone as the two solo voices; keep the written guitar score unchanged unless specifically asked otherwise.

Use convincing recorded instruments: expressive trumpet and sax, acoustic piano, pizzicato upright bass and an acoustic drum kit. Prefer good installed sample libraries and appropriate articulations to generic GM tones. You do not have to use iReal Pro sounds. It can provide chord-based accompaniment notes, but those notes can be revoiced/rephrased and rendered with other instruments. State what actually supplied the notes and sounds. Keep instrument stems so a balance change does not require rebuilding everything.

Make the swing more sophisticated than a fixed triplet long-short pattern. Use phrase-aware placement and articulation. At medium-up tempo, flowing eighth-note lines may approach even while shorter phrases have a light lilt. Let phrases cross barlines, respect breathing and contrapuntal spaces, and shape arrivals and releases. A particular percentage range is only a starting point. Do not swing explicit tuplets twice, accent every upbeat, or rely on random timing to create feel. Keep the bass's quarter-note pulse steady; let horns, comping and ride phrase around it. Vary ride skips, leave space in the snare part, and avoid stock fills at every boundary.

Keep both solo voices integrated into the band rather than too loud. Preserve their entrances, dropouts and conversational handovers. Use restrained room ambience, sensible stereo placement and dynamics appropriate to the musical phrase.

Give the upright bass an audible pitched body and string decay—not just the attack. Try softer pluck layers with more mix level, rather than harder velocities. Avoid cutting every walking note off prematurely; sustain toward the next note and damp intentionally. Retain the recorded string resonance and harmonic movement. Check roughly 120–250 Hz for body and 400–900 Hz for string definition if EQ is needed; these are starting points, not fixed boosts. Gentle compression can make the decay more audible. Check piano/kick masking and small-speaker audibility. Do not substitute a synthetic sub-bass for the upright's character.

Check real rendered audio: sample root pitches/octaves, instrument range, articulations, note-off behavior, count-in alignment, section transitions, bass presence, clipping and tails. A WAV and a MIDI exported from the same app can start at different offsets. Verify drum-key maps before assuming GM compatibility. Audition representative sections if you have an actual listening capability; otherwise say which technical checks were performed without claiming you listened.

Deliver the MP3 itself, preferably with a full performance and a separate two-chorus excerpt. Preserve prior mixes and deliver the revised version under a new name. Keep a lossless master and editable MIDI. A useful starting export is stereo 44.1 kHz, 320 kb/s MP3, around −17 LUFS integrated with true-peak headroom; verify the MP3 after encoding. Include concise production notes and distinguish sampled/programmed performance from live playing. Do not distribute proprietary sample files.

## Reusable skills included

- `skills/jazz-performance-midi/SKILL.md`: score-to-performance timing, articulation, phrasing and counterpoint.
- `skills/sampled-band-audio/SKILL.md`: sound-source selection, rendering, upright-bass troubleshooting, mixing, mastering and QA. Includes a Swift EXS renderer and a Python FFmpeg mastering helper.

These are portable skill folders stored with this project, not globally installed. An agent can read the relevant `SKILL.md` directly. To install them, copy the two folders into that agent's supported skills directory. Code is generic; the Apple renderer requires macOS and installed instruments, while the mastering helper requires Python, FFmpeg and FFprobe. No global settings or other attempts' files were changed.
