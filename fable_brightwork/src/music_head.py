"""Brightwork - changes and head melody (concert pitch, c' = middle C)."""

TITLE = "Brightwork"
COMPOSER = "Claude (Fable 5.2), for David Reinstein"
TEMPO = 160
TEMPO_TEXT = "Medium-up swing"

# 32 bars, A1 A2 B A3. Two symbols in a bar = two beats each.
CHANGES = [
    # A1
    "Fmaj7#11", "Fmaj7#11", "Bm7 E7", "Amaj7",
    "Abmaj7#11", "Dbmaj7#11", "Gm7", "Gb7#11",
    # A2
    "Fmaj7#11", "Fmaj7#11", "Bm7 E7", "Amaj7",
    "Abmaj7#11", "Dbmaj7#11", "F#m7", "B7",
    # B
    "Emaj7#11", "Emaj7#11", "Gmaj7#11", "Gmaj7#11",
    "Bbmaj7#11", "Dbmaj7#11", "C7sus", "C7alt",
    # A3
    "Fmaj7#11", "Fmaj7#11", "Bm7 E7", "Amaj7",
    "Abmaj7#11 Dbmaj7#11", "Gm7 C7", "Fmaj7#11", "Gbmaj7#11",
]
SECTIONS = {0: "A1", 8: "A2", 16: "B", 24: "A3"}

HOOK = [
    "c''8 a' f' g' b' d''~ d''4~",          # F triad down, G triad up -> 13th
    "d''2 r8 a' b' c''",
    "d''8 b' fis' gis' b' e''~ e''4~",      # same shape on the ii-V
    "e''2 fis''8 e'' cis'' r",
]

HEAD = (
    # A1
    HOOK + [
        "d''4. bes'8~ bes'4 f'",                # hook in augmentation: Bb triad over Ab lydian
        "ees'4. g'8~ g'4 bes'~",                # Eb triad over Db lydian
        "bes'4 d''8 f'' e'' c'' a' g'",
        "aes'4 bes'8 c''~ c''4 r",
    ]
    # A2
    + HOOK + [
        "d''4. bes'8~ bes'4 f'",
        "ees'4. g'8~ g'4 bes'",
        "r4 a'8 cis'' e'' dis'' b' gis'",
        "a'2. r4",
    ]
    # B - each long note is the 13th of one chord, then the #11 of the next
    + [
        "gis'2 \\tuplet 3/2 { fis'4 ais' cis''~ }",
        "cis''2 b'4 r8 cis''~",
        "cis''2 \\tuplet 3/2 { a'4 cis'' e''~ }",
        "e''2 d''4 r8 e''~",
        "e''2 \\tuplet 3/2 { c''4 e'' g''~ }",
        "g''2 f''4 ees''",
        "d''4. c''8 bes' g' f'4",
        "r8 e' ges' aes' bes' des''~ des''4",
    ]
    # A3
    + HOOK + [
        "d''8 bes' f' ees' g' bes'~ bes'4~",    # third hook statement, compressed
        "bes'4 a'8 c'' e'' des'' bes' c''~",
        "c''1~^\"last time: hold this bar\"",
        "c''2. r4",
    ]
)
