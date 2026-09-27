"""Turn a plain-text chord chart into an iReal Pro import link and a click-to-import page.

    python3 ireal_link.py chart.txt [--out DIR]

chart.txt:
    title: Parallax
    composer: Claude
    style: Medium Up Swing
    key: Eb
    [A] Ebmaj7#11 | Ebmaj7#11 | Dbmaj7#5 | Dbmaj7#5 | B7alt | Bbmaj9 | Abm9 | Db13#11
    [B] F#m11 F7#11 | Emaj7#11 | ...
    coda_jump: 31                      # optional: bar where the last chorus jumps to the coda
    coda: Abm9 | Db13#11 | Ebmaj7#11 | Ebmaj7#11
    note: any line(s) to print on the HTML page

Bars hold 1-4 chords (two chords = beats 1 and 3). "%" repeats the previous bar's chords.
Writes <Title>_iReal.html and <Title>_iReal_link.txt and prints the link.
"""

from __future__ import annotations

import argparse
import html
import os
import re
import sys
import urllib.parse

# common spellings -> iReal Pro qualities (checked longest first)
QUALITY = {
    "maj7#11": "^7#11", "maj9#11": "^9#11", "maj7#5": "^7#5", "maj13": "^13", "maj9": "^9",
    "maj7": "^7", "Δ7": "^7", "^7": "^7", "maj": "^", "6/9": "69", "69": "69",
    "m(maj7)": "-^7", "mMaj7": "-^7", "m(maj9)": "-^9", "m7b5": "h7", "ø7": "h7",
    "ø": "h7", "m11": "-11", "m9": "-9", "m7": "-7", "m6": "-6", "m69": "-69", "m": "-",
    "-11": "-11", "-9": "-9", "-7": "-7", "-6": "-6", "-": "-",
    "dim7": "o7", "o7": "o7", "dim": "o", "aug": "+", "+": "+",
    "7alt": "7alt", "13#11": "13#11", "9#11": "9#11", "7#11": "7#11", "7b9#11": "7b9#11",
    "7#9#5": "7#9#5", "7#9b5": "7#9b5", "7b9b13": "7b9b13", "7b9": "7b9", "7#9": "7#9",
    "7#5": "7#5", "7b5": "7b5", "7b13": "7b13", "13b9": "13b9", "13#9": "13#9",
    "7susb9": "7b9sus", "7sus(b9)": "7b9sus", "7b9sus": "7b9sus", "13sus": "13sus",
    "9sus": "9sus", "7sus4": "7sus", "7sus": "7sus", "sus4": "sus", "sus": "sus",
    "13": "13", "11": "11", "9": "9", "7": "7", "6": "6", "add9": "add9", "5": "5", "": "",
}
ROOT_RE = re.compile(r"^([A-G][b#]?)(.*?)(?:/([A-G][b#]?))?$")


def to_ireal(chord: str) -> str:
    m = ROOT_RE.match(chord.strip())
    if not m:
        raise ValueError(f"can't read chord {chord!r}")
    root, suffix, bass = m.groups()
    s = suffix.replace("(", "").replace(")", "") if suffix not in QUALITY else suffix
    if s.startswith("sus") and s != "sus" and s not in QUALITY:
        s = s.replace("sus", "", 1) + "sus"
    for key in sorted(QUALITY, key=len, reverse=True):
        if s == key:
            q = QUALITY[key]
            break
    else:
        raise ValueError(f"no iReal quality for {chord!r} (suffix {suffix!r}); "
                         "add it to QUALITY or respell")
    return root + q + (f"/{bass}" if bass else "")


def bar_cells(chords: list, prefix: str = "") -> str:
    """Four cells per bar: 'C^7   ', 'D-7 G7 ', or up to four chords joined by commas."""
    q = [to_ireal(c) for c in chords]
    if len(q) == 1:
        body = q[0] + "   "
    elif len(q) == 2:
        body = f"{q[0]} {q[1]} "
    elif len(q) == 3:
        body = ",".join(q) + " "
    elif len(q) == 4:
        body = ",".join(q)
    else:
        raise ValueError(f"too many chords in one bar: {chords}")
    return prefix + body


def parse(path):
    meta, sections, coda, notes = {}, [], [], []
    for raw in open(path, encoding="utf-8"):
        line = raw.strip()
        if line.startswith("#"):
            continue
        if not line.startswith("note:"):
            line = re.sub(r"\s+#\s.*$", "", line)   # "  # comment"; sharps in chords survive
        if not line:
            continue
        sec = re.match(r"^\[([^\]]+)\]\s*(.*)$", line)
        if sec:
            sections.append((sec.group(1), [b.split() for b in sec.group(2).split("|")]))
        elif line.startswith("coda:"):
            coda = [b.split() for b in line[5:].split("|")]
        elif line.startswith("note:"):
            notes.append(line[5:].strip())
        elif ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip().lower()] = v.strip()
    return meta, sections, coda, notes


def progression(sections, coda, coda_jump=None):
    out, n, prev = [], 0, None
    for i, (label, bars) in enumerate(sections):
        cells = []
        for chords in bars:
            n += 1
            chords = prev if chords == ["%"] else chords
            prev = chords
            prefix = ("T44" if n == 1 else "") + ("Q" if coda_jump and n == coda_jump else "")
            cells.append(bar_cells(chords, prefix))
        mark = "*" + label[0].upper() if label[0].upper() in "ABCDVI" else ""
        text = f"<{label}>" if len(label) > 1 and label[0].upper() in "ABCD" else ""
        close = "Z" if i == len(sections) - 1 else "]"
        out.append("[" + mark + text + "|".join(cells) + close)
    if coda:
        out.append("Y[Q" + "|".join(bar_cells(c) for c in coda) + "Z")
    return "".join(out), n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("chart")
    ap.add_argument("--out", default=".")
    args = ap.parse_args()
    meta, sections, coda, notes = parse(args.chart)
    jump = int(meta["coda_jump"]) if meta.get("coda_jump") else None
    prog, nbars = progression(sections, coda, jump)
    title = meta.get("title", "Untitled")
    fields = [title, meta.get("composer", "Unknown"), meta.get("style", "Medium Swing"),
              meta.get("key", "C"), "n", prog]
    url = "irealbook://" + urllib.parse.quote("=".join(fields), safe="")
    stem = re.sub(r"[^A-Za-z0-9]+", "_", title).strip("_")
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, f"{stem}_iReal_link.txt"), "w") as fh:
        fh.write(url + "\n")
    note_html = "".join(f"<li>{html.escape(n)}</li>" for n in notes)
    page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} - iReal Pro import</title></head>
<body style="font-family:-apple-system,Helvetica,Arial,sans-serif;max-width:42em;margin:2em auto;padding:0 1em;line-height:1.45">
<h1>{html.escape(title)}</h1>
<p>Open this page on a Mac, iPhone or iPad with iReal Pro and click the link.</p>
<p style="font-size:1.3em"><a href="{html.escape(url)}">Import {html.escape(title)} into iReal Pro</a></p>
<ul><li>{nbars} bars, key {html.escape(meta.get('key', 'C'))}, style {html.escape(meta.get('style', 'Medium Swing'))}.</li>{note_html}</ul>
<p>Raw chart string:</p><pre style="white-space:pre-wrap;font-size:.8em;background:#f4f4f4;padding:.8em">{html.escape(prog)}</pre>
</body></html>
"""
    with open(os.path.join(args.out, f"{stem}_iReal.html"), "w") as fh:
        fh.write(page)
    print(url)
    print(f"{nbars} bars; wrote {stem}_iReal.html and {stem}_iReal_link.txt", file=sys.stderr)


if __name__ == "__main__":
    main()
