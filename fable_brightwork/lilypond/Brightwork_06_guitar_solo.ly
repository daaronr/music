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
  subtitle = "Duo solo (2 choruses) - guitar (sounds an octave lower, as usual)"
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
  \clef "treble_8" \key c \major
  r1 | % 1
  r4 r8 c'8 ^\markup { \italic \fontsize #-3 "canon at the octave" } a8 f8 g8 b8 | % 2
  d'4. e'8 d'8 b8 gis8 a8~ | % 3
  a2 r2 | % 4
  r8 ees8 ^\markup { \italic \fontsize #-3 "triad pair Ab/Bb" } aes8 c'8 d'8 f'8 bes'4~ | % 5
  bes'8 ^\markup { \italic \fontsize #-3 "Eb/Db" } g'8 ees'8 f'8 des'8 aes8 c'4 | % 6
  r1 | % 7
  r8 des8 ^\markup { \italic \fontsize #-3 "Gb/Ab" } ges8 bes8 c'8 ees'8 aes'4 | % 8
  g'8 ^\markup { \italic \fontsize #-3 "G/F, descending" } d'8 b8 a8 f8 c8 e4 | % 9
  r8 a8 c'8 e'8 d'8 b8 g8 a8 | % 10
  cis'8 ^\markup { \italic \fontsize #-3 "ii-V line" } d'8 fis'8 a'8 gis'8 fis'8 e'8 d'8 | % 11
  cis'8 e'8 gis'8 b'8 a'4 r4 | % 12
  r1 | % 13
  f'8 ^\markup { \italic \fontsize #-3 "answer, up a 4th" } des'8 aes8 bes8 ees'8 g'8~ g'4 | % 14
  e'8 cis'8 b8 a8 fis8 e8 cis8 b,8 | % 15
  dis8 ^\markup { \italic \fontsize #-3 "3-5-7-b9" } fis8 a8 c'8 b4 r4 | % 16
  r8 b,8 ^\markup { \italic \fontsize #-3 "pentatonic shift: E" } cis8 e8 fis8 gis8 b8 cis'8 | % 17
  dis'8 ^\markup { \italic \fontsize #-3 "B" } cis'8 b8 gis8 fis8 ^\markup { \italic \fontsize #-3 "F#" } gis8 ais8 dis'8 | % 18
  d'2 ^\markup { \italic \fontsize #-3 "bridge theme" } \tuplet 3/2 { a4 cis'4 e'4~ } | % 19
  e'2 d'4 r4 | % 20
  \tuplet 3/2 { bes4 d'4 f'4~ } f'2 | % 21
  \tuplet 3/2 { ees'4 g'4 bes'4~ } bes'2 | % 22
  g4. bes8~ bes4 c'4 | % 23
  des'8 bes8 aes8 ges8 e8 des8 c4 | % 24
  r1 | % 25
  r4 r8 e'8 c'8 a8 g4 | % 26
  a4. gis8~ gis4 b4 | % 27
  cis'4 r8 e'8 fis'8 gis'8 b'8 cis''8 | % 28
  d''8 ^\markup { \italic \fontsize #-3 "head: compressed hook" } bes'8 f'8 ees'8 g'8 bes'8~ bes'4~ | % 29
  bes'4 a'8 g'8 e'8 ^\markup { \italic \fontsize #-3 "3-5-7-b9" } g'8 bes'8 des''8 | % 30
  c''8 ^\markup { \italic \fontsize #-3 "G pentatonic" } b'8 a'8 g'8 e'8 d'8 e'8 g'8 | % 31
  aes'8 ^\markup { \italic \fontsize #-3 "shift: Ab pentatonic" } bes'8 c''8 ees''8 f''8 ees''8 c''8 bes'8 | % 32
  r8 c''8 ^\markup { \italic \fontsize #-3 "hook displaced, then in sequence" } a'8 f'8 g'8 b'8 d''8 d''8 | % 33
  b'8 g'8 a'8 c''8 e''4 r4 | % 34
  r1 | % 35
  r2 e'8 cis'8 b8 a8 | % 36
  bes4. g8~ g4 d4 | % 37
  c4. ees8~ ees4 g8 r8 | % 38
  r1 | % 39
  r8 des8 ^\markup { \italic \fontsize #-3 "Gb/Ab" } ges8 bes8 c'8 ees'8 aes'4 | % 40
  r1 | % 41
  r2 e'8 d'8 b8 c'8 | % 42
  d'8 ^\markup { \italic \fontsize #-3 "ii-V line" } fis'8 a'8 cis''8 b'8 gis'8 e'8 d'8 | % 43
  cis'8 e8 ^\markup { \italic \fontsize #-3 "triad pair A/B" } a8 cis'8 dis'8 fis'8 b'4 | % 44
  r1 | % 45
  bes'8 ^\markup { \italic \fontsize #-3 "answer: Eb/Db" } g'8 ees'8 aes'8 f'8 des'8 g'8 ees'8 | % 46
  r2 e'8 fis'8 a'8 b'8 | % 47
  a'8 fis'8 dis'8 c'8 b4 r4 | % 48
  r2 r8 b8 ^\markup { \italic \fontsize #-3 "triad pair E/F#" } e'8 gis'8 | % 49
  ais'8 ^\markup { \italic \fontsize #-3 "in 3s" } fis'8 cis'8 b8 gis8 e8 fis8 ais8 | % 50
  b4 r4 r8 d'8 ^\markup { \italic \fontsize #-3 "G/A" } g'8 b'8 | % 51
  cis''8 a'8 e'8 d'8 b8 g8 a8 cis'8 | % 52
  d'4 r4 r8 f'8 ^\markup { \italic \fontsize #-3 "Bb, then Eb/Db" } bes'8 d''8 | % 53
  ees''8 bes'8 g'8 f'8 des'8 aes8 bes8 ees'8 | % 54
  g'4 ^\markup { \italic \fontsize #-3 "octaves" } f'8 d'8~ d'8 c'8 bes8 g8 | % 55
  aes8 ges8 ees8 des8~ des4 r4 | % 56
  r4 r8 g'8 b'8 d''8~ d''4~ | % 57
  d''2 r2 | % 58
  fis8 a8 b8 d'8 e'8 d'8 b8 gis8 | % 59
  a8 cis'8 ^\markup { \italic \fontsize #-3 "A/B" } e'8 dis'8 fis'8 b'8 a'4 | % 60
  ees8 ^\markup { \italic \fontsize #-3 "Ab, then Db" } aes8 c'8 ees'8 des'8 f'8 aes'4 | % 61
  g8 bes8 d'8 f'8 e'4 g4 | % 62
  a4 c'8 ^\markup { \italic \fontsize #-3 "F/G" } f'8 g'8 b'8 d''4 | % 63
  des'8 ^\markup { \italic \fontsize #-3 "Gb/Ab" } ges'8 bes'8 aes'8 c''8 ees''8~ ees''4 | % 64
}

chordsA = \chordmode {
  f1:maj7.11+ |
  f1:maj7.11+ |
  b2:m7 e2:7 |
  a1:maj7 |
  aes1:maj7.11+ |
  des1:maj7.11+ |
  g1:m7 |
  ges1:7.11+ |
  f1:maj7.11+ |
  f1:maj7.11+ |
  b2:m7 e2:7 |
  a1:maj7 |
  aes1:maj7.11+ |
  des1:maj7.11+ |
  fis1:m7 |
  b1:7 |
  e1:maj7.11+ |
  e1:maj7.11+ |
  g1:maj7.11+ |
  g1:maj7.11+ |
  bes1:maj7.11+ |
  des1:maj7.11+ |
  c1:sus4.7 |
  c1:7.5-.9+ |
  f1:maj7.11+ |
  f1:maj7.11+ |
  b2:m7 e2:7 |
  a1:maj7 |
  aes2:maj7.11+ des2:maj7.11+ |
  g2:m7 c2:7 |
  f1:maj7.11+ |
  ges1:maj7.11+ |
  f1:maj7.11+ |
  f1:maj7.11+ |
  b2:m7 e2:7 |
  a1:maj7 |
  aes1:maj7.11+ |
  des1:maj7.11+ |
  g1:m7 |
  ges1:7.11+ |
  f1:maj7.11+ |
  f1:maj7.11+ |
  b2:m7 e2:7 |
  a1:maj7 |
  aes1:maj7.11+ |
  des1:maj7.11+ |
  fis1:m7 |
  b1:7 |
  e1:maj7.11+ |
  e1:maj7.11+ |
  g1:maj7.11+ |
  g1:maj7.11+ |
  bes1:maj7.11+ |
  des1:maj7.11+ |
  c1:sus4.7 |
  c1:7.5-.9+ |
  f1:maj7.11+ |
  f1:maj7.11+ |
  b2:m7 e2:7 |
  a1:maj7 |
  aes2:maj7.11+ des2:maj7.11+ |
  g2:m7 c2:7 |
  f1:maj7.11+ |
  ges1:maj7.11+ |
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
