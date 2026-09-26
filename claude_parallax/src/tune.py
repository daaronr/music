"""PARALLAX - changes and head melody (all concert pitch).

Idea: the F major triad (F-A-C, plus G) is a fixed object heard against a moving
bass - Eb (lydian), Db (lydian augmented), B (altered), Bb (maj9). The same
melodic cell keeps changing colour, and each restatement arrives one eighth later
than the last (0, 1, 2 eighths): harmonic and rhythmic parallax. The bridge runs
ii - subV7#11 - Imaj7#11 cells down in major thirds (E, C, Ab), with the #11 held
on each bright lydian arrival, and repeats the 0/1/2-eighth displacement idea.
"""

TITLE = "Parallax"
SUBTITLE = "straightahead post-bop · medium-up swing"
COMPOSER = "Claude, 2026"
TEMPO_TEXT = "Medium-up swing"
BPM = 176

# 32-bar form, AABA. One chord = whole bar; two chords = two beats each.
FORM = [
    # A1
    "Ebmaj7#11", "Ebmaj7#11", "Dbmaj7#5", "Dbmaj7#5",
    "B7alt", "Bbmaj9", "Abm9", "Db13#11",
    # A2
    "Ebmaj7#11", "Ebmaj7#11", "Dbmaj7#5", "Dbmaj7#5",
    "B7alt", "Bbmaj9", "G#m7b5", "C#7alt",
    # B
    "F#m11 F7#11", "Emaj7#11", "Dm11 Db7#11", "Cmaj7#11",
    "Bbm11 A7#11", "Abmaj7#11", "Fm11", "E7#11",
    # A3
    "Ebmaj7#11", "Ebmaj7#11", "Dbmaj7#5", "Dbmaj7#5",
    "B7alt", "Bbmaj9", "Abm9", "Db13#11",
]
SECTIONS = {0: "A", 8: "A", 16: "B", 24: "A"}

_A_OPEN = [
    "C5/q. A4/8 F4/q G4/q",            # object on beat 1: 13 #11 9 3 of Eb
    "D5/h. r/q",                       # ...and up a 5th to the maj7
    "r/8 C5/q.!acc A4/8 F4/q G4/8~",   # same object one 8th late: 7 #5 3 #11 of Db
    "G4/8 C5/h r/q.",                  # up a 4th to Db's maj7
    "r/q C5/8!acc A4/8 F4/8 G4/8 Eb5/q",  # two 8ths late, in diminution: B altered
]
_A_CLOSE = [
    "D5/h. r/8 C5/8",                          # Eb(D#) -> D: 3rd of B7 to 3rd of Bb
    "3{Bb4/q Gb4/q Eb4/q} F4/q Cb5/q",         # the object a step down, Ab dorian
    "3{Bb4/q G4/q Eb4/q} F4/q. Cb5/8",         # G natural now: Db lydian dominant
]

HEAD = (
    ["@mf " + _A_OPEN[0]] + _A_OPEN[1:] + _A_CLOSE
    + _A_OPEN + [
        "D5/w~",                               # D held while the bass moves
        "D5/w~",                               # (b5 of G#m7b5)
        "D5/h r/8 E5/8 G5/8 G#5/8",            # (b9 of C#7alt), then launch
    ]
    + [
        "@f A5/q. E5/8 Eb5/q. B4/8",           # b3 b7 | b7 #11
        "A#4/h. r/q",                          # #11 of E
        "r/8 F5/q C5/8 Cb5/q. G4/8",           # cell one 8th late
        "F#4/h. r/q",                          # #11 of C
        "r/q Db5/8 Ab4/8 G4/q. D#4/8",         # cell two 8ths late
        "@mp D4/h. r/q",                       # #11 of Ab
        "@cresc r/8 Ab4/8 C5/8 Eb5/8 G5/q F5/8 Eb5/8",
        "D5/q. C#5/8 A#4/8 G#4/8 A#4/8 @endw B4/8",
    ]
    + ["@mf " + _A_OPEN[0]] + _A_OPEN[1:] + _A_CLOSE
)

# Guitar intro: Eb and F triads as a 3-over-4 ostinato; the bass moves Eb -> Db
# under it (the same triad pair covers Ebmaj7#11 and Dbmaj7#5).
INTRO_CHORDS = ["Ebmaj7#11", "Ebmaj7#11", "Dbmaj7#5", "Dbmaj7#5"]
INTRO = [
    "@mp G4/8!acc Bb4/8 Eb5/8 C5/8!acc A4/8 F4/8 G4/8!acc Bb4/8",
    "Eb5/8 C5/8!acc A4/8 F4/8 G4/8!acc Bb4/8 Eb5/8 C5/8!acc",
    "A4/8 F4/8 G4/8!acc Bb4/8 Eb5/8 C5/8!acc A4/8 F4/8",
    "G4/8!acc Bb4/8 Eb5/8 C5/8 r/h",
]

# Coda (after the last A of the head out): tag bars 31-32, then the object
# once more, resolving to the bright maj7.
CODA_CHORDS = ["Abm9", "Db13#11", "Ebmaj7#11", "Ebmaj7#11"]
CODA = [
    "3{Bb4/q Gb4/q Eb4/q} F4/q Cb5/q",
    "3{Bb4/q G4/q Eb4/q} F4/q. Cb5/8",
    "@dim C5/q. A4/8 F4/q G4/q",
    "@endw D5/w!ferm",
]
