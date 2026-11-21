"""Sheets for the two-chorus duo solo: score, trumpet (concert + Bb), guitar."""


def build(E, H, S, part, emit, ch_c, ch_bb):
    tpt = E.parse_part(S.TRUMPET)
    gtr = E.parse_part(S.GUITAR)
    assert len(tpt) == len(gtr) == 2 * len(ch_c)
    tpt_bb = E.transpose_part(tpt, 1, 2)
    ch2_c, ch2_bb = ch_c + ch_c, ch_bb + ch_bb
    solo = dict(staffsize=18, pagebreaks=(32,), sysdist=13)
    return [
        emit("Brightwork_03_duo_solo_score_concert",
             [part("P1", "Trumpet (concert)", "Tpt.", tpt, ch2_c),
              part("P2", "Guitar", "Gtr.", gtr, None, clef="G8vb", program=27)],
             S.SECTIONS, "Duo solo (2 choruses) - score, concert pitch",
             staffsize=16, pagebreaks=(16, 32, 48), sysdist=20),
        emit("Brightwork_04_trumpet_solo_concert",
             [part("P1", "Trumpet (concert pitch)", "Tpt.", tpt, ch2_c)],
             S.SECTIONS, "Duo solo (2 choruses) - trumpet, concert pitch", **solo),
        emit("Brightwork_05_trumpet_solo_Bb",
             [part("P1", "Trumpet in Bb", "Bb Tpt.", tpt_bb, ch2_bb, fifths=2, transpose=(-1, -2))],
             S.SECTIONS, "Duo solo (2 choruses) - trumpet in B-flat", **solo),
        emit("Brightwork_06_guitar_solo",
             [part("P1", "Guitar", "Gtr.", gtr, ch2_c, clef="G8vb", program=27)],
             S.SECTIONS, "Duo solo (2 choruses) - guitar (sounds an octave lower, as usual)", **solo),
    ]
