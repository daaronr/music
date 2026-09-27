"""Worked example: an 8-bar lead sheet in concert and B-flat, plus a guitar line.

    cd <this scripts folder>; python3 example_tune.py /tmp/demo
Copy this file next to your project's data and edit; the library files
(notation.py, musicxml.py, check.py, render.py) sit alongside it.
"""

import os
import sys

import check
from musicxml import PartSpec, ScoreSpec, write_score
from notation import Measure, link_ties, parse_chords, parse_measure
from render import render

CHORDS = ["Fmaj7#11", "Fmaj7#11", "Ebmaj7#5", "Ebmaj7#5",
          "Em7b5 A7alt", "Dm9", "Gm9 C7alt", "Fmaj9"]
MELODY = [                                   # concert pitch, 4/4, durations w h. h q. q 8. 8 16
    "@mf r/8 A4/8 C5/8 G4/8 B4/q. D5/8~",
    "D5/h. r/q",
    "r/8 B4/q.!acc G4/8 D5/8 F5/8 D5/8",
    "C5/h 3{B4/8 C5/8 B4/8} G4/q",
    "Bb4/8 A4/8 G4/8 E4/8 G4/8 Bb4/8 C#5/8 F5/8",
    "D5/w",
    "r/q F4/8 Bb4/8 Ab4/8 Gb4/8 E4/8 Db4/8",
    "F4/h. r/q",
]
GUITAR = [                                   # sounding pitch: shown an octave up (treble 8vb)
    "F3+C4/h r/h", "r/w", "Eb3+G3/h r/h", "r/w",
    "Bb3/q E3/q C#4/q G3/q", "F3/w", "Bb3/q D3/q r/h", "A3+C4/w!ferm",
]


def measures(lines, where):
    out = []
    for i, (ch, line) in enumerate(zip(CHORDS, lines)):
        m = Measure(parse_measure(line, f"{where} bar {i + 1}"), parse_chords(ch))
        m.new_system = i % 4 == 0
        out.append(m)
    out[0].rehearsal = "A"
    out[-1].barline = "light-heavy"
    link_ties(out)
    return out


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    print("harmony check (every flag should be intended):")
    check.check(measures(MELODY, "melody"), "melody")
    check.counterpoint(measures(MELODY, "melody"), measures(GUITAR, "guitar"))
    jobs = {
        "demo_concert": [PartSpec("P1", "Melody", "Mel.", measures(MELODY, "m"))],
        "demo_Bb": [PartSpec("P1", "Trumpet in Bb", "Tpt.", measures(MELODY, "m"),
                             transpose=(1, 2), simplify=True)],
        "demo_duo": [PartSpec("P1", "Trumpet", "Tpt.", measures(MELODY, "m")),
                     PartSpec("P2", "Guitar", "Gtr.", measures(GUITAR, "g"), clef="treble8vb",
                              program=27, show_chords=False)],
    }
    for name, parts in jobs.items():
        score = ScoreSpec("Demo", parts, subtitle="notation smoke test", composer="",
                          tempo_text="Medium swing", bpm=160, staff_mm=6.5)
        path = os.path.join(outdir, name + ".musicxml")
        write_score(score, path)
        for w in render(path, ("pdf", "mscz"), png=name == "demo_duo"):
            print("wrote", w)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "demo_out")
