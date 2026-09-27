// Sample sets, shared by the browser engine and the offline MP3 renderer.
// All are CC0 / royalty-free recordings hosted (with CORS) by smpldsnds:
//   piano - Splendid Grand Piano, mezzo-piano layer
//   bass  - 1958 Otto Rubner double bass, pizzicato (D. Smolken)
//   drums - Versilian Community Sample Library suspended cymbal (stick) and hi-hat
// URLs are given without extension; each exists as .ogg and .m4a.

import type { DrumHit } from '../music/arranger.ts';

export interface PitchedSample {
  midi: number;
  url: string;
}

const PIANO_BASE = 'https://smpldsnds.github.io/sfzinstruments-splendid-grand-piano/samples/';
const PIANO_NOTES: Array<[number, string]> = [
  [48, 'C2'], [50, 'D2'], [53, 'F2'], [56, 'G#2'], [59, 'B2'], [62, 'D3'], [65, 'F3'],
  [67, 'G3'], [71, 'B3'], [74, 'D4'], [77, 'F4'], [80, 'G#4'], [83, 'B4'],
];
export const PIANO: PitchedSample[] = PIANO_NOTES.map(([midi, name]) => ({
  midi,
  url: PIANO_BASE + encodeURIComponent(`Mp ${name}`),
}));

const BASS_BASE = 'https://smpldsnds.github.io/sfzinstruments-dsmolken-double-bass/pizz/';
export const BASS: PitchedSample[] = [
  [24, 'c1_ma'], [27, 'eb1_ma'], [31, 'g1_ma'], [34, 'bb1_fa'], [38, 'd2_ma'],
  [41, 'f2_ma'], [45, 'a2_ma'], [48, 'c3_ma'], [52, 'e3_ma'],
].map(([midi, name]) => ({ midi: midi as number, url: `${BASS_BASE}pizz_${name}` }));

const VCSL = 'https://smpldsnds.github.io/sgossner-vcsl/Idiophones/Struck%20Idiophones/';
export const DRUMS: Record<DrumHit, string[]> = {
  ride: [`${VCSL}Suspended%20Cymbal%202/susCymb2_hit_stick_mp1`],
  rideSkip: [`${VCSL}Suspended%20Cymbal%202/susCymb2_hit_stick_pp1`],
  crash: [`${VCSL}Suspended%20Cymbal%202/susCymb2_hit_stick_mf1`],
  hat: [`${VCSL}Hi-Hat%20Cymbal/HiHat_Close_rr1_Mid`, `${VCSL}Hi-Hat%20Cymbal/HiHat_Close_rr2_Mid`],
  click: [`${VCSL}Hi-Hat%20Cymbal/HiHat_HitC_v2_rr1_Mid`],
};

export function nearestSample<T extends { midi: number }>(set: T[], midi: number): T {
  let best = set[0];
  for (const s of set) if (Math.abs(s.midi - midi) < Math.abs(best.midi - midi)) best = s;
  return best;
}

/** How each drum hit decays (seconds for the level to fall by 1/e); 0 = natural. */
export const DRUM_DECAY: Record<DrumHit, number> = { ride: 0.8, rideSkip: 0.5, crash: 2.2, hat: 0, click: 0 };

// The cymbal is an orchestral suspended cymbal. Played a little faster and with
// its low ring filtered off, a stick hit reads as a jazz ride.
export const DRUM_RATE: Record<DrumHit, number> = { ride: 1.25, rideSkip: 1.25, crash: 1.1, hat: 1, click: 1 };
export const DRUM_HIGHPASS: Record<DrumHit, number> = { ride: 900, rideSkip: 900, crash: 500, hat: 0, click: 0 };
export const DRUM_LEVEL: Record<DrumHit, number> = { ride: 1, rideSkip: 1, crash: 0.9, hat: 0.8, click: 1.1 };

// Mix: overall level per part, stereo position (-1 left .. 1 right), reverb send.
export const MIX = {
  keys: { gain: 0.42, pan: 0.18, send: 0.22 },
  bass: { gain: 0.9, pan: 0, send: 0.05 },
  drums: { gain: 0.62, pan: -0.28, send: 0.12 },
} as const;

/** Two-pole (12 dB/octave) high-pass, applied in place. */
export function highpassInPlace(x: Float32Array, sampleRate: number, freq: number) {
  if (freq <= 0) return;
  const w = (2 * Math.PI * freq) / sampleRate;
  const q = Math.SQRT1_2;
  const alpha = Math.sin(w) / (2 * q);
  const cos = Math.cos(w);
  const a0 = 1 + alpha;
  const b0 = (1 + cos) / 2 / a0;
  const b1 = -(1 + cos) / a0;
  const b2 = b0;
  const a1 = (-2 * cos) / a0;
  const a2 = (1 - alpha) / a0;
  let x1 = 0, x2 = 0, y1 = 0, y2 = 0;
  for (let i = 0; i < x.length; i++) {
    const y = b0 * x[i] + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2;
    x2 = x1;
    x1 = x[i];
    y2 = y1;
    y1 = y;
    x[i] = y;
  }
}

export function normalizeInPlace(channels: Float32Array[]) {
  let peak = 1e-9;
  for (const ch of channels) for (let i = 0; i < ch.length; i++) peak = Math.max(peak, Math.abs(ch[i]));
  for (const ch of channels) for (let i = 0; i < ch.length; i++) ch[i] /= peak;
}
