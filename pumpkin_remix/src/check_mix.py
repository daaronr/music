"""Objective checks on the rendered remix (no ears available, so measure).

  * short-term loudness per section and vocal-to-backing ratio
  * spectral balance by band
  * vocal timing vs the kick grid
  * vocal/backing harmonic agreement per bar (chroma correlation)
"""
import json
from pathlib import Path

import librosa
import numpy as np
import pyloudnorm as pyln
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
W = ROOT / "work"
tl = json.load(open(W / "timeline.json"))
S = tl["sections"]
mix, sr = sf.read(str(ROOT / "output" / "Glory_of_the_Pumpkin_Disco_Trap_Remix.wav"), dtype="float32")
stems = {k: sf.read(str(W / "mix_stems" / f"{k}.wav"), dtype="float32")[0] * 2 for k in
         ["music", "drums", "low", "vocals", "fx"]}
recorded_brass = W / "mix_stems" / "recorded_brass.wav"
if recorded_brass.is_file():
    stems["music"] += sf.read(recorded_brass, dtype="float32")[0] * 2
meter = pyln.Meter(sr)
names = list(S.keys())
print("section          start  LUFS   vox-vs-backing dB")
for a, b in zip(names, names[1:]):
    i0, i1 = int(S[a] * sr), int(S[b] * sr)
    L = meter.integrated_loudness(mix[i0:i1].astype(np.float64))
    v = stems["vocals"][i0:i1]
    bk = stems["music"][i0:i1] + stems["drums"][i0:i1] + stems["low"][i0:i1]
    rv = np.sqrt(np.mean(v ** 2)) + 1e-9
    rb = np.sqrt(np.mean(bk ** 2)) + 1e-9
    print(f"{a:15s} {S[a]:6.1f} {L:6.1f}   {20*np.log10(rv/rb):6.1f}")

m = mix.mean(axis=1)
spec = np.abs(librosa.stft(m, n_fft=8192, hop_length=4096)) ** 2
f = librosa.fft_frequencies(sr=sr, n_fft=8192)
tot = spec.sum()
print("\nspectral balance (% energy):")
for lo, hi, nm in [(20, 60, "sub"), (60, 250, "bass"), (250, 2000, "low-mid"), (2000, 6000, "hi-mid"),
                   (6000, 20000, "air")]:
    e = spec[(f >= lo) & (f < hi)].sum() / tot * 100
    print(f"  {nm:8s} {lo:5d}-{hi:5d} Hz  {e:5.1f}%")

# vocal timing: onset times of the vocal stem vs the beat grid (beats every 60/128 s from T0)
beat = 60 / 128
y = librosa.resample(stems["vocals"].mean(axis=1), orig_sr=sr, target_sr=22050)
env = librosa.onset.onset_strength(y=y, sr=22050, hop_length=128)
on = librosa.onset.onset_detect(onset_envelope=env, sr=22050, hop_length=128, units="time")
s = env[librosa.time_to_frames(on, sr=22050, hop_length=128)]
on = on[s > np.percentile(s, 50)]
dev = ((on - tl["T0"]) / (beat / 2))
dev = (dev - np.round(dev)) * beat / 2 * 1000
print(f"\nvocal onsets vs 8th-note grid: median |dev| {np.median(np.abs(dev)):.0f} ms (n={len(on)}), "
      f"p80 {np.percentile(np.abs(dev), 80):.0f} ms")

# harmonic agreement per bar
bar = 4 * beat
vb = librosa.resample(stems["vocals"].mean(axis=1), orig_sr=sr, target_sr=22050)
mb = librosa.resample(stems["music"].mean(axis=1), orig_sr=sr, target_sr=22050)
c2 = librosa.note_to_hz("C2")
cv = librosa.feature.chroma_cqt(y=vb, sr=22050, hop_length=512, fmin=c2)
cm = librosa.feature.chroma_cqt(y=mb, sr=22050, hop_length=512, fmin=c2)
ft = librosa.frames_to_time(np.arange(cv.shape[1]), sr=22050, hop_length=512)
low = []
print("\nbars where vocal chroma fits the backing poorly (corr < 0.3):")
for k in range(96):
    t0 = tl["T0"] + k * bar
    sel = (ft >= t0) & (ft < t0 + bar)
    v = cv[:, sel].mean(axis=1)
    if np.sqrt(np.mean(stems["vocals"][int(t0 * sr):int((t0 + bar) * sr)] ** 2)) < 0.01:
        continue
    c = np.corrcoef(v, cm[:, sel].mean(axis=1))[0, 1]
    low.append((k, c))
bad = [(k, round(c, 2)) for k, c in low if c < 0.3]
print(" ", bad if bad else "none", f"| median corr {np.median([c for _, c in low]):.2f} over {len(low)} sung bars")
