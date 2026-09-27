"""Video scripts: what is on screen and in the captions while each recording plays.

Bar numbers are bars of the recording: intro 0-3, head 4-35, duo chorus 1 36-67,
chorus 2 68-99, head out from 100. Captions describe each run's own notes (Halation's
README, Parallax's README table, Glass Meridian's performance notes); the recording
plays the guitar line on alto sax, so captions say "sax" for it.
"""
M = "/Users/yosemite/githubs/music/"

INTRO_1 = ("This is one of three tunes from an informal trial run by David Reinstein: can AI "
           "write a modern jazz tune? Three AI agents got exactly the same prompt.")
INTRO_2 = ("The prompt asked for an original straight-ahead post-bop tune with some bright, "
           "lydian sounds, plus two written choruses of a trumpet and guitar duo solo, weaving "
           "in and out, with counterpoint and theme development.")
OUTRO = ("To hear the other two tunes, read the scores and vote, visit ai jazz tune trial dot "
         "netlify dot app. And if you play, record one of these and send me a link. I'd love "
         "to hear them played live.")


def intro_3(name, agent):
    return (f"This one is {name}, written by {agent}. What you'll hear is a programmed recording "
            "with sampled instruments, with alto sax playing the guitar line. The score is on "
            "the left, and the captions describe what's going on.")


TUNES = {
    "halation": dict(
        name="Halation", tempo=184, end_bar=130,
        agent="a Claude Code session running Claude Opus 5.5",
        agent_short="Claude Opus 5.5 (Claude Code)",
        facts="F lydian · ♩ = 184 · 32 bars · A B A′ C",
        audio=M + "trial_recordings/output/Halation_band_trumpet_alto.mp3",
        lead=M + "claude_halation/pdf/Halation_LeadSheet_C.pdf",
        duo=M + "claude_halation/pdf/Halation_Solo_BothChoruses_Score_Concert.pdf",
        systems=[[1, 5, 9, 13], [17, 21, 25, 29], [33, 37, 41, 45], [49, 53, 57, 61]],  # solo bar starting each system, per page
        segments=[
            (0, "Intro", "Piano, bass and drums vamp on the last four bars of the form: a lydian "
                         "version of the “Lady Bird” turnaround."),
            (4, "Head · A", "Trumpet melody, alto sax an octave below. Phrases start just after the "
                            "downbeat on the ♯11 (B over F), which then rings on as the ♯5 of "
                            "E♭maj7♯5: one note, new colour."),
            (12, "Head · B", "A deceptive move to D♭maj7♯11, then ii–Vs falling by half steps. The "
                             "melody traces the guide tones D♭–C–B–B♭."),
            (20, "Head · A′", "The opening returns, then turns to Em7♭5, A7(♭9) and a minor–major "
                              "chord, Dm(maj7)."),
            (28, "Head · C", "The melody climbs to its peak, A over E♭9♯11, and ends on the lydian "
                             "turnaround: each chord's ♯11 blooms in turn (B, D, G, C)."),
            (36, "Duo chorus 1 · bars 1–8", "The trumpet restates the opening bloom a beat late, then "
                                            "quotes the head's bars 5–8 a full beat late. The sax "
                                            "answers with the head's zig-zag motif upside down. "
                                            "Piano lays out."),
            (44, "Duo chorus 1 · bars 9–16", "The sax plays a bebop line with classic ii–V "
                                             "vocabulary while the trumpet holds the head's "
                                             "guide-tone line in long notes."),
            (52, "Duo chorus 1 · bars 17–24", "Trumpet runs F and G triads in three-note groups "
                                              "against the sax's dotted quarters, in contrary "
                                              "motion. Then short exchanges and a diminished lick."),
            (60, "Duo chorus 1 · bars 25–32", "The trumpet quotes the head's climax while the sax "
                                              "falls away; a sax break with a tritone-sub arpeggio; "
                                              "the two harmonize in sixths, then split the "
                                              "turnaround blooms between them."),
            (68, "Duo chorus 2 · bars 1–8", "The sax loops the zig-zag motif in five-eighth-note "
                                            "cells, so it slides against the bar line. The trumpet "
                                            "shifts a pentatonic out a half step and back. Then a "
                                            "canon: the sax copies the trumpet two beats later."),
            (76, "Duo chorus 2 · bars 9–16", "Bebop trumpet with a classic enclosure; the sax recalls "
                                             "the head's bloom; the two trade half-bars as the "
                                             "trumpet slides one pentatonic shape down by half "
                                             "steps; an octave unison splits apart."),
            (84, "Duo chorus 2 · bars 17–24", "The trumpet plays the motif in long notes while the "
                                              "sax spins triplet triad pairs around it. Then a "
                                              "rising build."),
            (92, "Duo chorus 2 · bars 25–32", "Climax: the trumpet climbs to its high C over a "
                                              "falling sax cascade. The sax quotes the head's bars "
                                              "27–30 under a trumpet counter-line; they end "
                                              "together in ninths."),
            (100, "Head out", "The head again, trumpet and sax an octave apart."),
            (130, "Ending", "The ♯11 held over Fmaj7♯11, the sax a fifth below, with a cymbal swell."),
        ]),
    "parallax": dict(
        name="Parallax", tempo=176, end_bar=135,
        agent="a second Claude Code session running Claude Opus 5.5",
        agent_short="Claude Opus 5.5 (a second Claude Code session)",
        facts="E♭ lydian · ♩ = 176 · 32 bars · A A B A",
        audio=M + "trial_recordings/output/Parallax_band_trumpet_alto.mp3",
        lead=M + "claude_parallax/output/Parallax_lead_sheet_concert.pdf",
        duo=M + "claude_parallax/output/Parallax_duo_solo_score_concert.pdf",
        systems=[[1, 5, 9, 13, 17], [21, 25, 29], [33, 37, 41, 45, 49], [53, 57, 61]],
        segments=[
            (0, "Intro", "Piano, bass and drums vamp on the last four bars of the form. (Parallax's "
                         "own written intro, a guitar ostinato, is left out: all three recordings "
                         "use the same vamp.)"),
            (4, "Head · A", "One fixed cell (F–A–C with G) over a moving bass: lydian over E♭, "
                            "lydian augmented over D♭, altered over B, maj9 over B♭. Each "
                            "restatement arrives an eighth later than the last."),
            (12, "Head · A", "The same cell and displacements. The section ends on a held D while "
                             "the harmony moves under it: the 3rd of B♭, the ♭5 of G♯m7♭5, the ♭9 "
                             "of C♯7alt."),
            (20, "Head · B", "The bridge: ii – subV7♯11 – Imaj7♯11 cells falling in major thirds "
                             "(E, C, A♭), holding the ♯11 on each bright lydian arrival."),
            (28, "Head · A", "The last A, as at the start."),
            (36, "Duo chorus 1 · bars 1–8", "Trumpet: the opening cell in eighths, displaced; F "
                                            "major pentatonic over B7alt. The sax answers with "
                                            "the cell inverted, quotes the head an octave down, "
                                            "and adds a bebop enclosure."),
            (44, "Duo chorus 1 · bars 9–16", "Trumpet: four-note pentatonic cells in a 4+1-eighth "
                                             "cycle, so each lands later, then held notes from the "
                                             "head. Sax: the cell in half notes, then a B7♯5♭9 "
                                             "line."),
            (52, "Duo chorus 1 · bars 17–24", "Bridge. Trumpet long tones at 0, 1 and 2 eighths' "
                                              "offset, climbing to a high G♯. Sax: 1-2-3-5 patterns "
                                              "and triad pairs (E/F♯, C/D, A♭/B♭)."),
            (60, "Duo chorus 1 · bars 25–32", "The cell displaced three eighths; a high A held from "
                                              "E♭ into D♭ (♯11 becomes ♯5); a hocket with the sax, "
                                              "whose triplet motif leads into chorus 2."),
            (68, "Duo chorus 2 · bars 1–8", "The trumpet sits out, then enters on a high A (♭7 of "
                                            "B7, then maj7 of B♭). The sax alone: 3-over-4 "
                                            "pentatonic cells with a half-step side-slip, and a "
                                            "B♭/C triad pair."),
            (76, "Duo chorus 2 · bars 9–16", "An E♭/F triad pair in triplets, the cell in "
                                             "augmentation, contrary motion with the voices "
                                             "crossing, then an octave unison run."),
            (84, "Duo chorus 2 · bars 17–24", "The bridge cell in octaves, then handed back and "
                                              "forth; the climax on B♭ (11 of Fm, ♯11 of E7), with "
                                              "E/F♯ and A♭/B♭ runs in the sax."),
            (92, "Duo chorus 2 · bars 25–32", "A canon on the cell at the octave, a voice exchange, "
                                              "and the head's bars 5–8 leading into the out-head."),
            (100, "Head out", "The head again, trumpet and sax an octave apart."),
            (132, "Coda", "Parallax's written coda: bars 31–32 tagged, then the cell once more, "
                          "resolving to E♭maj7♯11."),
        ]),
    "glass_meridian": dict(
        name="Glass Meridian", tempo=164, end_bar=131,
        agent="a Codex session running GPT-6 Astra",
        agent_short="GPT-6 Astra (Codex)",
        facts="F major, lydian colour · ♩ = 164 · 32 bars · A A2 B C",
        audio=M + "trial_recordings/output/Glass_Meridian_band_trumpet_alto.mp3",
        lead=M + "codex_glass_meridian/output/pdf/01_head_concert.pdf",
        duo=M + "codex_glass_meridian/output/pdf/03_duo_score_concert.pdf",
        systems=[[1, 5, 9, 13], [17, 21, 25, 29], [33, 37, 41, 45], [49, 51, 53, 55, 57, 61]],
        segments=[
            (0, "Intro", "Piano, bass and drums vamp on the last four bars of the form. (Glass "
                         "Meridian's notes ask for no intro; all three recordings use the same "
                         "vamp.)"),
            (4, "Head · A", "The core cell, A–C–G–B (up a minor 3rd, down a 4th, up a major 3rd), "
                            "enters on the & of 1 and opens into D. F and G triads give the bright "
                            "F-lydian colour."),
            (12, "Head · A2", "The cell over new roots, through E♭maj9♯11 and Cmaj9♯11."),
            (20, "Head · B", "The bridge opens into an E-major area (Emaj9♯11, then Gmaj9♯11)."),
            (28, "Head · C", "Back to F, through D7alt, ending on F6/9."),
            (36, "Duo chorus 1 · bars 1–8", "The trumpet quotes the cell; the sax answers a bar "
                                            "later and takes over while the trumpet rests. Bars "
                                            "6–7: the trumpet rises as the sax falls."),
            (44, "Duo chorus 1 · bars 9–16", "The sax takes the F/G triad-pair run, then gives the "
                                             "motif a new home over C and A♭; the trumpet holds "
                                             "tones and makes short replies."),
            (52, "Duo chorus 1 · bars 17–24", "The E-major area opens up; the sax briefly shifts a "
                                              "pentatonic fragment, and the line breaks into gaps "
                                              "and replies."),
            (60, "Duo chorus 1 · bars 25–32", "The opening cell breaks apart, and an altered-dominant "
                                              "descent resolves onto C over the final F chord."),
            (68, "Duo chorus 2 · bars 1–8", "The trumpet stretches the cell into 3+3+2 eighth-note "
                                            "spans while the sax runs F/G triad shapes underneath."),
            (76, "Duo chorus 2 · bars 9–16", "The sax restates the head while the trumpet rests or "
                                             "answers in slower values."),
            (84, "Duo chorus 2 · bars 17–24", "A wider-register climax: the trumpet pairs F-major "
                                              "and B-major pentatonic fragments and reaches high C, "
                                              "while the sax recalls the bridge melody."),
            (92, "Duo chorus 2 · bars 25–32", "The sax answers below the returning head; both lines "
                                              "settle and release together."),
            (100, "Head out", "The head again, trumpet and sax an octave apart."),
            (131, "Ending", "The written last bar, F6/9, held, with a cymbal swell."),
        ]),
}
