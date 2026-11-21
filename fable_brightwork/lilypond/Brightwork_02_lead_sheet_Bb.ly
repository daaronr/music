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
  subtitle = "Lead sheet - B-flat instruments"
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
  \clef treble \key d \major
  d''8 b'8 g'8 a'8 cis''8 e''8~ e''4~ | % 1
  e''2 r8 b'8 cis''8 d''8 | % 2
  e''8 cis''8 gis'8 ais'8 cis''8 fis''8~ fis''4~ | % 3
  fis''2 gis''8 fis''8 dis''8 r8 | % 4
  e''4. c''8~ c''4 g'4 | % 5
  f'4. a'8~ a'4 c''4~ | % 6
  c''4 e''8 g''8 fis''8 d''8 b'8 a'8 | % 7
  bes'4 c''8 d''8~ d''4 r4 | % 8
  d''8 b'8 g'8 a'8 cis''8 e''8~ e''4~ | % 9
  e''2 r8 b'8 cis''8 d''8 | % 10
  e''8 cis''8 gis'8 ais'8 cis''8 fis''8~ fis''4~ | % 11
  fis''2 gis''8 fis''8 dis''8 r8 | % 12
  e''4. c''8~ c''4 g'4 | % 13
  f'4. a'8~ a'4 c''4 | % 14
  r4 b'8 dis''8 fis''8 f''8 cis''8 ais'8 | % 15
  b'2. r4 | % 16
  ais'2 \tuplet 3/2 { gis'4 c''4 dis''4~ } | % 17
  dis''2 cis''4 r8 dis''8~ | % 18
  dis''2 \tuplet 3/2 { b'4 dis''4 fis''4~ } | % 19
  fis''2 e''4 r8 fis''8~ | % 20
  fis''2 \tuplet 3/2 { d''4 fis''4 a''4~ } | % 21
  a''2 g''4 f''4 | % 22
  e''4. d''8 c''8 a'8 g'4 | % 23
  r8 fis'8 aes'8 bes'8 c''8 ees''8~ ees''4 | % 24
  d''8 b'8 g'8 a'8 cis''8 e''8~ e''4~ | % 25
  e''2 r8 b'8 cis''8 d''8 | % 26
  e''8 cis''8 gis'8 ais'8 cis''8 fis''8~ fis''4~ | % 27
  fis''2 gis''8 fis''8 dis''8 r8 | % 28
  e''8 c''8 g'8 f'8 a'8 c''8~ c''4~ | % 29
  c''4 b'8 d''8 fis''8 ees''8 c''8 d''8~ | % 30
  d''1~ ^\markup { \italic \fontsize #-3 "last time: hold this bar" } | % 31
  d''2. r4 | % 32
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
