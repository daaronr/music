"""Extra data for the Netlify version of the page: recordings and tooltip glossary."""

HAL_AUDIO = "claude_halation/audio"
GM_AUDIO = "codex_glass_meridian/audio/output"
TRIAL_AUDIO = "trial_recordings/output"

SAME_RECIPE = ("Same recipe as the other two headline recordings: the audio instructions that "
               "produced the Halation recording, applied unchanged (code, samples, mix, random "
               "seed), at the composer's own tempo. Trumpet: University of Iowa samples. Alto "
               "sax (playing the guitar line), piano, bass and drums: Apple GarageBand "
               "instruments, with the rhythm section generated from the run's own iReal chart. "
               "Details: trial_recordings/README.md. On 28 Sep the rhythm section was redone "
               "for every recording on this page, the same way: a softer ride cymbal and less "
               "repetitive drums, bass and piano.")
GROOVE_NOTE = (" On 28 Sep the rhythm section was redone for every recording on this page, the "
               "same way: a softer ride cymbal and less repetitive drums, bass and piano.")
WALTZ_RECIPE = ("Made by the session that wrote the tune, from one audio request in the same words "
                "for both waltzes: clarinet on the top line, trombone on the lower line, adapting "
                "the round-1 recording engine to 3/4. Clarinet: Apple GarageBand samples; trombone: "
                "University of Iowa samples; piano, bass and drums: Apple GarageBand. Afterwards, "
                "by hand and the same for both waltzes: the bass raised 4.5 dB." + GROOVE_NOTE)
TRIAL_ENGINE = "trial_recordings/output"

# score videos hosted on the site itself (current audio); none of them names the model
VID = "trial_recordings/video/output"
HOSTED_VIDEO = {
    "halation": (f"{VID}/Halation_AI_jazz_trial.mp4", "2:58"),
    "parallax": (f"{VID}/Parallax_AI_jazz_trial.mp4", "3:12"),
    "glass_meridian": (f"{VID}/Glass_Meridian_AI_jazz_trial.mp4", "3:20"),
    "tenebrae": (f"{VID}/Tenebrae_atmospheric.mp4", "4:25"),
    "noctilucent": (f"{VID}/Noctilucent_atmospheric.mp4", "4:13"),
}
POSTER = f"{VID}/posters"

# per tune: recordings in display order; the first "main" one is the headline player
RECORDINGS = {
    "halation": [
        {"label": "Band recording: trumpet and alto sax, with piano, bass and drums", "length": "2:58",
         "src": f"{TRIAL_ENGINE}/Halation_band_trumpet_alto.mp3", "file": "Halation_band_trumpet_alto.mp3",
         "main": True, "video": "https://youtu.be/BWSs51RqMY4",
         "note": "Made by the Halation session from one audio request: a better-than-MIDI "
                 "recording with alto sax playing the guitar line. Its instructions are the "
                 "recipe for the other two round-1 recordings. Trumpet: University of Iowa "
                 "samples. Sax, piano, bass and drums: Apple GarageBand instruments, with a "
                 "rhythm section generated from the chords." + GROOVE_NOTE},
        {"label": "The original band demo, before the rhythm-section update", "length": "2:58",
         "src": f"{HAL_AUDIO}/Halation_band_demo.mp3", "file": "Halation_band_demo.mp3", "main": False,
         "note": "As the Halation session first made it, with the louder ride and simpler drums."},
    ],
    "tenebrae": [
        {"label": "Band recording: clarinet and trombone, with piano, bass and drums", "length": "4:25",
         "src": "claude_tenebrae/audio/Tenebrae_band_clarinet_trombone.mp3",
         "file": "Tenebrae_band_clarinet_trombone.mp3", "main": True,
         "video": "https://youtu.be/yWvjmh0TBig",   # blind, new mix (28 Sep); earlier versions unlisted
         "note": WALTZ_RECIPE},
    ],
    "noctilucent": [
        {"label": "Band recording: clarinet and trombone, with piano, bass and drums", "length": "4:13",
         "src": "trial_recordings/noctilucent/output/Noctilucent_clarinet_trombone_band.mp3",
         "file": "Noctilucent_band_clarinet_trombone.mp3", "main": True,
         "video": "https://youtu.be/zWQCC5xPcQ0",
         "note": WALTZ_RECIPE + " This one's clarinet was also raised about 2 dB, with its "
                 "softest passages lifted, after a listen."},
    ],
    "parallax": [
        {"label": "Band recording: trumpet and alto sax, with piano, bass and drums", "length": "3:12",
         "src": f"{TRIAL_AUDIO}/Parallax_band_trumpet_alto.mp3",
         "file": "Parallax_band_trumpet_alto.mp3", "main": True,
         "video": "https://youtu.be/vRtIxdXL3ck",
         "note": SAME_RECIPE + " Parallax's written 4-bar guitar intro is left out (the recipe's "
                 "intro is a rhythm-section vamp); its written coda ends the recording."},
    ],
    "glass_meridian": [
        {"label": "Band recording: trumpet and alto sax, with piano, bass and drums", "length": "3:20",
         "src": f"{TRIAL_AUDIO}/Glass_Meridian_band_trumpet_alto.mp3",
         "file": "Glass_Meridian_band_trumpet_alto.mp3", "main": True,
         "video": "https://youtu.be/fsyuVkLZ6jU",
         "note": SAME_RECIPE},
        {"label": "The run's own v1: trumpet and guitar as written, over an iReal Pro rhythm section",
         "length": "3:16", "src": f"{GM_AUDIO}/Glass_Meridian_full_band.mp3",
         "file": "Glass_Meridian_v1_trumpet_guitar.mp3", "main": False,
         "note": "This run's first recording, made from a single audio request (like the others, "
                 "but without the ask to swap guitar for sax). Trumpet: VSCO 2 samples. "
                 "Guitar: Apple's sampled Strat. Rhythm section: iReal Pro."},
        {"label": "The run's own v3: trumpet and alto sax, programmed band, fuller bass",
         "length": "3:16", "src": f"{GM_AUDIO}/Glass_Meridian_full_band_trumpet_sax_v3.mp3",
         "file": "Glass_Meridian_v3_trumpet_sax.mp3", "main": False,
         "note": "After three more rounds of my feedback: a more natural sound, sax instead of "
                 "guitar, a less clichéd swing feel and a fuller upright bass. The other "
                 "two got one audio request each, so this version had extra help."},
    ],
}
PENDING = {}

GLOSSARY = {
    "lydian": "A major scale with a raised 4th (the ♯11). It sounds bright and open, and "
              "modern jazz uses it a lot.",
    "♯11": "The raised 11th, or raised 4th, above the root: the note that gives lydian "
                "chords their bright sound.",
    "triad pair": "Two neighbouring major or minor triads (say E♭ and F over "
                  "E♭maj7♯11) played in alternation, giving a six-note line with a "
                  "bright, modern sound.",
    "pentatonic shifting": "Moving a five-note (pentatonic) shape from one key to another in "
                           "mid-phrase, to change the colour over the same chord.",
    "rhythmic displacement": "Restating a figure an eighth note or a beat earlier or later, so "
                             "it falls differently against the bar line.",
    "counterpoint": "Two independent lines that make sense together, instead of a melody "
                    "with accompaniment.",
    "duo solo": "Here, a written-out improvisation-style solo for trumpet and guitar together "
                "over the tune's changes, two times through the form.",
    "head": "The tune's melody, played at the start and again at the end.",
    "chorus": "One time through the form, here 32 bars.",
    "changes": "The chord progression.",
    "post-bop": "The style that grew out of 1960s Blue Note records (Wayne Shorter, Herbie "
                "Hancock, Joe Henderson): swinging, with freer harmony than bebop.",
    "iReal Pro": "A practice app that plays a piano, bass and drums backing from a chord "
                 "chart.",
    "MusicXML": "A standard sheet-music file format. MuseScore, Sibelius, Finale and Dorico "
                "can all open it.",
    "MuseScore": "Free notation software. The .mscz files open in it directly.",
    "Band-in-a-Box": "Long-standing software that generates backing tracks from chord "
                     "symbols.",
    "concert pitch": "Written as it sounds. A B♭ trumpet part is written a whole step "
                     "higher.",
    "max effort": "Claude Code's highest thinking setting: slower, and usually more careful.",
    "reasoning effort": "How long the model thinks before acting. Codex offers low to xhigh.",
    "Claude Code": "Anthropic's coding agent; here its desktop app, working in a folder on "
                   "my Mac.",
    "Codex": "OpenAI's coding agent; here its desktop app, working in the same repo.",
    "mocked-up": "Rendered from the sheet music with sampled instruments and programmed "
                 "timing, not played by people.",
}
