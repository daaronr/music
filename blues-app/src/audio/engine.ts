// Real-time playback: a look-ahead scheduler on the Web Audio clock, feeding
// the shared Arranger. The UI supplies the chords bar by bar (so switching
// form, key or a mixed bar while playing takes effect at the next bar) and
// receives beat positions timed to what is actually heard.

import { Soundfont } from 'smplr';
import { Arranger, DEFAULT_SETTINGS, type ArrangerSettings, type DrumHit, type NoteEvent, type Part } from '../music/arranger.ts';
import type { Chord } from '../music/theory.ts';
import {
  BASS,
  DRUMS,
  DRUM_DECAY,
  DRUM_HIGHPASS,
  DRUM_LEVEL,
  DRUM_RATE,
  MIX,
  PIANO,
  highpassInPlace,
  nearestSample,
  normalizeInPlace,
} from './samples.ts';

export type KeysSound = 'piano' | 'epiano' | 'guitar' | 'organ';
export const KEYS_SOUNDS: Record<KeysSound, string> = {
  piano: 'Grand piano',
  epiano: 'Electric piano',
  guitar: 'Jazz guitar',
  organ: 'Organ',
};
const GM_NAMES: Record<Exclude<KeysSound, 'piano'>, string> = {
  epiano: 'electric_piano_1',
  guitar: 'electric_guitar_jazz',
  organ: 'drawbar_organ',
};

export interface BarPlan<T = unknown> {
  chords: Chord[]; // concert pitch
  next: Chord;
  tag: T; // passed back with positions, e.g. which form and bar this is
}

export interface Position<T = unknown> {
  countIn: boolean;
  chorus: number;
  bar: number; // 0-11
  beat: number; // 0-3
  tag: T | null;
}

interface Pitched {
  midi: number;
  buffer: AudioBuffer;
}

const LOOKAHEAD = 0.15;
const TICK_MS = 25;

function preferredFormat(): 'ogg' | 'm4a' {
  const a = typeof Audio !== 'undefined' ? new Audio() : null;
  return a && a.canPlayType('audio/ogg; codecs="opus"') && a.canPlayType('audio/ogg; codecs="vorbis"') ? 'ogg' : 'm4a';
}

async function fetchArrayBuffer(url: string): Promise<ArrayBuffer> {
  try {
    const cache = await caches.open('blues-flow-samples-v1');
    const hit = await cache.match(url);
    if (hit) return hit.arrayBuffer();
    const res = await fetch(url);
    if (!res.ok) throw new Error(`${res.status} ${url}`);
    await cache.put(url, res.clone());
    return res.arrayBuffer();
  } catch {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`${res.status} ${url}`);
    return res.arrayBuffer();
  }
}

function impulseResponse(ctx: AudioContext, seconds = 1.6): AudioBuffer {
  const n = Math.round(ctx.sampleRate * seconds);
  const ir = ctx.createBuffer(2, n, ctx.sampleRate);
  for (let ch = 0; ch < 2; ch++) {
    const d = ir.getChannelData(ch);
    let lp = 0;
    for (let i = 0; i < n; i++) {
      lp = lp * 0.6 + (Math.random() * 2 - 1) * 0.4; // soften the top end
      d[i] = lp * Math.exp((-4 * i) / n);
    }
  }
  return ir;
}

export class Engine<T = unknown> {
  ctx: AudioContext | null = null;
  tempo = 120;
  settings: ArrangerSettings = { ...DEFAULT_SETTINGS };
  countInEnabled = true;

  planBar: (chorus: number, bar: number) => BarPlan<T> = () => {
    throw new Error('planBar not set');
  };
  onPosition: (p: Position<T> | null) => void = () => {};
  onLoading: (fraction: number | null) => void = () => {};

  private buses = {} as Record<Part, GainNode>;
  private levels: Record<Part, number> = { keys: 1, bass: 1, drums: 1 };
  private piano: Pitched[] = [];
  private bass: Pitched[] = [];
  private drums = {} as Record<DrumHit, AudioBuffer[]>;
  private gm: Partial<Record<KeysSound, Soundfont>> = {};
  private keysSound: KeysSound = 'piano';
  private ready: Promise<void> | null = null;

  private arranger = new Arranger(Date.now() % 100000);
  private auditioner = new Arranger(17);
  private timer: number | null = null;
  private nextBeatTime = 0;
  private beatCount = 0;
  private countInBeats = 0;
  private pending: NoteEvent[] = [];
  private currentTag: T | null = null;
  private uiQueue: Array<{ time: number; pos: Position<T> }> = [];
  private raf: number | null = null;
  private voices = new Set<{ src: AudioScheduledSourceNode; gain: GainNode }>();
  private auditionVoices = new Set<{ src: AudioScheduledSourceNode; gain: GainNode }>();
  private drumTurn = 0;

  get playing() {
    return this.timer !== null;
  }

  connect(handlers: Pick<Engine<T>, 'planBar' | 'onPosition' | 'onLoading'>) {
    this.planBar = handlers.planBar;
    this.onPosition = handlers.onPosition;
    this.onLoading = handlers.onLoading;
  }

  /** Tempo and feel; changes apply from the next beat (tempo) or bar (feel). */
  configure(o: { tempo: number; settings: ArrangerSettings; countIn: boolean }) {
    this.tempo = o.tempo;
    this.settings = o.settings;
    this.countInEnabled = o.countIn;
  }

  /** Create the audio graph and load the default sounds. Call from a user gesture. */
  ensureReady(): Promise<void> {
    if (!this.ctx) {
      const nav = navigator as Navigator & { audioSession?: { type: string } };
      if (nav.audioSession) nav.audioSession.type = 'playback'; // play through the iPhone silent switch
      this.ctx = new AudioContext({ latencyHint: 'interactive' });
      this.buildGraph();
    }
    void this.ctx.resume();
    if (!this.ready) this.ready = this.loadAll().catch((err) => {
      this.ready = null;
      throw err;
    });
    return this.ready;
  }

  private buildGraph() {
    const ctx = this.ctx!;
    const comp = ctx.createDynamicsCompressor();
    comp.threshold.value = -14;
    comp.ratio.value = 3;
    comp.attack.value = 0.01;
    comp.release.value = 0.2;
    const master = ctx.createGain();
    master.gain.value = 0.9;
    master.connect(comp).connect(ctx.destination);
    const verb = ctx.createConvolver();
    verb.buffer = impulseResponse(ctx);
    const verbOut = ctx.createGain();
    verbOut.gain.value = 0.9;
    verb.connect(verbOut).connect(master);
    for (const part of ['keys', 'bass', 'drums'] as Part[]) {
      const bus = ctx.createGain();
      bus.gain.value = MIX[part].gain * this.levels[part];
      const pan = ctx.createStereoPanner();
      pan.pan.value = MIX[part].pan;
      const send = ctx.createGain();
      send.gain.value = MIX[part].send;
      bus.connect(pan).connect(master);
      pan.connect(send).connect(verb);
      this.buses[part] = bus;
    }
  }

  private async loadAll() {
    const ctx = this.ctx!;
    const ext = preferredFormat();
    const jobs: Array<() => Promise<void>> = [];
    const decode = async (url: string) => {
      let buf: AudioBuffer;
      try {
        buf = await ctx.decodeAudioData(await fetchArrayBuffer(`${url}.${ext}`));
      } catch {
        buf = await ctx.decodeAudioData(await fetchArrayBuffer(`${url}.m4a`));
      }
      return buf;
    };
    const channels = (b: AudioBuffer) => Array.from({ length: b.numberOfChannels }, (_, i) => b.getChannelData(i));
    const piano: Pitched[] = [];
    const bass: Pitched[] = [];
    for (const s of PIANO) jobs.push(async () => {
      const buffer = await decode(s.url);
      normalizeInPlace(channels(buffer));
      piano.push({ midi: s.midi, buffer });
    });
    for (const s of BASS) jobs.push(async () => {
      const buffer = await decode(s.url);
      normalizeInPlace(channels(buffer));
      bass.push({ midi: s.midi, buffer });
    });
    const drums = {} as Record<DrumHit, AudioBuffer[]>;
    for (const [hit, urls] of Object.entries(DRUMS) as Array<[DrumHit, string[]]>) {
      drums[hit] = [];
      urls.forEach((url, i) => jobs.push(async () => {
        const buffer = await decode(url);
        for (const ch of channels(buffer)) highpassInPlace(ch, buffer.sampleRate, DRUM_HIGHPASS[hit]);
        normalizeInPlace(channels(buffer));
        drums[hit][i] = buffer;
      }));
    }
    let done = 0;
    this.onLoading(0);
    await Promise.all(jobs.map((job) => job().then(() => this.onLoading(++done / jobs.length))));
    this.piano = piano.sort((a, b) => a.midi - b.midi);
    this.bass = bass.sort((a, b) => a.midi - b.midi);
    this.drums = drums;
    this.onLoading(null);
  }

  async setKeysSound(sound: KeysSound) {
    this.keysSound = sound;
    if (sound === 'piano' || !this.ctx || this.gm[sound]) return;
    this.onLoading(0);
    const inst = new Soundfont(this.ctx, { instrument: GM_NAMES[sound], kit: 'FluidR3_GM', destination: this.buses.keys });
    this.gm[sound] = inst;
    try {
      await inst.load;
    } finally {
      this.onLoading(null);
    }
  }

  setLevel(part: Part, level: number) {
    this.levels[part] = level;
    if (this.ctx) this.buses[part].gain.setTargetAtTime(MIX[part].gain * level, this.ctx.currentTime, 0.03);
  }

  // ---------------------------------------------------------------- transport

  async start() {
    await this.ensureReady();
    if (this.playing) return;
    const ctx = this.ctx!;
    this.arranger.reset(Math.floor(Math.random() * 1e6));
    this.countInBeats = this.countInEnabled ? 4 : 0;
    this.beatCount = 0;
    this.pending = [];
    this.uiQueue = [];
    this.nextBeatTime = ctx.currentTime + 0.12;
    this.timer = window.setInterval(() => this.tick(), TICK_MS);
    this.tick();
    const frame = () => {
      this.flushUi();
      this.raf = requestAnimationFrame(frame);
    };
    this.raf = requestAnimationFrame(frame);
  }

  stop() {
    if (this.timer !== null) clearInterval(this.timer);
    if (this.raf !== null) cancelAnimationFrame(this.raf);
    this.timer = null;
    this.raf = null;
    this.uiQueue = [];
    this.silence(this.voices);
    for (const inst of Object.values(this.gm)) inst?.stop();
    this.onPosition(null);
  }

  private silence(set: Set<{ src: AudioScheduledSourceNode; gain: GainNode }>) {
    if (!this.ctx) return;
    const now = this.ctx.currentTime;
    for (const v of set) {
      v.gain.gain.cancelScheduledValues(now);
      v.gain.gain.setTargetAtTime(0, now, 0.015);
      try {
        v.src.stop(now + 0.1);
      } catch {
        /* already stopped */
      }
    }
    set.clear();
  }

  private tick() {
    const ctx = this.ctx!;
    this.flushUi(); // animation frames pause in hidden tabs; this keeps positions flowing
    while (this.nextBeatTime < ctx.currentTime + LOOKAHEAD) {
      this.scheduleBeat(this.nextBeatTime);
      this.nextBeatTime += 60 / this.tempo;
      this.beatCount++;
    }
  }

  private scheduleBeat(t: number) {
    const spb = 60 / this.tempo;
    const i = this.beatCount;
    let pos: Position<T>;
    if (i < this.countInBeats) {
      if (i === 0) this.pending = this.arranger.countIn(this.countInBeats);
      pos = { countIn: true, chorus: 0, bar: 0, beat: i, tag: null };
      this.playDue(i, t, spb);
    } else {
      const k = i - this.countInBeats;
      const barIndex = Math.floor(k / 4);
      const beat = k % 4;
      const chorus = Math.floor(barIndex / 12);
      const bar = barIndex % 12;
      if (beat === 0) {
        const plan = this.planBar(chorus, bar);
        this.currentTag = plan.tag;
        this.pending = this.arranger.bar({ chords: plan.chords, next: plan.next, chorusStart: bar === 0 }, this.settings);
      }
      pos = { countIn: false, chorus, bar, beat, tag: this.currentTag };
      this.playDue(beat, t, spb);
    }
    this.uiQueue.push({ time: t, pos });
  }

  private playDue(beat: number, t: number, spb: number) {
    for (const e of this.pending) {
      if (e.beat >= beat && e.beat < beat + 1) {
        const jitter = e.part === 'bass' ? 0 : (Math.random() - 0.5) * 0.008;
        this.play(e, t + (e.beat - beat) * spb + jitter, spb, this.voices);
      }
    }
  }

  private flushUi() {
    const ctx = this.ctx;
    if (!ctx) return;
    const heard = ctx.currentTime - (ctx.outputLatency || ctx.baseLatency || 0);
    let latest: Position<T> | null = null;
    while (this.uiQueue.length && this.uiQueue[0].time <= heard) latest = this.uiQueue.shift()!.pos;
    if (latest) this.onPosition(latest);
  }

  /** Play one bar's chords right away (clicking a bar). */
  async audition(chords: Chord[]) {
    await this.ensureReady();
    const ctx = this.ctx!;
    this.silence(this.auditionVoices);
    const spb = 60 / Math.max(this.tempo, 90);
    const t = ctx.currentTime + 0.03;
    for (const e of this.auditioner.audition(chords)) this.play(e, t + e.beat * spb, spb, this.auditionVoices);
  }

  // ---------------------------------------------------------------- voices

  private play(e: NoteEvent, t: number, spb: number, set: Set<{ src: AudioScheduledSourceNode; gain: GainNode }>) {
    const ctx = this.ctx!;
    if (e.part === 'keys' && this.keysSound !== 'piano') {
      const inst = this.gm[this.keysSound];
      if (inst) inst.start({ note: e.midi, velocity: Math.round(50 + e.vel * 80), time: t, duration: e.dur * spb });
      return;
    }
    let buffer: AudioBuffer;
    let rate = 1;
    let level: number;
    let release: number;
    let decay = 0;
    let hold = e.dur * spb;
    if (e.part === 'keys') {
      const s = nearestSample(this.piano, e.midi);
      if (!s) return;
      buffer = s.buffer;
      rate = 2 ** ((e.midi - s.midi) / 12);
      level = e.vel ** 1.5;
      release = 0.1;
    } else if (e.part === 'bass') {
      const s = nearestSample(this.bass, e.midi);
      if (!s) return;
      buffer = s.buffer;
      rate = 2 ** ((e.midi - s.midi) / 12);
      level = e.vel ** 1.3;
      release = 0.025;
    } else {
      const hit = e.drum!;
      const set = this.drums[hit];
      if (!set?.length) return;
      buffer = set[this.drumTurn++ % set.length];
      rate = DRUM_RATE[hit];
      level = DRUM_LEVEL[hit] * e.vel;
      release = 0.02;
      decay = DRUM_DECAY[hit];
      hold = buffer.duration / rate;
    }
    const src = ctx.createBufferSource();
    src.buffer = buffer;
    src.playbackRate.value = rate;
    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0, t);
    gain.gain.linearRampToValueAtTime(level, t + 0.003);
    if (decay > 0) gain.gain.setTargetAtTime(0, t + 0.003, decay);
    else gain.gain.setTargetAtTime(0, t + hold, release);
    src.connect(gain).connect(this.buses[e.part]);
    src.start(t);
    const end = Math.min(t + buffer.duration / rate, decay > 0 ? t + decay * 6 : t + hold + release * 8);
    src.stop(end);
    const voice = { src, gain };
    set.add(voice);
    src.onended = () => {
      set.delete(voice);
      gain.disconnect();
    };
  }
}
