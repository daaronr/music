"""Objective checks on a render: per-note pitch accuracy of the stems,
click detection, and a spectrogram image of a time window.

usage: python3 verify.py <stem prefix> [start_s end_s]
"""
from __future__ import annotations

import sys
import wave

import numpy as np

from perform import build
from pitch import estimate_midi

SR = 44100


def load(path):
    with wave.open(path) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), "<i2").reshape(-1, 2).astype(np.float32) / 32768
    return x.mean(axis=1)


def pitch_report(name, notes, x, fmin, fmax, transpose=0, limit=None):
    errs, bad = [], []
    for n in notes:
        if limit and n.t > limit - 0.5:
            continue
        if n.dur < 0.14:
            continue
        a = int((n.t + min(0.09, n.dur * 0.35)) * SR)
        b = a + int(min(0.12, n.dur * 0.5) * SR)
        seg = x[a:b]
        if len(seg) < 2048 or np.abs(seg).max() < 1e-3:
            continue
        est = estimate_midi(seg, fmin=fmin, fmax=fmax)
        want = n.midi + transpose
        err = est - want
        err_oct = (err + 6) % 12 - 6          # ignore octave errors of the estimator
        errs.append(err_oct)
        if abs(err_oct) > 0.35:
            bad.append((round(n.t, 2), want, round(est, 2)))
    errs = np.array(errs)
    print(f"{name}: {len(errs)} notes checked, median |err| {np.median(np.abs(errs)) * 100:.0f} cents, "
          f"{len(bad)} off by > 35 cents")
    for b in bad[:12]:
        print("   t={} want {} got {}".format(*b))


def clicks(name, x):
    d = np.abs(np.diff(x))
    thr = 0.25
    idx = np.where(d > thr)[0]
    print(f"{name}: {len(idx)} sample jumps > {thr} (possible clicks)")


def main():
    prefix = sys.argv[1]
    t0 = float(sys.argv[2]) if len(sys.argv) > 2 else 0
    t1 = float(sys.argv[3]) if len(sys.argv) > 3 else 20
    perf = build()
    limit = None
    stems = {k: load(f"{prefix}_{k}.wav") for k in ("tpt", "alto", "bass", "piano", "drums")}
    limit = len(stems["tpt"]) / SR
    pitch_report("trumpet", perf["trumpet"], stems["tpt"], 150, 1300, limit=limit)
    pitch_report("alto", perf["alto"], stems["alto"], 120, 1000, limit=limit)
    pitch_report("bass", perf["bass"], stems["bass"], 35, 200, limit=limit)
    for k, x in stems.items():
        clicks(k, x)
    # spectrogram of the full mix window
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    mix = load(prefix + ".wav")
    seg = mix[int(t0 * SR):int(t1 * SR)]
    fig, axes = plt.subplots(3, 1, figsize=(14, 9), sharex=True)
    for ax, (label, sig_) in zip(axes, [("mix", seg), ("trumpet", stems["tpt"][int(t0 * SR):int(t1 * SR)]),
                                         ("drums", stems["drums"][int(t0 * SR):int(t1 * SR)])]):
        ax.specgram(sig_, NFFT=2048, Fs=SR, noverlap=1536, cmap="magma", vmin=-110)
        ax.set_ylim(0, 6000 if label != "drums" else 16000)
        ax.set_ylabel(label)
    t = np.arange(len(seg)) / SR
    plt.xlabel("seconds from %.1f" % t0)
    plt.tight_layout()
    out = prefix + "_spec.png"
    plt.savefig(out, dpi=70)
    print("spectrogram:", out)


if __name__ == "__main__":
    main()
