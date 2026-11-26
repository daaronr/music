# The Glory of the Pumpkin (Disco-Trap Remix)

A dance remix of the 2023 Thanksgiving sing-along
([YouTube](https://www.youtube.com/watch?v=rMWoPkhzRvE)). The remix combines David's original
vocal and short passages of his recorded brass with new house drums, 808s, synth bass and
GarageBand/Logic instruments.

- `output/Glory_of_the_Pumpkin_Disco_Trap_Remix.mp3`: 3:14, 128 BPM, C major, about −11 LUFS integrated
- the 24-bit WAV master is in the same folder locally (not committed)

## Web player

[Listen on Netlify](https://glory-of-the-pumpkin.netlify.app/) or open [index.html](index.html)
locally. The cover is a still from the original sing-along.

For a Netlify deploy, package the player, cover and MP3 from the pushed commit.
From the repository root:

```bash
site_dir=$(mktemp -d)
git archive HEAD:pumpkin_remix index.html cover.webp output/Glory_of_the_Pumpkin_Disco_Trap_Remix.mp3 | tar -x -C "$site_dir"
netlify deploy --prod --no-build --dir "$site_dir" --site glory-of-the-pumpkin
```

## Structure

| Time | Bars | Section |
|---|---|---|
| 0:00 | — | Cold open: the original recording ("but the glory of the pumpkin is the pie"), tape stop |
| 0:08 | 0–7 | Intro: original brass pickup, then the disco groove and "pump-kin" chops |
| 0:23 | 8–23 | Verse 1, disco: "Oh a lone pumpkin… a useful fellow!" Four-on-the-floor, octave bass, strings, guitar, and an original brass reply after "yellow" |
| 0:53 | 24–31 | Break and build: piano and strings, "Oh a lone pumpkin" echo, snare build, "but the glory of the pumpkin is the…" |
| 1:08 | 32–47 | Drop: "PIE!", supersaws, the lead plays the tune's hook, vocal chops |
| 1:38 | 48–63 | Verse 2, half-time trap: 808s, hat rolls, a quiet octave-down double and a recorded brass fill. "So he raised up his head… Thanksgiving dinner" |
| 2:08 | 64–71 | Build: "Thanksgiving dinner" chops, back to four-on-the-floor |
| 2:23 | 72–87 | Final chorus, full disco: "For the glory of the Jack… the glory of the turkey is the drumstick". The band stops for "but the glory of the pumpkin is the…" (voice and strings) and comes back on "PIE", with low brass from the original coda |
| 2:53 | 88–95 | Outro: loop, last "pie", and the original video's final chord |

## How it was made

1. **Source.** The stereo GarageBand export `pumpkin - 21:11:2022, 23C.mp3` matches the
   performance in the 2023 sing-along. The build aligns the export to the video timing and
   can use the video soundtrack if the export is unavailable. The chords and melody come
   from `Glory_of_the_pumpkin.mscz`.
2. **Stems.** Demucs (`htdemucs_ft`) separates the vocal and accompaniment from the stereo
   export. The recorded brass comes from short instrumental passages in the accompaniment
   stem with minimal vocal bleed. Rubber Band fits each passage to the new tempo.
3. **Timing.** Whisper word timestamps plus pitch-track onsets locate each sung syllable. A smooth
   tempo fit shows the performance at a steady ~70 bpm with nearly straight eighths. It slows a lot
   at "is the pie".
4. **Re-timing.** One sung beat became two beats at 128 BPM, so the vocal plays about 9% slower
   than sung. Rubber Band (R3 engine, formants kept) uses a time map that puts the sung
   syllables on their written positions and straightens the final ritardando.
5. **Pitch.** Chord-aware correction (Rubber Band pitch map), one constant shift per sung note so
   vibrato survives. Each note goes to the written melody note when the voice is within 1.2
   semitones of it, otherwise to the nearest note that fits the chord.
6. **Arrangement, mix and master.** `src/song.py`, all numpy/scipy. Each bus is set to a loudness
   target. The mix uses a drier, centered lead with a slower compressor attack to let the
   consonants through. The backing dips under the voice. The synth bass and 808s use a
   lower register and a stronger low end.

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

## Listening checks

Check the words in the build into the first drop, the recorded brass in the intro and between
vocal lines, and the bass in both the disco and trap sections.

## Rebuild

```bash
bash pumpkin_remix/build.sh
```

`work/` (stems, warped vocals, mix stems) is regenerated and not committed.
