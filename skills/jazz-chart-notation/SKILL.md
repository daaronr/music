---
name: jazz-chart-notation
description: Engrave jazz lead sheets, written solos, duo or soli scores and transposed parts as PDF, MusicXML and MuseScore files from a compact text notation, rendered with the MuseScore 3 command line. Use this whenever David wants sheet music made or fixed - a head or lead sheet, a written-out solo, parts for B-flat trumpet or flugelhorn, guitar or other instruments, "something I can import into MuseScore", concert and transposed versions, chord symbols over a melody - even if he doesn't say MusicXML. Includes harmony and counterpoint checks and fixes for MuseScore's import quirks.
---

# Jazz chart notation

Write music as short text strings, generate MusicXML, let MuseScore 3 engrave it, then look at
the result. The scripts in `scripts/` are plain Python 3 (stdlib only):

| File | What it does |
|---|---|
| `notation.py` | The text notation parser, chord-symbol parser, pitch spelling and transposition |
| `musicxml.py` | `PartSpec` / `ScoreSpec` and `write_score()` (MusicXML 3.1, partwise) |
| `check.py` | Flags notes outside each chord's implied scale, out-of-range notes, and unisons or minor 2nd/9th rubs between two players |
| `render.py` | MusicXML -> MuseScore import -> style patch -> `.mscz` and `.pdf` (optionally `.mid`, page PNGs) |
| `example_tune.py` | A complete 8-bar example with a concert part, a B-flat part and a guitar line. Start from a copy of it. |

A full project built this way, with a 32-bar head, intro, coda and a 64-bar trumpet/guitar duo,
is `~/githubs/music/claude_parallax/` (`src/tune.py`, `src/solo_ch1.py`, `src/build.py`).

## The notation

One string per bar, whitespace-separated tokens, concert pitch. Guitar is written at
sounding pitch; the treble-8vb clef displays it an octave up.

```
C5/q.  A4/8  F4/q  G4/q~       pitch/duration; ~ ties into the next note (same pitch)
r/8                            rest; durations: w h. h q. q 8. 8 16
3{Bb4/q Gb4/q Eb4/q}           triplet group (inner durations scaled by 2/3)
F3+A3/h                        double stop or chord
C5/8!acc!fall                  articulations: acc stac ten marc fall doit scoop ferm
(C5/8 ... D5/8)                slur start / stop
@mf @cresc @endw               dynamics and hairpins (placed before the next note)
@txt=Guitar_alone              expression text (underscores become spaces)
@ann=triad_pair_Eb/F           analysis note, printed only when ScoreSpec(annotations=True)
```

Chords per bar: `"Ebmaj7#11"` fills the bar; `"F#m11 F7#11"` splits at beat 3; `"Cm7@1 F7@4"`
places them by beat. Supported suffixes are the keys of `KINDS` in `notation.py` (maj7#11,
maj9#11, maj7#5, maj9, maj7, m(maj7), m7b5, m11, m9, m7, 13#11, 9#11, 7#11, 7alt, 13, 7sus4, 7,
triad); add more there if needed.

Every bar is checked for exactly four beats when parsed, so a wrong duration fails loudly with
the bar number.

## Workflow

1. Put the changes and the lines in a data file (lists of bar strings). Keep the head, each
   solo chorus and each instrument separate so they can be rearranged into different outputs.
2. Build `Measure`s with `parse_measure` / `parse_chords`, set `new_system` every 4 bars,
   `rehearsal`, `barline`, `new_page` (for "each chorus on its own sheet"), `implicit=True` for
   intro bars so the head is numbered from 1, then `link_ties()` across the whole part.
3. Make parts: `PartSpec(..., transpose=(1, 2), simplify=True)` for B-flat trumpet (written a
   major 2nd up, with a `<transpose>` element so playback stays concert);
   `clef="treble8vb", program=27` for guitar; `show_chords=False` on lower staves of a score.
4. `ScoreSpec(title, parts, subtitle=..., composer=..., left_label="Trumpet in B♭",
   tempo_text=..., bpm=..., staff_mm=..., system_distance=...)`, then `write_score()`.
5. Run `check.check()` on each line and `check.counterpoint(upper, lower)` on duets. Every flag
   should be something you meant (a chromatic approach, a side-slip). Fix the rest.
6. `render()` and **look at the pages** (`--png`, then Read the PNG). Layout problems only
   show up in the render.
7. Deliver PDF + MusicXML + `.mscz`, a combined PDF (`pdfunite a.pdf b.pdf all.pdf`), and a
   README listing the files. `mscore -o x.mid x.mscz` gives MIDI if wanted.

## Layout recipes

- One-page lead sheet with intro and coda (40 bars): `staff_mm=6.1, system_distance=90`.
- Parts with a chorus per page: default 7 mm staff, 4 bars per system, `new_page` on the
  first bar of chorus 2.
- Two-staff score, 4 bars per line even with triplets: `staff_mm=5.8`.
- Extra header lines: `credits_extra=[(text, 0.5, -75, 8, "center")]` (x as a fraction of page
  width, negative y = offset below the top margin). A credit placed at the bottom becomes its own
  frame and can push a one-page sheet onto two pages.

## MuseScore 3 quirks already handled (and why)

- Binary: `/Applications/MuseScore 3.app/Contents/MacOS/mscore` (override with `$MSCORE`). The
  `libjack` dlopen warnings it prints are harmless.
- `7alt` written as MusicXML kind `dominant` renders as plain "7": it is written as kind
  `other` with text `7alt`. If another symbol renders wrong, do the same for it (other runs saw
  `13sus` mangled too) and re-check the render.
- Tempo words plus a `<metronome>` element run together ("swing♩ = 176"), so both go in one
  words element.
- MuseScore puts page numbers top-left on even pages, on top of rehearsal marks; `render.py`
  patches the style to put them in the footer.
- Mid-bar chord changes over a held note use a harmony `<offset>`, which MuseScore honours.
- Written B-flat parts respell E♯, B♯, C♭, F♭ and double accidentals
  (`simplify=True`); concert parts keep the functional spelling.
- Some web hosts refuse XML with a `<!DOCTYPE>`; MuseScore does not need it, so strip it for
  publishing if asked.

## Ranges (concert/sounding)

| Instrument | Full | Comfortable for lines |
|---|---|---|
| Trumpet / flugelhorn in B-flat | F♯3 - C6 (written G♯3 - D6) | B♭3 - B♭5 |
| Guitar | E2 - A5 (written an octave up) | G3 - E5 |
| Alto sax | D♭3 - A♭5 | F3 - F5 |
| Tenor sax | A♭2 - E♭5 | B♭2 - B♭4 |
| Trombone | E2 - F5 | B♭2 - B♭4 |

`check.RANGES` holds trumpet and guitar; add others as needed.
