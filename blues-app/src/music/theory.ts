// Pitch spelling, chord parsing, transposition and chord-symbol formatting.
//
// Everything is letter-based: a note is a letter plus an accidental, so
// transposing keeps the chart's spelling logic (F#-7 B7 in F becomes C#-7 F#7
// in C, not Db-7 Gb7). Awkward results (double accidentals, E#, Cb...) are
// respelled to the plain enharmonic so chord symbols stay readable.

export const LETTERS = ['C', 'D', 'E', 'F', 'G', 'A', 'B'] as const;
const LETTER_PC = [0, 2, 4, 5, 7, 9, 11];

export const mod = (n: number, m: number) => ((n % m) + m) % m;

export interface Spelling {
  letter: number; // 0 = C ... 6 = B
  acc: number; // -2..2
}

export interface Interval {
  letters: number;
  semis: number;
}

export function pc(s: Spelling): number {
  return mod(LETTER_PC[s.letter] + s.acc, 12);
}

export function parseSpelling(text: string): Spelling {
  const m = /^([A-G])(#{1,2}|b{1,2})?$/.exec(text);
  if (!m) throw new Error(`Bad note name: ${text}`);
  const acc = m[2] ? (m[2][0] === '#' ? m[2].length : -m[2].length) : 0;
  return { letter: LETTERS.indexOf(m[1] as (typeof LETTERS)[number]), acc };
}

export function intervalBetween(from: Spelling, to: Spelling): Interval {
  return { letters: mod(to.letter - from.letter, 7), semis: mod(pc(to) - pc(from), 12) };
}

const FLAT_NAMES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'];
const SHARP_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];

function readable(s: Spelling, preferFlats: boolean): Spelling {
  const awkward =
    Math.abs(s.acc) > 1 ||
    (s.acc === 1 && (s.letter === 2 || s.letter === 6)) || // E#, B#
    (s.acc === -1 && (s.letter === 0 || s.letter === 3)); // Cb, Fb
  if (!awkward) return s;
  return parseSpelling((preferFlats ? FLAT_NAMES : SHARP_NAMES)[pc(s)]);
}

export function transposeSpelling(s: Spelling, iv: Interval, preferFlats = true): Spelling {
  const letter = mod(s.letter + iv.letters, 7);
  const target = mod(pc(s) + iv.semis, 12);
  let acc = mod(target - LETTER_PC[letter], 12);
  if (acc > 6) acc -= 12;
  return readable({ letter, acc }, preferFlats);
}

export function noteName(s: Spelling, ascii = false): string {
  const glyph = ascii
    ? s.acc > 0 ? '#'.repeat(s.acc) : 'b'.repeat(-s.acc)
    : s.acc > 0 ? '♯'.repeat(s.acc) : '♭'.repeat(-s.acc);
  return LETTERS[s.letter] + glyph;
}

// ---------------------------------------------------------------- keys

export const KEYS = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'];
const SHARP_KEYS = new Set(['G', 'D', 'A', 'E', 'B', 'F#']);
// Written keys that are easier to read under their enharmonic name.
const KEY_RESPELL: Record<string, string> = { 'C#': 'Db', 'D#': 'Eb', 'G#': 'Ab', 'A#': 'Bb', Cb: 'B', Fb: 'E', 'E#': 'F', 'B#': 'C' };

export type Transposition = 'C' | 'Bb' | 'Eb' | 'F';
export const TRANSPOSITIONS: Record<Transposition, { label: string; iv: Interval }> = {
  C: { label: 'Concert', iv: { letters: 0, semis: 0 } },
  Bb: { label: 'B♭ instruments', iv: { letters: 1, semis: 2 } }, // written a major 2nd up
  Eb: { label: 'E♭ instruments', iv: { letters: 5, semis: 9 } }, // written a major 6th up
  F: { label: 'F instruments', iv: { letters: 4, semis: 7 } }, // written a perfect 5th up
};

const CHART_KEY = parseSpelling('F');

export interface DisplayKey {
  name: string; // written key, ASCII spelling ("Bb")
  iv: Interval; // from the chart's F to the written key
  preferFlats: boolean;
}

export function displayKey(concertKey: string, transposition: Transposition): DisplayKey {
  const concert = parseSpelling(concertKey);
  const written = transposeSpelling(concert, TRANSPOSITIONS[transposition].iv, !SHARP_KEYS.has(concertKey));
  let name = noteName(written, true);
  name = KEY_RESPELL[name] ?? name;
  const spelled = parseSpelling(name);
  return { name, iv: intervalBetween(CHART_KEY, spelled), preferFlats: !SHARP_KEYS.has(name) };
}

/** Semitones from the chart key (F) up to the concert key, for playback. */
export function concertOffset(concertKey: string): number {
  return mod(pc(parseSpelling(concertKey)) - pc(CHART_KEY), 12);
}

// ---------------------------------------------------------------- chords

// dom7 "F7", min7 "C-", maj7 "FΔ", dim7 "B°", maj "Gb" (plain triad),
// sus "C-/F" (minor seventh over the note a fifth below: F9sus4).
// hdim "Eø" (half-diminished, m7♭5) isn't on the chart but turns up in suggestions.
export type Quality = 'dom7' | 'min7' | 'maj7' | 'dim7' | 'hdim' | 'maj' | 'sus';

export interface Chord {
  root: Spelling; // for sus chords this is the bass note, the functional root
  quality: Quality;
  upper?: Spelling; // sus only: root of the minor chord on top
}

export function parseChord(sym: string): Chord {
  const slash = /^([A-G][#b]?)-\/([A-G][#b]?)$/.exec(sym);
  if (slash) return { root: parseSpelling(slash[2]), quality: 'sus', upper: parseSpelling(slash[1]) };
  const m = /^([A-G][#b]?)(7|-|Δ|°|ø)?$/.exec(sym);
  if (!m) throw new Error(`Bad chord symbol: ${sym}`);
  const quality: Quality = ({ '7': 'dom7', '-': 'min7', 'Δ': 'maj7', '°': 'dim7', 'ø': 'hdim' } as const)[m[2] as '7'] ?? 'maj';
  return { root: parseSpelling(m[1]), quality };
}

/** A bar as printed: one chord, or two chords of two beats each. */
export function parseBar(bar: string): Chord[] {
  return bar.trim().split(/\s+/).map(parseChord);
}

export function transposeChord(c: Chord, iv: Interval, preferFlats = true): Chord {
  return {
    root: transposeSpelling(c.root, iv, preferFlats),
    quality: c.quality,
    upper: c.upper && transposeSpelling(c.upper, iv, preferFlats),
  };
}

export type Notation = 'chart' | 'standard';

const SUFFIX: Record<Notation, Record<Exclude<Quality, 'sus'>, string>> = {
  chart: { dom7: '7', min7: '−', maj7: 'Δ', dim7: '°', hdim: 'ø', maj: '' },
  standard: { dom7: '7', min7: 'm7', maj7: 'maj7', dim7: '°7', hdim: 'm7♭5', maj: '' },
};

export function chordSymbol(c: Chord, notation: Notation = 'chart'): string {
  if (c.quality === 'sus') {
    const upper = noteName(c.upper!) + (notation === 'chart' ? '−' : 'm7');
    return `${upper}/${noteName(c.root)}`;
  }
  return noteName(c.root) + SUFFIX[notation][c.quality];
}

/** The chart's own ASCII spelling ("F#-", "BbΔ", "C-/F"), which parseChord reads back. */
export function chartString(c: Chord): string {
  const n = noteName(c.root, true);
  if (c.quality === 'sus') return `${noteName(c.upper!, true)}-/${n}`;
  return n + ({ dom7: '7', min7: '-', maj7: 'Δ', dim7: '°', hdim: 'ø', maj: '' } as const)[c.quality];
}

export function chordKey(c: Chord): string {
  return `${pc(c.root)}:${c.quality}:${c.upper ? pc(c.upper) : ''}`;
}

// ---------------------------------------------------------------- roman numerals

const F_MAJOR_BY_DEGREE = [5, 7, 9, 10, 0, 2, 4]; // F G A Bb C D E
const NUMERALS = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII'];

const ROMAN_SUFFIX: Record<Notation, Record<Quality, string>> = {
  chart: { dom7: '7', min7: '−7', maj7: 'Δ7', dim7: '°7', hdim: 'ø7', maj: '', sus: '9sus' },
  standard: { dom7: '7', min7: 'm7', maj7: 'maj7', dim7: '°7', hdim: 'm7♭5', maj: '', sus: '9sus4' },
};

/** Roman numeral for a chord spelled in the chart key (F). Key-independent. */
export function romanNumeral(chartChord: Chord, notation: Notation = 'chart'): string {
  const s = chartChord.root;
  const degree = mod(s.letter - CHART_KEY.letter, 7);
  let acc = mod(pc(s) - F_MAJOR_BY_DEGREE[degree], 12);
  if (acc > 6) acc -= 12;
  const prefix = acc < 0 ? '♭'.repeat(-acc) : '♯'.repeat(acc);
  const lower = chartChord.quality === 'min7' || chartChord.quality === 'dim7' || chartChord.quality === 'hdim';
  const numeral = lower ? NUMERALS[degree].toLowerCase() : NUMERALS[degree];
  return prefix + numeral + ROMAN_SUFFIX[notation][chartChord.quality];
}

// ---------------------------------------------------------------- chord tones

/** Pitch-class offsets above the (functional) root. */
export const CHORD_TONES: Record<Quality, number[]> = {
  dom7: [0, 4, 7, 10],
  min7: [0, 3, 7, 10],
  maj7: [0, 4, 7, 11],
  dim7: [0, 3, 6, 9],
  hdim: [0, 3, 6, 10],
  maj: [0, 4, 7],
  sus: [0, 5, 7, 10, 2],
};

export const SCALES: Record<Quality, number[]> = {
  dom7: [0, 2, 4, 5, 7, 9, 10], // mixolydian
  min7: [0, 2, 3, 5, 7, 9, 10], // dorian
  maj7: [0, 2, 4, 5, 7, 9, 11], // major
  dim7: [0, 2, 3, 5, 6, 8, 9, 11], // whole-half diminished
  hdim: [0, 1, 3, 5, 6, 8, 10], // locrian
  maj: [0, 2, 4, 5, 7, 9, 11],
  sus: [0, 2, 4, 5, 7, 9, 10],
};

export const SCALE_HINT: Record<Quality, string> = {
  dom7: 'Mixolydian, or the blues scale',
  min7: 'Dorian',
  maj7: 'Major (or Lydian)',
  dim7: 'Diminished, whole step–half step',
  hdim: 'Locrian (or Locrian ♮2)',
  maj: 'Major / major pentatonic',
  sus: 'Mixolydian; lean on the 4th, not the 3rd',
};

// Chord tones as intervals with letter steps, so they can be spelled.
const SPELLED_TONES: Record<Quality, Array<[string, Interval]>> = {
  dom7: [['1', { letters: 0, semis: 0 }], ['3', { letters: 2, semis: 4 }], ['5', { letters: 4, semis: 7 }], ['♭7', { letters: 6, semis: 10 }]],
  min7: [['1', { letters: 0, semis: 0 }], ['♭3', { letters: 2, semis: 3 }], ['5', { letters: 4, semis: 7 }], ['♭7', { letters: 6, semis: 10 }]],
  maj7: [['1', { letters: 0, semis: 0 }], ['3', { letters: 2, semis: 4 }], ['5', { letters: 4, semis: 7 }], ['7', { letters: 6, semis: 11 }]],
  dim7: [['1', { letters: 0, semis: 0 }], ['♭3', { letters: 2, semis: 3 }], ['♭5', { letters: 4, semis: 6 }], ['°7', { letters: 6, semis: 9 }]],
  hdim: [['1', { letters: 0, semis: 0 }], ['♭3', { letters: 2, semis: 3 }], ['♭5', { letters: 4, semis: 6 }], ['♭7', { letters: 6, semis: 10 }]],
  maj: [['1', { letters: 0, semis: 0 }], ['3', { letters: 2, semis: 4 }], ['5', { letters: 4, semis: 7 }]],
  sus: [['1', { letters: 0, semis: 0 }], ['4', { letters: 3, semis: 5 }], ['5', { letters: 4, semis: 7 }], ['♭7', { letters: 6, semis: 10 }], ['9', { letters: 1, semis: 2 }]],
};

const GUIDE_DEGREES: Record<Quality, [string, string]> = {
  dom7: ['3', '♭7'],
  min7: ['♭3', '♭7'],
  maj7: ['3', '7'],
  dim7: ['♭3', '°7'],
  hdim: ['♭3', '♭7'],
  maj: ['3', '5'],
  sus: ['4', '♭7'],
};

export interface SpelledTone {
  degree: string;
  name: string;
}

export function chordTones(c: Chord, preferFlats = true): SpelledTone[] {
  return SPELLED_TONES[c.quality].map(([degree, iv]) => ({
    degree,
    name: noteName(transposeSpelling(c.root, iv, preferFlats)),
  }));
}

/** The two notes that define the chord's sound: usually its 3rd and 7th. */
export function guideTones(c: Chord, preferFlats = true): SpelledTone[] {
  const wanted = GUIDE_DEGREES[c.quality];
  return chordTones(c, preferFlats).filter((t) => wanted.includes(t.degree));
}
