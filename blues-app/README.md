# Blues Flow

Play and study the 18 twelve-bar blues progressions from a printed chart in F
(photo: `../blues_variations_in_F.JPG`), from three chords up to Parker-style
changes. Live at https://daaronr.github.io/music/ (deployed by
`../.github/workflows/deploy.yml` on every push to `main`).

What it does:

- Shows any form as a 12-bar lead sheet in any key, with chord names for concert,
  B♭, E♭ or F instruments, roman numerals and guide tones (3rds and 7ths).
- Plays it with a backing trio: grand piano comping, a walking (or two-feel)
  upright bass and ride cymbal, swung, at any tempo, with a count-in. "Step
  through all 18" plays one chorus of each form in turn.
- Marks which bars changed from the previous form (or from the basic blues),
  explains what each form adds, and gives chord tones for any bar you click.
- A flowchart of every chord option in every bar. Click one to swap it into
  the progression, as the chart's own note suggests; mixes are kept in the URL.
- The full chart as a table in the chosen key.
- `public/audio/blues-18-forms.mp3`: all 18 forms with a short narrated intro
  to each, rendered offline from the same arranger.

## Source of truth

`src/music/progressions.ts` holds the chart exactly as printed (F, with `-`,
`Δ`, `°`, `C-/F`). Roman numerals, other keys and transposed parts are all
derived from it, and `src/music/music.test.ts` checks the data prints back
unchanged and matches the photo in hand-checked places. If a chord looks wrong,
compare that file with the photo; nothing else needs changing.

Forms 9 to 18 were wrong in earlier versions of this app (bars 6 to 12 had
been filled in from `../blues_variations_wrong.md`, and the `#iv°7` "fix" in
commit a171c74 was built on that wrong data). They were re-transcribed from the
photo in September 2026. `../blues_variations.md`, `../blues_flowchart*.md` and
the older static page `../index.html` still carry some of the old errors.

## Layout

- `src/music/theory.ts`: letter-based spelling, transposition, chord symbols,
  roman numerals, chord and guide tones.
- `src/music/arranger.ts`: voicings (rootless A/B forms, voice-led), walking
  bass (scored search over chord, scale and approach tones), comping rhythms,
  ride pattern. Deterministic for a seed.
- `src/audio/engine.ts`: look-ahead scheduler on the Web Audio clock; samples
  are defined in `src/audio/samples.ts` (Splendid Grand Piano, D. Smolken
  pizzicato bass, VCSL cymbals, all via smpldsnds.github.io; the electric
  piano, guitar and organ are General MIDI soundfonts through smplr).
- `scripts/render-tour.ts`: offline renderer for the MP3.

## Commands

```bash
npm install
npm run dev          # http://localhost:5173/music/
npm test             # theory, data and arranger checks
npm run build
npm run render:tour  # rebuild public/audio/blues-18-forms.mp3 (needs ffmpeg; narration via local Kokoro, else macOS say)
```

`render:tour` takes `--tempo`, `--key`, `--out` and `--voice say|kokoro`.
Narration text is in the script; samples and speech are cached in `.cache/`.
