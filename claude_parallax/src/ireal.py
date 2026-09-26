"""Write the iReal Pro import link (irealbook:// protocol) for the 32-bar form.

Protocol: irealbook://Title=Composer=Style=Key=n=Progression, 16 cells per line,
4 cells per bar. The first Q (bar 31, last A) jumps to the coda on the final chorus.
"""

from __future__ import annotations

import html
import os
import urllib.parse

import tune

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output")

# our chord suffix -> iReal quality
QUALITY = {
    "maj7#11": "^7#11", "maj7#5": "^7#5", "maj9": "^9", "7alt": "7alt", "m9": "-9",
    "13#11": "13#11", "m7b5": "h7", "m11": "-11", "7#11": "7#11",
}


def ireal_chord(sym: str) -> str:
    for suffix in sorted(QUALITY, key=len, reverse=True):
        if sym.endswith(suffix):
            return sym[: -len(suffix)] + QUALITY[suffix]
    raise ValueError(sym)


def bar_cells(chords: str, prefix: str = "") -> str:
    items = [ireal_chord(c) for c in chords.split()]
    if len(items) == 1:
        return f"{prefix}{items[0]}   "          # chord + 3 empty cells
    return f"{prefix}{items[0]} {items[1]} "      # two chords, two beats each


def progression() -> str:
    marks = ["*A", "*A", "*B", "*A"]
    out = []
    for s in range(4):
        bars = []
        for i in range(8):
            n = s * 8 + i
            prefix = ("T44" if n == 0 else "") + ("Q" if n == 30 else "")
            bars.append(bar_cells(tune.FORM[n], prefix))
        close = "Z" if s == 3 else "]"
        out.append("[" + marks[s] + "|".join(bars) + close)
    coda = [bar_cells(c) for c in ["Abm9", "Db13#11", "Abm9", "Db13#11",
                                   "Ebmaj7#11", "Ebmaj7#11"]]
    out.append("Y[Q" + "|".join(coda) + "Z")
    return "".join(out)


def main():
    body = "=".join([tune.TITLE, "Claude", "Medium Up Swing", "Eb", "n", progression()])
    url = "irealbook://" + urllib.parse.quote(body, safe="")
    with open(os.path.join(OUT, "Parallax_iReal_link.txt"), "w") as fh:
        fh.write(url + "\n")
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Parallax - iReal Pro Import</title>
</head>
<body style="font-family: -apple-system, Helvetica, Arial, sans-serif; max-width: 42em; margin: 2em auto; padding: 0 1em; line-height: 1.45;">
  <h1>Parallax</h1>
  <p>Open this file in a browser on a Mac, iPhone or iPad that has iReal Pro, then click the link.</p>
  <p style="font-size: 1.3em;"><a href="{html.escape(url)}">Import Parallax into iReal Pro</a></p>
  <ul>
    <li>32-bar AABA form in concert Eb, style "Medium Up Swing". Set the tempo to about 176.</li>
    <li>The chart loops the form, so the head and both solo choruses play straight through.
        On the last chorus it jumps at bar 31 to the coda (bars 31&ndash;32 tagged, then Ebmaj7#11).</li>
    <li>The 4-bar guitar intro (Ebmaj7#11 x2, Dbmaj7#5 x2) is written on the lead sheet and is not in the
        loop. Add it in iReal's editor if you want it in the backing track.</li>
    <li>For the trumpet chart, use iReal's transpose button (B&#9837; instrument) rather than editing chords.</li>
  </ul>
  <p>Chord spellings used: Eb^7#11 = Ebmaj7#11, Db^7#5 = Dbmaj7#5, Bb^9 = Bbmaj9, Ab-9 = Abm9,
     G#h7 = G#m7b5, F#-11 = F#m11.</p>
  <p>Raw progression string:</p>
  <pre style="white-space: pre-wrap; font-size: 0.8em; background: #f4f4f4; padding: 0.8em;">{html.escape(progression())}</pre>
</body>
</html>
"""
    with open(os.path.join(OUT, "Parallax_iReal_import.html"), "w") as fh:
        fh.write(page)
    print("  wrote output/Parallax_iReal_import.html and output/Parallax_iReal_link.txt")


if __name__ == "__main__":
    main()
