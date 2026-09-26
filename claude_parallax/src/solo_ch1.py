"""Duo solo, chorus 1 (bars 1-32). Concert pitch; guitar lines at sounding pitch.

Motifs from the head:
  X  = C-A-F-G + a leap (the F-triad "object"), heard at displacements of 0/1/2 eighths
  Y  = quarter-note triplet Bb-Gb-Eb (Bb-G-Eb over Db13#11) + F + Cb
  Z  = bridge cell: b3 (q.) - b7 | b7 (q.) - #11 | #11 held
  W  = a held note whose meaning changes as the bass moves (D over Bb, G#m7b5, C#7alt)
"""

TPT = [
    # ---- A1: trumpet opens, guitar answers in inversion, then quotes the head
    "@mf @ann=X_in_8ths,_+1/8 r/8 C5/8 A4/8 F4/8 G4/8 D5/8~ D5/q~",               # 1
    "D5/q r/q r/h",                                                              # 2
    "r/h r/8 Eb5/8 F5/8 A5/8~",                                                  # 3
    "A5/q G5/8 F5/8 Eb5/8 Bb4/8 A4/8 G4/8",                                      # 4
    "@ann=F_maj_pent_over_B7alt F4/8 A4/8 C5/8 D5/8 F5/8 G5/8 F5/8 Eb5/8~",       # 5
    "Eb5/8 D5/q. r/h",                                                           # 6
    "r/w",                                                                       # 7
    "r/w",                                                                       # 8
    # ---- A2: displaced pentatonic cells over X in augmentation
    "@ann=pent._shift_Bb/F,_4+1_cells F4/8!acc G4/8 Bb4/8 C5/8 r/8 G4/8!acc A4/8 C5/8",  # 9
    "D5/8 r/8 Bb4/8!acc C5/8 D5/8 F5/8 r/8 C5/8!acc",                            # 10
    "@ann=whole-tone_cell Eb5/8 F5/8 G5/8 r/8 A5/8!acc G5/8 F5/8 Eb5/8",          # 11
    "r/8 C5/8!acc Bb4/8 G4/8 F4/8 r/8 r/q",                                      # 12
    "@mp @ann=held_3rd Eb5/w",                                                   # 13
    "@ann=pedal_D_(head) D5/w~",                                                 # 14
    "D5/h. r/q",                                                                 # 15
    "r/8 E5/8 G5/8 A5/8~ A5/q r/q",                                              # 16
    # ---- B: guitar leads; trumpet places long tones at 0/1/2-eighth offsets
    "r/w",                                                                       # 17
    "@mp @ann=maj7,_on_1 D#5/h. r/q",                                            # 18
    "r/w",                                                                       # 19
    "@ann=#11,_on_&1 r/8 F#5/q.~ F#5/q r/q",                                     # 20
    "r/w",                                                                       # 21
    "@ann=#11,_on_2 r/q D5/h r/q",                                               # 22
    "@cresc @ann=Fm9_climb r/8 F4/8 Ab4/8 C5/8 Eb5/8 G5/8 F5/8 G5/8",            # 23
    "@f @endw G#5/q.!acc E5/8 D5/8 B4/8 C#5/8 D5/8",                            # 24
    # ---- A3: trading, then a hocket
    "@mf @ann=X_+3/8 r/q. C5/8 A4/8 F4/8 G4/8 D5/8~",                            # 25
    "D5/q. Bb4/8 C5/8 D5/8 F5/8 A5/8~",                                          # 26
    "@ann=A:_#11_becomes_#5 A5/h r/h",                                           # 27
    "r/w",                                                                       # 28
    "@ann=hocket G5/8 r/8 D5/8 r/8 A4/8 r/8 F4/8 r/8",                           # 29
    "D5/h r/h",                                                                  # 30
    "r/w",                                                                       # 31
    "r/w",                                                                       # 32
]

GTR = [
    # ---- A1
    "r/w",                                                                       # 1
    "@mf @ann=X_inverted r/q G3/8 Bb3/8 D4/8 C4/8 F3/8 G3/8",                    # 2
    "@ann=head_quote_8vb,_on_the_beat C4/q. A3/8 F3/q G3/q~",                    # 3
    "G3/8 C4/h r/q.",                                                            # 4
    "r/w",                                                                       # 5
    "r/h r/8 @ann=enclosure D4/8 C4/8 A3/8",                                     # 6
    "@ann=motif_Y 3{Bb3/q Gb3/q Eb3/q} F3/8 Ab3/8 Cb4/8 Eb4/8",                  # 7
    "3{F4/q Eb4/q Bb3/q} G3/8 Bb3/8 Cb4/8 Db4/8",                                # 8
    # ---- A2
    "@mp @ann=X_augmented C4/h A3/h",                                            # 9
    "F3/h G3/h",                                                                 # 10
    "C4/h. A3/q",                                                                # 11
    "F3/h G3/h",                                                                 # 12
    "@mf @ann=B7#5b9_line r/8 D#4/8 G4/8 B4/8 A4/8 F4/8 C4/8 A3/8",              # 13
    "@ann=voices_cross Bb3/8 D4/8 F4/8 A4/8 C5/8 E5/8 D5/8 C5/8",                # 14
    "@ann=triplet_turn B4/8 G#4/8 F#4/8 D4/8 3{E4/8 D4/8 C#4/8} B3/8 G#3/8",     # 15
    "@ann=enclosure_into_bridge A3/8 B3/8 D4/8 F4/8 G4/8 B4/8 E4/8 G4/8",        # 16
    # ---- B
    "@ann=1-2-3-5_(Coltrane) F#4/8 G#4/8 A4/8 C#5/8 C5/8 A4/8 G4/8 F4/8",        # 17
    "@ann=triad_pair_E/F# E4/8 G#4/8 F#4/8 A#4/8 G#4/8 B4/8 C#5/q",              # 18
    "C5/8 A4/8 F4/8 E4/8 Ab4/8 F4/8 Eb4/8 Db4/8",                                # 19
    "@ann=C/D_pair,_quarter_triplets 3{E4/q F#4/q A4/q} 3{G4/q D4/q E4/q}",       # 20
    "F4/8 Db4/8 C4/8 Bb3/8 C#4/8 E4/8 G4/8 B4/8",                                # 21
    "@ann=Ab/Bb_pair C5/8 D5/8 Bb4/8 C5/8 Ab4/8 Bb4/8 F4/q",                     # 22
    "r/w",                                                                       # 23
    "@ann=E7#11_rises_to_#11 r/q E3/8 G#3/8 B3/8 D4/8 F#4/8 A#4/8",              # 24
    # ---- A3
    "@ann=A#_->_A A4/q. r/8 r/h",                                                # 25
    "r/w",                                                                       # 26
    "@ann=X_+4/8 r/h C4/8 A3/8 F3/8 G3/8",                                       # 27
    "C4/q. Eb4/8 F4/8 A4/8 C5/8 Eb5/8",                                          # 28
    "r/8 F4/8 r/8 C4/8 r/8 G3/8 r/8 D#3/8",                                      # 29
    "D3/q r/8 F3/8 A3/8 C4/8 D4/8 F4/8",                                         # 30
    "@ann=Y_varied 3{Gb4/q Eb4/q Bb3/q} Cb4/8 Db4/8 Eb4/8 F4/8",                 # 31
    "3{G4/q Eb4/q Bb3/q} Ab3/8 Bb3/8 Db4/8 Eb4/8",                               # 32
]
