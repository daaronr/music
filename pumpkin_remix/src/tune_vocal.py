"""Chord-aware pitch correction of the grid-aligned vocal.

Target for each voiced frame: the written melody note (sung two octaves below the score)
when the voice is within 1.2 semitones of it, otherwise the nearest note allowed by the
current chord (C major scale with the chord's own altered tones).

  soft: one constant shift per sung note, so vibrato and slides survive
  hard: per-frame correction (the flat, stepped "autotune" sound)

Uses Rubber Band's --pitchmap (realtime engine), then re-aligns the output to the input
by cross-correlation, since the realtime engine adds latency.
"""
import json
import subprocess
import sys
from pathlib import Path

import librosa
import numpy as np
import scipy.signal as sig
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
W = ROOT / "work"
sys.path.insert(0, str(Path(__file__).parent))
from harmony import chord_pcs, score_chords, score_melody  # noqa: E402

meta = json.load(open(W / "vocal_grid.json"))
LEAD, SB = meta["lead"], meta["sb"]
HOP = 256
SR_A = 22050

y, sr = sf.read(str(W / "vocal_grid.wav"), dtype="float32", always_2d=True)
mono = librosa.resample(y.mean(axis=1), orig_sr=sr, target_sr=SR_A)
f0, voiced, prob = librosa.pyin(mono, fmin=65, fmax=700, sr=SR_A, frame_length=2048, hop_length=HOP,
                                resolution=0.02)
t = librosa.times_like(f0, sr=SR_A, hop_length=HOP)
m = librosa.hz_to_midi(f0)
beat = (t - LEAD) / SB

chords = score_chords()          # list of (start_beat, end_beat, name)
melody = score_melody()          # list of (start_beat, end_beat, midi)


def at(seq, b):
    for s, e, v in seq:
        if s <= b < e:
            return v
    return None


def target_for(mm, b):
    mel = at(melody, b)
    if mel is not None:
        for octv in (-24, -12, -36):
            if abs(mm - (mel + octv)) <= 1.2:
                return mel + octv
    ch = at(chords, b) or "C"
    pcs = chord_pcs(ch, scale=True)
    base = np.floor(mm) - 6
    cand = np.array([p for p in np.arange(base, base + 13) if int(p) % 12 in pcs])
    return float(cand[np.argmin(np.abs(cand - mm))])


ok = voiced & (prob > 0.2) & np.isfinite(m)
tgt = np.full_like(m, np.nan)
for i in np.where(ok)[0]:
    tgt[i] = target_for(m[i], beat[i])

# note segmentation (for soft mode)
seg_id = np.full(len(m), -1)
sid, last = -1, None
for i in range(len(m)):
    if not ok[i]:
        last = None
        continue
    if last is None or abs(m[i] - last) > 0.7 or tgt[i] != tgt[i - 1]:
        sid += 1
    seg_id[i] = sid
    last = m[i]

def build(mode):
    off = np.zeros(len(m))
    if mode == "hard":
        off[ok] = tgt[ok] - m[ok]
    else:
        for s in range(sid + 1):
            idx = np.where(seg_id == s)[0]
            if len(idx) < 3:
                continue
            core = idx[len(idx) // 5: max(len(idx) // 5 + 1, 4 * len(idx) // 5)]
            off[idx] = np.median(tgt[core] - m[core])
    off[np.abs(off) > 2.0] = 0.0
    # hold offsets through unvoiced gaps shorter than 80 ms, else relax to 0
    filled = off.copy()
    lastv, gap = 0.0, 0
    for i in range(len(off)):
        if ok[i]:
            lastv, gap = off[i], 0
        else:
            gap += 1
            filled[i] = lastv if gap * HOP / SR_A < 0.08 else 0.0
    k = int((0.012 if mode == "hard" else 0.03) * SR_A / HOP) | 1
    return np.convolve(filled, np.ones(k) / k, mode="same")


def run(mode):
    off = build(mode)
    pm = W / f"pitchmap_{mode}.txt"
    with open(pm, "w") as f:
        for ti, o in zip(t, off):
            f.write(f"{int(round(ti * sr))} {o:.4f}\n")
    raw = W / f"vocal_{mode}_raw.wav"
    subprocess.run(["/opt/homebrew/bin/rubberband", "-3", "-q", "--pitch-hq", "-F" if mode == "soft" else "-F",
                    "--pitchmap", str(pm), "-t", "1", str(W / "vocal_grid.wav"), str(raw)], check=True)
    z, _ = sf.read(str(raw), dtype="float32", always_2d=True)
    # latency compensation
    a = y.mean(axis=1)[: sr * 30]
    b = z.mean(axis=1)[: sr * 30]
    xc = sig.fftconvolve(b, a[::-1], mode="full")
    lag = int(np.argmax(xc) - (len(a) - 1))
    if lag > 0:
        z = z[lag:]
    elif lag < 0:
        z = np.vstack([np.zeros((-lag, 2), np.float32), z])
    out = np.zeros_like(y)
    n = min(len(out), len(z))
    out[:n] = z[:n]
    sf.write(str(W / f"vocal_{mode}.wav"), out, sr, subtype="FLOAT")
    # report residual intonation
    mm = librosa.hz_to_midi(librosa.pyin(librosa.resample(out.mean(axis=1), orig_sr=sr, target_sr=SR_A), fmin=65,
                                         fmax=700, sr=SR_A, frame_length=2048, hop_length=HOP, resolution=0.02)[0])
    L = min(len(mm), len(tgt))
    d = mm[:L] - tgt[:L]
    d = d[np.isfinite(d)]
    print(f"{mode}: latency {lag} samples, |pitch - target| median {100*np.median(np.abs(d)):.0f} cents "
          f"(before: {100*np.nanmedian(np.abs(m[ok] - tgt[ok])):.0f})")


for mode in sys.argv[1:] or ["soft", "hard"]:
    run(mode)
