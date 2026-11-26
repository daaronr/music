"""Syllable anchors: score beat position -> audio time, from Whisper words + vocal onsets."""
import difflib
import json
import re
import sys
from pathlib import Path
import numpy as np

score = json.load(open(sys.argv[1]))
words = json.load(open(sys.argv[2]))
d = Path(sys.argv[3])
notes = np.load(d / "vocal_notes.npy")          # start, dur, midi
onsets = np.load(d / "vocal_onsets.npy")
cand_on = np.unique(np.concatenate([notes[:, 0], onsets]))

norm = lambda s: re.sub(r"[^a-z]", "", s.lower())

# score syllables
syl = []
b0 = 0.0
for bi, m in enumerate(score):
    for n in m["notes"]:
        if n["lyric"]:
            syl.append(dict(beat=b0 + n["pos"], text=norm(n["lyric"]), bar=bi + 1, pitch=n["pitch"]))
    b0 += m["length"]

stext, sstart = "", []
for s in syl:
    sstart.append(len(stext))
    stext += s["text"]
wtext, wstart, wend = "", [], []
for w in words:
    wstart.append(len(wtext))
    wtext += norm(w["w"])
    wend.append(len(wtext))

sm = difflib.SequenceMatcher(None, stext, wtext, autojunk=False)
mapping = {}
for a, b, size in sm.get_matching_blocks():
    for k in range(size):
        mapping[a + k] = b + k

anchors = []
for i, s in enumerate(syl):
    c = mapping.get(sstart[i])
    if c is None:
        continue
    wi = int(np.searchsorted(wend, c, side="right"))
    if wi >= len(words):
        continue
    w = words[wi]
    if c == wstart[wi]:
        t = w["s"]
        kind = "word"
    else:
        frac = (c - wstart[wi]) / max(1, wend[wi] - wstart[wi])
        t = w["s"] + frac * (w["e"] - w["s"])
        kind = "inner"
    # snap to nearest onset; whisper starts tend to be early, so allow more room after
    near = cand_on[(cand_on > t - 0.12) & (cand_on < t + 0.25)]
    if len(near):
        t2 = near[np.argmin(np.abs(near - (t + 0.05)))]
    else:
        t2 = t
    anchors.append(dict(beat=s["beat"], t=float(t2), raw=t, kind=kind, text=s["text"], bar=s["bar"],
                        p=w["p"], pitch=s["pitch"]))

# outlier rejection: local beat duration must be plausible and monotone
def bad(a):
    out = []
    for k in range(1, len(a) - 1):
        db1 = a[k]["beat"] - a[k - 1]["beat"]
        db2 = a[k + 1]["beat"] - a[k]["beat"]
        r1 = (a[k]["t"] - a[k - 1]["t"]) / db1
        r2 = (a[k + 1]["t"] - a[k]["t"]) / db2
        span = (a[k + 1]["t"] - a[k - 1]["t"]) / (db1 + db2)
        out.append((abs(r1 - span) + abs(r2 - span), k))
    return out

json.dump(anchors, open(d / "anchors_all.json", "w"), indent=0)
keep = [a for a in anchors if a["p"] > 0.25 or a["kind"] == "inner"]
for _ in range(60):
    scores = bad(keep)
    worst, k = max(scores)
    if worst < 0.35:
        break
    keep.pop(k)
json.dump(keep, open(d / "anchors.json", "w"), indent=0)
prev = None
for a in keep:
    bpm = ""
    if prev:
        bpm = f"{60 * (a['beat'] - prev['beat']) / (a['t'] - prev['t']):6.1f}"
    print(f"bar {a['bar']:2d} beat {a['beat']:6.2f} t {a['t']:6.2f} (raw {a['raw']:6.2f}) {a['kind']:5s} {a['text']:10s} {bpm}")
    prev = a
print(len(anchors), "candidates", len(keep), "kept")
