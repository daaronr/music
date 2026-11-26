"""Smoke test: render every instrument once, report peak/RMS/spectral centroid, write a demo."""
import numpy as np

import inst
from dsp import SR, write_wav

items = {
    "kick_house": inst.kick_house(), "kick_big": inst.kick_big(), "808": inst.k808(36, 1.0, glide_to=43),
    "clap": inst.clap(), "snare_trap": inst.snare_trap(), "hat": inst.hat(), "hat_open": inst.hat(True),
    "crash": inst.crash(), "ride": inst.ride(), "tamb": inst.tamb().note(54, 0.3, 100, max_len=0.4),
    "shaker": inst.shaker().note(70, 0.3, 100, max_len=0.4),
    "supersaw": inst.supersaw(60, 0.8), "pluck": inst.pluck(72, 0.3), "bass": inst.bass_synth(36, 0.3),
    "pad": inst.pad(64, 1.0), "lead": inst.lead_saw(76, 0.8),
    "strings": inst.strings().note(64, 1.0, 100), "brass": inst.brass().note(67, 0.3, 110),
    "piano": inst.piano().note(60, 0.5, 100), "guitar": inst.guitar().note(64, 0.3, 100),
    "riser": inst.riser(2.0), "impact": inst.impact(), "downlifter": inst.downlifter(), "vinyl": inst.vinyl(1.0),
}
demo = []
for k, a in items.items():
    m = a.mean(axis=1)
    spec = np.abs(np.fft.rfft(m * np.hanning(len(m))))
    fr = np.fft.rfftfreq(len(m), 1 / SR)
    cent = (spec * fr).sum() / (spec.sum() + 1e-9)
    print(f"{k:11s} len {len(a)/SR:5.2f}s peak {np.abs(a).max():5.2f} rms {np.sqrt((a**2).mean()):.3f} "
          f"centroid {cent:6.0f} Hz  finite {np.isfinite(a).all()}")
    demo.append(a[:int(1.2 * SR)])
    demo.append(np.zeros((int(0.25 * SR), 2), np.float32))
write_wav("/Users/yosemite/githubs/music/pumpkin_remix/work/inst_demo.wav", np.vstack(demo) * 0.8)
