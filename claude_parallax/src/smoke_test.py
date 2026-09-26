"""Render a few bars to check chord symbols, clefs, tuplets, ties and transposition."""

import sys

from musicxml import PartSpec, ScoreSpec, write_score
from notation import Measure, link_ties, parse_chords, parse_measure

BARS = [
    ("Ebmaj7#11", "@mf C5/q. A4/8 F4/q G4/q~"),
    ("Dbmaj7#5", "G4/8 C5/h r/q."),
    ("B7alt", "r/q C5/8!acc A4/8 F4/8 G4/8 Eb5/q"),
    ("F#m11 F7#11", "A5/w"),
    ("G#m7b5", "3{Bb4/q Gb4/q Eb4/q} F4/q Cb5/q"),
    ("Db13#11", "3{C5/8 D5/8 E5/8} F4+A4/q. B#4/8 r/q"),
    ("C#7alt", "Fb4/q Cb5/q E#5/q B#4/q"),
    ("Ebmaj7#11", "D5/w!ferm"),
]


def measures():
    out = []
    for i, (ch, notes) in enumerate(BARS):
        m = Measure(parse_measure(notes, f"bar {i + 1}"), parse_chords(ch))
        m.new_system = i % 4 == 0
        out.append(m)
    out[0].rehearsal = "A"
    out[-1].barline = "light-heavy"
    link_ties(out)
    return out


def main(dest):
    parts = [
        PartSpec("P1", "Trumpet (concert)", "Tpt.", measures()),
        PartSpec("P2", "Trumpet in Bb", "Tpt.", measures(), transpose=(1, 2), simplify=True),
        PartSpec("P3", "Guitar", "Gtr.", measures(), clef="treble8vb", program=27),
    ]
    score = ScoreSpec("Smoke Test", parts, subtitle="checking the pipeline",
                      composer="Claude", tempo_text="Medium-up swing", bpm=176,
                      annotations=True)
    write_score(score, dest)


if __name__ == "__main__":
    main(sys.argv[1])
