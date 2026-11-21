\version "2.24.0"
#(set-default-paper-size "a4")
#(set-global-staff-size 18)
\paper {
  top-margin = 12\mm
  bottom-margin = 12\mm
  left-margin = 14\mm
  right-margin = 14\mm
  indent = 0\mm
  short-indent = 0\mm
  ragged-last-bottom = ##f
  ragged-bottom = ##f
  print-page-number = ##t
  markup-system-spacing.basic-distance = #18
  system-system-spacing.basic-distance = #13
  system-system-spacing.minimum-distance = #9
}
\header {
  title = "Brightwork"
  subtitle = "Duo solo (2 choruses) - trumpet in B-flat"
  composer = "Claude (Fable 5.2), for David Reinstein"
  poet = ""
  tagline = ""
}
chExc = {
  <c e g b fis'>1-\markup { "maj7(" \hspace #-0.5 \raise #0.9 \fontsize #-3 \sharp \hspace #-0.3 "11)" }
  <c e g bes fis'>1-\markup { "7(" \hspace #-0.5 \raise #0.9 \fontsize #-3 \sharp \hspace #-0.3 "11)" }
  <c e g bes des'>1-\markup { "7(" \hspace #-0.5 \raise #0.5 \fontsize #-3 \flat \hspace #-0.3 "9)" }
  <c f g bes>1-\markup { "7sus" }
  <c e ges bes dis'>1-\markup { "7alt" }
  <c e g bes>1-\markup { "7" }
  <c e g b>1-\markup { "maj7" }
  <c es g bes>1-\markup { "m7" }
}
chExceptions = #(append (sequential-music-to-chord-exceptions chExc #t) ignatzekExceptions)


global = {
  \time 4/4 \tempo "Medium-up swing" 4 = 160
  \mark \markup { \box \bold "Chorus 1 - A1" } s1
  s1
  s1
  s1 \break
  s1
  s1
  s1
  s1 \break
  \bar "||" \mark \markup { \box \bold "A2" } s1
  s1
  s1
  s1 \break
  s1
  s1
  s1
  s1 \break
  \bar "||" \mark \markup { \box \bold "B" } s1
  s1
  s1
  s1 \break
  s1
  s1
  s1
  s1 \break
  \bar "||" \mark \markup { \box \bold "A3" } s1
  s1
  s1
  s1 \break
  s1
  s1
  s1
  s1 \pageBreak
  \bar "||" \mark \markup { \box \bold "Chorus 2 - A1" } s1
  s1
  s1
  s1 \break
  s1
  s1
  s1
  s1 \break
  \bar "||" \mark \markup { \box \bold "A2" } s1
  s1
  s1
  s1 \break
  s1
  s1
  s1
  s1 \break
  \bar "||" \mark \markup { \box \bold "B" } s1
  s1
  s1
  s1 \break
  s1
  s1
  s1
  s1 \break
  \bar "||" \mark \markup { \box \bold "A3" } s1
  s1
  s1
  s1 \break
  s1
  s1
  s1
  s1 \bar "|."
}

partA = {
  \clef treble \key d \major
  r4 r8 d''8 ^\markup { \italic \fontsize #-3 "hook, displaced" } b'8 g'8 a'8 cis''8 | % 1
  e''4. fis''8 e''8 cis''8 a'8 b'8~ | % 2
  b'2 ais'2~ | % 3
  ais'4 r8 dis''8 ^\markup { \italic \fontsize #-3 "head: tail" } gis''8 fis''8 dis''8 e''8~ | % 4
  e''1 | % 5
  d''2. r4 | % 6
  a'8 ^\markup { \italic \fontsize #-3 "'the lick'" } b'8 c''8 d''8 b'4 g'8 a'8 | % 7
  bes'4 ^\markup { \italic \fontsize #-3 "head: cadence" } c''8 d''8~ d''4 r4 | % 8
  r1 | % 9
  r2 cis''2~ ^\markup { \italic \fontsize #-3 "guide tones" } | % 10
  cis''4 dis''4 e''2 | % 11
  fis''2 r2 | % 12
  d''8 ^\markup { \italic \fontsize #-3 "hook, shadowed" } bes'8 f'8 g'8 c''8 e''8~ e''4 | % 13
  r1 | % 14
  r8 dis'8 ^\markup { \italic \fontsize #-3 "wedge: contrary motion" } fis'8 gis'8 b'8 cis''8 dis''8 fis''8 | % 15
  gis''4 f''8 cis''8 b'2 | % 16
  ais'2 ^\markup { \italic \fontsize #-3 "head: bridge theme" } \tuplet 3/2 { gis'4 c''4 dis''4~ } | % 17
  dis''2 cis''4 r8 dis''8~ | % 18
  dis''4 b'8 ^\markup { \italic \fontsize #-3 "pentatonic in 4ths" } fis'8 gis'8 cis''8 b'8 dis''8 | % 19
  cis''8 fis''8 dis''8 gis''8 fis''4 r4 | % 20
  r2 \tuplet 3/2 { d''4 ^\markup { \italic \fontsize #-3 "stretto" } fis''4 a''4~ } | % 21
  a''2 g''4 f''4 | % 22
  e''8 ^\markup { \italic \fontsize #-3 "stacked 4ths" } b'8 d''8 a'8 c''8 g'8 a'8 b'8 | % 23
  r8 fis'8 ^\markup { \italic \fontsize #-3 "head: altered run" } aes'8 bes'8 c''8 ees''8~ ees''4 | % 24
  d''8 ^\markup { \italic \fontsize #-3 "hook" } b'8 g'8 a'8 cis''8 e''8~ e''4~ | % 25
  e''4 r4 \tuplet 3/2 { cis''8 e''8 fis''8 } a''4 | % 26
  gis''8 fis''8 e''8 dis''8 ais'8 ^\markup { \italic \fontsize #-3 "bebop: 3-5-7-b9" } cis''8 e''8 g''8 | % 27
  fis''4. dis''8 b'8 r8 r4 | % 28
  r1 | % 29
  r2 r4 r8 b'8~ | % 30
  b'1 | % 31
  c''1 | % 32
  cis''8 r8 r4 r2 | % 33
  r2 r8 e''8 cis''8 a'8 | % 34
  gis'8 ^\markup { \italic \fontsize #-3 "pentatonic shift over ii-V-I" } b'8 cis''8 e''8 g''8 e''8 d''8 c''8 | % 35
  ais'8 cis''8 dis''8 fis''8 gis''4 fis''8 r8 | % 36
  e''4. ^\markup { \italic \fontsize #-3 "head, in 10ths" } c''8~ c''4 g'4 | % 37
  f'4. a'8~ a'4 c''8 r8 | % 38
  e''8 ^\markup { \italic \fontsize #-3 "bebop scale + arpeggio" } d''8 c''8 b'8 a'8 c''8 e''8 g''8 | % 39
  fis''8 ees''8 c''8 bes'8 d''2 | % 40
  r8 e''8 ^\markup { \italic \fontsize #-3 "pentatonic" } cis''8 b'8 a'8 fis'8 a'8 b'8 | % 41
  cis''8 f''8 ^\markup { \italic \fontsize #-3 "side-slip, half step up" } d''8 c''8 bes'8 b'8 ^\markup { \italic \fontsize #-3 "back inside" } cis''8 e''8 | % 42
  fis''4 r4 r2 | % 43
  r2 ais'4. r8 | % 44
  g''8 ^\markup { \italic \fontsize #-3 "triad pair in 3s" } e''8 c''8 f''8 d''8 bes'8 e''8 c''8~ | % 45
  c''4 r4 r2 | % 46
  b'8 dis''8 fis''8 gis''8 r2 | % 47
  r8 b'8 cis''8 fis''8 ^\markup { \italic \fontsize #-3 "enclosure" } dis''8 f''8 gis''8 r8 | % 48
  \tuplet 3/2 { ais'4 ^\markup { \italic \fontsize #-3 "3 against 2" } cis''4 f''4 } \tuplet 3/2 { gis''4 f''4 cis''4 } | % 49
  dis''2.~ dis''8 r8 | % 50
  \tuplet 3/2 { cis''4 e''4 gis''4 } \tuplet 3/2 { b''4 gis''4 e''4 } | % 51
  fis''2.~ fis''8 r8 | % 52
  \tuplet 3/2 { e''4 g''4 b''4~ } b''4 a''4~ | % 53
  a''2. r4 | % 54
  a''4 ^\markup { \italic \fontsize #-3 "octaves: sus pentatonic" } g''8 e''8~ e''8 d''8 c''8 a'8 | % 55
  bes'8 ^\markup { \italic \fontsize #-3 "altered pentatonic" } aes'8 f'8 ees'8~ ees'4 r4 | % 56
  d''8 ^\markup { \italic \fontsize #-3 "hook as hocket" } b'8 g'8 r8 r2 | % 57
  r2 r8 b'8 cis''8 d''8 | % 58
  dis''4. cis''8 ais'4 cis''4 | % 59
  dis''2. r4 | % 60
  r2 r8 bes'8 d''8 f''8 | % 61
  g''8 e''8 c''8 a'8 b'8 ^\markup { \italic \fontsize #-3 "bebop chromatic run-up" } c''8 cis''8 d''8~ | % 62
  d''4 r4 r2 | % 63
  d''2. r4 | % 64
}

chordsA = \chordmode {
  g1:maj7.11+ |
  g1:maj7.11+ |
  cis2:m7 fis2:7 |
  b1:maj7 |
  bes1:maj7.11+ |
  ees1:maj7.11+ |
  a1:m7 |
  aes1:7.11+ |
  g1:maj7.11+ |
  g1:maj7.11+ |
  cis2:m7 fis2:7 |
  b1:maj7 |
  bes1:maj7.11+ |
  ees1:maj7.11+ |
  gis1:m7 |
  cis1:7 |
  fis1:maj7.11+ |
  fis1:maj7.11+ |
  a1:maj7.11+ |
  a1:maj7.11+ |
  c1:maj7.11+ |
  ees1:maj7.11+ |
  d1:sus4.7 |
  d1:7.5-.9+ |
  g1:maj7.11+ |
  g1:maj7.11+ |
  cis2:m7 fis2:7 |
  b1:maj7 |
  bes2:maj7.11+ ees2:maj7.11+ |
  a2:m7 d2:7 |
  g1:maj7.11+ |
  aes1:maj7.11+ |
  g1:maj7.11+ |
  g1:maj7.11+ |
  cis2:m7 fis2:7 |
  b1:maj7 |
  bes1:maj7.11+ |
  ees1:maj7.11+ |
  a1:m7 |
  aes1:7.11+ |
  g1:maj7.11+ |
  g1:maj7.11+ |
  cis2:m7 fis2:7 |
  b1:maj7 |
  bes1:maj7.11+ |
  ees1:maj7.11+ |
  gis1:m7 |
  cis1:7 |
  fis1:maj7.11+ |
  fis1:maj7.11+ |
  a1:maj7.11+ |
  a1:maj7.11+ |
  c1:maj7.11+ |
  ees1:maj7.11+ |
  d1:sus4.7 |
  d1:7.5-.9+ |
  g1:maj7.11+ |
  g1:maj7.11+ |
  cis2:m7 fis2:7 |
  b1:maj7 |
  bes2:maj7.11+ ees2:maj7.11+ |
  a2:m7 d2:7 |
  g1:maj7.11+ |
  aes1:maj7.11+ |
}

\score {
  <<
    \new ChordNames \with { chordNameExceptions = #chExceptions chordChanges = ##t \override ChordName.font-size = #1.5 \override ChordName.extra-spacing-width = #'(-0.3 . 1.6) } \chordsA
    \new Staff << \global \partA >>
  >>
  \layout {
    \context { \Score \override BarNumber.break-visibility = ##(#f #f #t)
      \override RehearsalMark.self-alignment-X = #LEFT
      \override MetronomeMark.padding = #2.5 }
    \context { \Staff \override TextScript.staff-padding = #2.2 }
  }
}
