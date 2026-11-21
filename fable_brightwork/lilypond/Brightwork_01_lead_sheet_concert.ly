\version "2.24.0"
#(set-default-paper-size "a4")
#(set-global-staff-size 20)
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
  system-system-spacing.basic-distance = #15
  system-system-spacing.minimum-distance = #11
}
\header {
  title = "Brightwork"
  subtitle = "Lead sheet - concert pitch"
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
  \mark \markup { \box \bold "A1" } s1
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
  \clef treble \key c \major
  c''8 a'8 f'8 g'8 b'8 d''8~ d''4~ | % 1
  d''2 r8 a'8 b'8 c''8 | % 2
  d''8 b'8 fis'8 gis'8 b'8 e''8~ e''4~ | % 3
  e''2 fis''8 e''8 cis''8 r8 | % 4
  d''4. bes'8~ bes'4 f'4 | % 5
  ees'4. g'8~ g'4 bes'4~ | % 6
  bes'4 d''8 f''8 e''8 c''8 a'8 g'8 | % 7
  aes'4 bes'8 c''8~ c''4 r4 | % 8
  c''8 a'8 f'8 g'8 b'8 d''8~ d''4~ | % 9
  d''2 r8 a'8 b'8 c''8 | % 10
  d''8 b'8 fis'8 gis'8 b'8 e''8~ e''4~ | % 11
  e''2 fis''8 e''8 cis''8 r8 | % 12
  d''4. bes'8~ bes'4 f'4 | % 13
  ees'4. g'8~ g'4 bes'4 | % 14
  r4 a'8 cis''8 e''8 dis''8 b'8 gis'8 | % 15
  a'2. r4 | % 16
  gis'2 \tuplet 3/2 { fis'4 ais'4 cis''4~ } | % 17
  cis''2 b'4 r8 cis''8~ | % 18
  cis''2 \tuplet 3/2 { a'4 cis''4 e''4~ } | % 19
  e''2 d''4 r8 e''8~ | % 20
  e''2 \tuplet 3/2 { c''4 e''4 g''4~ } | % 21
  g''2 f''4 ees''4 | % 22
  d''4. c''8 bes'8 g'8 f'4 | % 23
  r8 e'8 ges'8 aes'8 bes'8 des''8~ des''4 | % 24
  c''8 a'8 f'8 g'8 b'8 d''8~ d''4~ | % 25
  d''2 r8 a'8 b'8 c''8 | % 26
  d''8 b'8 fis'8 gis'8 b'8 e''8~ e''4~ | % 27
  e''2 fis''8 e''8 cis''8 r8 | % 28
  d''8 bes'8 f'8 ees'8 g'8 bes'8~ bes'4~ | % 29
  bes'4 a'8 c''8 e''8 des''8 bes'8 c''8~ | % 30
  c''1~ ^\markup { \italic \fontsize #-3 "last time: hold this bar" } | % 31
  c''2. r4 | % 32
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
