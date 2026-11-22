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
    "brightwork": [
        ("A1", ["Fmaj7#11", "Fmaj7#11", "Bm7 E7", "Amaj7",
                "Abmaj7#11", "Dbmaj7#11", "Gm7", "Gb7#11"]),
        ("A2", ["Fmaj7#11", "Fmaj7#11", "Bm7 E7", "Amaj7",
                "Abmaj7#11", "Dbmaj7#11", "F#m7", "B7"]),
        ("B", ["Emaj7#11", "Emaj7#11", "Gmaj7#11", "Gmaj7#11",
               "Bbmaj7#11", "Dbmaj7#11", "C7sus", "C7alt"]),
        ("A3", ["Fmaj7#11", "Fmaj7#11", "Bm7 E7", "Amaj7",
                "Abmaj7#11 Dbmaj7#11", "Gm7 C7", "Fmaj7#11", "Gbmaj7#11"]),
    ],
    # round 2 (the dark brief)
    "tenebrae": [
        ("A", ["D7sus(b9)", "D7sus(b9)", "Ebmaj7#11", "Ebmaj7#11",
               "Bbmaj7#5", "Bbmaj7#5", "A7sus(b9)", "A7alt"]),
        ("A′", ["D7sus(b9)", "D7sus(b9)", "Ebmaj7#11", "Ebmaj7#11",
                "Abmaj7#5", "Abmaj7#5", "Dbmaj7#11", "Dbmaj7#11"]),
        ("B", ["C7#11", "C7#11", "B7alt", "B7alt", "Bb7#11", "Bb7#11", "A7alt", "A7alt"]),
        ("C", ["Dm(maj9)", "Dm(maj9)", "Dm(maj9)", "Dm(maj9)",
               "Bbmaj7#5", "Bbmaj7#5", "Ebmaj7#11", "Ebmaj7#11"]),
    ],
    "noctilucent": [
        ("A", ["E7sus(b9)", "E7sus(b9)", "Fmaj7#11/E", "Fmaj7#11/E",
               "Am9", "C7alt", "F#m7b5", "B7alt"]),
        ("B", ["Em9", "Gm9", "Bbmaj7#11", "A7alt", "Dm9", "F7alt", "F#m7b5", "B7alt"]),
        ("A′", ["E7sus(b9)", "E7sus(b9)", "Fmaj7#11/E", "E7sus(b9)",
                "A7b9", "Dm9", "B7b9", "Em9"]),
        ("C", ["Cmaj7#11", "Abmaj7#11", "Am9", "D7alt",
               "Fmaj7#11/E", "E7sus(b9)", "F#m7b5", "B7alt"]),
    ],
}

import os as _os
_W = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "waltz_prompts")
WALTZ_COMPOSE = open(_os.path.join(_W, "01_compose.txt"), encoding="utf-8").read().strip()
WALTZ_RECORDING = open(_os.path.join(_W, "02_recording.txt"), encoding="utf-8").read().strip()
# one-line summaries of the round-2 brief, with the exact words on hover (like ASKS)
ASKS2 = [
    ("An original jazz waltz with a darker tonality and a Wayne Shorter-ish feel, with some "
     "Phrygian and sus(♭9) sounds",
     "Create an original jazz waltz (3/4) with a darker tonality and a Wayne Shorter-esque feel, "
     "e.g., with some Phrygian / sus(b9) sounds.  Melody and chord changes, etc."),
    ("A two-chorus trumpet and guitar duo, leaning on classical counterpoint",
     "This time focus a bit more on the principles of classical counterpoint, applied to jazz."),
    ("Two more choruses for one instrument, demonstrating soloing techniques one 8-bar block at "
     "a time, each block labelled",
     "Then write 2 more choruses of solo on a single instrument (trumpet or tenor sax), and have "
     "that solo illustrate some of the techniques and approaches discussed, doing so block by block."),
    ("The same formats as round 1: separate sheets, trumpet in concert and B♭, PDF, MuseScore, "
     "iReal", "Present the 2 duo choruses and the 2 single-instrument choruses in separate sheets."),
    ("Then a recording: clarinet on the top line, trombone on the lower one, adapting the round-1 "
     "recording engine to a waltz", WALTZ_RECORDING),
]

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
    {
        "key": "brightwork",
        "name": "Brightwork",
        "model": "Claude Fable 5.2, max effort",
        "where": "Claude Code, headless, 21 Nov",
        "meta": ["F lydian", "♩ = 160", "32 bars · A A B A"],
        "idea": ("The hook is a lydian triad pair: an F triad down, a G triad up, landing on the "
                 "13th. The A section brightens from F lydian to A major, drops into shade (A♭ "
                 "and D♭ lydian) and comes home. The bridge starts a half step below home, in E "
                 "lydian, and climbs by minor thirds; each long melody note is the 13th of one "
                 "chord and the ♯11 of the next. The duo opens with the hook in canon and ends "
                 "with it split between the players."),
        "sheets_note": ("Engraved with LilyPond (MuseScore no longer runs on this Mac), so the "
                        "editable files are MusicXML only; they open in MuseScore."),
        "lead": "fable_brightwork/pdf/Brightwork_01_lead_sheet_concert.pdf",
        "score": "fable_brightwork/pdf/Brightwork_03_duo_solo_score_concert.pdf",
        "pdfs": [
            ("Everything in one file (12 pp.)", "fable_brightwork/Brightwork_complete.pdf"),
            ("Lead sheet, concert", "fable_brightwork/pdf/Brightwork_01_lead_sheet_concert.pdf"),
            ("Lead sheet, B♭ trumpet", "fable_brightwork/pdf/Brightwork_02_lead_sheet_Bb.pdf"),
            ("Duo score, concert", "fable_brightwork/pdf/Brightwork_03_duo_solo_score_concert.pdf"),
            ("Trumpet, concert", "fable_brightwork/pdf/Brightwork_04_trumpet_solo_concert.pdf"),
            ("Trumpet in B♭", "fable_brightwork/pdf/Brightwork_05_trumpet_solo_Bb.pdf"),
            ("Guitar", "fable_brightwork/pdf/Brightwork_06_guitar_solo.pdf"),
        ],
        "bundle": ("Brightwork_editable_files.zip",
                   [f"fable_brightwork/musicxml/Brightwork_{n}.musicxml" for n in (
                       "01_lead_sheet_concert", "02_lead_sheet_Bb", "03_duo_solo_score_concert",
                       "04_trumpet_solo_concert", "05_trumpet_solo_Bb", "06_guitar_solo")] +
                   ["fable_brightwork/ireal/Brightwork_iReal.html",
                    "fable_brightwork/ireal/Brightwork_iReal_link.txt",
                    "fable_brightwork/README.md"]),
        "ireal": "fable_brightwork/ireal/Brightwork_iReal_link.txt",
        "timeline": [
            ("21 Nov 16:37 EST", "Write the tune and the duo solo (round 1's prompt, verbatim)",
             PROMPT_CLAUDE, "max",
             "Lead sheets written, then stopped at 17:30 on the 5-hour usage limit"),
            ("18:28", "Resume the same session", "Continue.", "max",
             "Duo score, parts, iReal chart and README, done by 18:57"),
        ],
    },
    # ---- round 2: the dark brief, one Claude run and one Codex run (see waltz_prompts/)
    {
        "key": "tenebrae",
        "name": "Tenebrae",
        "round": 2,
        "model": "Claude Opus 5.5, max effort",
        "where": "Claude Code, headless",
        "meta": ["D phrygian", "♩ = 138", "32 bars · A A′ B C", "intro and coda"],
        "idea": ("Everything grows from the half step above the root: D7sus(♭9) puts E♭ over D, "
                 "and the first gesture is that E♭ sighing down to D. In the B section the "
                 "dominants fall by half steps while the melody climbs against them across the "
                 "barline; the C section is a lament over Dm(maj9). The duo is written as a "
                 "fugato, canon, suspensions and stretto, and the etude works through one "
                 "technique per 8 bars. Named after the Holy Week service in which the candles "
                 "go out one by one."),
        "sheets_note": ("Concert pitch and B♭ trumpet throughout; the study scores print the "
                        "analysis under the staff. The packet has concert pitch first."),
        "lead": "claude_tenebrae/pdf/Tenebrae_lead_sheet_concert.pdf",
        "score": "claude_tenebrae/pdf/Tenebrae_duo_score_concert.pdf",
        "pdfs": [
            ("Everything in one packet, concert pitch first (27 pp.)", "claude_tenebrae/Tenebrae_complete_packet.pdf"),
            ("Lead sheet, concert", "claude_tenebrae/pdf/Tenebrae_lead_sheet_concert.pdf"),
            ("Lead sheet, B♭ trumpet", "claude_tenebrae/pdf/Tenebrae_lead_sheet_Bb_trumpet.pdf"),
            ("Duo score, concert (4 pp.)", "claude_tenebrae/pdf/Tenebrae_duo_score_concert.pdf"),
            ("Duo score, B♭ trumpet (4 pp.)", "claude_tenebrae/pdf/Tenebrae_duo_score_Bb.pdf"),
            ("Duo study score, counterpoint marked", "claude_tenebrae/pdf/Tenebrae_duo_study_score.pdf"),
            ("Etude, trumpet concert", "claude_tenebrae/pdf/Tenebrae_etude_trumpet_concert.pdf"),
            ("Etude, trumpet in B♭", "claude_tenebrae/pdf/Tenebrae_etude_trumpet_Bb.pdf"),
            ("Etude study score, techniques marked", "claude_tenebrae/pdf/Tenebrae_etude_study_score.pdf"),
            ("Duo trumpet part, concert", "claude_tenebrae/pdf/Tenebrae_duo_part_trumpet_concert.pdf"),
            ("Duo trumpet part, B♭", "claude_tenebrae/pdf/Tenebrae_duo_part_trumpet_Bb.pdf"),
            ("Duo guitar part", "claude_tenebrae/pdf/Tenebrae_duo_part_guitar.pdf"),
        ],
        "bundle": ("Tenebrae_editable_files.zip",
                   [f"claude_tenebrae/musicxml/{n}.musicxml" for n in (
                       "Tenebrae_lead_sheet_concert", "Tenebrae_lead_sheet_Bb_trumpet",
                       "Tenebrae_duo_score_concert", "Tenebrae_duo_score_Bb",
                       "Tenebrae_etude_trumpet_concert", "Tenebrae_etude_trumpet_Bb",
                       "Tenebrae_duo_part_trumpet_concert", "Tenebrae_duo_part_trumpet_Bb",
                       "Tenebrae_duo_part_guitar")] +
                   [f"claude_tenebrae/musescore/{n}.mscz" for n in (
                       "Tenebrae_lead_sheet_concert", "Tenebrae_lead_sheet_Bb_trumpet",
                       "Tenebrae_duo_score_concert", "Tenebrae_duo_score_Bb",
                       "Tenebrae_etude_trumpet_concert", "Tenebrae_etude_trumpet_Bb")] +
                   ["claude_tenebrae/ireal/Tenebrae_iReal.html",
                    "claude_tenebrae/ireal/Tenebrae_iReal_link.txt", "claude_tenebrae/README.md"]),
        "ireal": "claude_tenebrae/ireal/Tenebrae_iReal_link.txt",
        "timeline": [
            ("27 Sep 18:01", "Write the waltz, the duo and the etude", WALTZ_COMPOSE, "max",
             "Lead sheet, duo, etude, study scores and packet, done by 18:55"),
            ("18:55", "Record it: clarinet and trombone, adapting the round-1 engine", WALTZ_RECORDING,
             "high", "Band recording, done by 19:05"),
        ],
    },
    {
        "key": "noctilucent",
        "name": "Noctilucent",
        "round": 2,
        "model": "GPT-6 Astra, xhigh effort",
        "where": "Codex CLI, unattended",
        "meta": ["E, phrygian colour", "♩ = 144", "32 bars · A B A′ C", "2-bar ending"],
        "idea": ("Centred on E with F natural on top: E7sus(♭9) and Fmaj7♯11/E share an E pedal "
                 "and swap upper structures. The main motif is E–F–B–A (a half step, a tritone "
                 "leap and a step down). The duo uses imitation, contrary and oblique motion, "
                 "prepared dissonance and voice exchange, and the trumpet study has eight labelled "
                 "technique blocks. Named after clouds that glow after sunset."),
        "sheets_note": ("Concert pitch and B♭ trumpet; the B♭ duo score keeps concert chord "
                        "symbols for the guitarist. Parts have one chorus per page."),
        "lead": "codex_noctilucent/output/pdf/01_head_concert.pdf",
        "score": "codex_noctilucent/output/pdf/03_duo_score_concert.pdf",
        "pdfs": [
            ("Complete packet (20 pp.)", "codex_noctilucent/output/pdf/00_complete_score_packet.pdf"),
            ("Head, concert", "codex_noctilucent/output/pdf/01_head_concert.pdf"),
            ("Head, B♭ trumpet", "codex_noctilucent/output/pdf/02_head_Bb.pdf"),
            ("Duo score, concert (4 pp.)", "codex_noctilucent/output/pdf/03_duo_score_concert.pdf"),
            ("Duo score, B♭ trumpet (4 pp.)", "codex_noctilucent/output/pdf/04_duo_score_Bb.pdf"),
            ("Duo trumpet part, concert", "codex_noctilucent/output/pdf/05_duo_trumpet_concert.pdf"),
            ("Duo trumpet part, B♭", "codex_noctilucent/output/pdf/06_duo_trumpet_Bb.pdf"),
            ("Duo guitar part", "codex_noctilucent/output/pdf/07_duo_guitar.pdf"),
            ("Trumpet study, concert", "codex_noctilucent/output/pdf/08_trumpet_study_concert.pdf"),
            ("Trumpet study, B♭", "codex_noctilucent/output/pdf/09_trumpet_study_Bb.pdf"),
        ],
        "bundle": ("Noctilucent_editable_files.zip",
                   [f"codex_noctilucent/output/musicxml/{n}.musicxml" for n in (
                       "01_head_concert", "02_head_Bb", "03_duo_score_concert", "04_duo_score_Bb",
                       "05_duo_trumpet_concert", "06_duo_trumpet_Bb", "07_duo_guitar",
                       "08_trumpet_study_concert", "09_trumpet_study_Bb")] +
                   [f"codex_noctilucent/output/musescore/{n}.mscz" for n in (
                       "01_head_concert", "02_head_Bb", "03_duo_score_concert", "04_duo_score_Bb",
                       "08_trumpet_study_concert", "09_trumpet_study_Bb")] +
                   ["codex_noctilucent/ireal/Noctilucent_iReal.html",
                    "codex_noctilucent/ireal/Noctilucent_iReal_link.txt", "codex_noctilucent/README.md"]),
        "ireal": "codex_noctilucent/ireal/Noctilucent_iReal_link.txt",
        "timeline": [
            ("28 Sep 12:21", "Write the waltz, the duo and the etude", WALTZ_COMPOSE, "xhigh",
             "Head, duo, study, parts and packet, done by 12:48"),
            ("12:49", "Record it: clarinet and trombone, adapting the round-1 engine", WALTZ_RECORDING,
             "high", "Band recording, done by 13:05"),
        ],
    },
]
for _r in RUNS:
    _r.setdefault("round", 1)
