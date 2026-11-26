"""Small numpy DSP toolkit: oscillators, filters, envelopes, effects, mastering."""
from __future__ import annotations

import numpy as np
import scipy.signal as sig
from scipy.ndimage import maximum_filter1d, minimum_filter1d, uniform_filter1d

SR = 44100
rng = np.random.default_rng(1125)


def db(x):
    return 10 ** (x / 20)


def mtof(m):
    return 440.0 * 2 ** ((np.asarray(m, dtype=np.float64) - 69) / 12)


# ------------------------------------------------------------------ oscillators

def _blep(t, dt):
    y = np.zeros_like(t)
    m = t < dt
    x = t[m] / dt[m]
    y[m] = x + x - x * x - 1
    m = t > 1 - dt
    x = (t[m] - 1) / dt[m]
    y[m] = x * x + x + x + 1
    return y


def phase(freq, n, ph0=0.0):
    f = np.broadcast_to(np.asarray(freq, np.float64), (n,))
    dt = f / SR
    ph = (ph0 + np.concatenate([[0.0], np.cumsum(dt[:-1])])) % 1.0
    return ph, dt


def saw(freq, n, ph0=0.0):
    ph, dt = phase(freq, n, ph0)
    return (2 * ph - 1 - _blep(ph, dt)).astype(np.float32)


def square(freq, n, ph0=0.0, pw=0.5):
    ph, dt = phase(freq, n, ph0)
    a = 2 * ph - 1 - _blep(ph, dt)
    ph2 = (ph + pw) % 1.0
    b = 2 * ph2 - 1 - _blep(ph2, dt)
    return (0.5 * (a - b)).astype(np.float32)


def sine(freq, n, ph0=0.0):
    ph, _ = phase(freq, n, ph0)
    return np.sin(2 * np.pi * ph).astype(np.float32)


def noise(n):
    return rng.standard_normal(n).astype(np.float32)


# ------------------------------------------------------------------ envelopes

def adsr(n, a=0.005, d=0.1, s=0.7, r=0.1, gate=None):
    """gate = seconds the note is held (default: n - release)."""
    t = np.arange(n) / SR
    gate = (n / SR - r) if gate is None else gate
    e = np.where(t < a, t / max(a, 1e-6), s + (1 - s) * np.exp(-(t - a) / max(d, 1e-6)))
    rel = t > gate
    if rel.any():
        g_val = np.interp(gate, t, e)
        e[rel] = g_val * np.exp(-(t[rel] - gate) / max(r / 4.6, 1e-6))
    return e.astype(np.float32)


def expdec(n, tau, attack=0.001):
    t = np.arange(n) / SR
    return (np.minimum(1, t / attack) * np.exp(-t / tau)).astype(np.float32)


def fade_edges(x, fin=0.003, fout=0.01):
    x = x.copy()
    a, b = min(int(fin * SR), len(x) // 2), min(int(fout * SR), len(x) // 2)
    if a:
        x[:a] *= np.linspace(0, 1, a, dtype=np.float32)[:, None] if x.ndim == 2 else np.linspace(0, 1, a)
    if b:
        x[-b:] *= np.linspace(1, 0, b, dtype=np.float32)[:, None] if x.ndim == 2 else np.linspace(1, 0, b)
    return x


# ------------------------------------------------------------------ filters

def butter(x, kind, fc, order=2):
    wn = np.asarray(fc, dtype=np.float64) / (SR / 2)
    wn = float(wn) if wn.ndim == 0 else wn
    sos = sig.butter(order, wn, btype=kind, output="sos")
    return sig.sosfilt(sos, x, axis=0).astype(np.float32)


def rbj(kind, fc, q=0.707, gain_db=0.0):
    w = 2 * np.pi * min(fc, SR * 0.45) / SR
    cw, sw = np.cos(w), np.sin(w)
    al = sw / (2 * q)
    A = 10 ** (gain_db / 40)
    if kind == "lp":
        b = [(1 - cw) / 2, 1 - cw, (1 - cw) / 2]; a = [1 + al, -2 * cw, 1 - al]
    elif kind == "hp":
        b = [(1 + cw) / 2, -(1 + cw), (1 + cw) / 2]; a = [1 + al, -2 * cw, 1 - al]
    elif kind == "bp":
        b = [al, 0, -al]; a = [1 + al, -2 * cw, 1 - al]
    elif kind == "peak":
        b = [1 + al * A, -2 * cw, 1 - al * A]; a = [1 + al / A, -2 * cw, 1 - al / A]
    elif kind == "lshelf":
        sq = 2 * np.sqrt(A) * al
        b = [A * ((A + 1) - (A - 1) * cw + sq), 2 * A * ((A - 1) - (A + 1) * cw), A * ((A + 1) - (A - 1) * cw - sq)]
        a = [(A + 1) + (A - 1) * cw + sq, -2 * ((A - 1) + (A + 1) * cw), (A + 1) + (A - 1) * cw - sq]
    elif kind == "hshelf":
        sq = 2 * np.sqrt(A) * al
        b = [A * ((A + 1) + (A - 1) * cw + sq), -2 * A * ((A - 1) + (A + 1) * cw), A * ((A + 1) + (A - 1) * cw - sq)]
        a = [(A + 1) - (A - 1) * cw + sq, 2 * ((A - 1) - (A + 1) * cw), (A + 1) - (A - 1) * cw - sq]
    else:
        raise ValueError(kind)
    b, a = np.array(b) / a[0], np.array(a) / a[0]
    return b, a


def eq(x, kind, fc, q=0.707, gain_db=0.0):
    b, a = rbj(kind, fc, q, gain_db)
    return sig.lfilter(b, a, x, axis=0).astype(np.float32)


def sweep(x, kind, fc, q=0.707, block=128):
    """Time-varying biquad.  fc: array of cutoff per sample (or per block)."""
    x2 = x if x.ndim == 2 else x[:, None]
    n = len(x2)
    fc = np.broadcast_to(np.asarray(fc, np.float64), (n,))
    out = np.empty_like(x2)
    zi = np.zeros((2, x2.shape[1]))
    for i in range(0, n, block):
        b, a = rbj(kind, float(fc[min(i + block // 2, n - 1)]), q)
        seg, zi = sig.lfilter(b, a, x2[i:i + block], axis=0, zi=zi)
        out[i:i + block] = seg
    return out if x.ndim == 2 else out[:, 0]


# ------------------------------------------------------------------ stereo & dynamics

def pan(mono, p=0.0):
    th = (p + 1) * np.pi / 4
    return np.stack([mono * np.cos(th), mono * np.sin(th)], 1).astype(np.float32) * np.sqrt(2).astype(np.float32)


def width(x, w):
    m = (x[:, 0] + x[:, 1]) / 2
    s = (x[:, 0] - x[:, 1]) / 2 * w
    return np.stack([m + s, m - s], 1).astype(np.float32)


def sat(x, drive=1.0):
    return (np.tanh(x * drive) / np.tanh(drive)).astype(np.float32)


def compress(x, thresh_db=-18, ratio=3.0, attack=0.005, release=0.12, makeup_db=0.0, knee_db=6.0):
    win = 64
    mono = np.sqrt((x ** 2).mean(axis=1)) if x.ndim == 2 else np.abs(x)
    n = len(mono) // win + 1
    pad = np.zeros(n * win, np.float32)
    pad[:len(mono)] = mono
    lev = np.sqrt((pad.reshape(n, win) ** 2).mean(axis=1)) + 1e-9
    d = 20 * np.log10(lev)
    over = d - thresh_db
    gr = np.where(over <= -knee_db / 2, 0.0,
                  np.where(over >= knee_db / 2, over * (1 / ratio - 1),
                           (1 / ratio - 1) * (over + knee_db / 2) ** 2 / (2 * knee_db)))
    sm = np.empty_like(gr)
    aa, ar = np.exp(-win / SR / attack), np.exp(-win / SR / release)
    g = 0.0
    for i, tg in enumerate(gr):
        c = aa if tg < g else ar
        g = c * g + (1 - c) * tg
        sm[i] = g
    gain = np.interp(np.arange(len(mono)), np.arange(n) * win + win / 2, db(sm + makeup_db)).astype(np.float32)
    return x * (gain[:, None] if x.ndim == 2 else gain)


def duck_curve(n, times, depth_db=-10.0, release=0.2, attack=0.004, hold=0.01):
    """Sidechain-style gain curve: dips at each trigger time, recovers over `release`."""
    g = np.ones(n, np.float32)
    L = int((attack + hold + release) * SR)
    t = np.arange(L) / SR
    k = np.ones(L)
    k[t < attack] = 1 - (t[t < attack] / attack)
    rel = t >= attack + hold
    k[(t >= attack) & ~rel] = 0
    x = (t[rel] - attack - hold) / release
    k[rel] = np.clip(x, 0, 1) ** 1.6
    floor = db(depth_db)
    k = (floor + (1 - floor) * k).astype(np.float32)
    for tt in times:
        i = int(round((tt - attack) * SR))
        if i >= n or i + L <= 0:
            continue
        a, b = max(0, i), min(n, i + L)
        g[a:b] = np.minimum(g[a:b], k[a - i:b - i])
    return g


def limiter(x, ceiling_db=-1.0, look=0.004, rel=0.06):
    c = db(ceiling_db)
    peak = np.abs(x).max(axis=1)
    L = max(3, int(look * SR) | 1)
    env = maximum_filter1d(peak, size=L)
    graw = np.minimum(1.0, c / np.maximum(env, 1e-9))
    R = max(3, int(rel * SR) | 1)
    g = minimum_filter1d(graw, size=L)
    g = minimum_filter1d(g, size=R, origin=-(R // 2))       # hold through the release window
    g = uniform_filter1d(g, size=L)
    g = uniform_filter1d(g, size=R // 2 | 1)
    g = np.minimum(g, minimum_filter1d(graw, size=L))
    y = x * g[:, None]
    return np.clip(y, -c, c).astype(np.float32)


# ------------------------------------------------------------------ space

def reverb_ir(seconds=2.5, rt60=1.8, predelay=0.02, damp=6000, bright=0.0, seed=7):
    r = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = np.zeros((n, 2), np.float32)
    for ch in range(2):
        z = r.standard_normal(n).astype(np.float32)
        # darker as it decays: crossfade between bright and damped copies
        dark = butter(z, "low", damp * 0.5)
        lite = butter(z, "low", damp)
        mix = np.exp(-t / (rt60 * 0.35))
        z = lite * mix + dark * (1 - mix)
        ir[:, ch] = z * np.exp(-6.9 * t / rt60)
    ir = butter(ir, "high", 180)
    p = int(predelay * SR)
    ir = np.vstack([np.zeros((p, 2), np.float32), ir])
    return (ir / np.sqrt((ir ** 2).sum(axis=0, keepdims=True))).astype(np.float32)


def convolve(x, ir):
    out = np.zeros((len(x) + len(ir) - 1, 2), np.float32)
    for ch in range(2):
        out[:, ch] = sig.fftconvolve(x[:, ch], ir[:, ch]).astype(np.float32)
    return out[:len(x)]


def pingpong(x, delay_s, feedback=0.45, taps=8, lp=4500, hp=300):
    n = len(x)
    out = np.zeros_like(x)
    d = int(round(delay_s * SR))
    wet = butter(butter(x.mean(axis=1), "low", lp), "high", hp)
    for k in range(1, taps + 1):
        i = k * d
        if i >= n:
            break
        ch = (k + 1) % 2
        out[i:, ch] += wet[:n - i] * feedback ** (k - 1)
    return out


def write_wav(path, x, bits=24):
    import soundfile as sf
    sf.write(str(path), np.clip(x, -1, 1), SR, subtype="PCM_24" if bits == 24 else "PCM_16")


def lufs(x):
    import pyloudnorm as pyln
    return pyln.Meter(SR).integrated_loudness(x.astype(np.float64))
