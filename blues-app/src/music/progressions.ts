// The 18 blues progressions, exactly as printed on the chart photographed in
// ../../../blues_variations_in_F.JPG (key of F). Everything else - roman
// numerals, other keys, transposed parts - is derived from these strings, so
// this table is the single thing to check against the photo.
//
// Notation follows the chart: "-" minor seventh, "Δ" major seventh,
// "°" diminished seventh, "7" dominant seventh, "C-/F" a minor seventh chord
// over the bass note a fifth below (an F9sus4 sound). Two chords in a bar get
// two beats each.
//
// In the prose, {{Eb7}} or {{C- F7}} is a chord written in the chart's key;
// the app shows it in whatever key and notation the reader has chosen.

export interface Variation {
  id: number;
  name: string;
  bars: string[];
  /** What this form adds, in a sentence or three. */
  summary: string;
  /** Notes on particular bars, keyed by bar number (1-12). */
  notes: Record<number, string>;
  /** Chord to end on when this form is played as a final chorus. */
  ending: string;
}

export const INTRO =
  'Every form keeps the same frame. Bars 1–4 are I (or something standing in for it), bars 5–8 go to IV and head back toward I, ' +
  'and bars 9–12 are V (or a ii–V standing in for it) returning to I. Each row mostly builds on the one above, so stepping ' +
  'through them in order is a short course in blues reharmonization. Bars from different rows can also be mixed.';

export const VARIATIONS: Variation[] = [
  {
    id: 1,
    name: 'Basic blues',
    bars: ['F7', 'F7', 'F7', 'F7', 'Bb7', 'Bb7', 'F7', 'F7', 'C7', 'C7', 'F7', 'F7'],
    summary: 'Three dominant chords: I7, IV7 and V7. Everything below decorates this skeleton.',
    notes: {},
    ending: 'F7',
  },
  {
    id: 2,
    name: 'V–IV cadence',
    bars: ['F7', 'F7', 'F7', 'F7', 'Bb7', 'Bb7', 'F7', 'F7', 'C7', 'Bb7', 'F7', 'C7'],
    summary: 'Bar 10 steps down from {{C7}} to {{Bb7}} before home, and bar 12 ends on {{C7}} to send you back to the top.',
    notes: {
      10: '{{Bb7}} after {{C7}}: the V–IV–I cadence heard on countless blues records.',
      12: 'Turnaround: {{C7}} points back to bar 1.',
    },
    ending: 'F7',
  },
  {
    id: 3,
    name: 'Quick four + II7',
    bars: ['F7', 'Bb7', 'F7', 'F7', 'Bb7', 'Bb7', 'F7', 'F7', 'G7', 'C7', 'F7', 'C7'],
    summary: 'Bar 2 visits {{Bb7}} (the "quick change"), and bar 9 becomes {{G7}}, the V of V, which pulls to {{C7}}.',
    notes: {
      2: 'Quick change: IV7 for one bar, then back to I7.',
      9: '{{G7}} is a secondary dominant: V7 of {{C7}}.',
    },
    ending: 'F7',
  },
  {
    id: 4,
    name: 'VI7–II7–V7 chain',
    bars: ['F7', 'Bb7', 'F7', 'F7', 'Bb7', 'Bb7', 'F7', 'D7', 'G7', 'C7', 'F7', 'C7'],
    summary: 'Bar 8 adds {{D7}}, the V of {{G7}}. Bars 8–11 now run round the cycle of fifths, each dominant resolving to the next: VI7, II7, V7, I7.',
    notes: {
      8: '{{D7}} is V7 of {{G7}}.',
    },
    ending: 'F7',
  },
  {
    id: 5,
    name: 'Diatonic ii–V',
    bars: ['F7', 'Bb7', 'F7', 'F7', 'Bb7', 'Bb7', 'F7', 'D7', 'G-', 'C7', 'F7', 'G- C7'],
    summary: 'Bar 9 softens {{G7}} to {{G-}}, the ordinary ii of the key, so bars 9–10 are a ii–V. Bar 12 becomes a quick ii–V back to the top.',
    notes: {
      9: 'ii–7 instead of II7: same root, but diatonic and less insistent.',
      12: '{{G- C7}}: a ii–V turnaround, two beats each.',
    },
    ending: 'F7',
  },
  {
    id: 6,
    name: 'IV of IV + tritone subs',
    bars: ['F7', 'Bb7', 'F7', 'F7', 'Bb7', 'Eb7', 'F7', 'D7', 'Db7', 'C7', 'F7', 'Db7 C7'],
    summary:
      'Bar 6 moves to {{Eb7}}, the IV of {{Bb7}}. In bars 9 and 12, {{Db7}} stands in for {{G7}}: a tritone substitution that slides down a half step into {{C7}}.',
    notes: {
      6: '{{Eb7}} is IV of IV. Heard from the tonic it is also the "backdoor" dominant, ♭VII7 resolving to I7.',
      9: '{{Db7}} and {{G7}} share the same tritone, so either can lead to {{C7}}; with {{Db7}} the bass falls by a half step.',
      12: 'Tritone-sub turnaround: ♭VI7 to V7.',
    },
    ending: 'F7',
  },
  {
    id: 7,
    name: 'ii–V into IV; iii–VI–ii–V',
    bars: ['F7', 'Bb7', 'F7', 'C- F7', 'Bb7', 'Eb7', 'F7', 'A- D7', 'G-', 'C7', 'A- D7', 'G- C7'],
    summary:
      'Dominants get their own ii chords: {{C- F7}} sets up {{Bb7}}, {{A- D7}} sets up {{G-}}, and bars 11–12 become the iii–VI–ii–V turnaround.',
    notes: {
      4: '{{C- F7}}: the tonic turns into V7 of IV, with its own ii in front. A bebop staple.',
      8: '{{A- D7}}: ii–V into {{G-}}.',
      11: '{{A-}} stands in for the tonic (iii shares three notes with IΔ7), then {{D7}} leads to {{G-}}.',
    },
    ending: 'F7',
  },
  {
    id: 8,
    name: 'iii– in bar 7',
    bars: ['F7', 'Bb7', 'F7', 'C- F7', 'Bb7', 'Eb7', 'A-', 'D7', 'G-', 'C7', 'A- D7', 'G- C7'],
    summary: 'Bar 7 gives up the tonic for {{A-}} and bar 8 is all {{D7}}, so bars 7–10 walk iii–VI–ii–V at one chord per bar.',
    notes: {
      7: '{{A-}} replaces {{F7}}: iii as a tonic substitute.',
    },
    ending: 'F7',
  },
  {
    id: 9,
    name: 'Chromatic dominants',
    bars: ['F7', 'Bb7', 'F7', 'C- F7', 'Bb7', 'B- E7', 'F7 E7', 'Eb7 D7', 'G-', 'C7 Bb7', 'A- D7', 'G- C7'],
    summary:
      'Bar 6 is a ii–V a half step below the tonic, then bars 7–8 slide down in half steps, {{F7 E7}} {{Eb7 D7}}, landing on {{D7}}, the V of {{G-}}. Bar 10 brings back the V–IV move.',
    notes: {
      6: '{{B- E7}}: {{E7}} slides up a half step into bar 7. It is also the tritone sub of {{Bb7}}, so the bar still sounds like IV.',
      7: 'Dominant sevenths falling by half steps, two beats each, through bar 8.',
      10: '{{C7 Bb7}}: V–IV, as in form 2.',
    },
    ending: 'F7',
  },
  {
    id: 10,
    name: 'Bird blues',
    bars: ['FΔ', 'E- A7', 'D- G7', 'C- F7', 'Bb7', 'B°', 'A- D7', 'Ab- Db7', 'G- C7', 'Db- Gb7', 'F7 D7', 'G- C7'],
    summary:
      'Parker-style: after {{FΔ}}, ii–Vs fall by whole steps ({{E- A7}}, {{D- G7}}, {{C- F7}}) to {{Bb7}}. Bars 7–8 are ii–Vs falling by a half step, and bar 10 is a tritone-sub ii–V back to the tonic.',
    notes: {
      1: 'A major seventh, not a dominant: the jazz tonic.',
      6: '{{B°}} is built on the raised 4th. A diminished seventh repeats every minor third, so its notes are also a rootless {{E7}} with a ♭9, which is why it moves so well to {{A-}}.',
      8: '{{Ab- Db7}} slips down a half step to {{G-}}.',
      10: '{{Db- Gb7}} is the tritone substitute for {{G- C7}}.',
      11: '{{F7 D7}}: I7–VI7, the start of an I–VI–ii–V turnaround.',
    },
    ending: 'FΔ',
  },
  {
    id: 11,
    name: 'Chromatic minor sevenths',
    bars: ['FΔ', 'E- Eb-', 'D- Db-', 'C- B7', 'BbΔ', 'Bb-', 'A-', 'Ab-', 'G-', 'C7', 'A- Ab-', 'G- Gb'],
    summary:
      'Minor seventh chords descend by half steps from {{E-}} to {{C-}}, and {{B7}} (tritone sub for {{F7}}) lands on {{BbΔ}}. Bars 6–9 repeat the descent one chord per bar, and bars 11–12 do it again at double speed.',
    notes: {
      4: '{{B7}} replaces {{F7}}: a tritone substitute, resolving down a half step to {{BbΔ}}.',
      6: '{{Bb-}} is iv–7, the minor subdominant: a darker IV.',
      12: 'Printed as a plain {{Gb}} triad; the app plays it that way. Many players treat it as {{Gb7}}, the tritone substitute for {{C7}}.',
    },
    ending: 'FΔ',
  },
  {
    id: 12,
    name: 'Major sevenths + chromatic minors',
    bars: ['FΔ', 'BbΔ', 'A- G-', 'F#- B7', 'BbΔ', 'Bb-', 'A-', 'Ab-', 'G-', 'C7', 'FΔ Ab-', 'G- Gb'],
    summary:
      'A bright start ({{FΔ}} {{BbΔ}}) then a diatonic step-down ({{A- G-}}) and {{F#- B7}}, a tritone-substitute ii–V, into {{BbΔ}}. Bars 6–10 and 12 follow form 11.',
    notes: {
      4: '{{F#- B7}} replaces {{C- F7}}: same destination, roots a tritone away.',
      11: '{{Ab-}} is a chromatic passing chord between {{FΔ}} and {{G-}}.',
      12: 'Printed as a plain {{Gb}} triad, as in form 11.',
    },
    ending: 'FΔ',
  },
  {
    id: 13,
    name: 'ii–Vs to ♭III and ♭II',
    bars: ['FΔ', 'BbΔ', 'A- G-', 'F#- B7', 'BbΔ', 'Bb- Eb7', 'AbΔ', 'Ab- Db7', 'GbΔ', 'G- C7', 'A- D7', 'Db- Gb7'],
    summary:
      'From bar 6 the harmony visits distant keys: {{Bb- Eb7}} resolves to {{AbΔ}}, {{Ab- Db7}} to {{GbΔ}}, then {{G- C7}} brings it home. Bar 12 ends with the tritone-sub ii–V {{Db- Gb7}}.',
    notes: {
      6: '{{Bb- Eb7}} is a ii–V in the key a minor third up.',
      9: '{{GbΔ}}: a major chord a half step above home, before {{G- C7}}.',
      12: '{{Db- Gb7}}: tritone substitute for {{G- C7}}, resolving down a half step to bar 1.',
    },
    ending: 'FΔ',
  },
  {
    id: 14,
    name: 'Blues for Alice style',
    bars: ['FΔ', 'E- A7', 'D- G7', 'C- F7', 'BbΔ', 'Bb- Eb7', 'A-', 'Ab- Db7', 'G-', 'C7', 'A- D7', 'G- C7'],
    summary:
      'Close to the changes of Charlie Parker\'s "Blues for Alice": ii–Vs falling by whole steps in bars 2–4, then the backdoor ii–V {{Bb- Eb7}} resolving not to the tonic but to {{A-}}, and {{Ab- Db7}} slipping down to {{G-}}.',
    notes: {
      6: '{{Bb- Eb7}} is iv–7 to ♭VII7, the backdoor ii–V. Here it lands on {{A-}}, a tonic substitute.',
    },
    ending: 'FΔ',
  },
  {
    id: 15,
    name: 'Tritone-sub ii–V into IV',
    bars: ['FΔ', 'E- A7', 'D- G7', 'F#- B7', 'BbΔ', 'Bb- E7', 'A-', 'Ab- Db7', 'G-', 'C7 Bb7', 'A- D7', 'G- C7'],
    summary:
      'Like form 14, but bar 4 uses {{F#- B7}} to reach {{BbΔ}}, bar 6 aims at {{A-}} with its own dominant, {{E7}}, and bar 10 brings back {{C7 Bb7}}.',
    notes: {
      4: '{{F#- B7}}: tritone-substitute ii–V into {{BbΔ}}.',
      6: '{{E7}} is V7 of {{A-}}.',
    },
    ending: 'FΔ',
  },
  {
    id: 16,
    name: 'ii–V chain from bar 1',
    bars: ['F#- B7', 'E- A7', 'D- G7', 'C- F7', 'BbΔ', 'Bb- Eb7', 'AbΔ', 'Ab- Db7', 'GbΔ', 'G- C7', 'A- D7', 'G- C7'],
    summary:
      'Starts away from home: {{F#- B7}}, {{E- A7}}, {{D- G7}}, {{C- F7}}, ii–Vs falling by whole steps until {{BbΔ}}. The tonic never arrives as a resting point; the only I chord is the {{F7}} in bar 4, acting as V7 of IV. Bars 5–11 match form 13.',
    notes: {
      1: '{{F#- B7}} is a ii–V into {{E-}}, the next ii–V.',
    },
    ending: 'FΔ',
  },
  {
    id: 17,
    name: 'Major-seventh planing',
    bars: ['FΔ', 'F#- B7', 'EΔ EbΔ', 'DbΔ BΔ', 'BbΔ', 'B- E7', 'AΔ', 'A- D7', 'GΔ', 'GbΔ', 'FΔ AbΔ', 'GΔ GbΔ'],
    summary:
      'Nearly every chord is a major seventh. {{F#- B7}} resolves to {{EΔ}}, which slides down through {{EbΔ}}, {{DbΔ}} and {{BΔ}} to {{BbΔ}}. The ii–Vs in bars 6 and 8 resolve to major chords, {{AΔ}} and {{GΔ}}, and {{GbΔ}} slides down a half step to the tonic.',
    notes: {
      2: '{{F#- B7}} resolves to {{EΔ}}, a half step below the tonic.',
      12: '{{GΔ GbΔ}} approaches {{FΔ}} from above in half steps.',
    },
    ending: 'FΔ',
  },
  {
    id: 18,
    name: 'Sus-chord blues',
    bars: ['C-/F', 'F-/Bb', 'C-/F', 'C-/F', 'F-/Bb', 'F-/Bb', 'C-/F', 'C-/F', 'G-/C', 'F-/Bb', 'C-/F', 'G-/C'],
    summary:
      'Every bar is a minor seventh chord over the bass note a fifth below it, which sounds as a 9sus4 chord on that bass note. Underneath is a plain I–IV–V blues with the quick change and the V–IV cadence.',
    notes: {
      1: '{{C-/F}}: the 4th replaces the 3rd, so the chord floats rather than resolves.',
    },
    ending: 'C-/F',
  },
];
