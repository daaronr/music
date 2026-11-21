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
  subtitle = "Duo solo (2 choruses) - trumpet, concert pitch"
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
  \clef treble \key c \major
  r4 r8 c''8 ^\markup { \italic \fontsize #-3 "hook, displaced" } a'8 f'8 g'8 b'8 | % 1
  d''4. e''8 d''8 b'8 g'8 a'8~ | % 2
  a'2 gis'2~ | % 3
  gis'4 r8 cis''8 ^\markup { \italic \fontsize #-3 "head: tail" } fis''8 e''8 cis''8 d''8~ | % 4
  d''1 | % 5
  c''2. r4 | % 6
  g'8 ^\markup { \italic \fontsize #-3 "'the lick'" } a'8 bes'8 c''8 a'4 f'8 g'8 | % 7
  aes'4 ^\markup { \italic \fontsize #-3 "head: cadence" } bes'8 c''8~ c''4 r4 | % 8
  r1 | % 9
  r2 b'2~ ^\markup { \italic \fontsize #-3 "guide tones" } | % 10
  b'4 cis''4 d''2 | % 11
  e''2 r2 | % 12
  c''8 ^\markup { \italic \fontsize #-3 "hook, shadowed" } aes'8 ees'8 f'8 bes'8 d''8~ d''4 | % 13
  r1 | % 14
  r8 cis'8 ^\markup { \italic \fontsize #-3 "wedge: contrary motion" } e'8 fis'8 a'8 b'8 cis''8 e''8 | % 15
  fis''4 dis''8 b'8 a'2 | % 16
  gis'2 ^\markup { \italic \fontsize #-3 "head: bridge theme" } \tuplet 3/2 { fis'4 ais'4 cis''4~ } | % 17
  cis''2 b'4 r8 cis''8~ | % 18
  cis''4 a'8 ^\markup { \italic \fontsize #-3 "pentatonic in 4ths" } e'8 fis'8 b'8 a'8 cis''8 | % 19
  b'8 e''8 cis''8 fis''8 e''4 r4 | % 20
  r2 \tuplet 3/2 { c''4 ^\markup { \italic \fontsize #-3 "stretto" } e''4 g''4~ } | % 21
  g''2 f''4 ees''4 | % 22
  d''8 ^\markup { \italic \fontsize #-3 "stacked 4ths" } a'8 c''8 g'8 bes'8 f'8 g'8 a'8 | % 23
  r8 e'8 ^\markup { \italic \fontsize #-3 "head: altered run" } ges'8 aes'8 bes'8 des''8~ des''4 | % 24
  c''8 ^\markup { \italic \fontsize #-3 "hook" } a'8 f'8 g'8 b'8 d''8~ d''4~ | % 25
  d''4 r4 \tuplet 3/2 { b'8 d''8 e''8 } g''4 | % 26
  fis''8 e''8 d''8 cis''8 gis'8 ^\markup { \italic \fontsize #-3 "bebop: 3-5-7-b9" } b'8 d''8 f''8 | % 27
  e''4. cis''8 a'8 r8 r4 | % 28
  r1 | % 29
  r2 r4 r8 a'8~ | % 30
  a'1 | % 31
  bes'1 | % 32
  b'8 r8 r4 r2 | % 33
  r2 r8 d''8 b'8 g'8 | % 34
  fis'8 ^\markup { \italic \fontsize #-3 "pentatonic shift over ii-V-I" } a'8 b'8 d''8 f''8 d''8 c''8 bes'8 | % 35
  gis'8 b'8 cis''8 e''8 fis''4 e''8 r8 | % 36
  d''4. ^\markup { \italic \fontsize #-3 "head, in 10ths" } bes'8~ bes'4 f'4 | % 37
  ees'4. g'8~ g'4 bes'8 r8 | % 38
  d''8 ^\markup { \italic \fontsize #-3 "bebop scale + arpeggio" } c''8 bes'8 a'8 g'8 bes'8 d''8 f''8 | % 39
  e''8 des''8 bes'8 aes'8 c''2 | % 40
  r8 d''8 ^\markup { \italic \fontsize #-3 "pentatonic" } b'8 a'8 g'8 e'8 g'8 a'8 | % 41
  b'8 ees''8 ^\markup { \italic \fontsize #-3 "side-slip, half step up" } c''8 bes'8 aes'8 a'8 ^\markup { \italic \fontsize #-3 "back inside" } b'8 d''8 | % 42
  e''4 r4 r2 | % 43
  r2 gis'4. r8 | % 44
  f''8 ^\markup { \italic \fontsize #-3 "triad pair in 3s" } d''8 bes'8 ees''8 c''8 aes'8 d''8 bes'8~ | % 45
  bes'4 r4 r2 | % 46
  a'8 cis''8 e''8 fis''8 r2 | % 47
  r8 a'8 b'8 e''8 ^\markup { \italic \fontsize #-3 "enclosure" } cis''8 dis''8 fis''8 r8 | % 48
  \tuplet 3/2 { gis'4 ^\markup { \italic \fontsize #-3 "3 against 2" } b'4 dis''4 } \tuplet 3/2 { fis''4 dis''4 b'4 } | % 49
  cis''2.~ cis''8 r8 | % 50
  \tuplet 3/2 { b'4 d''4 fis''4 } \tuplet 3/2 { a''4 fis''4 d''4 } | % 51
  e''2.~ e''8 r8 | % 52
  \tuplet 3/2 { d''4 f''4 a''4~ } a''4 g''4~ | % 53
  g''2. r4 | % 54
  g''4 ^\markup { \italic \fontsize #-3 "octaves: sus pentatonic" } f''8 d''8~ d''8 c''8 bes'8 g'8 | % 55
  aes'8 ^\markup { \italic \fontsize #-3 "altered pentatonic" } ges'8 ees'8 des'8~ des'4 r4 | % 56
  c''8 ^\markup { \italic \fontsize #-3 "hook as hocket" } a'8 f'8 r8 r2 | % 57
  r2 r8 a'8 b'8 c''8 | % 58
  cis''4. b'8 gis'4 b'4 | % 59
  cis''2. r4 | % 60
  r2 r8 aes'8 c''8 ees''8 | % 61
  f''8 d''8 bes'8 g'8 a'8 ^\markup { \italic \fontsize #-3 "bebop chromatic run-up" } bes'8 b'8 c''8~ | % 62
  c''4 r4 r2 | % 63
  c''2. r4 | % 64
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
