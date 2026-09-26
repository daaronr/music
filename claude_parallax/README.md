# Parallax

An original medium-up post-bop tune, plus a two-chorus trumpet and guitar duo solo on its changes.
Written by Claude (Opus 5.5, max effort) in the Claude Code desktop app on 2026-09-26, as one of
three runs of the same prompt (the others are in `../claude_halation/` and `../codex_glass_meridian/`,
which this run did not look at while composing).

## Files (`output/`)

| What | PDF | MuseScore / MusicXML |
|---|---|---|
| Lead sheet, concert (intro, head, coda) | `Parallax_lead_sheet_concert.pdf` | `.mscz`, `.musicxml` |
| Lead sheet, Bb trumpet | `Parallax_lead_sheet_Bb_trumpet.pdf` | `.mscz`, `.musicxml` |
| Duo solo, study score in C, with analysis notes | `Parallax_duo_solo_score_concert.pdf` | `.musicxml` |
| Duo solo, transposing score for MuseScore (toggle Concert Pitch) | | `Parallax_duo_solo_MuseScore.mscz` |
| Trumpet solo part, concert pitch | `Parallax_solo_trumpet_concert.pdf` | `.mscz`, `.musicxml` |
| Trumpet solo part, Bb | `Parallax_solo_trumpet_Bb.pdf` | `.mscz`, `.musicxml` |
| Guitar solo part (treble clef, sounds 8vb) | `Parallax_solo_guitar.pdf` | `.mscz`, `.musicxml` |
| Everything above in one file | `Parallax_all_sheets.pdf` | |
| iReal Pro chart | open `Parallax_iReal_import.html`, click the link | `Parallax_iReal_link.txt` |
| MIDI of the duo solo | | `Parallax_duo_solo.mid` |

Each solo part puts chorus 1 on page 1 and chorus 2 on page 2.

## The tune

32 bars, AABA, concert, medium-up swing at about 176.

```
A  | Ebmaj7#11 | %           | Dbmaj7#5    | %        | B7alt       | Bbmaj9    | Abm9    | Db13#11 |
A  | Ebmaj7#11 | %           | Dbmaj7#5    | %        | B7alt       | Bbmaj9    | G#m7b5  | C#7alt  |
B  | F#m11 F7#11 | Emaj7#11  | Dm11 Db7#11 | Cmaj7#11 | Bbm11 A7#11 | Abmaj7#11 | Fm11    | E7#11   |
A  | Ebmaj7#11 | %           | Dbmaj7#5    | %        | B7alt       | Bbmaj9    | Abm9    | Db13#11 |
```

The idea behind the title: the F major triad (F-A-C, with G) sits still while the bass moves under
it, so the same notes read as lydian over Eb, lydian augmented over Db, altered over B and maj9
over Bb. The head states that cell three times, each time one eighth later than the last (0, 1, 2
eighths). The bridge runs ii - subV7#11 - Imaj7#11 down in major thirds (E, C, Ab), holds the #11
on each lydian arrival, and repeats the 0/1/2-eighth displacement. A2 ends with a held D (3rd of
Bb, b5 of G#m7b5, b9 of C#7alt): the melody stays still and the harmony moves.

Lydian triad pairs: Eb/F covers both Ebmaj7#11 and Dbmaj7#5; E/F#, C/D and Ab/Bb cover the bridge.

## The duo solo, eight bars at a time

| Bars | Trumpet | Guitar |
|---|---|---|
| 1-8 | opening cell in eighths, displaced; F major pentatonic over B7alt | answers with the cell inverted, quotes the head an octave down, bebop enclosure, triplet motif |
| 9-16 | four-note pentatonic cells (Bb, F, Eb) in a 4+1 eighth cycle, so each lands later; held Eb then D from the head | the cell in augmentation (half notes); B7#5b9 line; lines that cross above the trumpet |
| 17-24 | long tones at 0/1/2-eighth offsets; Fm9 climb to a high G# | 1-2-3-5 patterns and triad pairs (E/F#, C/D in quarter triplets, Ab/Bb); E7#11 rising to the #11 |
| 25-32 | cell displaced 3 eighths; high A held from Eb to Db (#11 becomes #5); hocket | cell displaced 4 eighths; hocket; triplet motif leads into chorus 2 |
| 33-40 | tacet, then a high A that is b7 of B7 and maj7 of Bb; head motif | alone: 3-over-4 pentatonic cells with a half-step side-slip; Bb/C triad pair; head motif in fourths |
| 41-48 | Eb/F triad pair in triplets; the cell in augmentation; contrary motion (voices cross); octave unison run | quartal lines; the same triad pair over Db; octave unison run |
| 49-56 | bridge cell in octaves, then handed back and forth; C/D pair; climax on Bb (11 of Fm, #11 of E7) | cell passes to guitar; E/F# and Ab/Bb runs; Wes-style octaves |
| 57-64 | resolves to A; canon on the cell at the octave; voice exchange; head bars 5-8 into the out-head | same canon; voice exchange; motif in sixths below |

Classic vocabulary, used sparingly: enclosures, a bebop triplet turn, Coltrane 1-2-3-5 patterns,
a B7#5b9 line, octaves. Modern devices: pentatonic shifting and side-slipping, triad pairs,
rhythmic displacement, 3-over-4 and 5-eighth groupings, quartal lines, hocket, canon, voice exchange.

## Rebuilding

Needs Python 3 and MuseScore 3 at `/Applications/MuseScore 3.app`.

```bash
python3 src/build.py
```

`src/tune.py` holds the changes and head, `src/solo_ch1.py` and `src/solo_ch2.py` the solo, all in a
small text notation (see `src/notation.py`). The build also runs `src/check.py`, which flags every
note outside the implied chord scale and every unison or minor-2nd/9th rub between the two players.
The remaining flags are intended (a side-slip, chromatic approach notes, one voice crossing).
`python3 src/ireal.py` rewrites the iReal link.
