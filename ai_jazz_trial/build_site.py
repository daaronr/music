"""Build the Netlify version of the trial page into web/public/.

    python3 ai_jazz_trial/build_site.py
    (then deploy from ai_jazz_trial/web with the Netlify CLI; see README.md)
"""

from __future__ import annotations

import datetime
import html
import os
import re
import shutil
import subprocess
import zipfile
from string import Template

import build_page as bp
from site_data import GLOSSARY, PENDING, RECORDINGS
from trial_data import ASKS, PROMPT_CLAUDE, RUNS

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SRC = os.path.join(HERE, "web_src")
PUB = os.path.join(HERE, "web", "public")
FILES = os.path.join(PUB, "files")
NAMES = {r["key"]: r["name"] for r in RUNS}
esc = bp.esc


def tipify(text: str) -> str:
    """[[term]] or [[term|shown words]] -> a tooltip span (text must already be escaped)."""
    def repl(m):
        term, shown = m.group(1), m.group(2) or m.group(1)
        if term not in GLOSSARY:
            raise SystemExit(f"no glossary entry for {term!r}")
        return (f'<span class="tip" tabindex="0" data-tip="{esc(GLOSSARY[term])}">'
                f"{shown}</span>")
    return re.sub(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", repl, text)


def put(src_rel: str, dest_rel: str) -> str:
    dest = os.path.join(FILES, dest_rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(os.path.join(REPO, src_rel), dest)
    return "files/" + dest_rel


def zip_bundle(run) -> str:
    name, members = run["bundle"]
    members = list(members)
    if run["key"] == "parallax":
        members.append("claude_parallax/output/Parallax_duo_solo.mid")
    dest = os.path.join(FILES, run["key"], name)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for m in members:
            z.write(os.path.join(REPO, m), arcname=os.path.basename(m))
    return f"files/{run['key']}/{name}"


def recording_block(rec, key, headline=False):
    url = put(rec["src"], f"audio/{rec['file']}")
    cls = "rec headline" if headline else "rec"
    return (f'<figure class="{cls}"><figcaption>{esc(rec["label"])} '
            f'<span class="len">{esc(rec["length"])}</span></figcaption>'
            f'<audio controls preload="none" src="{esc(url)}"></audio>'
            f'<p class="rec-note">{esc(rec["note"])}</p></figure>')


def listen_card(run):
    k = run["key"]
    recs = RECORDINGS[k]
    main = next((r for r in recs if r["main"]), None)
    lead_pdf = put(run["lead"], f"{k}/{os.path.basename(run['lead'])}")
    meta = " · ".join(esc(m) for m in run["meta"][:3])
    if main:
        headline = (f'<figure class="rec headline"><figcaption>{esc(main["label"])} '
                    f'<span class="len">{esc(main["length"])}</span></figcaption>'
                    f'<audio controls preload="none" src="files/audio/{esc(main["file"])}">'
                    f"</audio></figure>")
        put(main["src"], f"audio/{main['file']}")
    else:
        headline = f'<p class="pending">{esc(PENDING.get(k, "No recording yet."))}</p>'
    others = [r for r in recs if not r["main"]]
    fold_items = [f'<p class="rec-note">{esc(main["note"])}</p>'] if main else []
    fold_items += [recording_block(r, k) for r in others]
    fold = (f'<details class="fold"><summary>How this recording was made'
            f'{" and other versions" if others else ""}</summary>{"".join(fold_items)}</details>'
            if fold_items else "")
    return f"""
<article class="listen-card" data-tune="{k}">
  <h3>{esc(run["name"])}</h3>
  <p class="meta">{meta}</p>
  {headline}
  {fold}
  <p class="small"><a href="{esc(lead_pdf)}">Lead sheet (PDF)</a> · <a href="#card-{k}">Tune notes</a></p>
</article>"""


def tune_card(run):
    k = run["key"]
    pdfs = []
    for label, src in run["pdfs"]:
        url = put(src, f"{k}/{os.path.basename(src)}")
        pdfs.append(f'<li><a href="{esc(url)}">{esc(label)}</a></li>')
    zip_url = zip_bundle(run)
    os.makedirs(bp.PREV, exist_ok=True)
    png = bp.render_pages(run["lead"], f"{k}_lead", first_only=True)[0]
    preview = put(os.path.relpath(os.path.join(bp.SITE, png), REPO), f"previews/{k}_lead.png")
    lead_url = f"files/{k}/{os.path.basename(run['lead'])}"
    with open(os.path.join(REPO, run["ireal"])) as fh:
        ireal = fh.read().strip()
    recs = RECORDINGS[k]
    rec_html = "".join(recording_block(r, k) for r in recs) or \
        f'<p class="pending">{esc(PENDING.get(k, "No recording yet."))}</p>'
    model = tipify(esc(run["model"]).replace("max effort", "[[max effort]]"))
    where = tipify(esc(run["where"]).replace("Claude Code", "[[Claude Code]]")
                   .replace("Codex desktop app", "[[Codex]] desktop app"))
    return f"""
<article class="tune-card" id="card-{k}">
  <h3>{esc(run["name"])}</h3>
  <p class="by">{model} · {where}</p>
  <p class="meta">{" · ".join(esc(m) for m in run["meta"])}</p>
  <a class="sheet" href="{esc(lead_url)}"><img src="{esc(preview)}" alt="First page of the {esc(run["name"])} lead sheet" loading="lazy"><span>Open the lead sheet (PDF)</span></a>
  <details class="fold" open><summary>The idea, per the run’s own notes</summary><p>{esc(run["idea"])}</p></details>
  <details class="fold"><summary>Sheet music ({len(run["pdfs"])} PDFs)</summary><p class="note">{esc(run["sheets_note"])}</p><ul>{"".join(pdfs)}</ul></details>
  <details class="fold"><summary>Recordings</summary>{rec_html}</details>
  <details class="fold"><summary>Editable files and the iReal Pro chart</summary>
    <p><a class="btn small" href="{esc(zip_url)}">Download the files (.zip)</a></p>
    <p class="note">[[MusicXML|MusicXML]] for any notation program, [[MuseScore|MuseScore]] files with the engraved layout, and the iReal Pro import page.</p>
    <p><button type="button" class="btn small ghost" data-copy="{esc(ireal)}">Copy the iReal Pro link</button></p>
    <p class="note">Paste it into Safari on a phone, tablet or Mac that has iReal Pro, or open the iReal page from the zip.</p>
  </details>
</article>"""


def choices():
    items = [f'<label class="choice" data-tune="{r["key"]}"><input type="radio" name="pref" '
             f'value="{r["key"]}"> {esc(r["name"])}</label>' for r in RUNS]
    items.append('<label class="choice" data-last><input type="radio" name="pref" value="none"> '
                 "No preference</label>")
    return "".join(items)


def rating_rows():
    rows = []
    for r in RUNS:
        k = r["key"]
        stars = "".join(f'<label><input type="radio" name="r_{k}" value="{n}"><span>{n}</span></label>'
                        for n in range(1, 6))
        rows.append(f'<div class="rating-row" data-tune="{k}"><span class="rname">{esc(r["name"])}'
                    f'</span><div class="scale" role="radiogroup" aria-label="Rating for '
                    f'{esc(r["name"])}">{stars}</div></div>')
    return "".join(rows)


def main():
    if os.path.isdir(FILES):
        shutil.rmtree(FILES)
    os.makedirs(FILES)
    listen = "".join(listen_card(r) for r in RUNS)
    cards = "".join(tune_card(r) for r in RUNS)
    asks = "".join(f'<li><span class="tip" tabindex="0" data-tip="{esc(q)}">{esc(s)}</span></li>'
                   for s, q in ASKS)
    now = datetime.datetime.now().strftime("%-d %B %Y, %H:%M")
    subs = dict(
        listen_cards=listen, tune_cards=cards, pref_choices=choices(), rating_rows=rating_rows(),
        grids="".join(bp.grid_html(r["key"], r["name"]) for r in RUNS),
        timelines="".join(bp.timeline_html(r) for r in RUNS), asks=asks,
        prompt_full=esc(PROMPT_CLAUDE),
        prompt_codex_diff=esc("The Codex copy said “I'll be asking Claude” where the "
                              "Claude copies say “I'll be asking GPT.”"),
        built=now)
    for name in ("index.html", "results.html"):
        with open(os.path.join(SRC, name), encoding="utf-8") as fh:
            page = Template(fh.read()).substitute(subs)
        with open(os.path.join(PUB, name), "w", encoding="utf-8") as fh:
            fh.write(tipify(page))
    for name in ("style.css", "app.js", "results.js", "robots.txt", "sitemap.xml", "llms.txt"):
        shutil.copy2(os.path.join(SRC, name), os.path.join(PUB, name))
    size = subprocess.run(["du", "-sh", PUB], capture_output=True, text=True).stdout.split()[0]
    print(f"built {os.path.relpath(PUB, REPO)} ({size})")


if __name__ == "__main__":
    main()
