"""Everything the trial page says about the three runs. Paths are relative to the repo root."""

PROMPT_BODY = """Create an original jazz tune in the 'straightahead post-bop' style, incorporating some harmonic and melodic developments from the 1990s and beyond. At least some 'bright sounds' (e.g., lydian triad pairing).  Melody and chord changes, etc.

Also write a 2 chorus '2 instrument solo' for those same changes, for trumpet and guitar, weaving in and out of each other, entering and dropping out using extensive counterpoint, some dramatic lines, and substantial 'theme development' throughout this duo-solo.  Should cite and play with the melody a bit, use a few 'classic licks' (but not too much), and some other modern melodic soloing approaches (see the folder/repo ... things like pentatonic shifting, triad pairs, rythmic displacement, etc.)

Present the 2 choruses of solos in separate sheets. The trumpet one both in concert pitch and in Bb transposition.

For all of this, give it it to me as a pdf as well as  a  format we can import into  musescore score as well as  a chord chart for Ireal."""

PROMPT_CLAUDE = ("(Create a subfolder and work on this there.  Note, I'll be asking GPT to work in a "
                 "different subfolder -- don't look at its work)\n\n" + PROMPT_BODY)
PROMPT_CODEX = ("(Create a subfolder and work on this there.  Note, I'll be asking Claude to work in "
                "a different subfolder -- don't look at its work)\n\n" + PROMPT_BODY)

# (summary shown on the page, the exact words it summarizes)
ASKS = [
    ("An original tune in the straightahead post-bop style, with harmonic and melodic ideas "
     "from the 1990s on",
     "Create an original jazz tune in the 'straightahead post-bop' style, incorporating some "
     "harmonic and melodic developments from the 1990s and beyond."),
    ("Some bright sounds, such as lydian triad pairs; melody and chord changes",
     "At least some 'bright sounds' (e.g., lydian triad pairing).  Melody and chord changes, etc."),
    ("A two-chorus duo solo on the same changes for trumpet and guitar: weaving, dropping in "
     "and out, lots of counterpoint, some dramatic lines, real theme development",
     "Also write a 2 chorus '2 instrument solo' for those same changes, for trumpet and guitar, "
     "weaving in and out of each other, entering and dropping out using extensive counterpoint, "
     "some dramatic lines, and substantial 'theme development' throughout this duo-solo."),
    ("Quote and play with the melody, a few classic licks (not too many), and modern devices "
     "such as pentatonic shifting, triad pairs and rhythmic displacement",
     "Should cite and play with the melody a bit, use a few 'classic licks' (but not too much), "
     "and some other modern melodic soloing approaches (see the folder/repo ... things like "
     "pentatonic shifting, triad pairs, rythmic displacement, etc.)"),
    ("The two solo choruses on separate sheets, with the trumpet in concert pitch and in B♭",
     "Present the 2 choruses of solos in separate sheets. The trumpet one both in concert pitch "
     "and in Bb transposition."),
    ("Everything as PDF, as something MuseScore can import, and as an iReal Pro chart",
     "For all of this, give it it to me as a pdf as well as  a  format we can import into  "
     "musescore score as well as  a chord chart for Ireal."),
]

HALATION_AUDIO = ("ONce this is sorted, use some audio/midi tools to create so create an audio "
                  "recording of this for me to listen back as an MP3. Try to use more sophisticated "
                  "tools that you can access more towards band in a box then cheesy 8 bit midi. for "
                  "the recording only (not the score), make the second voice  a saxophone rather "
                  "than a guitar.")
GM_AUDIO_1 = ("Use some audio/midi tools to create so create an audio recording of this for me to "
              "listen back as an MP3. Try to use more sophisticated tools that you can access more "
              "towards band in a box then cheesy 8 bit midi")
GM_AUDIO_2 = ("create the mp3 file again but try to make it sound a bit more natural. Do you have to "
              "use irealpro sounds? Also, for the recording only, make the second voice  a saxophone "
              "rather than a guitar. I guess the horn and gtr are also slightly too loud in the mix.")
GM_AUDIO_3 = ("and try to use a slightly more sophisticated 'swing concept' -- you are being a bit "
              "cheesy/basic/cliche with that 'triplet eighth notes thing'")
GM_AUDIO_4 = ("improve the bass sound. I barely hear it, and it doesn't much like an upright bass so "
              "much -- I hear the attack but not much of the strings.\n\nAlso share the 'instructions "
              "for creating audio' so I can pass that to the other attempts at this.")
PAGE_PROMPT = ("After all of this is done, make and host a web page for this full 'can AI write a "
               "modern jazz tune' informal trial. It should link the outputs (both Claude Opus 5.5 "
               "max tunes and the one GPT Astra high) explain what I did (the prompt chains and "
               "enviromnment here and in Codex), summarize the instructions and link/fold/tooltip "
               "the full instructions, etc.\n\nI'll want to share it around (while keeping working "
               "on the project). This was a 60 minute project. Far from a clean trial, benchmark, or "
               "comparison. Use /david-writing-style")
SKILLS_PROMPT = "after this is done, remember to turn key elements of the process into 'skills'"
HALATION_KHOUSE = "wait -- what did you take from 'k-howuse'?"
GM_SKILLS = "also consider making 'skills' out of the key parts of this process"
WHERE_PARALLAX = ("where is the 'parralax' recording? I see the other 2 mp3s but not that one")
NETLIFY_PROMPT = ("make the audio more prominient on the hosted page (give a \"TLDR, just hear the "
                  "recordings\") consider hosting it on Netlify or github  rather than  here, and "
                  "make the web page styling more in my usual style, and less 'night mode'\n\n"
                  "Also give people a prominent option to rate and vote on the tunes (which do they "
                  "prefer, etc?), and a 'see how others voted' page they see only after voting")
FAIRNESS_PROMPT = ("when you can, adjust the glass_meridian recording to use the same audio "
                   "instructions as the others, for fairness (you can note this and preserve the "
                   "orig recording as an alternate link, with explanations. )\n\nBtw, use folds "
                   "and tooltips more.")

# chord changes, concert pitch: (section label, [8 bars]); two chords in a bar split at beat 3
FORMS = {
    "halation": [
        ("A", ["Fmaj7#11", "Fmaj7#11", "Ebmaj7#5", "Ebmaj7#5",
               "D7sus(b9)", "D7alt", "Gm9", "C13sus"]),
        ("B", ["Dbmaj7#11", "Cm7 F7", "Bbmaj7#11", "Bbm7 Eb7",
               "Am7 D7", "Abm7 Db7", "Gm9", "C7alt"]),
        ("A′", ["Fmaj7#11", "Fmaj7#11", "Ebmaj7#5", "Ebmaj7#5",
                     "Em7b5", "A7(b9)", "Dm(maj7)", "Cm7 F7"]),
        ("C", ["Bbmaj7#11", "Eb9(#11)", "Am7", "D7alt",
               "Gm9", "Gb7(#11)", "Fmaj7#11 Abmaj7#11", "Dbmaj7#11 Gbmaj7#11"]),
    ],
    "parallax": [
        ("A", ["Ebmaj7#11", "Ebmaj7#11", "Dbmaj7#5", "Dbmaj7#5",
               "B7alt", "Bbmaj9", "Abm9", "Db13#11"]),
        ("A", ["Ebmaj7#11", "Ebmaj7#11", "Dbmaj7#5", "Dbmaj7#5",
               "B7alt", "Bbmaj9", "G#m7b5", "C#7alt"]),
        ("B", ["F#m11 F7#11", "Emaj7#11", "Dm11 Db7#11", "Cmaj7#11",
               "Bbm11 A7#11", "Abmaj7#11", "Fm11", "E7#11"]),
        ("A", ["Ebmaj7#11", "Ebmaj7#11", "Dbmaj7#5", "Dbmaj7#5",
               "B7alt", "Bbmaj9", "Abm9", "Db13#11"]),
    ],
    "glass_meridian": [
        ("A", ["Fmaj9#11", "Fmaj9#11", "Em7b5 A7alt", "Dm9",
               "Dbmaj9#11", "Cm9 F13", "Bbmaj9#11", "Gm9 C7alt"]),
        ("A2", ["Fmaj9#11", "Ebmaj9#11", "Dm9 G13#11", "Cmaj9#11",
                "Bm7b5 E7alt", "Am9", "Abmaj9#11", "Gm9 C7alt"]),
        ("B", ["Emaj9#11", "Emaj9#11", "Gmaj9#11", "F#m7b5 B7alt",
               "Em9", "A13#11", "Dm9 G13#11", "Gm9 C7alt"]),
        ("C", ["Fmaj9#11", "Ebmaj9#11", "Dm9 G13#11", "Dbmaj9#11 C7alt",
               "Fmaj9#11", "D7alt", "Gm9 C7alt", "F6/9"]),
    ],
}

H, P, G = "claude_halation", "claude_parallax/output", "codex_glass_meridian/output"

RUNS = [
    {
        "key": "halation",
        "name": "Halation",
        "model": "Claude Opus 5.5, max effort",
        "where": "Claude Code · session 1",
        "meta": ["F lydian", "♩ = 184", "32 bars · A B A′ C"],
        "idea": ("Two motifs: a “bloom,” where the ♯11 comes in on the and of one "
                 "and rings, and a cell built from F and G triads (A–C–G–D). The same "
                 "B natural is the ♯11 of Fmaj7♯11 and then the ♯5 of "
                 "E♭maj7♯5. The last two bars are a Lady Bird-style turnaround with "
                 "every chord lydian."),
        "sheets_note": "Solo parts come one chorus per sheet.",
        "audio_note": ("Made at my request (23:21), with alto sax playing the guitar line: "
                       "University of Iowa trumpet samples, Apple GarageBand sax, piano, bass and "
                       "drums, and a rhythm section generated from the changes. Intro, head, the "
                       "two duo choruses, head out."),
        "audio": [
            ("Band demo · trumpet and alto sax (2:58)",
             "claude_halation/audio/Halation_band_demo.mp3", "Halation_band_demo.mp3"),
        ],
        "recordings_bundle": ("Halation_recording.zip", []),
        "lead": f"{H}/pdf/Halation_LeadSheet_C.pdf",
        "score": f"{H}/pdf/Halation_Solo_BothChoruses_Score_Concert.pdf",
        "pdfs": [
            ("Lead sheet, concert", f"{H}/pdf/Halation_LeadSheet_C.pdf"),
            ("Lead sheet, B♭ trumpet", f"{H}/pdf/Halation_LeadSheet_Bb.pdf"),
            ("Duo score, concert (4 pp.)", f"{H}/pdf/Halation_Solo_BothChoruses_Score_Concert.pdf"),
            ("Trumpet, concert, chorus 1", f"{H}/pdf/Halation_Solo_Chorus1_Trumpet_Concert.pdf"),
            ("Trumpet, concert, chorus 2", f"{H}/pdf/Halation_Solo_Chorus2_Trumpet_Concert.pdf"),
            ("Trumpet in B♭, chorus 1", f"{H}/pdf/Halation_Solo_Chorus1_Trumpet_Bb.pdf"),
            ("Trumpet in B♭, chorus 2", f"{H}/pdf/Halation_Solo_Chorus2_Trumpet_Bb.pdf"),
            ("Guitar, chorus 1", f"{H}/pdf/Halation_Solo_Chorus1_Guitar.pdf"),
            ("Guitar, chorus 2", f"{H}/pdf/Halation_Solo_Chorus2_Guitar.pdf"),
        ],
        "bundle": ("Halation_editable_files.zip", [
            f"{H}/musicxml/Halation_LeadSheet_C.musicxml",
            f"{H}/musicxml/Halation_LeadSheet_Bb.musicxml",
            f"{H}/musicxml/Halation_Solo_BothChoruses_Score_Concert.musicxml",
            f"{H}/musicxml/Halation_Solo_BothChoruses_Score_Bb.musicxml",
            f"{H}/musicxml/Halation_Solo_Chorus1_Trumpet_Concert.musicxml",
            f"{H}/musicxml/Halation_Solo_Chorus2_Trumpet_Concert.musicxml",
            f"{H}/musicxml/Halation_Solo_Chorus1_Trumpet_Bb.musicxml",
            f"{H}/musicxml/Halation_Solo_Chorus2_Trumpet_Bb.musicxml",
            f"{H}/musicxml/Halation_Solo_Chorus1_Guitar.musicxml",
            f"{H}/musicxml/Halation_Solo_Chorus2_Guitar.musicxml",
            f"{H}/musescore/Halation_LeadSheet_C.mscz",
            f"{H}/musescore/Halation_LeadSheet_Bb.mscz",
            f"{H}/musescore/Halation_Solo_BothChoruses_Score_Concert.mscz",
            f"{H}/musescore/Halation_Solo_BothChoruses_Score_Bb.mscz",
            f"{H}/musescore/Halation_Solo_Chorus1_Trumpet_Concert.mscz",
            f"{H}/musescore/Halation_Solo_Chorus2_Trumpet_Concert.mscz",
            f"{H}/musescore/Halation_Solo_Chorus1_Trumpet_Bb.mscz",
            f"{H}/musescore/Halation_Solo_Chorus2_Trumpet_Bb.mscz",
            f"{H}/musescore/Halation_Solo_Chorus1_Guitar.mscz",
            f"{H}/musescore/Halation_Solo_Chorus2_Guitar.mscz",
            f"{H}/ireal/Halation_iReal.html",
            f"{H}/ireal/Halation_iReal_link.txt",
        ]),
        "ireal": f"{H}/ireal/Halation_iReal_link.txt",
        "timeline": [
            ("22:27", "Write the tune and the duo solo", PROMPT_CLAUDE, None,
             "Lead sheet, duo score and parts done by 23:23"),
            ("23:21", "Make an MP3, with alto sax as the second voice", HALATION_AUDIO, None,
             "Band demo (2:58), finished at 23:46"),
            ("23:50", "A question about the K-house folder", HALATION_KHOUSE, None,
             "A question, not a change to the tune"),
        ],
    },
    {
        "key": "parallax",
        "name": "Parallax",
        "model": "Claude Opus 5.5, max effort",
        "where": "Claude Code · session 2",
        "meta": ["E♭ lydian", "♩ = 176", "32 bars · A A B A", "intro and coda"],
        "idea": ("An F major triad stays put while the bass moves under it (E♭, D♭, B, "
                 "B♭), so the same notes sound lydian, lydian augmented, altered and plain major "
                 "in turn. Each restatement comes in an eighth note later than the last. The duo "
                 "score has small notes naming the device in use (triad pair, displacement, "
                 "hocket and so on)."),
        "sheets_note": "Each part has chorus 1 on page 1 and chorus 2 on page 2.",
        "audio_note": "No recording requested; this session made the page instead.",
        "audio": [],
        "lead": f"{P}/Parallax_lead_sheet_concert.pdf",
        "score": f"{P}/Parallax_duo_solo_score_concert.pdf",
        "pdfs": [
            ("Lead sheet, concert", f"{P}/Parallax_lead_sheet_concert.pdf"),
            ("Lead sheet, B♭ trumpet", f"{P}/Parallax_lead_sheet_Bb_trumpet.pdf"),
            ("Duo score with analysis notes (4 pp.)", f"{P}/Parallax_duo_solo_score_concert.pdf"),
            ("Trumpet, concert", f"{P}/Parallax_solo_trumpet_concert.pdf"),
            ("Trumpet in B♭", f"{P}/Parallax_solo_trumpet_Bb.pdf"),
            ("Guitar", f"{P}/Parallax_solo_guitar.pdf"),
            ("Everything in one PDF (12 pp.)", f"{P}/Parallax_all_sheets.pdf"),
        ],
        "bundle": ("Parallax_editable_files.zip", [
            f"{P}/Parallax_lead_sheet_concert.musicxml",
            f"{P}/Parallax_lead_sheet_Bb_trumpet.musicxml",
            f"{P}/Parallax_duo_solo_score_concert.musicxml",
            f"{P}/Parallax_duo_solo_MuseScore.musicxml",
            f"{P}/Parallax_solo_trumpet_concert.musicxml",
            f"{P}/Parallax_solo_trumpet_Bb.musicxml",
            f"{P}/Parallax_solo_guitar.musicxml",
            f"{P}/Parallax_lead_sheet_concert.mscz",
            f"{P}/Parallax_lead_sheet_Bb_trumpet.mscz",
            f"{P}/Parallax_duo_solo_MuseScore.mscz",
            f"{P}/Parallax_solo_trumpet_concert.mscz",
            f"{P}/Parallax_solo_trumpet_Bb.mscz",
            f"{P}/Parallax_solo_guitar.mscz",
            f"{P}/Parallax_iReal_import.html",
            f"{P}/Parallax_iReal_link.txt",
            "claude_parallax/README.md",
        ]),
        "ireal": f"{P}/Parallax_iReal_link.txt",
        "timeline": [
            ("22:29", "Write the tune and the duo solo", PROMPT_CLAUDE, None,
             "Lead sheets, duo score and parts done by about 23:35"),
            ("23:32", "Make and host this page", PAGE_PROMPT, None,
             "A first version of this page"),
            ("23:42", "Turn key parts of the process into skills", SKILLS_PROMPT, None,
             "Four skills: notation, iReal charts, composition, trial pages"),
            ("23:54", "Where's the Parallax recording?", WHERE_PARALLAX, None,
             "None had been asked for; one is being made from Halation's audio request"),
            ("00:01", "Recordings first, host on Netlify, my usual style, add a vote",
             NETLIFY_PROMPT, None, "This page"),
            ("00:04", "Put Glass Meridian's recording on equal terms; more folds and tooltips",
             FAIRNESS_PROMPT, None, "A shared rendering pipeline for all three, in progress"),
        ],
    },
    {
        "key": "glass_meridian",
        "name": "Glass Meridian",
        "model": "GPT-6 Astra",
        "where": "Codex desktop app",
        "meta": ["F major, lydian colour", "♩ = 164", "32 bars · A A2 B C"],
        "idea": ("A four-note cell (A–C–G–B) that comes back over different roots, "
                 "in longer note values and split between the players. F and G triads give the "
                 "lydian colour, and the bridge moves to E major."),
        "sheets_note": ("Each part has chorus 1 on page 1 and chorus 2 on page 2. The guitar part "
                        "is written at sounding pitch, not the usual octave up."),
        "audio_note": ("v3 is trumpet and alto sax (the sax at my request) with a programmed "
                       "rhythm section; v1 is trumpet and guitar as written, over an iReal Pro "
                       "backing. The duo choruses start at 0:50."),
        "audio": [
            ("v3 · trumpet and alto sax, fuller bass (3:16)",
             "codex_glass_meridian/audio/output/Glass_Meridian_full_band_trumpet_sax_v3.mp3",
             "Glass_Meridian_v3_trumpet_sax.mp3"),
            ("v1 · trumpet and guitar, iReal Pro backing (3:16)",
             "codex_glass_meridian/audio/output/Glass_Meridian_full_band.mp3",
             "Glass_Meridian_v1_trumpet_guitar.mp3"),
        ],
        "lead": f"{G}/pdf/01_head_concert.pdf",
        "score": f"{G}/pdf/03_duo_score_concert.pdf",
        "pdfs": [
            ("Complete packet (14 pp.)", f"{G}/pdf/00_complete_packet.pdf"),
            ("Head, concert", f"{G}/pdf/01_head_concert.pdf"),
            ("Head, B♭ trumpet", f"{G}/pdf/02_head_trumpet_Bb.pdf"),
            ("Duo score, concert (4 pp.)", f"{G}/pdf/03_duo_score_concert.pdf"),
            ("Trumpet, concert", f"{G}/pdf/04_trumpet_concert.pdf"),
            ("Trumpet in B♭", f"{G}/pdf/05_trumpet_Bb.pdf"),
            ("Guitar (sounding pitch)", f"{G}/pdf/06_guitar_concert.pdf"),
            ("Performance and composition notes", f"{G}/pdf/07_performance_notes.pdf"),
            ("Chord chart", f"{G}/pdf/08_chord_chart.pdf"),
        ],
        "bundle": ("Glass_Meridian_editable_files.zip", [
            f"{G}/musicxml/01_head_concert.musicxml",
            f"{G}/musicxml/02_head_trumpet_Bb.musicxml",
            f"{G}/musicxml/03_duo_score_concert.musicxml",
            f"{G}/musicxml/04_trumpet_concert.musicxml",
            f"{G}/musicxml/05_trumpet_Bb.musicxml",
            f"{G}/musicxml/06_guitar_concert.musicxml",
            f"{G}/musescore/01_head_concert.mscz",
            f"{G}/musescore/02_head_trumpet_Bb.mscz",
            f"{G}/musescore/03_duo_score_concert.mscz",
            f"{G}/musescore/04_trumpet_concert.mscz",
            f"{G}/musescore/05_trumpet_Bb.mscz",
            f"{G}/musescore/06_guitar_concert.mscz",
            f"{G}/ireal/import_glass_meridian.html",
            f"{G}/ireal/glass_meridian.irealbook",
            f"{G}/ireal/chart_source.txt",
        ]),
        "recordings_bundle": ("Glass_Meridian_recordings.zip", []),
        "ireal": f"{G}/ireal/glass_meridian.irealbook",
        "timeline": [
            ("22:28", "Write the tune and the duo solo", PROMPT_CODEX, "xhigh",
             "Head, duo score and parts done by 22:50"),
            ("22:52", "Make an MP3, closer to Band-in-a-Box than 8-bit MIDI", GM_AUDIO_1, "xhigh",
             "v1: sampled trumpet and guitar over an iReal Pro rhythm section"),
            ("23:19", "More natural; sax instead of guitar; quieter leads", GM_AUDIO_2, "medium",
             "v2, with the next prompt"),
            ("23:23", "A less clichéd swing feel", GM_AUDIO_3, "medium",
             "v2: alto sax, programmed drums, looser eighth notes"),
            ("23:36", "A better upright bass; share the audio instructions", GM_AUDIO_4, "high",
             "v3, plus a written audio brief for the other runs"),
            ("23:38", "Consider making skills out of the process", GM_SKILLS, "high",
             "Two reusable audio skills"),
        ],
    },
]
