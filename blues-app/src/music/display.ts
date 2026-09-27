// Turns chart chords (spelled in F) into what the reader sees and what the
// engine plays.

import { VARIATIONS } from './progressions.ts';
import {
  chordSymbol,
  concertOffset,
  displayKey,
  guideTones,
  parseBar,
  romanNumeral,
  transposeChord,
  type Chord,
  type DisplayKey,
  type Notation,
  type Quality,
  type SpelledTone,
  type Transposition,
} from './theory.ts';

export interface ViewOptions {
  key: string; // concert key
  transposition: Transposition;
  notation: Notation;
  /** Show every chord as its roman numeral instead of a letter name. */
  romanOnly?: boolean;
}

export interface ShownChord {
  chart: Chord;
  shown: Chord;
  symbol: string;
  roman: string;
  quality: Quality;
  guide: SpelledTone[];
}

export class View {
  readonly dk: DisplayKey;
  readonly opts: ViewOptions;
  private readonly concertIv: { letters: number; semis: number };

  constructor(opts: ViewOptions) {
    this.opts = opts;
    this.dk = displayKey(opts.key, opts.transposition);
    this.concertIv = { letters: 0, semis: concertOffset(opts.key) };
  }

  chord(chart: Chord): ShownChord {
    const shown = transposeChord(chart, this.dk.iv, this.dk.preferFlats);
    return {
      chart,
      shown,
      symbol: this.opts.romanOnly ? romanNumeral(chart, this.opts.notation) : chordSymbol(shown, this.opts.notation),
      roman: romanNumeral(chart, this.opts.notation),
      quality: chart.quality,
      guide: guideTones(shown, this.dk.preferFlats),
    };
  }

  bar(bar: string): ShownChord[] {
    return parseBar(bar).map((c) => this.chord(c));
  }

  symbols(bar: string): string {
    return this.bar(bar).map((c) => c.symbol).join('  ');
  }

  /** Concert-pitch chords for playback (only pitch classes matter). */
  concert(bar: string): Chord[] {
    return parseBar(bar).map((c) => transposeChord(c, this.concertIv));
  }
}

// ---------------------------------------------------------------- flowchart / mixing

export interface FlowOption {
  bar: string;
  variations: number[];
}

/** For each bar, every distinct option on the chart, simplest (earliest) first. */
export const FLOW: FlowOption[][] = Array.from({ length: 12 }, (_, i) => {
  const map = new Map<string, number[]>();
  for (const v of VARIATIONS) {
    const list = map.get(v.bars[i]) ?? [];
    list.push(v.id);
    map.set(v.bars[i], list);
  }
  const mean = (xs: number[]) => xs.reduce((s, x) => s + x, 0) / xs.length;
  return [...map.entries()]
    .map(([bar, variations]) => ({ bar, variations }))
    .sort((a, b) => mean(a.variations) - mean(b.variations));
});

export function sourcesOf(barIndex: number, bar: string): number[] {
  return FLOW[barIndex].find((o) => o.bar === bar)?.variations ?? [];
}

const DIGITS = '0123456789abcdefghijklmnopqrstuvwxyz';

export function encodeMix(bars: string[]): string {
  return bars.map((b, i) => DIGITS[FLOW[i].findIndex((o) => o.bar === b)]).join('');
}

export function decodeMix(code: string): string[] | null {
  if (code.length !== 12) return null;
  const bars = [...code].map((ch, i) => FLOW[i][DIGITS.indexOf(ch)]?.bar);
  return bars.every(Boolean) ? (bars as string[]) : null;
}

/** Split text into plain runs and {{chord}} references. */
export function splitRefs(text: string): Array<{ text: string; chords?: string }> {
  const out: Array<{ text: string; chords?: string }> = [];
  const re = /\{\{(.+?)\}\}/g;
  let last = 0;
  for (let m = re.exec(text); m; m = re.exec(text)) {
    if (m.index > last) out.push({ text: text.slice(last, m.index) });
    out.push({ text: m[1], chords: m[1] });
    last = m.index + m[0].length;
  }
  if (last < text.length) out.push({ text: text.slice(last) });
  return out;
}
