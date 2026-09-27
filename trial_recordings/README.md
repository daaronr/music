# Trial recordings: one recipe for all three tunes

These are the comparison recordings for the three runs of the same composition prompt
(`../claude_halation`, `../claude_parallax`, `../codex_glass_meridian`). The model is the
Halation recording (`../claude_halation/audio/Halation_band_demo.mp3`), which was made from a
single audio request: a better-than-MIDI band recording with alto sax replacing the guitar.
It was not re-rendered. Parallax and Glass Meridian were rendered with the same code, samples,
settings and random seed.

| File | Tune | Length | Tempo (composer's marking) |
|---|---|---|---|
| `output/Halation_band_trumpet_alto.mp3` | Halation (copy of the model recording) | 2:58 | 184 |
| `output/Parallax_band_trumpet_alto.mp3` | Parallax | 3:12 | 176 |
| `output/Glass_Meridian_band_trumpet_alto.mp3` | Glass Meridian | 3:20 | 164 |

## The recipe

Halation's arrangement choices restated as rules (`engine/arrange.py`):

- Form: a 4-bar intro (rhythm section on the last four bars of the form), then the head,
  the two written duo choruses and the head out, closing with the composer's written ending.
  That ending is Halation's 2nd ending, Parallax's 4-bar coda, or Glass Meridian's last bar (F6/9).
- Head: trumpet melody, alto sax an octave below, 1.5 dB under the trumpet.
- Solos: trumpet as written; alto sax plays the guitar line. Guitar chords become their top note.
  A bar that leaves the alto's range (D♭3–A♭5) moves an octave; that happened only in Halation,
  bars 19 and 52.
- Ending: the trumpet's last note is held; the alto holds the final chord's tone nearest a fifth
  below it. The drummer swells on the ride, everyone cuts off on a crash, and piano and bass ring.
  The rule gives Halation's actual choice (E under B); Parallax gets G under D, Glass Meridian
  D under A.
- Rhythm section: generated from each run's own iReal Pro chart (checked bar by bar against the
  chord symbols in its scores). The bass plays in two for the head's A sections and walks
  elsewhere. Piano uses rootless voicings, lays out for the first eight solo bars and gets busier
  in chorus 2. Drums follow the same intensity curve with fills and crashes at the same form positions.
- Performance: swing 61% for the horns and 64% for the ride, the same humanised timing and
  dynamics, and each part's written dynamics and articulations.
- Sound and mix: University of Iowa solo trumpet; Apple GarageBand alto sax, Steinway,
  Upright Jazz Bass and SoCal drum kit. The same level targets, reverb and mastering are used,
  with every mix at -16 dBFS RMS.

Check: running Halation through the general code reproduces the original performance event for event.
Bass, piano and drums are identical; the horns differ only by 4 ms on the final held note.

Judgment calls:
- Each tune plays at its own marked tempo.
- Parallax's written intro (guitar alone, 4 bars) is left out, because the recipe's intro is the
  rhythm-section vamp that Halation used and Glass Meridian's notes ask for no intro.
- The notes come from each run's concert-pitch MusicXML. The chords come from each run's iReal link.

## Rebuilding

```bash
PY=/opt/homebrew/Caskroom/miniforge/base/bin/python3
$PY trial_recordings/check_inputs.py                  # chord cross-checks + Halation reproduction
$PY trial_recordings/engine/render.py parallax        # or glass_meridian / halation
$PY trial_recordings/engine/verify.py parallax <stem prefix>   # after rendering with --stems
```

`cache/trumpet_notes.npz` holds the Iowa trumpet notes (made by
`../claude_halation/src/audio/prepare_trumpet.py`); the Apple instruments are read from the
GarageBand library in place.
