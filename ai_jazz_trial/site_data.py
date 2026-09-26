"""Extra data for the Netlify version of the page: recordings and tooltip glossary."""

HAL_AUDIO = "claude_halation/audio"
GM_AUDIO = "codex_glass_meridian/audio/output"

# per tune: recordings in display order; the first "main" one is the headline player
RECORDINGS = {
    "halation": [
        {"label": "Band demo: trumpet and alto sax, with piano, bass and drums", "length": "2:58",
         "src": f"{HAL_AUDIO}/Halation_band_demo.mp3", "file": "Halation_band_demo.mp3",
         "main": True,
         "note": "Made by the Halation session from one audio request, the same one Parallax "
                 "got: a better-than-MIDI recording with alto sax playing the guitar line. "
                 "Trumpet: University of Iowa samples. Sax, piano, bass and drums: Apple "
                 "GarageBand instruments, with a rhythm section generated from the chords."},
    ],
    "parallax": [],
    "glass_meridian": [
        {"label": "v1: trumpet and guitar as written, over an iReal Pro rhythm section",
         "length": "3:16", "src": f"{GM_AUDIO}/Glass_Meridian_full_band.mp3",
         "file": "Glass_Meridian_v1_trumpet_guitar.mp3", "main": True,
         "note": "Codex's first recording, made from a single audio request (like the others, "
                 "but without the ask to swap guitar for sax). Trumpet: VSCO 2 samples. "
                 "Guitar: Apple's sampled Strat. Rhythm section: iReal Pro."},
        {"label": "v3: trumpet and alto sax, programmed band, fuller bass",
         "length": "3:16", "src": f"{GM_AUDIO}/Glass_Meridian_full_band_trumpet_sax_v3.mp3",
         "file": "Glass_Meridian_v3_trumpet_sax.mp3", "main": False,
         "note": "After three more rounds of my feedback: a more natural sound, sax instead of "
                 "guitar, a less clichéd swing feel and a fuller upright bass. The other "
                 "two got one audio request each, so this version had extra help."},
    ],
}
PENDING = {
    "parallax": "Being made now, from the same audio request the Halation session got. "
                "This page will be updated when it's ready.",
}

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
