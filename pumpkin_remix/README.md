# The Glory of the Pumpkin (Disco-Trap Remix)

A dance remix of the 2023 Thanksgiving sing-along
([YouTube](https://www.youtube.com/watch?v=rMWoPkhzRvE)). The vocal is David's own take from that
video, separated from the mix and re-timed. Everything else is new: synthesized house and 808 drums,
synth bass, supersaws, plus GarageBand/Logic sampled strings, brass, piano, guitar and claps.

- `output/Glory_of_the_Pumpkin_Disco_Trap_Remix.mp3`: 3:14, 128 BPM, C major, mastered to about −9.5 LUFS
- the 24-bit WAV master is in the same folder locally (not committed)

## Web player

Open [index.html](index.html) to listen locally. It plays the MP3 in `output/`
and jumps to the sections below. The cover is a still from the original sing-along.

For a Netlify deploy, package the player, cover and MP3 from the pushed commit.
From the repository root:

```bash
site_dir=$(mktemp -d)
git archive HEAD:pumpkin_remix index.html cover.webp output/Glory_of_the_Pumpkin_Disco_Trap_Remix.mp3 | tar -x -C "$site_dir"
netlify deploy --prod --no-build --dir "$site_dir" --site your-netlify-site-name
```

## Structure

| Time | Bars | Section |
|---|---|---|
| 0:00 | — | Cold open: the original video audio ("but the glory of the pumpkin is the pie"), lo-fi, tape stop |
| 0:08 | 0–7 | Intro: filtered disco groove on C · Am7 · Dm9 · G7, "pump-kin" chops |
| 0:23 | 8–23 | Verse 1, disco: "Oh a lone pumpkin… a useful fellow!" Four-on-the-floor, octave bass, strings, guitar, brass stabs |
| 0:53 | 24–31 | Break and build: piano and strings, "Oh a lone pumpkin" echo, snare build, "but the glory of the pumpkin is the…" |
| 1:08 | 32–47 | Drop: "PIE!", supersaws, the lead plays the tune's hook, vocal chops |
| 1:38 | 48–63 | Verse 2, half-time trap: 808s, hat rolls, a quiet octave-down double. "So he raised up his head… Thanksgiving dinner" |
| 2:08 | 64–71 | Build: "Thanksgiving dinner" chops, back to four-on-the-floor |
| 2:23 | 72–87 | Final chorus, full disco: "For the glory of the Jack… the glory of the turkey is the drumstick". The band stops for "but the glory of the pumpkin is the…" (voice and strings) and comes back on "PIE" |
| 2:53 | 88–95 | Outro: loop, last "pie", and the original video's final chord |

## How it was made

1. **Source.** The audio track of `Dropbox/large_videos/The Glory of the Pumpkin - Thanksgiving sing-along - SD 480p.mov`
   (the YouTube upload), plus the chords and melody from `~/Documents/MuseScore3/Scores/Glory_of_the_pumpkin.mscz`.
   The Nov 2022 GarageBand bounces in `Dropbox/music_recordings/pumpkin - *.mp3` were not used; no
   pumpkin `.band` project turned up.
2. **Stems.** Demucs (`htdemucs_ft`) split the video audio into vocals and accompaniment.
3. **Timing.** Whisper word timestamps plus pitch-track onsets locate each sung syllable. A smooth
   tempo fit shows the performance at a steady ~70 bpm with nearly straight eighths. It slows a lot
   at "is the pie".
4. **Re-timing.** One sung beat became two beats at 128 BPM, so the vocal plays about 9% slower
   than sung. Rubber Band (R3 engine, formants kept) uses a time map that puts 118 syllables on their
   written positions. The final ritardando is taken out. Onsets sit a median 28 ms from the grid.
5. **Pitch.** Chord-aware correction (Rubber Band pitch map), one constant shift per sung note so
   vibrato survives. Each note goes to the written melody note when the voice is within 1.2
   semitones of it, otherwise to the nearest note that fits the chord. Median error against those
   targets went from 29 to 13 cents.
6. **Arrangement, mix and master.** `src/song.py`, all numpy/scipy. Each bus is set to a loudness
   target. Kick sidechain pumps the bass and chords. The music dips up to 4 dB while the voice sings,
   and there is section-level gain so the break dips and the drops hit.

## Choices worth knowing about

- **Chords follow the performance where the chart differs.** A chroma comparison
  (`src/check_chords.py`) showed the video's accompaniment playing simpler chords than the MuseScore
  chart in places. In a few spots the chart's chord clashes with the sung note (C♯dim under a sung C
  on "head", A7 under a sung C on "Jack is in the"). Changes are listed in `CHORD_FIX` in
  `src/harmony.py`: G7 for bars 11–12, C for "winner", Dm7 for "true, he was", Am7 and Dm7 in bars 18–19,
  and plain G7 for G+7 / G7♭9.
- **The hook is spliced from the clearest takes.** In the video, "is the pie" is sung with a big
  ritardando and Whisper hears it as "is now ours". The drop chops use "glory of the pumpkin" from
  the last line, "is the" from "the turkey is the drumstick", and "PIE!" from "proud pumpkin pie".
  The final chorus keeps your held last "pie".
- The drop loop is C · Am7 · Dm9 · G7 (I–vi–ii–V), the song's own bars 18 and 24.

## Checks (no ears, so measured)

- Section loudness: break about 5 dB under the drops, intro 3–4 dB under. No silent gaps, peak −2.5 dBFS.
- Spectrum: sub 28%, bass 29%, low-mid 36%, upper bands 7% of energy. That started at 63% sub
  before the buses were set to loudness targets.
- Harmony: per-bar vocal vs. backing chroma correlation median 0.24. The same measure gives 0.13 on
  the original video's own vocal against its accompaniment.
- Words: Whisper (no lyric prompt) on the finished mix follows both verses and the final chorus
  nearly word for word ("So he raised up his head… his fondest wish came true… the pride of the
  whole Thanksgiving dinner… the glory of the turkey is the drumstick"). The hook was the weak spot.
  After the splice, vocal ducking and the stop, the drop reads "the glory of the pumpkin is
  good-bye" and the last line "the glory of the pumpkin is the sun". "Pie" stays soft, as it is in
  the original take.

Not verified by ear:
- whether the Demucs vocal has audible artifacts (the source is a 127 kbps AAC from an iMovie export)
- the build into the first drop (bars 28–31): the vocal reads clearly on its own, but Whisper finds
  no words in the mix there
- how the whole thing feels on a dance floor

## Rebuild

```bash
bash pumpkin_remix/build.sh
```

`work/` (stems, warped vocals, mix stems) is regenerated and not committed.
