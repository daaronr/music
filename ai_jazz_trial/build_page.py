"""Build the trial page: previews, zip bundles, index.html and the publish manifest.

Run from anywhere:  python3 ai_jazz_trial/build_page.py
Outputs go to ai_jazz_trial/site/; site/files.json maps published paths to sources
(relative to the repo root) for the Artifact publish call.
"""

from __future__ import annotations

import glob
import html
import json
import os
import re
import subprocess
import zipfile
from string import Template

from trial_data import ASKS, FORMS, PROMPT_CLAUDE, PROMPT_CODEX, RUNS

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SITE = os.path.join(HERE, "site")
PREV = os.path.join(SITE, "previews")
BUND = os.path.join(SITE, "bundles")
DPI = "110"


def rel(path):
    return os.path.relpath(path, REPO)


def esc(text):
    return html.escape(text, quote=True)


def chord_html(sym):
    s = re.sub(r"(?<=[A-G])b", "♭", sym)          # root / bass flats
    s = re.sub(r"b(?=\d)", "♭", s)                 # altered tensions: b9, b5, b13
    s = s.replace("#", "♯")
    s = esc(s)
    return s.replace("♯11", '<span class="s11">♯11</span>')


def render_pages(pdf, stem, first_only=False):
    """PDF -> grayscale PNGs; returns published paths."""
    out = os.path.join(PREV, stem)
    for old in glob.glob(out + "*.png"):
        os.remove(old)
    args = ["pdftoppm", "-r", DPI, "-gray", "-png"]
    if first_only:
        args += ["-f", "1", "-l", "1", "-singlefile"]
    subprocess.run(args + [os.path.join(REPO, pdf), out], check=True)
    pages = sorted(glob.glob(out + "*.png"))
    return ["previews/" + os.path.basename(p) for p in pages]


XML = "application/xml"
TEXT_TYPES = {".musicxml": XML, ".mscx": XML, ".irealbook": "text/plain"}   # else by extension
SERVED = {".html", ".txt", ".md", ".pdf", ".png", ".mp3"} | set(TEXT_TYPES)


def publish_members(key, members, files):
    """Publish each bundle member as its own served file; the page zips them on demand.

    .mscz archives cannot be attached, so their .mscx (MuseScore's own uncompressed XML,
    which MuseScore opens directly) is extracted and published instead.
    Returns [(published path, name inside the zip)].
    """
    out = []
    for m in members:
        src = os.path.join(REPO, m)
        name = os.path.basename(m)
        if name.endswith(".mscz"):
            with zipfile.ZipFile(src) as z:
                inner = [n for n in z.namelist() if n.endswith(".mscx")][0]
                name = name[:-5] + ".mscx"
                dest = os.path.join(BUND, key, name)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                with open(dest, "wb") as fh:
                    fh.write(z.read(inner))
            src = dest
        elif name.endswith(".musicxml"):
            # the host refuses XML with DTD declarations; MuseScore doesn't need the DOCTYPE
            with open(src, encoding="utf-8") as fh:
                text = re.sub(r"<!DOCTYPE[^>]*>\s*", "", fh.read(), count=1)
            dest = os.path.join(BUND, key, name)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "w", encoding="utf-8") as fh:
                fh.write(text)
            src = dest
        ext = os.path.splitext(name)[1]
        if ext not in SERVED:
            print(f"  skipping {m}: {ext} cannot be published")
            continue
        pub = f"{key}/files/{name}"
        files[pub] = {"from": rel(src), "contentType": TEXT_TYPES[ext]} if ext in TEXT_TYPES \
            else rel(src)
        out.append((pub, name))
    return out


def pdf_pages(pdf):
    out = subprocess.run(["pdfinfo", os.path.join(REPO, pdf)], capture_output=True, text=True)
    return int(re.search(r"Pages:\s+(\d+)", out.stdout).group(1))


def grid_html(key, name):
    rows = []
    for label, bars in FORMS[key]:
        cells = []
        for bar in bars:
            chords = bar.split()
            inner = "".join(f'<span class="ch">{chord_html(c)}</span>' for c in chords)
            cells.append(f'<div class="bar{" two" if len(chords) > 1 else ""}">{inner}</div>')
        rows.append(f'<div class="sec"><div class="sec-label">{esc(label)}</div>'
                    f'<div class="bars">{"".join(cells)}</div></div>')
    return (f'<div class="chart"><h3 class="chart-name">{esc(name)}</h3>{"".join(rows)}</div>')


def timeline_html(run):
    items = []
    for time, label, text, effort, outcome in run["timeline"]:
        chip = f'<span class="effort">effort: {esc(effort)}</span>' if effort else ""
        items.append(
            f'<li><div class="t-head"><span class="t-time">{time}</span>'
            f'<span class="t-label">{esc(label)}</span>{chip}</div>'
            f'<details><summary>Prompt as typed</summary><blockquote class="verbatim">'
            f'{esc(text)}</blockquote></details>'
            f'<div class="t-out">{esc(outcome)}</div></li>')
    return (f'<div class="tl"><h3>{esc(run["name"])}</h3><p class="tl-model">'
            f'{esc(run["model"])} · {esc(run["where"])}</p><ol>{"".join(items)}</ol></div>')


def card_html(run, views, files, bundles):
    k = run["key"]
    meta = "".join(f"<li>{esc(m)}</li>" for m in run["meta"])
    pdf_items = []
    for label, src in run["pdfs"]:
        pub = f"{k}/{os.path.basename(src)}"
        files[pub] = src
        pdf_items.append(f'<li><button type="button" class="linkish" data-save="{esc(pub)}" '
                         f'data-name="{esc(os.path.basename(src))}">{esc(label)}</button></li>')
    zname, members = run["bundle"]
    bundles[zname] = {"store": False, "files": publish_members(k, members, files)}
    extra_zip = ""
    audio = ""
    if run["audio"]:
        players, tracks = [], []
        for label, src, pubname in run["audio"]:
            pub = f"audio/{pubname}"
            files[pub] = src
            tracks.append((pub, pubname))
            players.append(f'<figure class="track"><figcaption>{esc(label)}</figcaption>'
                           f'<audio controls preload="none" src="{esc(pub)}"></audio></figure>')
        audio = "".join(players)
        rname = run["recordings_bundle"][0]
        bundles[rname] = {"store": True, "files": tracks}
        extra_zip = (f'<button type="button" class="btn ghost" data-zip="{esc(rname)}">'
                     f'Save the MP3s (.zip)</button>')
    with open(os.path.join(REPO, run["ireal"])) as fh:
        ireal = fh.read().strip()
    lead_pages, score_pages = views[k + "-lead"], views[k + "-score"]
    return f"""
<article class="card" id="{k}">
  <p class="model">{esc(run["model"])} <span>· {esc(run["where"])}</span></p>
  <h3 class="tune">{esc(run["name"])}</h3>
  <ul class="meta">{meta}</ul>
  <button type="button" class="preview" data-view="{k}-lead" data-title="{esc(run["name"])}: lead sheet">
    <img src="{esc(lead_pages[0])}" alt="First page of the {esc(run["name"])} lead sheet" loading="lazy">
    <span class="preview-cap">Read the lead sheet</span>
  </button>
  <p class="idea"><span class="idea-label">The idea, per the run’s own notes.</span> {esc(run["idea"])}</p>
  <div class="actions">
    <button type="button" class="btn" data-view="{k}-score" data-title="{esc(run["name"])}: duo solo score">Read the duo score ({len(score_pages)} pp.)</button>
    <button type="button" class="btn ghost" data-zip="{esc(zname)}">Save MusicXML, MuseScore and iReal files (.zip)</button>
    <button type="button" class="btn ghost" data-copy="{esc(ireal)}">Copy the iReal Pro link</button>
  </div>
  <details class="sheets"><summary>Save a sheet ({len(run["pdfs"])} PDFs)</summary>
    <p class="note">{esc(run["sheets_note"])}</p><ul>{"".join(pdf_items)}</ul></details>
  <div class="audio"><p class="note"><strong>Audio.</strong> {esc(run["audio_note"])}</p>{audio}{extra_zip}</div>
</article>"""


def main():
    os.makedirs(PREV, exist_ok=True)
    os.makedirs(BUND, exist_ok=True)
    files, views, bundles = {}, {}, {}
    for run in RUNS:
        views[run["key"] + "-lead"] = render_pages(run["lead"], run["key"] + "_lead", True)
        views[run["key"] + "-score"] = render_pages(run["score"], run["key"] + "_score")
    for pages in views.values():
        for p in pages:
            files[p] = rel(os.path.join(SITE, p))
    for run in RUNS:
        for label, src in run["pdfs"]:
            m = re.search(r"\((\d+) pp\.\)", label)
            if m and int(m.group(1)) != pdf_pages(src):
                raise SystemExit(f"page count in label is wrong: {label} ({pdf_pages(src)})")
    cards = "".join(card_html(r, views, files, bundles) for r in RUNS)
    grids = "".join(grid_html(r["key"], r["name"]) for r in RUNS)
    timelines = "".join(timeline_html(r) for r in RUNS)
    asks = "".join(f'<li><span class="tip" tabindex="0" data-tip="{esc(q)}">{esc(s)}</span></li>'
                   for s, q in ASKS)
    with open(os.path.join(HERE, "template.html"), encoding="utf-8") as fh:
        page = Template(fh.read()).substitute(
            cards=cards, grids=grids, timelines=timelines, asks=asks,
            prompt_claude=esc(PROMPT_CLAUDE), prompt_codex_diff=esc(
                "The Codex copy said “I'll be asking Claude” where the Claude copies say "
                "“I'll be asking GPT.”"),
            views=json.dumps(views), bundles=json.dumps(bundles))
    with open(os.path.join(SITE, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(page)
    with open(os.path.join(SITE, "files.json"), "w") as fh:
        json.dump(files, fh, indent=1)
    total = sum(os.path.getsize(os.path.join(REPO, s if isinstance(s, str) else s["from"]))
                for s in files.values())
    print(f"wrote {rel(os.path.join(SITE, 'index.html'))}; {len(files)} files, "
          f"{total / 1e6:.1f} MB to publish")


if __name__ == "__main__":
    main()
