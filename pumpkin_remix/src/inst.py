"""Instruments: synthesized dance drums and synths, plus GarageBand/Logic sampled instruments."""
from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
import soundfile as sf

from dsp import (SR, adsr, butter, db, eq, expdec, fade_edges, mtof, noise, pan, rng, sat, saw,
                 sine, square, sweep)

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "trial_recordings" / "engine"))
from samples import ExsInstrument, stretch  # noqa: E402

L = "/Library/Application Support/Logic/Sampler Instruments/"
DKD = L + "03 Drums & Percussion/04 Drum Kit Designer/"


# ------------------------------------------------------------------ sampled (EXS) instruments

class Exs(ExsInstrument):
    """ExsInstrument that can also read the GarageBand .wav sample files."""

    def _sample_array(self, si):
        if si not in self._loaded:
            rec = self.samples[si]
            path = str(Path(rec.path) / rec.filename)
            if path.lower().endswith(".wav"):
                a, _ = sf.read(path, dtype="float32", always_2d=True)
                self._loaded[si] = a
            else:
                return super()._sample_array(si)
        return self._loaded[si]


class Sampler:
    def __init__(self, exs, group_filter=None, norm=0.3):
        self.inst = Exs(exs, group_filter=group_filter)
        self.norm = norm
        self._lvl = {}

    def note(self, midi, dur, vel=100, release=0.2, max_len=None):
        zs = self.inst.candidates(int(midi), int(vel))
        if not zs:
            zs = self.inst.candidates(int(midi), 100)
        if not zs:
            return np.zeros((1, 2), np.float32)
        want = (dur + release) if max_len is None else max_len
        order = rng.permutation(len(zs))
        for j in order:                       # skip broken/very short regions
            z = zs[int(j)]
            ratio = 1.0
            if z.pitch and not z.oneshot:
                ratio = 2 ** ((midi - (z.key - z.coarse - z.fine / 100)) / 12)
            frames = int((want + 0.05) * SR * ratio) + 64
            a = self.inst.zone_audio(z, frames)
            if len(a) > min(frames, int(0.08 * SR)) * 0.9:
                break
        if id(z) not in self._lvl:
            self._lvl[id(z)] = self.norm / (np.abs(a[:int(0.3 * SR * ratio)]).max() + 1e-6)
        y = stretch(a, ratio, int(len(a) / ratio)) if abs(ratio - 1) > 1e-4 else a
        end = int(dur * SR)
        if end < len(y):
            env = np.ones(len(y), np.float32)
            env[end:] = np.exp(-np.arange(len(y) - end) / SR / max(release / 4.6, 1e-3))
            y = (y * env[:, None])[:end + int(release * SR)]
        y = fade_edges(y, 0.001, 0.01)
        return (y * self._lvl[id(z)] * (vel / 127) ** 1.3).astype(np.float32)


@lru_cache(maxsize=None)
def strings():
    return Sampler(L + "09 Orchestral/09 Strings/String Ensemble.exs")


@lru_cache(maxsize=None)
def brass():
    return Sampler(L + "09 Orchestral/02 Brass/Full Brass Staccato.exs")


@lru_cache(maxsize=None)
def piano():
    return Sampler(L + "01 Acoustic Pianos/Steinway Grand Piano 2.exs",
                   group_filter=lambda g: "No Dampers" not in g.name)


@lru_cache(maxsize=None)
def guitar():
    return Sampler(L + "08 Guitars/Vintage Strat.exs", group_filter=lambda g: "Main" in g.name)


@lru_cache(maxsize=None)
def claps():
    return Sampler(DKD + "Drum Kit Designer Claps/Stereo/AP v1 Claps.exs", group_filter=lambda g: "tight" in g.name)


@lru_cache(maxsize=None)
def tamb():
    return Sampler(DKD + "Drum Kit Designer Tambourine/Stereo/AP v1 Tambourine.exs",
                   group_filter=lambda g: "tempo140" in g.name and "hit" not in g.name)


@lru_cache(maxsize=None)
def shaker():
    return Sampler(DKD + "Drum Kit Designer Shaker/Stereo/AP v1 Shaker.exs",
                   group_filter=lambda g: "tempo140" in g.name and "accent" not in g.name)


@lru_cache(maxsize=None)
def kit():
    return Exs(DKD + "Drum Kit Designer/Stereo/SoCal Kit.exs")


def kit_hit(group_prefix, vel=110, length=3.0):
    k = kit()
    zs = [z for z in k.zones if k.groups[z.group].name.split(":")[1].startswith(group_prefix)
          and k.groups[z.group].vel_lo <= vel <= k.groups[z.group].vel_hi]
    if not zs:
        zs = [z for z in k.zones if k.groups[z.group].name.split(":")[1].startswith(group_prefix)]
    z = zs[int(rng.integers(len(zs)))]
    a = k.zone_audio(z, int(length * SR)).astype(np.float32)
    a = a / (np.abs(a).max() + 1e-6) * 0.5
    return fade_edges(a, 0.0005, 0.2)


# ------------------------------------------------------------------ drums

def kick_house(punch=1.0, length=0.36, tune=52.0):
    n = int(length * SR)
    t = np.arange(n) / SR
    f = tune + 120 * np.exp(-t / 0.026) * punch + 300 * np.exp(-t / 0.0025)
    body = sine(f, n) * expdec(n, 0.16, 0.0008)
    body *= np.clip((length - t) / 0.03, 0, 1)
    click = butter(noise(n), "band", [1500, 7000]) * expdec(n, 0.004) * 0.35
    y = sat(body * 1.15 + click, 2.2)
    return pan(y * 0.9)


def kick_big(length=0.45):
    a = kick_house(punch=1.25, length=length, tune=50.0)
    n = len(a)
    t = np.arange(n) / SR
    sub = sine(50 + 20 * np.exp(-t / 0.05), n) * expdec(n, 0.2, 0.003) * np.clip((length - t) / 0.05, 0, 1)
    top = butter(noise(n), "high", 4000) * expdec(n, 0.012) * 0.25
    return sat(a + pan(sub * 0.35 + top), 1.4)


def k808(midi, dur, glide_to=None, glide_at=None, drive=2.2):
    """808 sub: pitch punch, long decay, optional glide to another note."""
    n = int((dur + 0.08) * SR)
    t = np.arange(n) / SR
    f0 = mtof(midi)
    f = np.full(n, f0)
    if glide_to is not None:
        ga = glide_at if glide_at is not None else dur * 0.6
        g = np.clip((t - ga) / 0.07, 0, 1)
        f = f0 * (mtof(glide_to) / f0) ** g
    f = f * (1 + 1.6 * np.exp(-t / 0.010))
    amp = np.minimum(1, t / 0.002) * np.exp(-t / max(0.9, dur * 0.8))
    amp *= np.clip((dur + 0.08 - t) / 0.06, 0, 1)
    y = sat(sine(f, n) * amp, drive)
    y = butter(y, "low", 1800)
    return pan(y * 0.85)


def clap(tight=True, vel=110):
    s = claps().note(39, 0.6, vel=vel, release=0.2, max_len=0.6)
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    burst = np.zeros(n, np.float32)
    for i, d in enumerate([0, 0.009, 0.018, 0.027]):
        k = int(d * SR)
        burst[k:] += expdec(n - k, 0.006 if i < 3 else 0.11)
    syn = butter(noise(n), "band", [900, 4200]) * burst * 0.5
    out = np.zeros((max(len(s), n), 2), np.float32)
    out[:len(s)] += s * 1.3
    out[:n] += pan(syn)
    return out


def snare_trap():
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    tone = (sine(185 * (1 + 0.5 * np.exp(-t / 0.01)), n) * 0.6 + sine(330, n) * 0.25) * expdec(n, 0.045)
    nz = butter(noise(n), "high", 1800) * expdec(n, 0.16) * 0.55
    y = pan(sat(tone + nz, 1.6))
    c = clap()
    out = np.zeros((max(len(y), len(c)), 2), np.float32)
    out[:len(y)] += y
    out[:len(c)] += c * 0.7
    return out


_HAT_F = np.array([205.3, 304.4, 369.6, 522.7, 540.0, 800.0]) * 1.4


def hat(open_=False, vel=1.0, tone=1.0):
    n = int((0.45 if open_ else 0.09) * SR)
    m = sum(square(f * tone, n) for f in _HAT_F) / 6
    m = butter(m, "band", [6500, 14000]) * 1.6
    m = m + butter(noise(n), "high", 9000) * 0.25
    env = expdec(n, 0.16 if open_ else 0.022, 0.0005)
    return pan(m * env * vel * 0.55, 0.0)


def crash(vel=120):
    a = kit_hit("Cr", vel=vel, length=3.5)
    return butter(a, "high", 400)


def ride(vel=100):
    return kit_hit("Rd", vel=vel, length=2.0)


def snare_ac(vel=110):
    return kit_hit("Sn", vel=vel, length=0.8)


# ------------------------------------------------------------------ synths

DETUNE7 = np.array([-0.191, -0.112, -0.035, 0.0, 0.038, 0.11, 0.187])   # semitones


def supersaw(midi, dur, attack=0.01, release=0.25, spread=1.0, sub=False):
    n = int((dur + release) * SR)
    out = np.zeros((n, 2), np.float32)
    f0 = mtof(midi)
    for k, d in enumerate(DETUNE7 * spread):
        v = saw(f0 * 2 ** (d / 12), n, rng.uniform())
        p = (-0.85, 0.85, -0.55, 0.0, 0.55, -0.25, 0.25)[k]
        out += pan(v, p) * (0.9 if d else 1.0)
    if sub:
        out += pan(sine(f0 / 2, n) * 1.2)
    env = adsr(n, attack, 0.3, 0.85, release, gate=dur)
    return (out * env[:, None] * 0.12).astype(np.float32)


def pluck(midi, dur, bright=1.0, decay=0.18):
    n = int((dur + 0.35) * SR)
    f0 = mtof(midi)
    v = saw(f0, n, rng.uniform()) + saw(f0 * 2 ** (0.08 / 12), n, rng.uniform()) * 0.8 \
        + square(f0 / 2, n) * 0.35
    t = np.arange(n) / SR
    fc = 500 + 7000 * bright * np.exp(-t / decay)
    y = sweep(v, "lp", fc, q=1.1)
    env = adsr(n, 0.002, decay * 1.5, 0.35, 0.25, gate=dur)
    return pan(y * env * 0.32)


def bass_synth(midi, dur, cutoff=900, env_amt=1800, decay=0.12, sub_level=0.8):
    n = int((dur + 0.06) * SR)
    f0 = mtof(midi)
    t = np.arange(n) / SR
    v = saw(f0, n) * 0.7 + square(f0, n, pw=0.4) * 0.3
    y = sweep(v, "lp", cutoff + env_amt * np.exp(-t / decay), q=1.4)
    y = y + sine(f0, n) * sub_level
    env = adsr(n, 0.003, 0.15, 0.8, 0.05, gate=dur)
    return pan(sat(y * env, 1.3) * 0.5)


def pad(midi, dur, attack=0.4, release=0.8, cutoff=2400):
    a = supersaw(midi, dur, attack=attack, release=release, spread=0.7)
    return butter(a, "low", cutoff)


def lead_saw(midi, dur, vib=True):
    n = int((dur + 0.3) * SR)
    t = np.arange(n) / SR
    f = mtof(midi) * 2 ** ((12 * np.clip((t - 0.15) / 0.3, 0, 1) * np.sin(2 * np.pi * 5.5 * t) / 1200) if vib else 1)
    v = saw(f, n) + saw(f * 1.004, n, 0.3) + square(f * 2, n) * 0.2
    v = butter(v, "low", 6000)
    env = adsr(n, 0.004, 0.2, 0.75, 0.2, gate=dur)
    return pan(v * env * 0.22)


# ------------------------------------------------------------------ fx

def riser(dur, f_lo=300, f_hi=9000, curve=2.2):
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    fc = f_lo * (f_hi / f_lo) ** (t ** curve)
    nz = np.stack([noise(n), noise(n)], 1)
    y = sweep(nz, "bp", fc, q=2.0)
    tone = saw(110 * 2 ** (3 * t ** 1.5), n) * 0.15
    tone = butter(tone, "low", 5000)
    y = y + pan(tone)
    return (y * (t ** 1.6)[:, None] * 0.5).astype(np.float32)


def downlifter(dur=2.0):
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    fc = 8000 * (200 / 8000) ** t
    nz = np.stack([noise(n), noise(n)], 1)
    y = sweep(nz, "bp", fc, q=1.5)
    return (y * ((1 - t) ** 2)[:, None] * 0.45).astype(np.float32)


def impact(length=3.0):
    n = int(length * SR)
    t = np.arange(n) / SR
    boom = sine(55 * (1 + 1.2 * np.exp(-t / 0.04)) * np.exp(-t / 2.0) + 30, n) * expdec(n, 0.9, 0.002)
    nz = butter(noise(n), "low", 3000) * expdec(n, 0.25, 0.001) * 0.4
    y = pan(sat(boom + nz, 1.5))
    return butter(y, "high", 25)


def reverse_swell(length=1.875):
    n = int(length * SR)
    c = crash(110)[:n]
    if len(c) < n:
        c = np.vstack([c, np.zeros((n - len(c), 2), np.float32)])
    return c[::-1].copy() * np.linspace(0.2, 1, n)[:, None] ** 2


def vinyl(length, level=0.04):
    n = int(length * SR)
    hiss = butter(noise(n), "band", [800, 6000]) * 0.15
    clicks = np.zeros(n, np.float32)
    idx = rng.integers(0, n, int(length * 9))
    clicks[idx] = rng.uniform(0.3, 1.0, len(idx)) * rng.choice([-1, 1], len(idx))
    clicks = butter(clicks, "band", [1000, 8000]) * 3
    return pan((hiss + clicks) * level)
