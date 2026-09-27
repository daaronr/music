"""Pitch estimation (autocorrelation with parabolic refinement)."""
from __future__ import annotations

import numpy as np

SR = 44100


def estimate_midi(x: np.ndarray, fmin=30.0, fmax=1600.0, sr=SR) -> float:
    """x: mono float array (a steady chunk of a note)."""
    x = x - x.mean()
    n = len(x)
    size = 1 << (2 * n - 1).bit_length()
    spec = np.fft.rfft(x * np.hanning(n), size)
    ac = np.fft.irfft(np.abs(spec) ** 2, size)[:n]
    ac /= ac[0] + 1e-12
    lo, hi = int(sr / fmax), min(int(sr / fmin), n - 2)
    seg = ac[lo:hi]
    # first strong peak (avoid octave errors): the earliest peak within 90% of the max
    peaks = [i for i in range(1, len(seg) - 1) if seg[i] > seg[i - 1] and seg[i] >= seg[i + 1]]
    if not peaks:
        return float("nan")
    best = max(seg[p] for p in peaks)
    p = next(p for p in peaks if seg[p] >= 0.9 * best)
    a, b, c = seg[p - 1], seg[p], seg[p + 1]
    shift = 0.5 * (a - c) / (a - 2 * b + c + 1e-12)
    lag = lo + p + shift
    f0 = sr / lag
    return 69 + 12 * np.log2(f0 / 440.0)
