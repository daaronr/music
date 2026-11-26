"""Re-time the isolated vocal from the 2023 sing-along onto a straight 128 BPM grid.

One sung beat (about 70 bpm in the video) becomes two beats at 128 BPM, so the vocal
runs about 9% slower than sung and every syllable that could be located lands on its
written (straight-eighth) position.  The ritardando at "is the pie" is taken out.

Output: work/vocal_grid.wav, where score beat b (beat 0 = the "Oh" pickup) sits at
LEAD + b * SB seconds.  Also shifts pitch +8 cents (the video is 8 cents flat).
"""
import json
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
W = ROOT / "work"
BPM = 128.0
SB = 2 * 60.0 / BPM          # seconds per score beat on the new grid
LEAD = 3.0                   # target time of score beat 0
TUNE_SEMITONES = 0.08

cands = json.load(open(W / "stems" / "anchors_all.json"))
bm = json.load(open(W / "stems" / "beat_map.json"))
grid, gt = np.array(bm["grid"]), np.array(bm["t"])

# Hand-checked anchors (score beat -> source seconds) where the automatic pass was unsure:
# the pickup (Whisper puts "lone" late; the pitch track shows E-F-G at 2.73/3.12/3.59)
# and the final phrase, which was sung with a ritardando and a high C on "is".
OVERRIDE = {0.0: 2.73, 0.5: 3.12, 1.0: 3.59,
            16.0: 16.40,                      # "No" (Whisper start is 1.4 s early)
            # "but the" is one F, "glo-ry of the" one E; onsets from the onset detector
            88.0: 78.20, 88.5: 78.81, 89.0: 79.20, 90.0: 80.17, 90.5: 80.65,
            91.0: 81.07, 91.5: 81.70, 92.0: 82.49, 92.5: 83.40, 93.0: 84.45}

import sys
MODE = sys.argv[1] if len(sys.argv) > 1 else "all"     # all | beats | smooth
OUT = W / (sys.argv[2] if len(sys.argv) > 2 else "vocal_grid.wav")
pts = {}
if MODE == "smooth":
    for b in np.arange(0, 93, 1.0):
        pts[float(b)] = float(np.interp(b, grid, gt))
else:
    for c in cands:
        b, t = c["beat"], c["t"]
        res = t - np.interp(b, grid, gt)
        on_beat = abs(b - round(b)) < 1e-6
        if abs(res) < (0.25 if MODE == "all" else 0.15) and (on_beat or MODE == "all"):
            pts[b] = t
pts.update(OVERRIDE)
# drop anything inside the overridden final phrase window except the overrides
pts = {b: t for b, t in pts.items() if not (88 <= b <= 93 and b not in OVERRIDE)}

beats = sorted(pts)
sel = []
for b in beats:
    t = pts[b]
    if sel:
        pb, pt = sel[-1]
        ratio = ((b - pb) * SB) / max(t - pt, 1e-6)
        if t - pt < 0.08 or not (0.45 < ratio < 2.6):
            # keep the override if one of the two is an override; otherwise skip the new one
            if b in OVERRIDE and pb not in OVERRIDE:
                sel.pop()
            else:
                continue
    sel.append((b, t))

src_len = sf.info(str(W / "stems" / "vocals.wav")).frames
sr = sf.info(str(W / "stems" / "vocals.wav")).samplerate
first_b, first_t = sel[0]
last_b, last_t = sel[-1]
r0 = SB / np.median(np.diff(gt[::2]))               # typical stretch ratio
assert abs(LEAD + first_b * SB - first_t * r0) < 0.3, "LEAD should put source 0 near target 0"
tmap = [(t, LEAD + b * SB) for b, t in sel]
tail = src_len / sr - last_t
tmap.append((src_len / sr, LEAD + last_b * SB + tail * 1.0))
total = tmap[-1][1]

with open(W / "vocal_timemap.txt", "w") as f:
    for s, t in tmap:
        f.write(f"{int(round(s * sr))} {int(round(t * sr))}\n")
json.dump(dict(anchors=sel, lead=LEAD, sb=SB, bpm=BPM, total=total), open(OUT.with_suffix(".json"), "w"), indent=0)
print(f"{len(sel)} anchors, output {total:.2f}s, typical ratio {r0:.3f}")
for (b0, t0), (b1, t1) in zip(sel, sel[1:]):
    r = (b1 - b0) * SB / (t1 - t0)
    if not 0.7 < r < 1.6:
        print(f"  strong warp {r:.2f} between beat {b0} ({t0:.2f}s) and {b1} ({t1:.2f}s)")

subprocess.run(["/opt/homebrew/bin/rubberband", "-3", "-F", "-q", "-p", str(TUNE_SEMITONES),
                "-M", str(W / "vocal_timemap.txt"), "-D", f"{total:.6f}",
                str(W / "stems" / "vocals.wav"), str(OUT)], check=True)
print("wrote", OUT)
