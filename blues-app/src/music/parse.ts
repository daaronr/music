// Reads chords the way people type them, for suggested forms: letter names in
// the key on screen (C7, Fm7, Bbmaj7, E°, Gm7b5, C-/F, B♭Δ...) or roman
// numerals (ii-7, V7, bVII7, #iv°7, I9sus). Returns chart chords spelled in F,
// the same form as the chart data, or an error message for the reader.

import { mod, parseSpelling, pc, transposeSpelling, type Chord, type Interval, type Quality } from './theory.ts';

const normalise = (s: string) =>
  s
    .trim()
    .replace(/♭/g, 'b')
    .replace(/♯/g, '#')
    .replace(/[−–—]/g, '-')
    .replace(/\s+/g, '');

/** Suffix after the root, loosely. Extensions collapse to the chord family the app can voice. */
function quality(suffix: string): Quality | null {
  const s = suffix.replace(/[()]/g, '');
  if (/^(ø7?|m7b5|-7b5|mi7b5|min7b5|h7?)$/i.test(s)) return 'hdim';
  if (/^(°7?|o7?|dim7?)$/i.test(s)) return 'dim7';
  if (/^(sus4?|7sus4?|9sus4?|11|13sus4?)$/i.test(s)) return 'sus';
  if (/^(Δ7?|\^7?|maj7|maj9|maj13|M7|M9|ma7|6|69|6\/9|maj)$/.test(s)) return 'maj7';
  if (/^(-|-7|-9|-11|m|m7|m9|m11|m6|min|min7|mi|mi7|-6)$/.test(s)) return 'min7';
  if (/^(7|9|13|7b9|7#9|7#11|7b13|7alt|alt|9#11|13b9|7#5|7b5|aug7|\+7)$/i.test(s)) return 'dom7';
  if (s === '' || s === 'M') return 'maj';
  return null;
}

const FIFTH: Interval = { letters: 4, semis: 7 };

function susOn(root: Chord['root']): Chord {
  return { root, quality: 'sus', upper: transposeSpelling(root, FIFTH) };
}

/** One chord, letters, typed in a key whose interval from the chart's F is `iv`. */
function letterChord(text: string, iv: Interval): Chord | string {
  const slash = /^([A-G][#b]?)(.*)\/([A-G][#b]?)$/.exec(text);
  const back = (sp: Chord['root']) => transposeSpelling(sp, { letters: mod(-iv.letters, 7), semis: mod(-iv.semis, 12) });
  if (slash) {
    const upper = parseSpelling(slash[1]);
    const bass = parseSpelling(slash[3]);
    const q = quality(slash[2]);
    // A minor seventh a fifth above the bass is the chart's sus sound (C-/F).
    if (q === 'min7' && mod(pc(upper) - pc(bass), 12) === 7) return susOn(back(bass));
    if (!q) return `Can't read "${text}"`;
    return { root: back(upper), quality: q === 'sus' ? 'sus' : q, ...(q === 'sus' ? { upper: back(transposeSpelling(upper, FIFTH)) } : {}) };
  }
  const m = /^([A-G][#b]?)(.*)$/.exec(text);
  if (!m) return `Can't read "${text}"`;
  const q = quality(m[2]);
  if (!q) return `Can't read "${text}"`;
  const root = back(parseSpelling(m[1]));
  return q === 'sus' ? susOn(root) : { root, quality: q };
}

const NUMERALS = ['vii', 'iii', 'vi', 'iv', 'ii', 'v', 'i'];
const DEGREE: Record<string, number> = { i: 0, ii: 1, iii: 2, iv: 3, v: 4, vi: 5, vii: 6 };
const F_MAJOR = [5, 7, 9, 10, 0, 2, 4];
const LETTER_PC = [0, 2, 4, 5, 7, 9, 11];

function romanChord(text: string): Chord | string {
  const m = /^([b#]*)([ivIV]+)(.*)$/.exec(text);
  if (!m) return `Can't read "${text}"`;
  const numeral = NUMERALS.find((n) => m[2].toLowerCase() === n);
  if (numeral === undefined) return `Can't read "${text}"`;
  const degree = DEGREE[numeral];
  const lower = m[2] === m[2].toLowerCase();
  let q = quality(m[3]);
  if (m[3] === '' && lower) q = 'min7';
  if (!q) return `Can't read "${text}"`;
  const shift = [...m[1]].reduce((n, ch) => n + (ch === '#' ? 1 : -1), 0);
  const letter = (3 + degree) % 7; // F is letter 3
  let acc = mod(F_MAJOR[degree] + shift - LETTER_PC[letter], 12);
  if (acc > 6) acc -= 12;
  const root = { letter, acc };
  return q === 'sus' ? susOn(root) : { root, quality: q };
}

export function looksRoman(text: string) {
  return /^[b#]*(?:VII|VI|V|IV|III|II|I|vii|vi|v|iv|iii|ii|i)(?![a-z])/.test(normalise(text).split(/\s+/)[0] ?? '');
}

/** A bar: one chord, or two separated by a space (two beats each). */
export function parseTypedBar(text: string, iv: Interval): Chord[] | string {
  const parts = text.replace(/[|,]/g, ' ').trim().split(/\s+/).filter(Boolean).map(normalise);
  if (parts.length === 0) return 'Empty bar';
  if (parts.length > 2) return 'At most two chords a bar';
  const out: Chord[] = [];
  for (const p of parts) {
    const c = /^[b#]*[ivIV]/.test(p) && !/^[A-G]/.test(p) ? romanChord(p) : letterChord(p, iv);
    if (typeof c === 'string') return c;
    out.push(c);
  }
  return out;
}
