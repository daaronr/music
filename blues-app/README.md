# Blues Flow

Play and study the 18 twelve-bar blues progressions from a printed chart in F
(photo: `../blues_variations_in_F.JPG`), from three chords up to Parker-style
changes. By David Reinstein.

Two copies, same code:

- **https://blues-flow.netlify.app** (the one to share): deployed by hand with
  `bash blues-app/deploy-netlify.sh "message"`. Also hosts the functions below.
- https://daaronr.github.io/music/: deployed by `../.github/workflows/deploy.yml`
  on every push to `main`. It calls the Netlify functions for votes etc.

So after a change: push, and run `deploy-netlify.sh`.

What it does:

- Shows any form as a 12-bar lead sheet in any key, with chord names for concert,
  B♭, E♭ or F instruments, roman numerals and guide tones (3rds and 7ths).
- Plays it with a backing trio: grand piano comping, a walking (or two-feel)
  upright bass and ride cymbal, swung, at any tempo, with a count-in. "Step
  through all 18" plays one chorus of each form in turn.
- Marks which bars changed from the previous form (or from the basic blues),
  explains what each form adds, and gives chord tones for any bar you click.
- A flowchart of every chord option in every bar (zoom, full screen, roman
  numerals only if you like). Click one to swap it into
  the progression, as the chart's own note suggests; mixes are kept in the URL.
- The full chart as a table in the chosen key.
- A vote on favourite forms; results (a bar chart) only after voting.
- Credit and links (K-House, YouTube), a feedback form, and a nudge to donate
  to The Unjournal or GiveWell instead of paying, with a form to say you did.
- Printable posters in `public/posters/` (map of every option per bar,
  flowchart, table), in several keys and in roman numerals only.
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

## Votes, feedback, donations and usage counts

Netlify functions in `netlify/functions/`, data in Netlify Blobs (site
`blues-flow`): `vote` and `results` (store `votes`), `note` (store `notes`:
feedback and "I donated" messages, never served back), `hit` (store `hits`:
cookie-free usage counter; skipped under Do Not Track). Ids starting `test-`
(all ids in `npm run dev`) are kept out of results and counts.

```bash
node blues-app/netlify/stats.mjs            # visits, events, devices, referrers, votes
node blues-app/netlify/stats.mjs notes      # feedback and donation notes (names, emails)
node blues-app/netlify/stats.mjs votes      # every vote with comments
node blues-app/netlify/stats.mjs --days 7
```

There are no notifications yet: check `stats.mjs notes` to see new feedback.

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
node scripts/make-poster.ts  # rebuild public/posters/*.pdf (needs Google Chrome); --key Eb --for Bb --paper A3 --roman yes for one-offs
```

YouTube videos (outputs and ready-to-paste descriptions in `video/output/`):

```bash
# 1. All 18 forms, narrated, lead sheet lit bar by bar (needs rsvg-convert)
node scripts/render-tour.ts --out .cache/video1/music.wav --timeline .cache/video1/timeline.json
node scripts/make-video-forms.ts --force
# 2. Narrated app walkthrough: needs the dev server on port 5178 and step 1's files
npm run dev -- --port 5178 &
node scripts/make-video-tour.ts
```

`render:tour` takes `--tempo`, `--key`, `--out` and `--voice say|kokoro`.
Narration text is in the script; samples and speech are cached in `.cache/`.
