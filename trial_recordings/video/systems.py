"""Find the systems (groups of staves) on a rendered score page."""
from __future__ import annotations

import numpy as np
from PIL import Image


def staff_rows(img: Image.Image):
    g = np.asarray(img.convert("L"), dtype=np.float32)
    h, w = g.shape
    dark = (g[:, int(w * 0.15):int(w * 0.95)] < 150).mean(axis=1)
    rows = np.where(dark > 0.45)[0]
    lines = []
    for r in rows:                       # merge adjacent pixel rows into one line
        if lines and r - lines[-1][-1] <= 1:
            lines[-1].append(r)
        else:
            lines.append([r])
    centers = [sum(l) / len(l) for l in lines]
    staves = []
    i = 0
    while i + 4 < len(centers):          # five roughly evenly spaced lines = a staff
        c = centers[i:i + 5]
        gaps = np.diff(c)
        if gaps.max() < 2.2 * gaps.min() + 2 and gaps.mean() < h * 0.02:
            staves.append((c[0], c[4]))
            i += 5
        else:
            i += 1
    return staves


def systems(img: Image.Image, staves_per_system: int):
    st = staff_rows(img)
    out = []
    for k in range(0, len(st) - staves_per_system + 1, staves_per_system):
        out.append((st[k][0], st[k + staves_per_system - 1][1]))
    return out


if __name__ == "__main__":
    import sys
    im = Image.open(sys.argv[1])
    print(len(staff_rows(im)), "staves;", systems(im, int(sys.argv[2])))
