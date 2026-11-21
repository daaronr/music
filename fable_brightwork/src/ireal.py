#!/usr/bin/env python3
"""iReal Pro chart for Brightwork: builds an irealb:// link and an import page.

`python3 ireal.py --decode <file.html>` prints the decoded chart of an existing
iReal export (used to check the obfuscation routine against a real file).
"""
import re
import sys
from pathlib import Path
from urllib.parse import quote, unquote

PREFIX = "1r34LbKcu7"


def _swap50(s):
    """iReal's 50-character block scramble (it is its own inverse)."""
    c = list(s)
    for i in list(range(5)) + list(range(10, 24)):
        c[i], c[49 - i] = c[49 - i], c[i]
    return "".join(c)


def scramble(s):
    out = ""
    while len(s) > 50:
        block, s = s[:50], s[50:]
        out += block if len(s) < 2 else _swap50(block)
    return out + s


def decode_music(body):
    s = scramble(body)  # same routine both ways
    return s.replace("XyQ", "   ").replace("LZ", " |").replace("Kcl", "| x")


def encode_music(music):
    for tok in ("XyQ", "LZ", "Kcl"):
        assert tok not in music, f"raw chart must not contain the reserved token {tok}"
    out = scramble(music)
    assert scramble(out) == music
    return out


def irealb_url(title, composer, style, key, music, bpm=0, repeats=0):
    fields = [title, composer, "", style, key, "", PREFIX + encode_music(music), "", str(bpm), str(repeats)]
    return "irealb://" + quote("=".join(fields), safe="=")


def irealbook_url(title, composer, style, key, music):
    """Older plain-text form, kept as a fallback link."""
    return "irealbook://" + quote("=".join([title, composer, style, key, "n", music]), safe="=")


def decode_file(path):
    html = Path(path).read_text(encoding="utf-8")
    m = re.search(r'irealb://([^"]+)"', html)
    parts = unquote(m.group(1)).split("=")
    print("fields:", [p if not p.startswith(PREFIX) else "<music>" for p in parts])
    music = next(p for p in parts if p.startswith(PREFIX))[len(PREFIX):]
    print(decode_music(music))


def chart_music(changes, sections, qual_table, parse_chord, root_name):
    """Changes (list of 'Fmaj7#11' / 'Bm7 E7' bars) -> iReal chart body, 4 cells per bar."""
    letters = {k: v.strip()[0] for k, v in sections.items()}
    out, small = "", False
    for bi, bar in enumerate(changes):
        toks = []
        for sym in bar.split():
            root, qual = parse_chord(sym)
            toks.append(root_name(root) + qual_table[qual][5])
        if bi in letters:
            out += "[*" + letters[bi] + ("T44" if bi == 0 else "")
        crowded = len(toks) == 2 and len("".join(toks)) > 10
        if crowded:
            out += "s"
        elif small:
            out += "l"
        small = crowded
        out += f"{toks[0]}   " if len(toks) == 1 else f"{toks[0]} {toks[1]} "
        out += "Z" if bi == len(changes) - 1 else ("]" if bi + 1 in letters else "|")
    return out


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} - iReal Pro chart</title>
<style>
body {{ font-family: Helvetica, Arial, sans-serif; max-width: 46em; margin: 2em auto; padding: 0 1em; }}
table {{ border-collapse: collapse; margin: 1em 0; }}
td {{ border: 1px solid #999; padding: .5em .7em; min-width: 7.5em; font-size: 1.05em; }}
td.sec {{ border: none; font-weight: bold; min-width: 2em; }}
a.big {{ font-size: 1.3em; }}
</style>
</head>
<body>
<h1>{title}</h1>
<p>{composer} &middot; {style}, quarter = {bpm} &middot; 32 bars, A1 A2 B A3 &middot; F lydian</p>
<p><a class="big" href="{url}">Import into iReal Pro</a></p>
<p>Open this page on the device that has iReal Pro and click the link (on a Mac you can also
drag this file onto the iReal Pro icon). If that link is refused, try the
<a href="{url_plain}">plain-format link</a>.</p>
<table>
{rows}
</table>
<p>Last bar of the head out: hold Fmaj7(#11) instead of going to Gbmaj7(#11).</p>
</body>
</html>
"""


def write_chart(outdir, title, composer, style, key, bpm, changes, sections, qual_table, parse_chord,
                root_name):
    outdir = Path(outdir)
    outdir.mkdir(exist_ok=True)
    music = chart_music(changes, sections, qual_table, parse_chord, root_name)
    url = irealb_url(title, composer, style, key, music, bpm=bpm, repeats=4)
    url_plain = irealbook_url(title, composer, style, key, music)
    rows = []
    for r in range(0, len(changes), 4):
        cells = "".join(f"<td>{' &nbsp; '.join(b.split())}</td>" for b in changes[r:r + 4])
        sec = sections.get(r, "")
        rows.append(f'<tr><td class="sec">{sec}</td>{cells}</tr>')
    (outdir / f"{title}_iReal.html").write_text(
        PAGE.format(title=title, composer=composer, style=style, bpm=bpm, url=url, url_plain=url_plain,
                    rows="\n".join(rows)), encoding="utf-8")
    text = [f"{title} - {style}, quarter = {bpm}, key F (lydian), 32 bars A1 A2 B A3", ""]
    for r in range(0, len(changes), 4):
        text.append(f"{sections.get(r, ''):3s}| " + " | ".join(f"{b:22s}" for b in changes[r:r + 4]) + "|")
    text += ["", "iReal Pro import link:", url, "", "Plain-format fallback:", url_plain, ""]
    (outdir / f"{title}_chords.txt").write_text("\n".join(text), encoding="utf-8")
    return music, url


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--decode":
        decode_file(sys.argv[2])
