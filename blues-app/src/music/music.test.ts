import { describe, expect, it } from 'vitest';
import { VARIATIONS } from './progressions.ts';
import {
  KEYS,
  chordSymbol,
  concertOffset,
  displayKey,
  guideTones,
  mod,
  parseBar,
  pc,
  romanNumeral,
  transposeChord,
  type Chord,
} from './theory.ts';
import { Arranger, BASS_RANGE, VOICING_TOP, voicingCandidates } from './arranger.ts';

const ascii = (s: string) => s.replace(/♭/g, 'b').replace(/♯/g, '#').replace(/−/g, '-');
const barText = (chords: Chord[]) => chords.map((c) => ascii(chordSymbol(c, 'chart'))).join(' ');

function inKey(bar: string, key: string, transposition: 'C' | 'Bb' | 'Eb' = 'C') {
  const dk = displayKey(key, transposition);
  return barText(parseBar(bar).map((c) => transposeChord(c, dk.iv, dk.preferFlats)));
}

describe('chart data', () => {
  it('has 18 forms of 12 bars that all parse', () => {
    expect(VARIATIONS).toHaveLength(18);
    for (const v of VARIATIONS) {
      expect(v.bars).toHaveLength(12);
      for (const bar of v.bars) expect(parseBar(bar).length).toBeGreaterThan(0);
      parseBar(v.ending);
    }
  });

  it('prints back exactly as written in F', () => {
    for (const v of VARIATIONS) for (const bar of v.bars) expect(inKey(bar, 'F')).toBe(bar);
  });

  it('matches the photographed chart in a few hand-checked places', () => {
    const row = (id: number) => VARIATIONS[id - 1].bars;
    expect(row(9).slice(5, 8)).toEqual(['B- E7', 'F7 E7', 'Eb7 D7']);
    expect(row(10).slice(5, 12)).toEqual(['B°', 'A- D7', 'Ab- Db7', 'G- C7', 'Db- Gb7', 'F7 D7', 'G- C7']);
    expect(row(15)[5]).toBe('Bb- E7');
    expect(row(16)[0]).toBe('F#- B7');
    expect(row(17)[11]).toBe('GΔ GbΔ');
    expect(row(18)[7]).toBe('C-/F');
  });

  it('keeps the roman numerals of forms 1-8 that were already right', () => {
    const roman = (id: number) =>
      VARIATIONS[id - 1].bars.map((b) => parseBar(b).map((c) => ascii(romanNumeral(c))).join(' '));
    expect(roman(6)).toEqual(['I7', 'IV7', 'I7', 'I7', 'IV7', 'bVII7', 'I7', 'VI7', 'bVI7', 'V7', 'I7', 'bVI7 V7']);
    expect(roman(8)).toEqual(['I7', 'IV7', 'I7', 'v-7 I7', 'IV7', 'bVII7', 'iii-7', 'VI7', 'ii-7', 'V7', 'iii-7 VI7', 'ii-7 V7']);
    expect(roman(10)[5]).toBe('#iv°7');
    expect(roman(18)[0]).toBe('I9sus');
  });
});

describe('transposition', () => {
  it('keeps letter-based spelling', () => {
    expect(inKey('DbΔ BΔ', 'C')).toBe('AbΔ F#Δ');
    expect(inKey('F#- B7', 'C')).toBe('C#- F#7');
    expect(inKey('Bb7', 'Bb')).toBe('Eb7');
    expect(inKey('B°', 'Bb')).toBe('E°');
    expect(inKey('C-/F', 'Eb')).toBe('Bb-/Eb');
  });

  it('respells awkward names instead of printing double accidentals', () => {
    for (const key of KEYS)
      for (const v of VARIATIONS)
        for (const bar of v.bars) expect(inKey(bar, key)).not.toMatch(/##|bb|E#|B#|Cb|Fb/);
  });

  it('writes parts for transposing instruments', () => {
    expect(displayKey('F', 'Bb').name).toBe('G');
    expect(displayKey('Bb', 'Bb').name).toBe('C');
    expect(displayKey('F', 'Eb').name).toBe('D');
    expect(displayKey('E', 'Bb').name).toBe('F#');
    expect(inKey('F7', 'F', 'Bb')).toBe('G7');
    expect(inKey('Bb7', 'F', 'Eb')).toBe('G7');
  });

  it('spells guide tones', () => {
    const names = (sym: string) => guideTones(parseBar(sym)[0]).map((t) => ascii(t.name));
    expect(names('F7')).toEqual(['A', 'Eb']);
    expect(names('Bb7')).toEqual(['D', 'Ab']);
    expect(names('F#-')).toEqual(['A', 'E']);
    expect(names('C-/F')).toEqual(['Bb', 'Eb']);
  });
});

describe('arranger', () => {
  const concertBars = (bars: string[], key: string) => {
    const iv = { letters: 0, semis: concertOffset(key) };
    return bars.map((b) => parseBar(b).map((c) => transposeChord(c, iv)));
  };

  it('finds a playable voicing for every chord in every key', () => {
    for (const key of KEYS)
      for (const v of VARIATIONS)
        for (const bar of concertBars(v.bars, key))
          for (const chord of bar) {
            const cands = voicingCandidates(chord);
            expect(cands.length).toBeGreaterThan(0);
            for (const c of cands) {
              expect(Math.max(...c)).toBeLessThanOrEqual(VOICING_TOP);
              // Voicings use chord tones plus 9ths and 13ths only.
              const rel = c.map((n) => mod(n - pc(chord.root), 12));
              const allowed: Record<string, number[]> = {
                dom7: [0, 4, 7, 10, 2, 9],
                min7: [0, 3, 7, 10, 2],
                maj7: [0, 4, 7, 11, 2],
                dim7: [0, 3, 6, 9],
                maj: [0, 4, 7],
                sus: [0, 5, 7, 10, 2],
              };
              for (const r of rel) expect(allowed[chord.quality]).toContain(r);
            }
          }
  });

  for (const style of ['walk', 'two'] as const) {
    it(`writes a sensible ${style} bass line for every form in every key`, () => {
      for (const key of KEYS)
        for (const v of VARIATIONS) {
          const bars = concertBars(v.bars, key);
          const arr = new Arranger(v.id * 31 + key.length);
          const bassLine: Array<{ midi: number; downbeatOf?: Chord }> = [];
          for (let chorus = 0; chorus < 3; chorus++)
            bars.forEach((chords, i) => {
              const next = bars[(i + 1) % 12][0];
              const events = arr.bar({ chords, next, chorusStart: i === 0 }, { swing: 0.64, comp: 'swing', bass: style });
              const bass = events.filter((e) => e.part === 'bass').sort((a, b) => a.beat - b.beat);
              for (const e of bass) {
                expect(e.midi).toBeGreaterThanOrEqual(BASS_RANGE[0]);
                expect(e.midi).toBeLessThanOrEqual(BASS_RANGE[1]);
                const seg = chords.length === 2 && e.beat >= 2 ? chords[1] : chords[0];
                const downbeat = e.beat === 0 || (chords.length === 2 && e.beat === 2);
                bassLine.push({ midi: e.midi, downbeatOf: downbeat ? seg : undefined });
              }
              for (const e of events.filter((x) => x.part === 'keys')) {
                expect(e.midi).toBeGreaterThanOrEqual(49);
                expect(e.midi).toBeLessThanOrEqual(VOICING_TOP);
              }
            });
          for (let i = 0; i < bassLine.length; i++) {
            const { midi, downbeatOf } = bassLine[i];
            if (downbeatOf) expect(mod(midi, 12)).toBe(pc(downbeatOf.root));
            if (i > 0) expect(Math.abs(midi - bassLine[i - 1].midi)).toBeLessThanOrEqual(12);
          }
        }
    });
  }
});

describe('typed chords for suggestions', async () => {
  const { parseTypedBar } = await import('./parse.ts');
  const { chartString } = await import('./theory.ts');
  const read = (text: string, key = 'F', t: 'C' | 'Bb' = 'C') => {
    const r = parseTypedBar(text, displayKey(key, t).iv);
    return typeof r === 'string' ? r : r.map(chartString).join(' ');
  };

  it('reads letter names in the key on screen, back into the chart key', () => {
    expect(read('F7')).toBe('F7');
    expect(read('Fm7 Bb7')).toBe('F- Bb7');
    expect(read('B♭maj7')).toBe('BbΔ');
    expect(read('Em7b5 A7')).toBe('Eø A7');
    expect(read('E°7')).toBe('E°');
    expect(read('C−  F7')).toBe('C- F7');
    expect(read('Eb7', 'Bb')).toBe('Bb7'); // IV7 in B♭ is IV7 in F
    expect(read('C7', 'F', 'Bb')).toBe('Bb7'); // written C7 for B♭ trumpet is concert B♭7
  });

  it('reads sus and slash chords', () => {
    expect(read('Cm7/F')).toBe('C-/F');
    expect(read('F7sus4')).toBe('C-/F');
    expect(read('F9sus')).toBe('C-/F');
  });

  it('reads roman numerals', () => {
    expect(read('bVII7')).toBe('Eb7');
    expect(read('#iv°7')).toBe('B°');
    expect(read('ii-7 V7')).toBe('G- C7');
    expect(read('I9sus')).toBe('C-/F');
    expect(read('IΔ7')).toBe('FΔ');
    expect(read('♭VI7 V7')).toBe('Db7 C7');
  });

  it('explains what it cannot read', () => {
    expect(read('H7')).toMatch(/Can't read/);
    expect(read('F7 Bb7 C7')).toMatch(/two chords/);
    expect(read('')).toMatch(/Empty/);
  });

  it('round-trips every chart bar through its own display (same pitches; spelling may differ)', async () => {
    const { chordKey } = await import('./theory.ts');
    for (const key of ['Eb', 'A', 'F'])
      for (const v of VARIATIONS)
        for (const bar of v.bars) {
          const shown = parseBar(bar).map((c) => chordSymbol(transposeChord(c, displayKey(key, 'C').iv), 'standard')).join(' ');
          const back = parseTypedBar(shown, displayKey(key, 'C').iv);
          expect(typeof back === 'string' ? back : back.map(chordKey).join(' ')).toBe(parseBar(bar).map(chordKey).join(' '));
        }
  });
});
