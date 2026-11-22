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
from site_data import GLOSSARY, HOSTED_VIDEO, PENDING, POSTER, RECORDINGS
from trial_data import ASKS, ASKS2, PROMPT_CLAUDE, RUNS
from tv_data import TV_ALT, TV_MAIN, TV_PROMPT_NOTE, TV_RECIPE, TV_RUNS

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


def _anchor(target: str) -> str:
    return (f'<a class="anchor" href="#{target}" aria-label="Link to this section" '
            f'title="Link to this section">#</a>')


def add_anchors(page: str) -> str:
    """A small '#' link after every section heading, round heading and tune heading, so any
    part of the page can be linked to directly."""
    # section headings: <section id="X"><h2 id="X-h">...</h2> -> link to #X
    page = re.sub(r'(<h2 id="([\w-]+)-h">)(.*?)(</h2>)',
                  lambda m: f"{m.group(1)}{m.group(3)} {_anchor(m.group(2))}{m.group(4)}", page)
    # round headings: before the sub-line when there is one
    def round_h(m):
        open_tag, hid, body = m.group(1), m.group(2), m.group(3)
        if '<span class="round-sub">' in body:
            body = body.replace('<span class="round-sub">', f'{_anchor(hid)} <span class="round-sub">', 1)
        else:
            body = f"{body} {_anchor(hid)}"
        return f"{open_tag}{body}</h3>"
    page = re.sub(r'(<h3 class="round-h[^"]*" id="([\w-]+)">)(.*?)</h3>', round_h, page, flags=re.S)
    # tune cards: the card's own id
    page = re.sub(r'(<article class="(?:listen|tune)-card"[^>]*id="([\w-]+)">\s*<h3>)(.*?)(</h3>)',
                  lambda m: f"{m.group(1)}{m.group(3)} {_anchor(m.group(2))}{m.group(4)}", page)
    return page


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
    # the score video, hosted here; none of these videos says which AI wrote the tune
    video = ""
    if k in HOSTED_VIDEO:
        src, length = HOSTED_VIDEO[k]
        url = put(src, f"video/{run['name'].replace(' ', '_')}.mp4")
        poster = put(f"{POSTER}/{k}.jpg", f"video/{k}_poster.jpg")
        video = (f'<figure class="rec vid"><figcaption>Video: the score, with the theory bar by bar '
                 f'<span class="len">{esc(length)}</span></figcaption>'
                 f'<video controls preload="none" playsinline poster="{esc(poster)}" src="{esc(url)}"></video></figure>')
    return f"""
<article class="listen-card" data-tune="{k}" id="listen-{k}">
  <h3>{esc(run["name"])}</h3>
  <p class="meta">{meta}</p>
  {f'<p class="pending added-later">{esc(run["added_later"])}</p>' if run.get("added_later") else ""}
  {video}
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
                   .replace("Codex desktop app", "[[Codex]] desktop app").replace("Codex CLI", "[[Codex]] CLI"))
    main = next((r for r in recs if r["main"]), None)
    video = (f'<p class="watch"><a href="{esc(main["video"])}" target="_blank" rel="noopener">'
             f"The video on YouTube</a> (the same video is playable at the top of this page)</p>"
             if main and main.get("video") else "")
    return f"""
<article class="tune-card" id="card-{k}">
  <h3>{esc(run["name"])}</h3>
  <p class="by">{model} · {where}</p>
  <p class="meta">{" · ".join(esc(m) for m in run["meta"])}</p>
  {f'<p class="pending added-later">{esc(run["added_later"])}</p>' if run.get("added_later") else ""}
  <a class="sheet" href="{esc(lead_url)}"><img src="{esc(preview)}" alt="First page of the {esc(run["name"])} lead sheet" loading="lazy"><span>Open the lead sheet (PDF)</span></a>
  {video}
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


def tv_card(run):
    """A bonus TV-theme card: sources live outside the repo (absolute paths), not in the vote."""
    k = run["key"]
    pdfs = []
    for label, src in run["pdfs"]:
        url = put(src, f"{k}/{os.path.basename(src)}")
        pdfs.append(f'<li><a href="{esc(url)}">{esc(label)}</a></li>')
    zname = f"{run['name'].replace(' ', '_').replace(chr(39), '')}_MusicXML.zip"
    zdest = os.path.join(FILES, k, zname)
    with zipfile.ZipFile(zdest, "w", zipfile.ZIP_DEFLATED) as z:
        for n in sorted(os.listdir(run["xml_dir"])):
            if n.endswith(".musicxml"):
                z.write(os.path.join(run["xml_dir"], n), arcname=n)
        z.write(run["ireal"], arcname=os.path.basename(run["ireal"]))
    os.makedirs(bp.PREV, exist_ok=True)
    png = bp.render_pages(run["lead"], f"{k}_lead", first_only=True)[0]
    preview = put(os.path.join(bp.SITE, png), f"previews/{k}_lead.png")
    lead_url = put(run["lead"], f"{k}/{os.path.basename(run['lead'])}")
    with open(run["ireal"]) as fh:
        ireal = fh.read().strip()
    recs = []
    for i, entry in enumerate(run["audio"]):
        src, fname, length = entry[:3]
        label, note = entry[3:5] if len(entry) >= 5 else (TV_MAIN if i == 0 else TV_ALT)
        recs.append((label, length, put(src, f"audio/{fname}"), note + TV_RECIPE))
    m_label, m_len, m_url, m_note = recs[0]
    others = "".join(
        f'<figure class="rec"><figcaption>{esc(lab)} <span class="len">{esc(ln)}</span></figcaption>'
        f'<audio controls preload="none" src="{esc(u)}"></audio><p class="rec-note">{esc(nt)}</p></figure>'
        for lab, ln, u, nt in recs[1:])
    return f"""
<article class="tune-card" id="card-{k}">
  <h3>{esc(run["name"])}</h3>
  <p class="by">{esc(run["credit"])}</p>
  <p class="meta">{" · ".join(esc(m) for m in run["meta"])}</p>
  <figure class="rec headline"><figcaption>{esc(m_label)} <span class="len">{esc(m_len)}</span></figcaption>
    <audio controls preload="none" src="{esc(m_url)}"></audio></figure>
  <details class="fold"><summary>How this recording was made and other versions</summary>
    <p class="rec-note">{esc(m_note)}</p>
    {others}</details>
  <a class="sheet" href="{esc(lead_url)}"><img src="{esc(preview)}" alt="First page of the {esc(run["name"])} lead sheet" loading="lazy"><span>Open the lead sheet (PDF)</span></a>
  <details class="fold" open><summary>The idea, per the run’s own notes</summary><p>{esc(run["idea"])}</p></details>
  <details class="fold"><summary>Sheet music ({len(run["pdfs"])} PDFs)</summary><p class="note">Engraved with LilyPond, as the run left them. No lyrics.</p><ul>{"".join(pdfs)}</ul></details>
  <details class="fold"><summary>Editable files and the iReal Pro chart</summary>
    <p><a class="btn small" href="files/{k}/{esc(zname)}">Download the MusicXML files (.zip)</a></p>
    <p><button type="button" class="btn small ghost" data-copy="{esc(ireal)}">Copy the iReal Pro link</button></p>
  </details>
</article>"""


def round2_notes():
    """How round 2 was run, for the 'How it was made' section (models named: it sits below the vote)."""
    prompts = []
    for name, label in [("01_compose.txt", "The composition prompt, identical for both runs"),
                        ("02_recording.txt", "The recording prompt, sent to the same session afterwards")]:
        with open(os.path.join(HERE, "waltz_prompts", name), encoding="utf-8") as fh:
            prompts.append(f'<p><strong>{esc(label)}</strong></p><pre class="verbatim">{esc(fh.read().strip())}</pre>')
    return f"""
    <ul>
      <li><strong>Dark, where round 1 was light.</strong> Round 1 asked for &ldquo;bright sounds&rdquo; (lydian triad pairs) in a post-bop tune. Round 2 asked for a darker jazz waltz with a Wayne Shorter-ish feel and Phrygian, sus&#9837;9 sounds, a duo leaning on classical counterpoint, and two more choruses for one instrument that demonstrate soloing techniques 8 bars at a time.</li>
      <li><strong>Two runs, same conditions.</strong> Tenebrae: one Claude Code session, Claude Opus 5.5 at max effort, run headless on 27 September. Noctilucent: one Codex session, GPT-6 Astra at xhigh (its top setting), run unattended on 28 September. Each got the same two prompts, word for word, with no questions answered and no feedback in between.</li>
      <li><strong>Same starting knowledge.</strong> Both could use the four skills written after round 1 (composing, engraving, iReal charts, trial pages) and the round-1 folders and recording engine. Astra worked in a copy of the repo with no trace of Tenebrae. Each read its own memory notes from round 1.</li>
      <li><strong>One slip.</strong> Astra's recording step ran in the main repo by mistake (the command that continues a Codex session can't set a folder). Its tune was already finished; during the recording it saw the file names of Tenebrae's videos but opened none of them. Details in <code>ai_jazz_trial/waltz_prompts/astra_logs/RUN_RECORD.md</code>.</li>
      <li><strong>Hand fixes after listening, applied to both waltzes alike:</strong> the bass raised 4.5 dB, and the shared rhythm-section update (below). Noctilucent's clarinet was also raised about 2 dB because it dipped under the band.</li>
      <li><strong>Time taken.</strong> Tenebrae: 53 minutes to compose, 10 to record. Noctilucent: 27 minutes to compose, 16 to record.</li>
    </ul>
    {"".join(prompts)}"""


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
        tag = "round 2, dark" if r["round"] == 2 else "round 1, bright"
        rows.append(f'<div class="rating-row" data-tune="{k}"><span class="rname">{esc(r["name"])}'
                    f' <span class="rtag">{tag}</span></span><div class="scale" role="radiogroup" aria-label="Rating for '
                    f'{esc(r["name"])}">{stars}</div></div>')
    return "".join(rows)


def main():
    if os.path.isdir(FILES):
        shutil.rmtree(FILES)
    os.makedirs(FILES)
    listen = "".join(listen_card(r) for r in RUNS if r["round"] == 1)
    listen2 = "".join(listen_card(r) for r in RUNS if r["round"] == 2)
    cards = "".join(tune_card(r) for r in RUNS if r["round"] == 1)
    cards2 = "".join(tune_card(r) for r in RUNS if r["round"] == 2)
    asks2 = "".join(f'<li><span class="tip" tabindex="0" data-tip="{esc(q)}">{esc(s)}</span></li>'
                    for s, q in ASKS2)
    asks = "".join(f'<li><span class="tip" tabindex="0" data-tip="{esc(q)}">{esc(s)}</span></li>'
                   for s, q in ASKS)
    now = datetime.datetime.now().strftime("%-d %B %Y, %H:%M")
    subs = dict(
        listen_cards=listen, listen_cards_2=listen2, tune_cards=cards, tune_cards_2=cards2,
        round2_notes=round2_notes(), asks2=asks2,
        tv_cards="".join(tv_card(r) for r in TV_RUNS), tv_prompt_note=esc(TV_PROMPT_NOTE), pref_choices=choices(), rating_rows=rating_rows(),
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
            fh.write(add_anchors(tipify(page)))
    for name in ("style.css", "app.js", "results.js", "robots.txt", "sitemap.xml", "llms.txt"):
        shutil.copy2(os.path.join(SRC, name), os.path.join(PUB, name))
    size = subprocess.run(["du", "-sh", PUB], capture_output=True, text=True).stdout.split()[0]
    print(f"built {os.path.relpath(PUB, REPO)} ({size})")


if __name__ == "__main__":
    main()
