---
name: jazz-composition
description: Compose original jazz tunes and written-out solos - heads and changes (straightahead, post-bop, modern lydian or modal harmony), reharmonizations, contrapuntal duo or soli choruses, practice etudes built on devices like triad pairs, pentatonic shifting or rhythmic displacement - with a motivic plan, register plan and checked harmony. Use this whenever David asks for an original tune, a composed solo, a duet or trading-chorus arrangement, an etude for trumpet, flugelhorn or tuba, or wants to test what AI can compose, even if he doesn't say "compose". Pair with jazz-chart-notation to engrave and ireal-pro-chart for the backing chart.
---

# Jazz composition

Plan before writing notes. Most weak AI jazz writing comes from choosing notes bar by bar
without a governing idea, so every step below produces something you can point to in the
finished score. `references/devices.md` has the chord-by-chord device map and the texture
palette; read it before writing solo lines.

A worked example of the whole method (Parallax: 32-bar post-bop head plus a 64-bar
trumpet/guitar duo, with analysis notes printed in the score) is in
`~/githubs/music/claude_parallax/` (`src/tune.py`, `src/solo_ch1.py`, `src/solo_ch2.py`, README).

## 1. Harmonic concept and form

- Pick one organising harmonic idea and state it in a sentence. Examples: a fixed upper
  triad over a moving bass (F triad over E♭, D♭, B, B♭ = lydian, lydian
  augmented, altered, maj9); maj7♯11 chords planing by whole steps; ii - subV7♯11 -
  Imaj7♯11 cells moving in major thirds; a pivot tone that changes meaning under each
  chord.
- Keep a straight-ahead anchor players can blow on: walkable ii-Vs, a backdoor
  (iv - ♭VII7) or a clear dominant back to the top.
- Form: 32 bars (AABA, ABAC) is easiest to play and loop in iReal; an extension or odd phrase
  length is fine if it's deliberate. Decide intro, coda and endings now.
- Check the loop: the last bar must lead back to bar 1.

## 2. Motifs

- Write 2-3 short motifs (3-6 notes) with a rhythmic identity, designed to survive
  transformation: inversion, retrograde, augmentation, diminution, displacement, transposition
  along the form. Name them (X, Y, Z) and say where each first appears.
- A strong head often states one motif several times over changing harmony, displacing each
  restatement (by an eighth, then a quarter), then answers it.

## 3. Melody

- Put long notes on colour tones (♯11, 9, 13, maj7) and guide tones; use shorter notes to
  connect. Plan the contour: one high point per chorus, usually two-thirds of the way through.
- Keep the head in the lead instrument's comfortable register (trumpet concert B♭3-G5 for a
  head; the solo can go higher).

## 4. A written solo, especially a duo

1. Write a roadmap first: an 8-bar-per-row table of who plays, what device, and the energy
   level, across both choruses. Aim for a real arc: an opening that quotes or transforms the
   head, build-ups, one climax (last third of the last chorus), and a wind-down into the out-head.
2. Give each player solo space as well as overlap. Roughly half the bars with both playing
   reads as "weaving"; both silent at once only for a deliberate breath.
3. Use the texture palette in `references/devices.md`: call and response, canon, inversion in
   the second voice, augmentation against diminution, a held note whose meaning changes under
   the other voice's line, hocket, voice exchange, contrary motion with crossing, octave unison
   for drama.
4. Quote the head a few times, literally once and transformed more often. Use classic licks
   sparingly (an enclosure, a 1-2-3-5 pattern, a bebop triplet turn, a ♭9 arpeggio, guitar
   octaves) and label them.
5. Registers: keep the guitar mostly below the trumpet; make crossings events, not accidents.

## 5. Check and annotate

- Run the chord-scale check and the two-voice check from jazz-chart-notation
  (`check.check`, `check.counterpoint`). Every flag should be intentional: a side-slip, a
  chromatic approach, a planned voice crossing. Avoid minor-9th rubs between the players on
  strong beats.
- Print short analysis notes in a study score (`@ann=...` with `annotations=True`) and keep
  clean parts without them.
- In the README, say which devices are where, and present them as claims to check against the
  score. Recommend a human play-through; nothing here has been heard unless someone played it.
