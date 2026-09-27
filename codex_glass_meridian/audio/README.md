# Glass Meridian - audio recording

## Fuller upright bass (v3 — current)

Use **`output/Glass_Meridian_full_band_trumpet_sax_v3.mp3`** (3:16) or **`output/Glass_Meridian_duo_only_trumpet_sax_v3.mp3`** (1:34).

The bass now uses softer recorded plucks from the same installed upright library, rendered directly with longer string decay and controlled damping near the next note. A gentler initial attack, broad body/string-harmonic EQ and light compression accompany a 3.7 dB increase in its active-level target. No synthetic sub-bass was added. The trumpet, sax, piano and drum stems are reused exactly from v2, preserving that version's phrasing and balance between those instruments. Scores and earlier audio exports are unchanged.

Across 467 suitably spaced bass notes, median post-attack body level increased by 2.8 dB before mastering, and the median body-to-attack ratio increased by about 1.3 dB. These measurements support the mix change; they are not a human assessment of the timbre. Both v3 MP3s passed full decode checks. Full recording: −17.0 LUFS, −1.34 dBTP. Duo: −16.8 LUFS, −1.49 dBTP. Details are in `output/recording_details_v3.json` and `output/bass_qa_v3.json`. The reproducible bass/mix script is `source/revision3_bass.py`; uncompressed files are in `work/v3/`.

**Shareable production instructions and skills:** `share/AUDIO_PRODUCTION_BRIEF.md` and `share/skills/`. The share ZIP contains only that brief and the two reusable skills, including generic tested helpers; it contains no composition, proprietary sound libraries, or other attempts' files. These skills are project-local, not installed globally.

## Revised recording: trumpet and alto sax (v2)

**Use `output/Glass_Meridian_full_band_trumpet_sax_v2.mp3`** for the revised 3:16 recording, or `output/Glass_Meridian_duo_only_trumpet_sax_v2.mp3` for the 1:34 duo. The original trumpet/guitar MP3s remain available below. All PDFs, MusicXML and MuseScore files are unchanged.

The alto sax plays the original guitar line at its written concert pitch. Both leads use active-level targets about **4.7 dB below v1**, with a newly balanced acoustic rhythm section. This is a mix-setting comparison, not a measured perceptual loudness difference between different instruments.

The groove no longer imposes a fixed triplet eighth-note ratio. Flowing horn phrases approach even eighths, shorter gestures retain a light lilt, and placement evolves within phrases across barlines. The second eighth falls roughly 51–61% through its beat, rather than always at two-thirds. Bass keeps a steady quarter-note foundation; horns, comping and ride have distinct placement. A new drum part uses variable ride skips, sparse snare responses, soft kick and foot hi-hat. Most trumpet eighths use connected sustained samples instead of repeated staccato attacks. These are programmed interpretive choices, not a claim to reproduce a particular player.

**No iReal audio or iReal instrument sounds are used in v2.** Piano voicings and the walking-bass note arrangement originate in the earlier iReal MIDI export; piano density, timing, velocities and gates were revised. The drums are newly programmed. Sound sources are VSCO 2 CE trumpet and the installed Apple Alto Sax, Upright Jazz Bass, Steinway Grand Piano 2 and SoCal acoustic drum samples. Sax and bass render through Apple AVAudioUnitSampler. The newer piano and drum maps were rejected by that sampler, so a small local renderer reads their sample zones, pitch ranges and velocity layers directly from the installed libraries. It uses 18 piano zones and 20 drum zones in this arrangement, with full drum sample decays. It does not reproduce all of Logic's instrument DSP. Apple samples and compatibility copies remain in ignored local working folders and are not redistributed.

The [EXS binary field reference](https://github.com/asatamax/tonverk-elmulti-converter/blob/main/docs/EXS24_FORMAT_SPEC.md) informed the local map reader. Drum-key remapping is explicit: portable MIDI pedal hi-hat 44 uses Apple foot-hat key 33; MIDI high-tom 50 uses Apple high-tom key 48.

Both revised MP3s are 320 kb/s stereo, 44.1 kHz. Full-file decoding and loudness checks passed: full performance −17.0 LUFS / −1.33 dBTP; duet −16.79 LUFS / −1.47 dBTP. Lead pitch order matches the original score (634 trumpet and 309 sax notes). Local tuning spot checks and groove ranges are in `output/pitch_timing_qa_v2.json`; mix/export facts are in `output/recording_details_v2.json`. These technical checks are not a human listening review.

Reproduction sources: `source/revision2.py`, `source/exs_sample_render.py`, `source/render_exs_v2.swift`, `source/qa_revision2.py`. Editable full-band MIDI: `output/Glass_Meridian_trumpet_sax_v2.mid`. It carries the interpreted timing but playback elsewhere will use that application's sounds. Uncompressed stems and master are in `work/v2/`. Section times are the same as v1 below.

## Original recording: trumpet and guitar (v1)

Open **output/Glass_Meridian_full_band.mp3** for the full 3:16 performance. **output/Glass_Meridian_duo_only.mp3** is the 1:34 two-chorus solo excerpt.

This is a programmed sample performance of the existing score. The trumpet and guitar pitches and their order are preserved. Eighth-note swing, small timing deviations, note lengths, attacks and phrase dynamics are interpreted for playback.

## Sound sources

- **Trumpet:** 64 original WAV samples (45.3 MB) from [Versilian Studios' VSCO 2 Community Edition](https://versilian-studios.com/vsco-community/), recorded solo trumpet, with separate sustained and short-note articulations, soft/loud layers, and alternating short-note takes. The downloaded subset is CC0/public domain. No score or user material was uploaded. All sample transpositions stay within two semitones of a recorded pitch. `source/sample_manifest.json` records the individual URLs and SHA-256 checksums.
- **Guitar:** the installed GarageBand/Logic **Vintage Strat** EXS24 multisample instrument, rendered offline by Apple's **AVAudioUnitSampler**, then shaped with a mellow clean-guitar EQ, light compression, and room ambience. This uses the actual Apple sample instrument, not a General MIDI replacement. Apple documents [EXS24 loading through AVAudioUnitSampler](https://developer.apple.com/documentation/avfaudio/avaudiounitsampler/loadinstrument(at:)). Apple sample assets remain in their existing installed locations and are not redistributed.
- **Rhythm section:** an actual **iReal Pro** WAV export using **Jazz - Medium Up Swing**, piano, acoustic bass and **Real Drums**, at 164 BPM and four choruses. The original Glass Meridian chart was imported into iReal Pro to make this rendering. iReal contributes comping, walking bass, drum variations and a final tonic ring-out.

The trumpet is slightly left and the guitar slightly right. The backing is held below the soloists. Effects and mixing use floating-point audio and Spotify's Pedalboard DSP library. Final mastering uses FFmpeg and a stereo 320 kb/s MP3 encode at 44.1 kHz.

## Form and listening points

| Time in full recording | Section |
| --- | --- |
| 0:00 | Two-bar count-in |
| 0:02.93 | Head |
| 0:49.76 | Duo chorus I |
| 1:36.59 | Duo chorus II |
| 2:23.41 | Head out |
| 3:10.24 | Final rhythm-section tonic hit and decay |

The duet-only excerpt begins at the first duet downbeat and ends at the next head's downbeat, with a short fade at its final release.

## Verification

- The source is the delivered concert-pitch MusicXML, including the final head register adjustments and the guitar's planned dropouts.
- The lead MIDI and renderer contain 634 trumpet notes and 309 guitar notes across the complete performance. Pitch order is checked against the score.
- Audio root-note checks confirmed VSCO's octave naming (its C3 is sounding middle C).
- The iReal WAV's music starts after **eight** count-in beats; its separately exported MIDI starts after **four**. The soloists are aligned to the WAV. The backing's low-register onset was checked against the eight-beat timing.
- Sampled pitch spot checks for 35 longer notes in each lead found median deviations below five cents. These checks establish tuning, not a human assessment of musical phrasing.
- Full MP3 decode, duration, sample rate, loudness and true-peak checks are recorded in `output/recording_details.json`. Both exports have peak headroom and no decoding errors.
- No claim of a live-band recording or human listening review is made. This is a detailed rehearsal mock-up with sampled instruments.

## Editable / reproducible files

`output/Glass_Meridian_expressive_leads.mid` contains the two lead voices with the timing used in the audio. It is not the iReal rhythm-section arrangement. Load it at its embedded tempo, 164 BPM; it includes the WAV's eight-beat count-in offset.

`source/performance.py` prepares the events, renders trumpet samples, and mixes the result. `source/render_exs.swift` renders the installed guitar through Apple's sampler. `source/master.py` creates and checks both MP3s. Python packages are isolated in `audio/.venv` and pinned in `source/requirements.txt`. The `work` directory retains the uncompressed iReal backing, guitar, trumpet, mix and 24-bit master for later changes. These working assets are excluded from Git.

The MIDI and raw samples are not presented as alternative listening files: use the MP3s for the mixed performance.
