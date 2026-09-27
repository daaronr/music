// Render all 18 forms to one MP3, a chorus each with a spoken introduction,
// using the same arranger (voicings, walking bass, comping, ride) as the app.
//
//   node scripts/render-tour.ts [--tempo 126] [--key F] [--out public/audio/blues-18-forms.mp3] [--voice kokoro|say]
//
// Needs ffmpeg. Narration uses the local Kokoro setup from
// ~/githubs/claude_code_misc_work/brass_playing_next_step (falls back to macOS `say`).
// Samples and speech are cached in .cache/tour/.

import { execFileSync, spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { Arranger, type DrumHit, type NoteEvent } from '../src/music/arranger.ts';
import { VARIATIONS } from '../src/music/progressions.ts';
import { concertOffset, parseBar, transposeChord, type Chord } from '../src/music/theory.ts';
import { BASS, DRUMS, DRUM_DECAY, DRUM_HIGHPASS, DRUM_LEVEL, DRUM_RATE, MIX, PIANO, highpassInPlace, nearestSample, normalizeInPlace } from '../src/audio/samples.ts';

const SR = 44100;
const APP = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const CACHE = join(APP, '.cache', 'tour');
mkdirSync(join(CACHE, 'samples'), { recursive: true });

const args = new Map<string, string>();
for (let i = 2; i < process.argv.length; i += 2) args.set(process.argv[i].replace(/^--/, ''), process.argv[i + 1]);
const TEMPO = Number(args.get('tempo') ?? 126);
const KEY = args.get('key') ?? 'F';
const OUT = resolve(APP, args.get('out') ?? 'public/audio/blues-18-forms.mp3');
const VOICE = args.get('voice') ?? 'kokoro';

// ---------------------------------------------------------------- narration

const NUMBER_WORDS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven',
  'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen'];

const INTRO_SPEECH =
  'Eighteen ways through a twelve-bar blues, in the key of F. Each form is played once, after a one-bar count. ' +
  'They start with three chords and get steadily more adventurous.';

// Chord names are for the key of F, spelled out for the speech engine.
const FORM_SPEECH: Record<number, string> = {
  1: 'The basic blues. F seven, B-flat seven, and C seven.',
  2: 'Bar ten steps down from C seven to B-flat seven, and bar twelve turns around on C seven.',
  3: 'The quick change to B-flat seven in bar two, and G seven, the five of five, in bar nine.',
  4: 'D seven in bar eight starts a chain of dominants: D seven, G seven, C seven, F seven.',
  5: 'G minor seven in bar nine makes a two-five, and bar twelve becomes a quick two-five turnaround.',
  6: 'E-flat seven in bar six, the four of four. And D-flat seven, a tritone substitute, in bars nine and twelve.',
  7: 'Two-fives everywhere: C minor to F seven in bar four, A minor to D seven in bar eight, and a three-six-two-five turnaround.',
  8: 'Bar seven swaps F seven for A minor, so bars seven to ten walk three, six, two, five, one chord per bar.',
  9: 'Dominant sevenths sliding down in half steps: F seven, E seven, E-flat seven, D seven, into G minor.',
  10: 'The Bird blues. F major seven, two-fives falling by whole steps, a diminished chord in bar six, and a tritone-substitute two-five in bar ten.',
  11: 'Minor seventh chords falling in half steps: two per bar, then one per bar, then two per bar again.',
  12: 'F major seven, B-flat major seven, then F-sharp minor to B seven, a tritone-substitute two-five into bar five.',
  13: 'Two-fives to distant keys: A-flat major in bar seven, G-flat major in bar nine.',
  14: "Close to Charlie Parker's Blues for Alice.",
  15: 'Like fourteen, but with F-sharp minor to B seven in bar four, and E seven pointing at A minor in bar six.',
  16: 'A chain of two-fives from the very first bar. The tonic never really arrives.',
  17: 'Major seventh chords almost everywhere, sliding down by half steps and whole steps.',
  18: 'Sus chords. Each bar is a minor seventh chord over the bass note a fifth below.',
};

const OUTRO_SPEECH = 'That was all eighteen.';

function speechTexts(): string[] {
  return [
    INTRO_SPEECH,
    ...VARIATIONS.map((v) => `Form ${NUMBER_WORDS[v.id]}. ${FORM_SPEECH[v.id]}`),
    OUTRO_SPEECH,
  ];
}

function renderSpeech(texts: string[]): string[] {
  const dir = join(CACHE, `speech-${VOICE}`);
  mkdirSync(dir, { recursive: true });
  const manifest = join(dir, 'texts.json');
  const files = texts.map((_, i) => join(dir, `speech_${String(i).padStart(3, '0')}.wav`));
  const previous = existsSync(manifest) ? readFileSync(manifest, 'utf8') : '';
  const current = JSON.stringify(texts);
  if (previous === current && files.every(existsSync)) return files;
  writeFileSync(manifest, current);

  if (VOICE === 'kokoro') {
    const tools = join(homedir(), 'githubs/claude_code_misc_work/brass_playing_next_step');
    const python = join(tools, '.venv_kokoro/bin/python');
    if (existsSync(python)) {
      console.log('Narration: Kokoro');
      const r = spawnSync(python, [join(tools, 'render_kokoro_segments.py'), manifest, dir], { stdio: 'inherit' });
      if (r.status === 0 && files.every(existsSync)) return files;
      console.warn('Kokoro failed; falling back to say');
    }
  }
  console.log('Narration: macOS say');
  texts.forEach((text, i) => {
    const aiff = files[i].replace(/\.wav$/, '.aiff');
    execFileSync('say', ['-v', 'Samantha', '-r', '185', '-o', aiff, text]);
    execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', aiff, files[i]]);
  });
  return files;
}

// ---------------------------------------------------------------- audio io

interface Stereo {
  L: Float32Array;
  R: Float32Array;
}

function decode(file: string, normalize = true): Stereo {
  const raw = execFileSync('ffmpeg', ['-loglevel', 'error', '-i', file, '-f', 'f32le', '-ac', '2', '-ar', String(SR), 'pipe:1'], {
    maxBuffer: 1 << 30,
  });
  const inter = new Float32Array(raw.buffer, raw.byteOffset, raw.byteLength / 4);
  const n = inter.length / 2;
  const L = new Float32Array(n);
  const R = new Float32Array(n);
  let peak = 1e-9;
  for (let i = 0; i < n; i++) {
    L[i] = inter[2 * i];
    R[i] = inter[2 * i + 1];
    peak = Math.max(peak, Math.abs(L[i]), Math.abs(R[i]));
  }
  if (normalize) {
    for (let i = 0; i < n; i++) {
      L[i] /= peak;
      R[i] /= peak;
    }
  }
  return { L, R };
}

async function sample(url: string): Promise<Stereo> {
  const file = join(CACHE, 'samples', decodeURIComponent(url.split('/').slice(-2).join('_')).replace(/[^\w.-]+/g, '_') + '.ogg');
  if (!existsSync(file)) {
    const res = await fetch(`${url}.ogg`);
    if (!res.ok) throw new Error(`${res.status} ${url}`);
    writeFileSync(file, Buffer.from(await res.arrayBuffer()));
  }
  return decode(file);
}

// ---------------------------------------------------------------- mixing

class Bus {
  length: number;
  L: Float32Array;
  R: Float32Array;
  sendL: Float32Array;
  sendR: Float32Array;
  constructor(length: number) {
    this.length = length;
    this.L = new Float32Array(length);
    this.R = new Float32Array(length);
    this.sendL = new Float32Array(length);
    this.sendR = new Float32Array(length);
  }

  add(src: Stereo, at: number, o: { rate: number; gain: number; pan: number; hold: number; release: number; decay: number; send: number }) {
    const start = Math.max(0, Math.round(at * SR));
    const attack = 0.003 * SR;
    const holdN = o.hold * SR;
    const relN = Math.max(1, o.release * SR);
    const avail = Math.floor((src.L.length - 2) / o.rate);
    const n = Math.min(avail, Math.ceil(holdN + relN), this.length - start);
    const pl = Math.cos(((o.pan + 1) * Math.PI) / 4) * o.gain;
    const pr = Math.sin(((o.pan + 1) * Math.PI) / 4) * o.gain;
    for (let i = 0; i < n; i++) {
      const pos = i * o.rate;
      const j = Math.floor(pos);
      const f = pos - j;
      let env = i < attack ? i / attack : 1;
      if (i > holdN) env *= Math.max(0, 1 - (i - holdN) / relN);
      if (o.decay > 0) env *= Math.exp(-i / (o.decay * SR));
      const l = (src.L[j] + (src.L[j + 1] - src.L[j]) * f) * env;
      const r = (src.R[j] + (src.R[j + 1] - src.R[j]) * f) * env;
      const k = start + i;
      this.L[k] += l * pl;
      this.R[k] += r * pr;
      this.sendL[k] += l * pl * o.send;
      this.sendR[k] += r * pr * o.send;
    }
  }
}

// Small Schroeder-style room: parallel combs into series all-passes.
function reverb(input: Float32Array, spread: number): Float32Array {
  const out = new Float32Array(input.length);
  const combs = [1116, 1188, 1277, 1356].map((d) => Math.round((d + spread) * (SR / 44100)));
  for (const d of combs) {
    const buf = new Float32Array(d);
    let idx = 0;
    let lp = 0;
    for (let i = 0; i < input.length; i++) {
      const y = buf[idx];
      lp = y * 0.7 + lp * 0.3; // damping
      buf[idx] = input[i] + lp * 0.78;
      out[i] += y * 0.25;
      idx = (idx + 1) % d;
    }
  }
  for (const d of [556, 441].map((x) => x + spread)) {
    const buf = new Float32Array(d);
    let idx = 0;
    for (let i = 0; i < out.length; i++) {
      const b = buf[idx];
      const y = -out[i] + b;
      buf[idx] = out[i] + b * 0.5;
      out[i] = y;
      idx = (idx + 1) % d;
    }
  }
  return out;
}

// ---------------------------------------------------------------- main

const piano = await Promise.all(PIANO.map(async (s) => ({ midi: s.midi, audio: await sample(s.url) })));
const bass = await Promise.all(BASS.map(async (s) => ({ midi: s.midi, audio: await sample(s.url) })));
const drums: Record<string, Stereo[]> = {};
for (const [hit, urls] of Object.entries(DRUMS)) {
  drums[hit] = await Promise.all(urls.map(sample));
  for (const d of drums[hit]) {
    highpassInPlace(d.L, SR, DRUM_HIGHPASS[hit as DrumHit]);
    highpassInPlace(d.R, SR, DRUM_HIGHPASS[hit as DrumHit]);
    normalizeInPlace([d.L, d.R]);
  }
}
console.log('Samples ready');

const spb = 60 / TEMPO;
const iv = { letters: 0, semis: concertOffset(KEY) };
const concert = (bar: string): Chord[] => parseBar(bar).map((c) => transposeChord(c, iv));
let hatTurn = 0;

function renderForm(id: number): Stereo {
  const v = VARIATIONS[id - 1];
  const bars = v.bars.map(concert);
  const arranger = new Arranger(1000 + id);
  const timed: Array<{ e: NoteEvent; t: number }> = [];
  const put = (events: NoteEvent[], bar: number) => events.forEach((e) => timed.push({ e, t: (bar * 4 + e.beat) * spb }));
  put(arranger.countIn(), 0);
  bars.forEach((chords, i) => {
    put(arranger.bar({ chords, next: bars[(i + 1) % 12][0], chorusStart: i === 0 }), i + 1);
  });
  put(arranger.ending(concert(v.ending)[0]), 13);

  const bus = new Bus(Math.ceil((14 * 4 * spb + 2.5) * SR));
  let jitter = 12345 + id;
  const rand = () => ((jitter = (jitter * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff) - 0.5;
  for (const { e, t } of timed) {
    const at = t + (e.part === 'bass' ? 0 : rand() * 0.008);
    if (e.part === 'keys') {
      const s = nearestSample(piano, e.midi);
      bus.add(s.audio, at, { rate: 2 ** ((e.midi - s.midi) / 12), gain: MIX.keys.gain * e.vel ** 1.5, pan: MIX.keys.pan, hold: e.dur * spb, release: 0.3, decay: 0, send: MIX.keys.send });
    } else if (e.part === 'bass') {
      const s = nearestSample(bass, e.midi);
      bus.add(s.audio, at, { rate: 2 ** ((e.midi - s.midi) / 12), gain: MIX.bass.gain * e.vel ** 1.3, pan: MIX.bass.pan, hold: e.dur * spb, release: 0.07, decay: 0, send: MIX.bass.send });
    } else {
      const set = drums[e.drum!];
      const src = set[hatTurn++ % set.length];
      const pan = e.drum === 'hat' ? -0.15 : e.drum === 'click' ? 0 : MIX.drums.pan;
      const hit = e.drum!;
      bus.add(src, at, { rate: DRUM_RATE[hit], gain: MIX.drums.gain * DRUM_LEVEL[hit] * e.vel, pan, hold: 30, release: 0.05, decay: DRUM_DECAY[hit], send: MIX.drums.send });
    }
  }
  const wetL = reverb(bus.sendL, 0);
  const wetR = reverb(bus.sendR, 23);
  for (let i = 0; i < bus.length; i++) {
    bus.L[i] += wetL[i] * 0.9;
    bus.R[i] += wetR[i] * 0.9;
  }
  return { L: bus.L, R: bus.R };
}

function rms(x: Stereo): number {
  let s = 0;
  for (let i = 0; i < x.L.length; i++) s += x.L[i] ** 2 + x.R[i] ** 2;
  return Math.sqrt(s / (2 * x.L.length));
}

const texts = speechTexts();
const speech = renderSpeech(texts).map((f) => decode(f, false));
const forms = VARIATIONS.map((v) => {
  process.stdout.write(`\rRendering form ${v.id}/18`);
  return renderForm(v.id);
});
console.log();

// Balance: narration a little louder (RMS) than the band.
const musicRms = forms.reduce((s, f) => s + rms(f), 0) / forms.length;
for (const s of speech) {
  const g = (musicRms * 1.35) / Math.max(1e-9, rms(s));
  for (let i = 0; i < s.L.length; i++) {
    s.L[i] *= g;
    s.R[i] *= g;
  }
}

const silence = (sec: number): Stereo => ({ L: new Float32Array(Math.round(sec * SR)), R: new Float32Array(Math.round(sec * SR)) });
const timeline: Stereo[] = [silence(0.4), speech[0], silence(0.9)];
const chapters: Array<{ title: string; start: number }> = [{ title: 'Introduction', start: 0 }];
const lengthOf = (parts: Stereo[]) => parts.reduce((s, p) => s + p.L.length, 0);
VARIATIONS.forEach((v, i) => {
  chapters.push({ title: `${v.id}. ${v.name}`, start: lengthOf(timeline) / SR });
  timeline.push(speech[i + 1], silence(0.35), forms[i], silence(0.4));
});
chapters.push({ title: 'End', start: lengthOf(timeline) / SR });
timeline.push(speech[speech.length - 1], silence(1));

const total = lengthOf(timeline);
const inter = new Float32Array(total * 2);
let off = 0;
let peak = 1e-9;
for (const part of timeline) {
  for (let i = 0; i < part.L.length; i++) {
    inter[2 * (off + i)] = part.L[i];
    inter[2 * (off + i) + 1] = part.R[i];
    peak = Math.max(peak, Math.abs(part.L[i]), Math.abs(part.R[i]));
  }
  off += part.L.length;
}
const scale = 0.89 / peak; // -1 dBFS
for (let i = 0; i < inter.length; i++) inter[i] *= scale;

const meta = join(CACHE, 'chapters.txt');
const ms = (s: number) => Math.round(s * 1000);
writeFileSync(
  meta,
  ';FFMETADATA1\ntitle=Blues Flow: 18 ways through a 12-bar blues\nartist=Blues Flow\n' +
    chapters
      .map((c, i) => `[CHAPTER]\nTIMEBASE=1/1000\nSTART=${ms(c.start)}\nEND=${ms(chapters[i + 1]?.start ?? total / SR)}\ntitle=${c.title}\n`)
      .join(''),
);
mkdirSync(dirname(OUT), { recursive: true });
execFileSync(
  'ffmpeg',
  ['-y', '-loglevel', 'error', '-f', 'f32le', '-ar', String(SR), '-ac', '2', '-i', 'pipe:0', '-i', meta, '-map_metadata', '1', '-map_chapters', '1',
    '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', String(SR), '-codec:a', 'libmp3lame', '-q:a', '3', '-id3v2_version', '3', OUT],
  { input: Buffer.from(inter.buffer), maxBuffer: 1 << 30 },
);

const stamp = (s: number) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;
const tracklist = chapters.map((c) => `${stamp(c.start)}  ${c.title}`).join('\n');
writeFileSync(OUT.replace(/\.mp3$/, '.txt'), `Blues Flow: 18 ways through a 12-bar blues (key of ${KEY}, ${TEMPO} bpm)\n\n${tracklist}\n`);
console.log(`Wrote ${OUT} (${stamp(total / SR)})\n${tracklist}`);
