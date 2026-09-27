"""Render the Halation performance to audio.

Instruments
  trumpet  University of Iowa MIS B-flat trumpet (real solo trumpet, mf/ff)
  alto sax Apple GarageBand "Alto Sax" (Yamaha alto samples)
  piano    Apple "Steinway Grand Piano" (4 velocity layers)
  bass     Apple "Upright Jazz Bass" (4 velocity layers)
  drums    Apple Drum Kit Designer "SoCal" kit (ride, hat foot, snare, kick, toms, crashes)

usage: python3 render.py [--seconds N]   (N limits the render for quick tests)
"""
from __future__ import annotations

import argparse
import subprocess
import wave
from pathlib import Path

import numpy as np
import scipy.signal as sig

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import arrange
import tunes
from samples import CACHE, SR, ExsInstrument, stretch, to_stereo

ROOT = Path(__file__).resolve().parents[2]
L = "/Library/Application Support/Logic/Sampler Instruments/"
PIANO_EXS = L + "01 Acoustic Pianos/Steinway Grand Piano 2.exs"
BASS_EXS = L + "02 Bass/01 Acoustic Bass/Upright Jazz Bass.exs"
ALTO_EXS = L + "09 Orchestral/01 Woodwinds/Alto Sax.exs"
KIT_EXS = (L + "03 Drums & Percussion/04 Drum Kit Designer/Drum Kit Designer/Stereo/SoCal Kit.exs")

rng = np.random.default_rng(11)


def db2lin(db):
    return 10 ** (db / 20)


def lowpass(x, fc):
    if fc >= 15000:
        return x
    a = np.exp(-2 * np.pi * fc / SR)
    return sig.lfilter([1 - a], [1, -a], x, axis=0).astype(np.float32)


def place(buf, start_s, audio):
    i = int(round(max(0.0, start_s) * SR))
    if i >= len(buf):
        return
    n = min(len(audio), len(buf) - i)
    buf[i:i + n] += audio[:n]


def rms(x):
    return float(np.sqrt(np.mean(x.astype(np.float64) ** 2)) + 1e-12)


# ------------------------------------------------------------------ horns

def horn_note(x, ratio, dur, gain, flags, legato_in, vib_cents, vib_rate, release):
    ext = 0.30 if ("f" in flags or "d" in flags) else 0.0
    n_out = int((dur + release + ext) * SR)
    t = np.arange(n_out) / SR
    cents = np.zeros(n_out)
    if dur >= 0.42 and vib_cents > 0:
        depth = vib_cents * np.clip((t - 0.20) / 0.35, 0, 1)
        cents += depth * np.sin(2 * np.pi * vib_rate * t + rng.uniform(0, 6.28))
    if "s" in flags:
        cents += -150 * np.clip(1 - t / 0.08, 0, 1) ** 1.5
    if "f" in flags:
        cents += -800 * np.clip((t - dur * 0.8) / 0.32, 0, 1) ** 2
    if "d" in flags:
        cents += 450 * np.clip((t - dur * 0.8) / 0.30, 0, 1) ** 1.5
    rate = ratio * 2 ** (cents / 1200)
    skip = int(0.014 * SR) if legato_in else 0
    y = stretch(x[skip:], rate, n_out)
    env = np.ones(len(y), dtype=np.float32)
    if legato_in:
        k = min(len(env), int(0.010 * SR))
        env[:k] = np.linspace(0.25, 1, k)
    r0 = int(dur * SR)
    if r0 < len(env):
        tail = len(env) - r0
        rel = release + ext
        env[r0:] *= np.exp(-np.arange(tail) / SR / (rel / 4.6)).astype(np.float32)
    return y * env[:, None] * gain


class Trumpet:
    def __init__(self):
        d = np.load(CACHE / "trumpet_notes.npz")
        self.notes = {k: d[k] for k in d.files}

    def render(self, notes, length):
        buf = np.zeros((int(length * SR), 1), np.float32)
        for i, n in enumerate(notes):
            nxt = notes[i + 1] if i + 1 < len(notes) else None
            dur = n.dur
            if nxt and nxt.legato_in and nxt.t - (n.t + n.dur) < 0.05:
                dur = max(dur, nxt.t - n.t + 0.012)          # overlap into the slur
            layer = "ff" if n.db >= -1 else "mf"
            midi = min(max(n.midi, 52), 87 if layer == "ff" else 86)
            key = f"{layer}_{midi}"
            x = self.notes[key][:, None]
            tune = float(self.notes[key + "_tune"])
            ratio = 2 ** ((n.midi - midi - tune) / 12)
            level = db2lin(n.db) * (0.10 / float(self.notes[key + "_rms"])) ** 0.75
            y = horn_note(x, ratio, dur, level, n.flags, n.legato_in, vib_cents=16, vib_rate=5.6,
                          release=0.07)
            fc = np.interp(n.db, [-14, -8, -4, 0], [2600, 4200, 7000, 16000])
            y = lowpass(y, fc)
            for g_i, g in enumerate(n.graces):
                gk = f"mf_{min(max(g, 52), 86)}"
                gy = horn_note(self.notes[gk][:, None], 1.0, 0.045, level * 0.7, "", False, 0, 5, 0.02)
                place(buf, n.t - 0.05 + 0.0 * g_i, gy)
            place(buf, n.t, y)
        return buf


class Alto:
    def __init__(self):
        self.inst = ExsInstrument(ALTO_EXS)
        self.cache = {}

    def render(self, notes, length):
        buf = np.zeros((int(length * SR), 2), np.float32)
        for i, n in enumerate(notes):
            nxt = notes[i + 1] if i + 1 < len(notes) else None
            dur = n.dur
            if nxt and nxt.legato_in and nxt.t - (n.t + n.dur) < 0.05:
                dur = max(dur, nxt.t - n.t + 0.012)
            z = self.inst.candidates(n.midi, 80)[0]
            if id(z) not in self.cache:
                a = self.inst.zone_audio(z, SR * 8)
                self.cache[id(z)] = (a, rms(a[int(0.2 * SR):int(0.8 * SR)]))
            x, r = self.cache[id(z)]
            root = z.key - z.coarse - z.fine / 100      # EXS tuning is added to the pitch
            ratio = 2 ** ((n.midi - root) / 12)
            level = db2lin(n.db) * 0.10 / r
            y = horn_note(x, ratio, dur, level, n.flags, n.legato_in, vib_cents=20, vib_rate=5.2,
                          release=0.09)
            fc = np.interp(n.db, [-14, -8, -4, 0], [2400, 3800, 6500, 15000])
            place(buf, n.t, lowpass(y, fc))
        return buf


# ------------------------------------------------------------------ piano / bass / drums

class Sampled:
    """Velocity-layered EXS instrument; levels normalised per zone."""

    def __init__(self, exs, group_filter=None, transpose=0, release=0.25, curve=1.6):
        self.inst = ExsInstrument(exs, group_filter=group_filter)
        self.transpose, self.release, self.curve = transpose, release, curve
        self.norm = {}

    def zone_level(self, z, a):
        if id(z) not in self.norm:
            head = a[:int(0.25 * SR)]
            self.norm[id(z)] = 0.25 / (np.abs(head).max() + 1e-6)
        return self.norm[id(z)]

    def render(self, notes, length, key_filter=None, gains=None):
        buf = np.zeros((int(length * SR), 2), np.float32)
        for n in notes:
            key = n.midi + self.transpose
            vel = int(min(127, max(1, n.vel)))
            zs = self.inst.candidates(key, vel)
            if key_filter:
                zs = [z for z in zs if key_filter(key, self.inst.groups[z.group])]
            if not zs:
                continue
            z = zs[int(rng.integers(len(zs)))]
            ratio = 1.0
            if z.pitch and not z.oneshot:
                ratio = 2 ** ((key - (z.key - z.coarse - z.fine / 100)) / 12)   # tuning adds
            frames = int((n.dur + self.release + 0.1) * SR * ratio) + 64
            if z.oneshot:
                frames = int(3.0 * SR)
            a = self.inst.zone_audio(z, frames)
            lvl = self.zone_level(z, a) * (vel / 127) ** self.curve * db2lin(n.db)
            if gains:
                lvl *= gains.get(n.midi, 1.0)
            y = stretch(a, ratio, int(len(a) / ratio)) if ratio != 1.0 else a
            if z.oneshot:                     # sample ends are hard cuts: fade the last 25%
                k = max(1, len(y) // 4)
                y = y.copy()
                y[-k:] *= np.linspace(1, 0, k, dtype=np.float32)[:, None] ** 2
            else:
                end = int(n.dur * SR)
                if end < len(y):
                    tail = len(y) - end
                    env = np.ones(len(y), np.float32)
                    env[end:] = np.exp(-np.arange(tail) / SR / (self.release / 4.6))
                    y = y * env[:, None]
                y = y[:end + int(self.release * SR)]
            place(buf, n.t, y * lvl)
        return buf


# ------------------------------------------------------------------ mix

def reverb_ir(seconds=2.2, rt60=1.35, predelay=0.014):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = np.zeros((n, 2), np.float32)
    decay = np.exp(-6.9 * t / rt60)
    for ch in range(2):
        noise = rng.standard_normal(n).astype(np.float32)
        noise = lowpass(noise[:, None], 6500)[:, 0]
        ir[:, ch] = noise * decay
    p = int(predelay * SR)
    ir = np.vstack([np.zeros((p, 2), np.float32), ir])
    for d, g in [(0.007, 0.5), (0.013, 0.35), (0.021, 0.3), (0.029, 0.22)]:   # early reflections
        k = p + int(d * SR)
        ir[k, 0] += g
        ir[k + int(0.0023 * SR), 1] += g
    return ir / np.sqrt((ir ** 2).sum(axis=0, keepdims=True)) * 0.9


def pan_mono(x, pan):
    """x [n,1] -> [n,2], constant power, pan -1..1"""
    th = (pan + 1) * np.pi / 4
    return np.hstack([x * np.cos(th), x * np.sin(th)]).astype(np.float32)


def shape_stereo(x, width, pan):
    mid = (x[:, 0] + x[:, 1]) / 2
    side = (x[:, 0] - x[:, 1]) / 2 * width
    th = (pan + 1) * np.pi / 4
    left = mid * np.cos(th) * np.sqrt(2) + side
    right = mid * np.sin(th) * np.sqrt(2) - side
    return np.stack([left, right], axis=1).astype(np.float32)


def active_rms(x):
    m = np.abs(x).max(axis=1)
    win = int(0.05 * SR)
    n = len(m) // win
    blocks = np.sqrt((x[:n * win] ** 2).mean(axis=1).reshape(n, win).mean(axis=1))
    act = blocks[blocks > blocks.max() * db2lin(-40)]
    return float(np.sqrt(np.mean(act ** 2))) if len(act) else 1e-6


def compress(x, thresh_db=-20, ratio=2.0, attack=0.01, release=0.15):
    win = int(0.01 * SR)
    n = len(x) // win + 1
    pad = np.zeros((n * win, x.shape[1]), np.float32)
    pad[:len(x)] = x
    level = np.sqrt((pad ** 2).mean(axis=1).reshape(n, win).mean(axis=1)) + 1e-9
    db = 20 * np.log10(level)
    over = np.maximum(0, db - thresh_db)
    gr = -over * (1 - 1 / ratio)
    # smooth: fast attack, slower release
    sm = np.zeros_like(gr)
    a_att = np.exp(-0.01 / attack)
    a_rel = np.exp(-0.01 / release)
    g = 0.0
    for i, target in enumerate(gr):
        coef = a_att if target < g else a_rel
        g = coef * g + (1 - coef) * target
        sm[i] = g
    gain = np.repeat(db2lin(sm), win)[:len(x)]
    return x * gain[:, None].astype(np.float32)


def write_wav(path, x):
    y = np.clip(x, -1, 1)
    pcm = (y * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tune", choices=sorted(tunes.ALL))
    ap.add_argument("--seconds", type=float, default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--stems", action="store_true")
    args = ap.parse_args()

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    tune = tunes.ALL[args.tune]
    if args.out is None:
        args.out = str(ROOT / 'trial_recordings' / 'output' / (tune.name.replace(' ', '_') + '_band_trumpet_alto'))
    perf = arrange.build(tune)
    print('arrangement:', perf['info'])
    length = perf["length"] if args.seconds is None else args.seconds
    if args.seconds:
        for k in ("trumpet", "alto", "piano", "bass", "drums"):
            perf[k] = [n for n in perf[k] if n.t < args.seconds]

    print("rendering trumpet...")
    tpt = Trumpet().render(perf["trumpet"], length)
    print("rendering alto sax...")
    alto = Alto().render(perf["alto"], length)
    print("rendering piano...")
    piano = Sampled(PIANO_EXS, group_filter=lambda g: not g.name.startswith("p"), release=0.22,
                    curve=1.5).render(perf["piano"], length)
    print("rendering bass...")
    bass = Sampled(BASS_EXS, group_filter=lambda g: not g.name.startswith("NOTE"), transpose=12,
                   release=0.07, curve=1.1).render(perf["bass"], length)
    print("rendering drums...")
    hh_ok = lambda key, g: (not g.name.startswith("AnKit2:HH:o")) or g.name.startswith("AnKit2:HH:o1")
    piece = {99: 1.0, 51: 1.0, 53: 0.9, 33: 0.55, 36: 0.9, 38: 0.55, 49: 0.6, 57: 0.6,
             43: 0.6, 47: 0.6, 48: 0.6}
    kit_notes = [n for n in perf["drums"]]
    for n in kit_notes:
        if n.midi == 51:
            n.midi = 99                      # ride bow articulation with 41 layers
    drums = Sampled(KIT_EXS, curve=1.8).render(kit_notes, length, key_filter=hh_ok, gains=piece)

    # ---- balance: active-level targets relative to the trumpet
    targets = {"tpt": 0.0, "alto": -0.5, "piano": -7.5, "bass": -4.0, "drums": -6.5}
    tracks = {"tpt": pan_mono(tpt, -0.22), "alto": shape_stereo(alto, 0.25, 0.22),
              "piano": shape_stereo(piano, 0.75, 0.12), "bass": pan_mono(bass.mean(axis=1, keepdims=True), 0.0),
              "drums": shape_stereo(drums, 0.85, -0.03)}
    ref = active_rms(tracks["tpt"])
    for k, x in tracks.items():
        g = ref * db2lin(targets[k]) / active_rms(x)
        tracks[k] = x * g
        print(f"  {k:<6} gain {20 * np.log10(g):6.1f} dB")
    if args.stems:
        for k, x in tracks.items():
            write_wav(f"{args.out}_{k}.wav", x / (np.abs(x).max() + 1e-9) * 0.9)

    sends = {"tpt": 0.26, "alto": 0.24, "piano": 0.18, "bass": 0.05, "drums": 0.12}
    dry = sum(tracks.values())
    send = sum(tracks[k] * s for k, s in sends.items())
    ir = reverb_ir()
    wet = np.stack([sig.fftconvolve(send[:, c], ir[:, c])[:len(send)] for c in range(2)], axis=1)
    mix = dry + wet.astype(np.float32)
    mix = sig.sosfilt(sig.butter(2, 32, "hp", fs=SR, output="sos"), mix, axis=0).astype(np.float32)
    mix = compress(mix / (np.abs(mix).max() + 1e-9) * 0.7, thresh_db=-19, ratio=1.8)
    # loudness: aim for ~ -16 dBFS RMS, then a soft limiter at -1 dBFS
    mix *= db2lin(-16) / rms(mix)
    ceiling = db2lin(-1.0)
    over = np.abs(mix) > ceiling * 0.8
    mix = np.where(over, np.sign(mix) * (ceiling * 0.8 + (ceiling * 0.2) *
                                          np.tanh((np.abs(mix) - ceiling * 0.8) / (ceiling * 0.2))), mix)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    wav = Path(args.out + ".wav")
    write_wav(wav, mix)
    mp3 = Path(args.out + ".mp3")
    subprocess.run(["lame", "--quiet", "-V", "1", "--tt", f"{tune.name} (trial recording)", "--ta", "AI jazz tune trial",
                    str(wav), str(mp3)], check=True)
    peak = 20 * np.log10(np.abs(mix).max())
    print(f"wrote {mp3}  length {len(mix) / SR:.1f}s  peak {peak:.1f} dBFS  rms {20 * np.log10(rms(mix)):.1f} dBFS")


if __name__ == "__main__":
    main()
