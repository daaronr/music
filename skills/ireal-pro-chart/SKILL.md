---
name: ireal-pro-chart
description: Make an iReal Pro chord chart as an irealbook:// import link plus a small click-to-import HTML page, from a plain list of chords. Use this whenever David wants changes "in iReal", "for iReal Pro", as a practice loop or backing track, or converted from a lead sheet, handwritten chart, PDF or MusicXML, including gig-packet tunes and original tunes, even if he just says "chord chart for iReal".
---

# iReal Pro chart

`scripts/ireal_link.py` turns a small text chart into the import link and an HTML page with a
button. David opens the HTML on a device with iReal Pro and clicks; iReal shows a preview and
asks before adding the song.

```
python3 scripts/ireal_link.py chart.txt --out <folder>
```

```
title: Parallax
composer: Claude
style: Medium Up Swing
key: Eb
[A] Ebmaj7#11 | % | Dbmaj7#5 | % | B7alt | Bbmaj9 | Abm9 | Db13#11
[B] F#m11 F7#11 | Emaj7#11 | Dm11 Db7#11 | Cmaj7#11 | ...
coda_jump: 31                      # optional: the last chorus jumps here to the coda
coda: Abm9 | Db13#11 | Ebmaj7#11 | Ebmaj7#11
note: Set the tempo to about 176.   # shown on the HTML page
```

One to four chords per bar (two = beats 1 and 3); `%` repeats the previous bar. Section labels
become rehearsal marks (`[A2]` prints as A with an "A2" text cue). It prints the bar count; check
it against the form before handing over.

Don't open the `irealbook://` link yourself: that imports into David's library. Give him the
HTML page (and the raw link in the .txt) instead, unless he asks you to import it.

## Protocol notes (for hand edits)

Source: iReal's [custom chord chart protocol](https://www.irealpro.com/ireal-pro-custom-chord-chart-protocol).

- `irealbook://Title=Composer=Style=Key=n=Progression`, percent-encoded as a whole. Titles
  starting with "The" go as "Title, The"; composer as "Last First".
- 16 cells per line, max 12 lines; a chord or a space is one cell, a comma or symbol is none.
  Four cells per bar keeps four bars to a line: `Eb^7#11   |` or `F#-11 F7#11 |`.
- `[` `]` double bars, `{` `}` repeats, `|` bar, `Z` final bar; `T44` time signature; `*A`
  `*B` `*C` `*D` `*V` `*i` rehearsal marks; `N1` `N2` endings; `Q` coda (first Q = jump on
  the last chorus, second Q = the coda); `S` segno; `f` fermata; `<text>` staff text; `Y`
  extra space before a line; `x` repeat one bar; `n` N.C.; `s`/`l` small/large chords;
  `(Db^7)` alternate chord.
- Qualities: `^7 ^9 ^13 ^7#11 ^9#11 ^7#5 6 69 - -7 -9 -11 -6 -69 -^7 -^9 h7 h9 o o7 + 7 9
  13 7alt 7b9 7#9 7#11 7b5 7#5 7b13 9#11 13#11 13b9 7sus 9sus 13sus 7b9sus 11 5 2 add9`.
  The script maps common spellings (maj7#11, m7b5, m(maj7), 7sus(b9), 9(#11)...) and stops
  with a clear message on anything it can't map; respell or add to `QUALITY`.
- Styles include Medium Swing, Medium Up Swing, Up Tempo Swing, Ballad, Bossa Nova, Latin,
  Samba, Funk, Waltz, Even 8ths. Tempo is set in the app.

## Playback gotchas

- iReal loops the whole chart for each chorus. An intro section may be replayed every chorus,
  so keep the loop to the form and put intros on the lead sheet (or tell David to add one in
  iReal's editor).
- A coda needs both `Q` marks: the jump point inside the form and the coda section after `Z`.
  To tag the last bars, include them again at the start of the coda.
- Chords with parentheses or unusual extensions may not parse in iReal; stay with the quality
  list above.
