// Turns chords into notes: piano voicings, a walking (or two-feel) bass line,
// swing comping and a ride-cymbal pattern. Pure and deterministic for a given
// seed, so the browser engine and the offline MP3 renderer play the same thing.
//
// Times are in beats from the start of the bar; the caller converts to seconds.

import { CHORD_TONES, SCALES, mod, pc, type Chord, type Quality } from './theory.ts';

export type Part = 'keys' | 'bass' | 'drums';
export type DrumHit = 'ride' | 'rideSkip' | 'crash' | 'hat' | 'click';

export interface NoteEvent {
  part: Part;
  beat: number;
  dur: number;
  vel: number; // 0..1
  midi: number; // for drums, unused (0)
  drum?: DrumHit;
}

export interface ArrangerSettings {
  swing: number; // position of the off-beat eighth, 0.5 (straight) to 0.75
  comp: 'swing' | 'sustain';
  bass: 'walk' | 'two';
}

export const DEFAULT_SETTINGS: ArrangerSettings = { swing: 0.64, comp: 'swing', bass: 'walk' };

export interface BarInput {
  chords: Chord[]; // concert pitch; one chord (4 beats) or two (2 beats each)
  next: Chord; // first chord of the following bar
  chorusStart?: boolean;
}

// ---------------------------------------------------------------- randomness

export function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function weighted<T>(rng: () => number, items: Array<[number, T]>): T {
  const total = items.reduce((s, [w]) => s + w, 0);
  let r = rng() * total;
  for (const [w, item] of items) {
    r -= w;
    if (r <= 0) return item;
  }
  return items[items.length - 1][1];
}

// ---------------------------------------------------------------- voicings

// Offsets above the chord root. Dominant, minor and major sevenths use the
// standard rootless "A" (3-5-7-9 family) and "B" (7-9-3-5 family) shapes;
// the bass supplies the root.
const SHAPES: Record<Quality, number[][]> = {
  dom7: [
    [4, 9, 10, 14], // 3 13 b7 9
    [10, 14, 16, 21], // b7 9 3 13
  ],
  min7: [
    [3, 7, 10, 14], // b3 5 b7 9
    [10, 14, 15, 19], // b7 9 b3 5
  ],
  maj7: [
    [4, 7, 11, 14], // 3 5 7 9
    [11, 14, 16, 19], // 7 9 3 5
  ],
  dim7: [
    [0, 3, 6, 9],
    [3, 6, 9, 12],
    [6, 9, 12, 15],
    [9, 12, 15, 18],
  ],
  maj: [
    [0, 4, 7, 12],
    [4, 7, 12, 16],
    [7, 12, 16, 19],
  ],
  // Minor seventh a fifth above the bass: 5 b7 9 11 over the root.
  sus: [
    [7, 10, 14, 17],
    [10, 14, 17, 19],
    [2, 5, 7, 10],
    [5, 7, 10, 14],
  ],
};

export const VOICING_LOW: [number, number] = [49, 62]; // allowed lowest note (C#3..D4)
export const VOICING_TOP = 79;
const VOICING_CENTER = 61;

export function voicingCandidates(chord: Chord): number[][] {
  const root = pc(chord.root);
  const out: number[][] = [];
  for (const shape of SHAPES[chord.quality]) {
    for (let base = root + 24; base <= 84; base += 12) {
      const notes = shape.map((o) => base + o);
      const lo = notes[0];
      if (lo >= VOICING_LOW[0] && lo <= VOICING_LOW[1] && notes[notes.length - 1] <= VOICING_TOP) out.push(notes);
    }
  }
  return out;
}

function movement(a: number[], b: number[]): number {
  if (a.length === b.length) return a.reduce((s, n, i) => s + Math.abs(n - b[i]), 0);
  return a.reduce((s, n) => s + Math.min(...b.map((m) => Math.abs(n - m))), 0);
}

export function voiceChord(chord: Chord, prev: number[] | null, rng: () => number = Math.random): number[] {
  const cands = voicingCandidates(chord);
  let best = cands[0];
  let bestScore = Infinity;
  for (const c of cands) {
    const mean = c.reduce((s, n) => s + n, 0) / c.length;
    let score = 0.35 * Math.abs(mean - VOICING_CENTER);
    if (prev) score += movement(c, prev);
    score += rng() * 0.5;
    if (score < bestScore) {
      bestScore = score;
      best = c;
    }
  }
  return best;
}

// ---------------------------------------------------------------- bass

export const BASS_RANGE: [number, number] = [28, 50]; // E1..D3 (sounding)
const BASS_CENTER = 39;

function inRange(n: number) {
  return n >= BASS_RANGE[0] && n <= BASS_RANGE[1];
}

function nearestOctave(pitchClass: number, near: number): number {
  let best = -1;
  for (let n = BASS_RANGE[0]; n <= BASS_RANGE[1]; n++) {
    if (mod(n, 12) !== pitchClass) continue;
    const score = Math.abs(n - near) + 0.15 * Math.abs(n - BASS_CENTER);
    if (best < 0 || score < Math.abs(best - near) + 0.15 * Math.abs(best - BASS_CENTER)) best = n;
  }
  return best;
}

function leapCost(a: number, b: number): number {
  const d = Math.abs(a - b);
  if (d === 0) return 4;
  if (d <= 2) return 0;
  if (d <= 4) return 0.3;
  if (d <= 7) return 0.7;
  if (d <= 9) return 1.6;
  return 4;
}

function directionChanges(line: number[]): number {
  let changes = 0;
  let dir = 0;
  for (let i = 1; i < line.length; i++) {
    const d = Math.sign(line[i] - line[i - 1]);
    if (d !== 0 && dir !== 0 && d !== dir) changes++;
    if (d !== 0) dir = d;
  }
  return changes;
}

interface BassCtx {
  chord: Chord;
  start: number; // first note, already chosen
  target: number; // the note the line is heading for (next segment's root)
  targetChord: Chord;
  rng: () => number;
}

function toneKind(chord: Chord, note: number): 'root' | 'chord' | 'scale' | 'chromatic' {
  const rel = mod(note - pc(chord.root), 12);
  if (rel === 0) return 'root';
  if (CHORD_TONES[chord.quality].includes(rel)) return 'chord';
  if (SCALES[chord.quality].includes(rel)) return 'scale';
  return 'chromatic';
}

function approachCost(ctx: BassCtx, note: number): number {
  const d = note - ctx.target;
  if (Math.abs(d) === 1) return 0; // chromatic approach
  if (Math.abs(d) === 2) {
    const inScale = toneKind(ctx.chord, note) !== 'chromatic' || toneKind(ctx.targetChord, note) !== 'chromatic';
    return inScale ? 0.4 : 0.9;
  }
  if (mod(note - ctx.target, 12) === 7) return 0.6; // dominant (fifth) approach
  return Infinity;
}

function walkFour(ctx: BassCtx): number[] {
  const { start, target, chord, rng } = ctx;
  let best: number[] = [start, start + 7, start + 4, target - 1];
  let bestScore = Infinity;
  const approaches = [target - 1, target + 1, target - 2, target + 2, target + 7, target - 5].filter(inRange);
  for (let b2 = start - 9; b2 <= start + 9; b2++) {
    if (!inRange(b2) || b2 === start) continue;
    const k2 = toneKind(chord, b2);
    for (let b3 = b2 - 7; b3 <= b2 + 7; b3++) {
      if (!inRange(b3) || b3 === b2) continue;
      const k3 = toneKind(chord, b3);
      for (const b4 of approaches) {
        if (b4 === b3 || b4 === target) continue;
        const a = approachCost(ctx, b4);
        if (!Number.isFinite(a)) continue;
        let s = a;
        s += { root: 1.2, chord: 0, scale: 0.8, chromatic: 2.0 }[k2];
        if (k3 === 'chromatic') {
          const passing = Math.abs(b3 - b2) <= 2 && Math.abs(b4 - b3) <= 2 && Math.sign(b3 - b2) === Math.sign(b4 - b3);
          s += passing ? 0.9 : 2.2;
        } else {
          s += { root: 0.8, chord: 0, scale: 1.0, chromatic: 0 }[k3];
        }
        const line = [start, b2, b3, b4, target];
        for (let i = 1; i < line.length; i++) s += leapCost(line[i - 1], line[i]);
        s += 0.35 * directionChanges(line);
        s += 0.03 * (Math.abs(b2 - BASS_CENTER) + Math.abs(b3 - BASS_CENTER) + Math.abs(b4 - BASS_CENTER));
        s += rng() * 0.9;
        if (s < bestScore) {
          bestScore = s;
          best = [start, b2, b3, b4];
        }
      }
    }
  }
  return best;
}

function walkTwo(ctx: BassCtx): number[] {
  const { start, target, rng } = ctx;
  let best = [start, target - 1];
  let bestScore = Infinity;
  for (const b2 of [target - 1, target + 1, target - 2, target + 2, target + 7, target - 5, start + 7, start - 5]) {
    if (!inRange(b2) || b2 === start || b2 === target) continue;
    let s = Number.isFinite(approachCost(ctx, b2)) ? approachCost(ctx, b2) : 1.5;
    s += leapCost(start, b2) + leapCost(b2, target) + rng() * 0.6;
    if (s < bestScore) {
      bestScore = s;
      best = [start, b2];
    }
  }
  return best;
}

// ---------------------------------------------------------------- comping

interface Hit {
  at: number; // beat position (already swung)
  dur: number;
  chord: 0 | 1 | 'next';
  vel: number;
}

function compPattern(n: number, s: ArrangerSettings, rng: () => number, nextDiffers: boolean): Hit[] {
  const sw = s.swing;
  if (s.comp === 'sustain') {
    return n === 1
      ? [{ at: 0, dur: 3.85, chord: 0, vel: 0.55 }]
      : [
          { at: 0, dur: 1.9, chord: 0, vel: 0.55 },
          { at: 2, dur: 1.85, chord: 1, vel: 0.55 },
        ];
  }
  if (n === 1) {
    const options: Array<[number, Hit[]]> = [
      [3, [{ at: 0, dur: 1.2, chord: 0, vel: 0.62 }, { at: 1 + sw, dur: 0.45, chord: 0, vel: 0.5 }]], // Charleston
      [2, [{ at: 1, dur: 0.5, chord: 0, vel: 0.55 }, { at: 3, dur: 0.5, chord: 0, vel: 0.55 }]], // 2 and 4
      [2, [{ at: 0, dur: 2.4, chord: 0, vel: 0.58 }]],
      [1.5, [{ at: 1 + sw, dur: 1.6, chord: 0, vel: 0.56 }]],
      [2, [{ at: 0, dur: 0.9, chord: 0, vel: 0.6 }, { at: 2 + sw, dur: 1.2, chord: 0, vel: 0.52 }]],
    ];
    if (nextDiffers)
      options.push([1.5, [{ at: 0, dur: 0.8, chord: 0, vel: 0.6 }, { at: 3 + sw, dur: 1.4, chord: 'next', vel: 0.58 }]]);
    return weighted(rng, options);
  }
  const options: Array<[number, Hit[]]> = [
    [3, [{ at: 0, dur: 1.4, chord: 0, vel: 0.6 }, { at: 2, dur: 1.5, chord: 1, vel: 0.57 }]],
    [2, [{ at: 0, dur: 0.8, chord: 0, vel: 0.6 }, { at: 1 + sw, dur: 2, chord: 1, vel: 0.57 }]],
  ];
  if (nextDiffers)
    options.push([
      1,
      [
        { at: 0, dur: 0.9, chord: 0, vel: 0.6 },
        { at: 2, dur: 0.9, chord: 1, vel: 0.55 },
        { at: 3 + sw, dur: 1.3, chord: 'next', vel: 0.57 },
      ],
    ]);
  return weighted(rng, options);
}

// ---------------------------------------------------------------- arranger

export class Arranger {
  private rng: () => number;
  private voicing: number[] | null = null;
  private bassNote: number | null = null;
  private plannedBass: number | null = null;
  private anticipated: number[] | null = null; // voicing already struck for this bar's first chord

  constructor(seed = 7) {
    this.rng = mulberry32(seed);
  }

  reset(seed?: number) {
    if (seed !== undefined) this.rng = mulberry32(seed);
    this.voicing = null;
    this.bassNote = null;
    this.plannedBass = null;
    this.anticipated = null;
  }

  private voice(chord: Chord): number[] {
    this.voicing = voiceChord(chord, this.voicing, this.rng);
    return this.voicing;
  }

  bar(input: BarInput, s: ArrangerSettings = DEFAULT_SETTINGS): NoteEvent[] {
    const events: NoteEvent[] = [];
    const { chords, next } = input;
    const n = chords.length;
    const segBeats = 4 / n;

    // Bass --------------------------------------------------------------
    for (let i = 0; i < n; i++) {
      const chord = chords[i];
      const targetChord = i + 1 < n ? chords[i + 1] : next;
      const rootPc = pc(chord.root);
      const start =
        this.plannedBass !== null && mod(this.plannedBass, 12) === rootPc && inRange(this.plannedBass)
          ? this.plannedBass
          : nearestOctave(rootPc, this.bassNote ?? BASS_CENTER);
      const target = nearestOctave(pc(targetChord.root), start);
      const ctx: BassCtx = { chord, start, target, targetChord, rng: this.rng };
      const t0 = i * segBeats;
      let line: number[];
      let step: number;
      if (s.bass === 'two') {
        line = segBeats === 4 ? walkTwo(ctx) : [start];
        step = 2;
      } else {
        line = segBeats === 4 ? walkFour(ctx) : walkTwo(ctx);
        step = 1;
      }
      line.forEach((note, k) => {
        events.push({ part: 'bass', beat: t0 + k * step, dur: step * 0.93, midi: note, vel: k === 0 ? 0.82 : 0.72 });
      });
      this.bassNote = line[line.length - 1];
      this.plannedBass = target;
    }

    // Keys --------------------------------------------------------------
    const nextDiffers = pc(next.root) !== pc(chords[n - 1].root) || next.quality !== chords[n - 1].quality;
    const hits = compPattern(n, s, this.rng, nextDiffers);
    const voicings: number[][] = [];
    for (let i = 0; i < n; i++) {
      if (i === 0 && this.anticipated) voicings.push(this.anticipated);
      else voicings.push(this.voice(chords[i]));
    }
    const skipFirstDownbeat = this.anticipated !== null;
    this.anticipated = null;
    for (const hit of hits) {
      if (skipFirstDownbeat && hit.chord === 0 && hit.at === 0) continue;
      let notes: number[];
      if (hit.chord === 'next') {
        notes = this.voice(next);
        this.anticipated = notes;
      } else {
        notes = voicings[hit.chord];
      }
      const vel = hit.vel * (0.9 + this.rng() * 0.2);
      notes.forEach((midi, k) => {
        // A little spread, lowest note first, like a real hand.
        events.push({ part: 'keys', beat: hit.at + k * 0.012, dur: hit.dur, midi, vel: vel * (k === notes.length - 1 ? 1.08 : 1) });
      });
    }

    // Drums -------------------------------------------------------------
    const sw = s.swing;
    for (let beat = 0; beat < 4; beat++) {
      const accent = beat % 2 === 1;
      if (beat === 0 && input.chorusStart) {
        events.push({ part: 'drums', drum: 'crash', beat, dur: 3, midi: 0, vel: 0.7 });
      } else {
        events.push({ part: 'drums', drum: 'ride', beat, dur: 1.5, midi: 0, vel: accent ? 0.72 : 0.6 });
      }
      if (accent) {
        events.push({ part: 'drums', drum: 'rideSkip', beat: beat + sw, dur: 1, midi: 0, vel: 0.45 + this.rng() * 0.08 });
        events.push({ part: 'drums', drum: 'hat', beat, dur: 0.5, midi: 0, vel: 0.62 });
      }
    }
    return events;
  }

  countIn(beats = 4): NoteEvent[] {
    return Array.from({ length: beats }, (_, i) => ({
      part: 'drums' as const,
      drum: 'click' as const,
      beat: i,
      dur: 0.5,
      midi: 0,
      vel: i === 0 ? 0.8 : 0.65,
    }));
  }

  /** A held final chord with bass root and a cymbal. */
  ending(chord: Chord): NoteEvent[] {
    const notes = this.voice(chord);
    const bass = nearestOctave(pc(chord.root), this.bassNote ?? BASS_CENTER - 6);
    return [
      ...notes.map((midi, k) => ({ part: 'keys' as const, beat: k * 0.02, dur: 3.6, midi, vel: 0.6 })),
      { part: 'bass', beat: 0, dur: 3.2, midi: bass, vel: 0.85 },
      { part: 'drums', drum: 'crash', beat: 0, dur: 4, midi: 0, vel: 0.6 },
    ];
  }

  /** Just the chord(s) of one bar, for clicking a bar to hear it. */
  audition(chords: Chord[]): NoteEvent[] {
    const events: NoteEvent[] = [];
    const segBeats = 4 / chords.length;
    chords.forEach((chord, i) => {
      const notes = this.voice(chord);
      notes.forEach((midi, k) => events.push({ part: 'keys', beat: i * segBeats + k * 0.015, dur: segBeats * 0.95, midi, vel: 0.6 }));
      events.push({ part: 'bass', beat: i * segBeats, dur: segBeats * 0.9, midi: nearestOctave(pc(chord.root), BASS_CENTER), vel: 0.8 });
    });
    return events;
  }
}
