"""The Glory of the Pumpkin (Thanksgiving Disco-Trap Remix).

Arrangement, mix and master.  128 BPM; one sung beat of the 2023 sing-along = two beats here.

  cold open  the original video audio, "...the glory of the pumpkin is the pie", lo-fi, tape stop
  0-8    intro       filtered disco groove on the loop C | A7 | Dm7 | G7
  8-24   verse 1     disco: "Oh a lone pumpkin ... a useful fellow!"
  24-32  break/build piano + strings, "Oh a lone pumpkin" echo, snare build, "but the glory of the pumpkin is the..."
  32-48  drop 1      "PIE!" supersaws, lead plays the hook, vocal chops
  48-64  verse 2     half-time trap: 808s, hat rolls, "So he raised up his head ... Thanksgiving dinner"
  64-72  build 2     "Thanksgiving dinner" chops, back to four-on-the-floor
  72-88  final       full disco: "For the glory of the Jack ... the glory of the pumpkin is the pie"
  88-96  outro       loop, last "pie", the original's final chord
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).parent))
import inst  # noqa: E402
from dsp import (SR, butter, compress, convolve, db, duck_curve, eq, fade_edges, limiter, lufs, pan,  # noqa: E402
                 pingpong, reverb_ir, rng, sat, sweep, width, write_wav)
from harmony import chords_between, root_midi, score_melody, voice  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
W = ROOT / "work"
OUT = ROOT / "output"

BPM = 128.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
SB = 2 * BEAT                       # one sung (score) beat
VMETA = json.load(open(W / "vocal_grid.json"))
VLEAD = VMETA["lead"]

LOOP = ["Cadd9", "A-7", "D-9", "G7"]          # I-vi-ii-V; the song's own bars 18 and 24

# ------------------------------------------------------------------ source audio

vox, _ = sf.read(str(W / "vocal_soft.wav"), dtype="float32", always_2d=True)
orig, osr = sf.read(str(W / "video_audio.wav"), dtype="float32", always_2d=True)
assert osr == SR


def vseg(b0, b1, fin=0.01, fout=0.03):
    """Vocal audio for score beats [b0, b1)."""
    i0 = int((VLEAD + b0 * SB) * SR)
    i1 = int((VLEAD + b1 * SB) * SR)
    return fade_edges(vox[max(0, i0):i1].copy(), fin, fout)


# ------------------------------------------------------------------ cold open

def cold_open():
    a = orig[int(78.05 * SR):int(85.6 * SR)].copy()         # "but the glory of the pumpkin is the pie"
    a = fade_edges(a, 0.02, 0.01)
    n = len(a)
    # tape stop over the last 0.7 s
    k = int(0.7 * SR)
    head, tail = a[:-k], a[-k:]
    rate = np.linspace(1.0, 0.0, k) ** 1.4
    pos = np.cumsum(rate)
    pos = pos[pos < k - 1]
    i = pos.astype(int)
    f = (pos - i)[:, None]
    ts = tail[i] * (1 - f) + tail[i + 1] * f
    ts *= np.linspace(1, 0, len(ts))[:, None] ** 0.5
    a = np.vstack([head, ts])
    # lo-fi: band-limit, mono-ish, crackle
    a = butter(a, "band", [280, 3800])
    a = width(sat(a * 1.6, 1.5), 0.3)
    v = inst.vinyl(len(a) / SR, 0.05)
    return (a + v[:len(a)]) * 0.9


COLD = cold_open()
T0 = len(COLD) / SR + 0.05


def T(bar, beat=0.0):
    return T0 + bar * BAR + beat * BEAT


END = T(96) + 6.0
N = int(END * SR)


# ------------------------------------------------------------------ mixer

class Bus:
    def __init__(self, name):
        self.name = name
        self.x = np.zeros((N, 2), np.float32)

    def add(self, t, a, g_db=0.0):
        i = int(round(t * SR))
        if i < 0:
            a = a[-i:]
            i = 0
        if i >= N or len(a) == 0:
            return
        m = min(len(a), N - i)
        self.x[i:i + m] += a[:m] * db(g_db)


B = {k: Bus(k) for k in ["kick", "drums", "perc", "bass", "sub808", "chords", "strings", "keys",
                          "brass", "lead", "vocal", "chops", "fx", "orig"]}
KICKS = []          # sidechain triggers (four-on-the-floor sections)
K808 = []


# ------------------------------------------------------------------ helpers

def song_chords_score(bar_anchor, beat_anchor, b0, b1):
    """Score chords in [b0,b1) as (t0, t1, name) in song time; score beat_anchor sits at bar_anchor."""
    out = []
    for s, e, name in chords_between(b0, b1):
        out.append((T(bar_anchor) + (s - beat_anchor) * SB, T(bar_anchor) + (e - beat_anchor) * SB, name))
    return out


def loop_chords(bar0, bar1):
    return [(T(b), T(b + 1), LOOP[(b - bar0) % 4]) for b in range(bar0, bar1)]


def chord_at(chords, t):
    for a, b, name in chords:
        if a <= t < b:
            return name
    return chords[-1][2]


# ------------------------------------------------------------------ drum patterns

def house_drums(bar0, bar1, kick=True, clap=True, ohat=True, chat=True, tamb=False, shaker=False,
                big=False, crash_at=(), vel=1.0):
    for bar in range(bar0, bar1):
        for bt in range(4):
            t = T(bar, bt)
            if kick:
                B["kick"].add(t, inst.kick_big() if big else inst.kick_house(), -1)
                KICKS.append(t)
            if clap and bt in (1, 3):
                B["drums"].add(t, inst.clap(vel=110), -5)
            if ohat:
                B["drums"].add(t + BEAT / 2, inst.hat(True, 0.9 * vel), -6)
            for s in range(4):
                if chat and not (ohat and s == 2):
                    v = (0.75, 0.4, 0.9, 0.45)[s] * vel * rng.uniform(0.85, 1.0)
                    B["drums"].add(t + s * BEAT / 4 + rng.normal(0, 0.002), inst.hat(False, v), -8)
                if tamb:
                    v = (0.5, 0.8, 0.6, 1.0)[s]
                    B["perc"].add(t + s * BEAT / 4, inst.tamb().note(54, 0.1, int(70 + 50 * v), max_len=0.3), -10)
                if shaker:
                    B["perc"].add(t + s * BEAT / 4, inst.shaker().note(70, 0.1, int(60 + 40 * (s % 2)), max_len=0.3),
                                  -12)
    for b in crash_at:
        B["drums"].add(T(b), inst.crash(), -6)


def snare_build(bar0, bars=4, g=-6):
    """Quarters, eighths, sixteenths, thirty-seconds, rising in level."""
    divs = [1, 2, 4, 8][-bars:] if bars <= 4 else [1] * (bars - 4) + [1, 2, 4, 8]
    for k, d in enumerate(divs):
        n = 4 * d
        for j in range(n):
            t = T(bar0 + k, j * 4 / n)
            lvl = g - 10 + 10 * ((k * n + j) / (len(divs) * n)) ** 0.7 + 2 * k
            B["drums"].add(t, inst.snare_trap(), lvl)


TRAP_HATS = {
    0: [(s / 2, 1) for s in range(8)],
    1: [(s / 2, 1) for s in range(6)] + [(3 + k / 4, 0.7) for k in range(4)],
    2: [(s / 2, 1) for s in range(8)],
    3: [(s / 2, 1) for s in range(5)] + [(2.5 + k / 6, 0.6) for k in range(3)] + [(3 + k / 8, 0.55 + 0.05 * k) for k in range(8)],
}


def trap_drums(bar0, bar1, chords, roll_end=True):
    for bar in range(bar0, bar1):
        q = (bar - bar0) % 4
        B["drums"].add(T(bar, 2), inst.snare_trap(), -4)
        if q == 3:
            B["drums"].add(T(bar, 3.75), inst.snare_trap(), -12)
        for pos, v in TRAP_HATS[q]:
            B["drums"].add(T(bar, pos), inst.hat(False, v * rng.uniform(0.8, 1.0), tone=1.05), -9)
        if q in (1, 3):
            B["drums"].add(T(bar, 1.5), inst.hat(True, 0.6), -11)
        # 808 pattern: 1, a-of-2 (syncopation), 3-and in odd bars
        hits = [(0.0, 1.4), (1.75, 0.7), (2.5, 0.45)] if q % 2 == 0 else [(0.0, 1.0), (1.0, 0.45), (2.75, 1.1)]
        for pos, dur in hits:
            t = T(bar, pos)
            name = chord_at(chords, t + 0.01)
            r = root_midi(name, lo=31)
            glide = None
            if pos == 2.75:                  # slide up into the next bar's root
                nxt = chord_at(chords, T(bar + 1) + 0.01)
                glide = root_midi(nxt, lo=31)
                if glide == r:
                    glide = r + 12
            B["sub808"].add(t, inst.k808(r, dur * BEAT, glide_to=glide, glide_at=dur * BEAT * 0.6), -3)
            B["kick"].add(t, inst.kick_house(punch=0.7, length=0.25, tune=50), -9)
            K808.append(t)


# ------------------------------------------------------------------ harmonic parts

def disco_bass(chords, g=-4):
    for t0, t1, name in chords:
        r = root_midi(name, lo=33)
        steps = int(round((t1 - t0) / (BEAT / 2)))
        for s in range(steps):
            t = t0 + s * BEAT / 2
            note = r + (12 if s % 2 else 0)
            B["bass"].add(t, inst.bass_synth(note, BEAT * 0.42, cutoff=700, env_amt=2200), g)


def offbeat_bass(chords, g=-3):
    for t0, t1, name in chords:
        r = root_midi(name, lo=33)
        steps = int(round((t1 - t0) / BEAT))
        for s in range(steps):
            B["bass"].add(t0 + s * BEAT + BEAT / 2, inst.bass_synth(r, BEAT * 0.45, cutoff=500, env_amt=1500,
                                                                    decay=0.08, sub_level=1.0), g)


def saw_chords(chords, g=-8, attack=0.01, lo=57, hi=79, sustain=True):
    prev = None
    for t0, t1, name in chords:
        v = voice(name, prev, lo, hi, n=4)
        prev = v
        for m in v:
            B["chords"].add(t0, inst.supersaw(m, (t1 - t0) * 0.98, attack=attack, release=0.2), g)
        B["chords"].add(t0, inst.supersaw(v[0] - 12, (t1 - t0) * 0.98, attack=attack, release=0.2), g - 4)


def string_pads(chords, g=-6, lo=55, hi=76, vel=90):
    prev = None
    for t0, t1, name in chords:
        v = voice(name, prev, lo, hi, n=4)
        prev = v
        for m in v:
            B["strings"].add(t0, inst.strings().note(m, t1 - t0, vel, release=0.5), g)


def string_run(t, start=72, n=8, step=BEAT / 4, g=-8):
    scale = [0, 2, 4, 5, 7, 9, 11]
    pc = start % 12
    k = scale.index(pc) if pc in scale else 0
    oct_ = start - pc
    for j in range(n):
        idx = k + j
        m = oct_ + scale[idx % 7] + 12 * (idx // 7)
        B["strings"].add(t + j * step, inst.strings().note(m, step * 1.6, 110, release=0.15), g)


def brass_stab(t, name, g=-6, dur=0.16, lo=60, hi=80):
    for m in voice(name, None, lo, hi, n=4):
        B["brass"].add(t, inst.brass().note(m, dur, 118, release=0.12), g)


def guitar_scratch(chords, g=-14):
    prev = None
    for t0, t1, name in chords:
        v = voice(name, prev, 62, 76, n=3)
        prev = v
        steps = int(round((t1 - t0) / (BEAT / 4)))
        for s in range(steps):
            if s % 4 in (1, 3) or (s % 8 == 6):
                t = t0 + s * BEAT / 4
                for k, m in enumerate(v):
                    B["keys"].add(t + k * 0.004, inst.guitar().note(m, 0.055, 95 if s % 4 == 1 else 80,
                                                                    release=0.04), g)


def piano_chords(chords, g=-6, rhythm="sustain"):
    prev = None
    for t0, t1, name in chords:
        v = voice(name, prev, 55, 76, n=4)
        prev = v
        bass = root_midi(name, lo=36)
        if rhythm == "sustain":
            for m in v + [bass]:
                B["keys"].add(t0, inst.piano().note(m, t1 - t0, 85, release=0.8), g)
        else:                                   # house stabs on the offbeats
            steps = int(round((t1 - t0) / BEAT))
            for s in range(steps):
                for m in v:
                    B["keys"].add(t0 + s * BEAT + BEAT / 2, inst.piano().note(m, BEAT * 0.3, 100, release=0.15), g)


def arp(chords, g=-14, step=BEAT / 2, lo=72):
    prev = None
    for t0, t1, name in chords:
        v = voice(name, prev, lo, lo + 14, n=4)
        prev = v
        seq = v + v[-2:0:-1]
        steps = int(round((t1 - t0) / step))
        for s in range(steps):
            B["keys"].add(t0 + s * step, inst.piano().note(seq[s % len(seq)], step * 1.5, 70, release=0.4), g)


# ------------------------------------------------------------------ melody

MEL = score_melody()


def melody_notes(b0, b1):
    return [(s, e, m) for s, e, m in MEL if b0 <= s < b1]


def lead_phrase(t_start, b0, b1, transpose=0, g=-8, synth="lead"):
    for s, e, m in melody_notes(b0, b1):
        t = t_start + (s - b0) * SB
        dur = (e - s) * SB * 0.9
        a = inst.lead_saw(m + transpose, dur) if synth == "lead" else inst.pluck(m + transpose, dur)
        B["lead"].add(t, a, g)


# ------------------------------------------------------------------ vocal placement

def vocal_section(b0, b1, bar_anchor, beat_anchor, g=0.0, bus="vocal"):
    t = T(bar_anchor) + (b0 - beat_anchor) * SB
    B[bus].add(t, vseg(b0, b1), g)


def chop(b0, b1, t, g=0.0, bus="chops", reverse=False, semis=0):
    a = vseg(b0, b1, 0.004, 0.02)
    if semis:
        k = 2 ** (semis / 12)
        idx = np.arange(0, len(a) - 1, k)
        i = idx.astype(int)
        f = (idx - i)[:, None]
        a = a[i] * (1 - f) + a[i + 1] * f
    if reverse:
        a = a[::-1].copy()
    B[bus].add(t, a, g)


def hook(t_glory, g=0.0, bus="chops", pie=True, long_pie=False):
    """'(the) glory of the pumpkin is the PIE', built from the clearest takes.

    t_glory = song time of "glo-".  "glory of the pumpkin" is from the last line (score 89-92);
    "is the" from the turkey line (84-85), because the last line's "is the" was sung with a
    big ritardando and is hard to make out; "PIE" from "proud pumpkin pie" (55), or the held
    final "pie" (93) when long_pie."""
    chop(88.95, 91.98, t_glory - 0.05 * SB, g=g, bus=bus)
    chop(83.97, 84.98, t_glory + 3 * SB - 0.03 * SB, g=g, bus=bus)
    if pie:
        if long_pie:
            chop(92.95, 97.2, t_glory + 4 * SB - 0.05 * SB, g=g + 1, bus=bus)
        else:
            chop(54.95, 55.95, t_glory + 4 * SB - 0.05 * SB, g=g + 4, bus=bus)


def stutter(b0, length_beats, t, repeats, g=0.0, step=None):
    step = step or length_beats * BEAT
    a = vseg(b0, b0 + length_beats * BEAT / SB, 0.002, 0.015)
    for k in range(repeats):
        B["chops"].add(t + k * step, a, g - 0.4 * k)


# ================================================================== ARRANGEMENT

B["orig"].add(0.0, COLD, 0)
B["fx"].add(T0 - 2.0 * BAR, inst.riser(2.0 * BAR, 400, 8000), -10)

# ---- intro (0-8)
intro_ch = loop_chords(0, 8)
house_drums(0, 8, clap=False, ohat=True, chat=True)
house_drums(4, 8, kick=False, ohat=False, chat=False, clap=True)
offbeat_bass(loop_chords(0, 8), g=-6)
piano_chords(intro_ch, g=-7, rhythm="stab")
string_pads(loop_chords(4, 8), g=-12)
B["fx"].add(T(0), inst.impact(), -8)
B["drums"].add(T(0), inst.crash(), -6)
chop(1.95, 3.0, T(3, 2), g=-3)                      # "pump-kin"
chop(1.95, 3.0, T(7, 0), g=-3)
B["fx"].add(T(6), inst.riser(2 * BAR, 500, 9000), -14)

# ---- verse 1 (8-24): score beats 0..32, beat 1 at bar 8
v1_ch = song_chords_score(8, 1, 1, 33)
house_drums(8, 24, shaker=True, crash_at=(8, 16))
disco_bass(v1_ch)
string_pads(v1_ch, g=-9)
guitar_scratch(v1_ch)
vocal_section(-0.25, 31.8, 8, 1)
for b in (14.5, 22.5):                              # gaps after "yellow" and "said"
    t = T(8) + (b + 0.0 - 1) * SB
    for k, off in enumerate([0, 1.5, 2.0]):
        brass_stab(t + off * BEAT, chord_at(v1_ch, t + off * BEAT + 0.01), g=-7)
    string_run(T(8) + (b + 1.0 - 1) * SB, start=72, g=-10)
t_fellow = T(8) + (30.0 - 1) * SB
brass_stab(t_fellow, "G7", g=-6, dur=0.3)
B["fx"].add(T(22), inst.downlifter(2 * BAR), -12)
B["drums"].add(T(23, 2), inst.snare_ac(115), -8)
B["drums"].add(T(23, 3), inst.snare_ac(120), -7)
B["drums"].add(T(23, 3.5), inst.snare_ac(125), -6)

# ---- break + build 1 (24-32)
brk_ch = loop_chords(24, 32)
piano_chords(loop_chords(24, 28), g=-5, rhythm="sustain")
string_pads(loop_chords(24, 28), g=-7, vel=100)
string_pads(loop_chords(28, 32), g=-12, vel=90)
B["fx"].add(T(24), inst.impact(), -10)
B["fx"].add(T(24), inst.reverse_swell(BAR)[::-1].copy(), -12)
chop(-0.25, 3.0, T(24) - 0.25 * SB, g=-2, bus="chops")          # "Oh a lone pumpkin" echo
chop(1.95, 3.0, T(26, 0), g=-4)
chop(1.95, 3.0, T(27, 0), g=-6)
house_drums(28, 31, clap=False, ohat=False, chat=False)
house_drums(30, 31, kick=False, ohat=False, chat=True, clap=False)
saw_chords(loop_chords(28, 32), g=-21, attack=0.3)
offbeat_bass(loop_chords(28, 30), g=-9)
snare_build(28, 4, g=-12)
B["fx"].add(T(28), inst.riser(4 * BAR, 300, 11000), -14)
for k in range(4):                                  # "glo-" stutter, bar 28
    chop(89.0, 89.5, T(28, k), g=-6 + k)
for k in range(4):
    chop(89.0, 89.5, T(29, k * 0.5), g=-4 + 0.5 * k, semis=k)
chop(87.85, 88.98, T(29, 2) - 0.15 * SB, g=1.0)                  # "but the"
hook(T(30), g=1.5, pie=False)                                    # "glory of the pumpkin is the..."
B["fx"].add(T(31, 3), inst.reverse_swell(BEAT), -8)

# ---- drop 1 (32-48): B A B A'
drop_ch = loop_chords(32, 48)
house_drums(32, 48, big=True, tamb=False, crash_at=(32, 40))
B["fx"].add(T(32), inst.impact(), -4)
offbeat_bass(drop_ch, g=-2)
saw_chords(drop_ch, g=-9)
for L in range(4):
    b = 32 + 4 * L
    if L % 2 == 0:                                   # B: "PIE!" + lead plays the hook
        chop(54.95, 55.95, T(b) - 0.05 * SB, g=5.0)   # "PIE!" (from "proud pumpkin pie")
        lead_phrase(T(b), 65, 69, g=-7)                # bar 18 melody over C | A7
        lead_phrase(T(b + 2), 89, 93, g=-7)            # bar 24 melody over Dm7 | G7
        stutter(91.0, 0.5, T(b + 3, 2), 4, g=-2)      # "pump-pump-pump-pump"
    else:                                              # A: the vocal sings it
        chop(64.9, 69.0, T(b) - 0.1 * SB, g=0.0)       # "glory of the Jack is in the"
        if L < 3:
            hook(T(b + 2), g=0.0, pie=False)                # "glory of the pumpkin is the"
        else:
            chop(88.9, 91.95, T(b + 2) - 0.1 * SB, g=0.0)  # stop before "is the": "So he" comes in
        lead_phrase(T(b), 65, 69, transpose=12, g=-16, synth="pluck")
        lead_phrase(T(b + 2), 89, 93, transpose=12, g=-16, synth="pluck")
B["fx"].add(T(46), inst.riser(2 * BAR, 600, 9000), -14)

# ---- verse 2, trap (48-64): score beats 32..64, beat 33 at bar 48
v2_ch = song_chords_score(48, 33, 33, 65)
B["fx"].add(T(48), inst.impact(), -6)
B["drums"].add(T(48), inst.crash(), -8)
trap_drums(48, 64, v2_ch)
for t0, t1, name in v2_ch:                         # dark pads
    for m in voice(name, None, 52, 72, n=4):
        B["chords"].add(t0, inst.pad(m, t1 - t0, attack=0.25, release=0.6, cutoff=1500), -9)
arp(v2_ch, g=-17, step=BEAT / 2, lo=74)
vocal_section(31.85, 63.9, 48, 33)
# dark double an octave down (formants kept), quiet, for the trap verse
low_path = W / "vocal_soft_oct_down.wav"
if not low_path.exists():
    import subprocess
    subprocess.run(["/opt/homebrew/bin/rubberband", "-3", "-F", "-q", "-p", "-12",
                    str(W / "vocal_soft.wav"), str(low_path)], check=True)
low_all, _ = sf.read(str(low_path), dtype="float32", always_2d=True)
i0, i1 = int((VLEAD + 31.85 * SB) * SR), int((VLEAD + 63.9 * SB) * SR)
dbl = fade_edges(butter(low_all[i0:i1], "low", 2500), 0.01, 0.05)
B["vocal"].add(T(48) + (31.85 - 33) * SB, dbl, -12)
B["fx"].add(T(62), inst.riser(2 * BAR, 400, 6000), -16)

# ---- build 2 (64-72)
b2a = loop_chords(64, 68)
trap_drums(64, 68, b2a)
for t0, t1, name in b2a:
    for m in voice(name, None, 52, 72, n=4):
        B["chords"].add(t0, inst.pad(m, t1 - t0, attack=0.2, release=0.5, cutoff=1800), -10)
chop(59.4, 62.0, T(64), g=0.0)                    # "Thanksgiving dinner"
chop(59.4, 60.95, T(66), g=-1.0)                   # "Thanksgiving"
chop(59.4, 60.95, T(66, 2), g=-2.0)
chop(61.0, 62.0, T(67), g=0.0)                    # "dinner"
house_drums(68, 71, clap=False, ohat=False, chat=False)
house_drums(70, 71, kick=False, ohat=True, chat=True, clap=True)
string_pads(loop_chords(68, 72), g=-8, vel=105)
saw_chords(loop_chords(68, 72), g=-14, attack=0.4)
snare_build(68, 4, g=-10)
B["fx"].add(T(68), inst.riser(4 * BAR, 300, 12000), -9)
string_run(T(71, 2), start=67, n=8, g=-7)

# ---- final chorus (72-88): score beats 64..97, beat 65 at bar 72
v3_ch = song_chords_score(72, 65, 65, 97)
house_drums(72, 88, tamb=True, crash_at=(72, 80))
B["fx"].add(T(72), inst.impact(), -6)
disco_bass(v3_ch, g=-3)
string_pads(v3_ch, g=-8, vel=105)
saw_chords(v3_ch, g=-13)
guitar_scratch(v3_ch, g=-15)
vocal_section(63.85, 88.98, 72, 65, g=0.5)
hook(T(72) + (89 - 65) * SB, g=0.5, bus="vocal", long_pie=True)
for b in (70.5, 78.5, 86.5):                       # gaps after "lantern", "high", "drumstick"
    t = T(72) + (b - 65) * SB
    for off in (0, 0.5, 1.5):
        brass_stab(t + off * BEAT, chord_at(v3_ch, t + off * BEAT + 0.01), g=-6)
    string_run(t + 2 * BEAT, start=72, g=-9)
B["drums"].add(T(86), inst.crash(), -5)

# ---- outro (88-96)
out_ch = loop_chords(88, 96)
house_drums(88, 92, big=False, crash_at=(88,))
house_drums(92, 94, kick=True, clap=False, ohat=False, chat=True)
offbeat_bass(loop_chords(88, 92), g=-4)
saw_chords(loop_chords(88, 92), g=-12)
piano_chords(loop_chords(92, 96), g=-8, rhythm="sustain")
hook(T(90), g=-1, pie=False)                       # "glory of the pumpkin is the"
chop(92.95, 96.0, T(92), g=3)                      # "pie"
B["fx"].add(T(92), inst.downlifter(2 * BAR), -12)
fin = orig[int(84.4 * SR):int(93.0 * SR)].copy()      # the original's last "pie" and chord
fin = butter(fin, "band", [250, 5000])
fin = fade_edges(fin, 0.05, 1.5)
B["orig"].add(T(94), fin, -2)
B["orig"].add(T(94), inst.vinyl(len(fin) / SR, 0.04), 0)


# ================================================================== MIX

def env_curve(points):
    """points: list of (time, value) -> per-sample array (linear in value)."""
    ts = np.array([p[0] for p in points]) * SR
    vs = np.array([p[1] for p in points], dtype=np.float64)
    return np.interp(np.arange(N), ts, vs)


def log_curve(points):
    ts = np.array([p[0] for p in points]) * SR
    vs = np.log(np.array([p[1] for p in points], dtype=np.float64))
    return np.exp(np.interp(np.arange(N), ts, vs))


print("mixing ...")
# the last line ("but the glory of the pumpkin is the...") is sung over strings alone; the band
# comes back on "PIE"
STOP0, STOP1 = T(83, 2), T(86)
_stop = env_curve([(0, 1), (STOP0 - 0.03, 1), (STOP0, 0.0), (STOP1 - 0.005, 0.0), (STOP1, 1), (END, 1)])
for k in ["kick", "drums", "perc", "bass", "chords", "keys", "brass", "lead", "sub808"]:
    B[k].x *= _stop[:, None].astype(np.float32)
KICKS[:] = [k for k in KICKS if not (STOP0 <= k < STOP1)]
B["fx"].add(T(85), inst.riser(BAR, 500, 9000), -10)
B["fx"].add(T(86), inst.impact(), -4)
duck = duck_curve(N, KICKS, depth_db=-9, release=0.2)
duck_soft = duck_curve(N, KICKS, depth_db=-4, release=0.16)
duck808 = duck_curve(N, K808, depth_db=-5, release=0.3)

# filter automation: intro opens from 350 Hz; the build-up high-passes the music
lp_intro = log_curve([(0, 350), (T(0), 350), (T(6), 2500), (T(8) - 0.01, 19000), (END, 19000)])
hp_build1 = log_curve([(0, 20), (T(28), 20), (T(31, 3), 900), (T(32) - 0.005, 900), (T(32), 20), (END, 20)])
hp_build2 = log_curve([(0, 20), (T(68), 20), (T(71, 3), 800), (T(72) - 0.005, 800), (T(72), 20), (END, 20)])
lp_outro = log_curve([(0, 19000), (T(92), 19000), (T(95), 900), (END, 600)])
hp_total = np.maximum(hp_build1, hp_build2)
lp_total = np.minimum(lp_intro, lp_outro)

plate = reverb_ir(3.0, 1.9, 0.025, damp=7000)
room = reverb_ir(1.2, 0.6, 0.008, damp=9000, seed=3)
hall = reverb_ir(5.0, 3.6, 0.04, damp=5000, seed=5)

kick = B["kick"].x
drums = butter(B["drums"].x, "high", 120)
perc = butter(B["perc"].x, "high", 300)
bass = butter(B["bass"].x, "low", 3500) * duck[:, None]
sub808 = B["sub808"].x
chords = butter(B["chords"].x, "high", 160) * duck[:, None] * duck808[:, None]
strings = butter(B["strings"].x, "high", 140) * duck_soft[:, None]
keys = butter(B["keys"].x, "high", 120) * duck_soft[:, None]
brass_b = butter(B["brass"].x, "high", 150)
lead = B["lead"].x * duck_soft[:, None]
lead = lead + pingpong(lead, 0.75 * BEAT, 0.4, 6) * 0.35


def vocal_chain(x):
    x = butter(x, "high", 95)
    x = eq(x, "peak", 320, 1.0, -2.5)
    x = eq(x, "peak", 3500, 0.8, 4.5)
    x = eq(x, "hshelf", 9000, 0.7, 3.0)
    x = compress(x, -26, 4.0, 0.003, 0.08, makeup_db=6)
    x = compress(x, -14, 8.0, 0.001, 0.05)
    return sat(x, 1.15)


voc = vocal_chain(B["vocal"].x)
chp = vocal_chain(B["chops"].x)
# more space on the vocal in the break, the trap verse and the outro
vrev_amt = env_curve([(0, 0.18), (T(24), 0.18), (T(24) + 0.01, 0.4), (T(28), 0.4), (T(28) + 0.01, 0.2),
                      (T(48), 0.2), (T(48) + 0.01, 0.28), (T(64), 0.28), (T(64) + 0.01, 0.2), (T(92), 0.2),
                      (T(92) + 0.01, 0.45), (END, 0.45)])
vdelay = pingpong(voc, 0.75 * BEAT, 0.35, 5, lp=3500, hp=500) * 0.22
cdelay = pingpong(chp, 0.5 * BEAT, 0.45, 6, lp=4000, hp=400) * 0.28

# relative levels inside groups (dB)
G = dict(chords=-3, strings=-1, keys=-2, brass=-1, lead=-2, vocal=1, chops=0, drums=0, perc=-3)
# loudness targets per group (integrated LUFS, gated, so silent stretches do not count)
TARGET = dict(kick=-15.5, bass=-17.0, sub808=-15.5, drums=-16.0, music=-14.5, vocals=-11.5, fx=-21.0,
              orig=-14.0)


def to_lufs(x, target):
    L = lufs(x)
    return x * db(target - L) if np.isfinite(L) else x


music = (chords * db(G["chords"]) + strings * db(G["strings"]) + keys * db(G["keys"]) +
         brass_b * db(G["brass"]) + lead * db(G["lead"]))
# make room for the voice: dip the music up to 4 dB while it sings, and a static 3 kHz notch
from scipy.ndimage import minimum_filter1d, uniform_filter1d  # noqa: E402
key = (B["vocal"].x + B["chops"].x).mean(axis=1)
e_db = 10 * np.log10(uniform_filter1d(key.astype(np.float64) ** 2, int(0.03 * SR)) + 1e-12)
ref = np.percentile(e_db[e_db > -90], 95)
gr = -4.0 * np.clip((e_db - ref + 24) / 18, 0, 1)
gr = uniform_filter1d(minimum_filter1d(gr, int(0.12 * SR)), int(0.06 * SR))
music = music * db(gr)[:, None].astype(np.float32)
music = eq(music, "peak", 3000, 0.9, -2.0)
music_wet = convolve(butter(music, "high", 300), plate) * 0.18
music = to_lufs(music + music_wet, TARGET["music"])
music = sweep(music, "hp", hp_total, q=0.75)
drums_all = drums * db(G["drums"]) + perc * db(G["perc"])
drums_all = drums_all + convolve(drums_all, room) * 0.12
drums_all = to_lufs(drums_all, TARGET["drums"])
drums_all = sweep(drums_all, "hp", np.minimum(hp_total, 400), q=0.7)
vox_all = voc * db(G["vocal"]) + chp * db(G["chops"])
vox_wet = convolve(butter(vox_all, "high", 250), plate) * vrev_amt[:, None]
vox_all = to_lufs(vox_all + vox_wet + (vdelay * db(G["vocal"]) + cdelay * db(G["chops"])), TARGET["vocals"])
fx = B["fx"].x
fx = to_lufs(fx + convolve(fx, hall) * 0.25, TARGET["fx"])
low_end = to_lufs(kick, TARGET["kick"]) + to_lufs(bass, TARGET["bass"]) + to_lufs(sub808, TARGET["sub808"])

inst_mix = music + drums_all + low_end
inst_mix = sweep(inst_mix, "lp", lp_total, q=0.8)
mix = inst_mix + vox_all + fx + to_lufs(B["orig"].x, TARGET["orig"])

# stems for checking
stem_dir = W / "mix_stems"
stem_dir.mkdir(exist_ok=True)
for name, x in [("music", music), ("drums", drums_all), ("low", low_end), ("vocals", vox_all), ("fx", fx)]:
    write_wav(stem_dir / f"{name}.wav", x * 0.5, bits=16)

# ---- macro dynamics: quieter break and builds so the drops land
SECTION_DB = [(0, -2.0), (T0 - 0.01, -2.0), (T(0), -4.0), (T(7), -2.5), (T(8), -1.5), (T(24) - 0.01, -1.5),
              (T(24), -6.5), (T(28), -5.0), (T(31, 3.9), -1.5), (T(32), 0.0), (T(48) - 0.01, 0.0),
              (T(48), -1.5), (T(64) - 0.01, -1.5), (T(64), -2.5), (T(68), -3.5), (T(71, 3.9), -1.0),
              (T(72), 0.0), (T(88) - 0.01, 0.0), (T(88), -1.0), (T(92), -2.0), (END, -3.0)]
mix = mix * db(env_curve(SECTION_DB))[:, None].astype(np.float32)

# ---- master
print("mastering ...")
m = butter(mix, "high", 28)
m = eq(m, "lshelf", 90, 0.7, 1.0)
m = eq(m, "hshelf", 3500, 0.6, 2.0)
m = eq(m, "hshelf", 11000, 0.7, 1.5)
m = compress(m, -14, 2.0, 0.01, 0.15, makeup_db=1.5)
pre = lufs(m)
target = -9.5
m = m * db(target - pre)
m = sat(m * 0.9, 1.2) / 0.9 * 0.97
m = limiter(m, -1.0, look=0.003, rel=0.08)
post = lufs(m)
m = limiter(m * db(target - post), -1.0)
print(f"LUFS before {pre:.1f}, after {lufs(m):.1f}; peak {20*np.log10(np.abs(m).max()):.2f} dBFS; "
      f"length {len(m)/SR:.1f}s")
OUT.mkdir(exist_ok=True)
write_wav(OUT / "Glory_of_the_Pumpkin_Disco_Trap_Remix.wav", m)
json.dump(dict(T0=T0, bpm=BPM, bar=BAR, sections={"intro": T(0), "verse1": T(8), "break": T(24), "drop1": T(32),
               "trap_verse2": T(48), "build2": T(64), "final": T(72), "outro": T(88), "end": END}),
          open(W / "timeline.json", "w"), indent=1)
print("done")
