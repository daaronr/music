#!/usr/bin/env python3
"""Build every Halation deliverable from the text sources in src/.

    python3 src/build.py            # MusicXML -> MuseScore -> PDF / .mscz / .musicxml, iReal chart

Pipeline: my MusicXML (notes, layout, chords) is imported by MuseScore 3, the
native .mscx is patched with the MuseJazz house style and with the exact chord
spellings (MusicXML cannot carry "7alt" or "13sus" through MuseScore's import),
then MuseScore renders the PDFs and saves .mscz files.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

from musiclib import BAR, MSCORE_NAME, Chord, parse_changes, parse_chord, parse_line
from xmlwriter import Layout, PartSpec, build_musicxml

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
BUILD = ROOT / "build"
OUT = {"pdf": ROOT / "pdf", "mscz": ROOT / "musescore", "xml": ROOT / "musicxml",
       "ireal": ROOT / "ireal", "audio": ROOT / "audio"}
MSCORE = "/Applications/MuseScore 3.app/Contents/MacOS/mscore"
JAZZ_TEMPLATE = Path("/Applications/MuseScore 3.app/Contents/Resources/templates/05-Jazz/"
                     "01-Jazz_Lead_Sheet.mscx")

TITLE = "Halation"
COMPOSER = "Music: Claude"
TEMPO = 184
TEMPO_TEXT = "Medium-up swing"
BB = (1, 2)              # concert -> written, B-flat trumpet (up a major 2nd)

TRUMPET_BB = dict(name="Trumpet in B♭", abbrev="Tpt.", sound="brass.trumpet.bflat", program=57,
                  transpose=BB)
TRUMPET_C = dict(name="Trumpet (concert pitch)", abbrev="Tpt. (C)", sound="brass.trumpet.c",
                 program=57)
GUITAR = dict(name="Guitar", abbrev="Gtr.", sound="pluck.guitar.electric", program=27, clef="G8vb")


def shifted(changes, bars_offset):
    return [[Chord(c.root_step, c.root_alter, c.suffix, c.tick + bars_offset * BAR) for c in bar]
            for bar in changes]


def load():
    changes = parse_changes((SRC / "changes.txt").read_text())
    head = parse_line((SRC / "head.txt").read_text())
    ending = parse_line("r/8 B4/4.@-~ B4/2@F", start_tick=32 * BAR)
    tpt = parse_line((SRC / "solo_trumpet.txt").read_text())
    gtr = parse_line((SRC / "solo_guitar.txt").read_text())
    assert len(changes) == 32 and len(head) == 32 and len(tpt) == 64 and len(gtr) == 64
    lead_changes = changes + [[parse_chord("Fmaj7#11", 32 * BAR)]]
    return changes, head + ending, lead_changes, tpt, gtr


# ------------------------------------------------------------ score definitions

def lead_sheet_jobs(head, lead_changes):
    layout = Layout(system_breaks=list(range(0, 32, 4)), rehearsal={0: "A", 8: "B", 16: "A'", 24: "C"},
                    double_bars=[7, 15, 23], tempo_text=TEMPO_TEXT, tempo_bpm=TEMPO,
                    repeat_start=0, repeat_end=31, endings=[(30, 31, "1", "1."), (32, 32, "2", "2.")],
                    top_texts={30: ["Solos: repeat the form (take 1st ending)"],
                               32: ["Last time"]})
    jobs = []
    for tag, spec, sub in [("C", TRUMPET_C, "Lead sheet — concert pitch"),
                           ("Bb", TRUMPET_BB, "Lead sheet — B♭ trumpet")]:
        spec = dict(spec)
        spec["name"] = "Melody (concert)" if tag == "C" else "B♭ Trumpet"
        part = PartSpec("P1", bars=head, chords=lead_changes, **spec)
        xml = build_musicxml(TITLE, sub, COMPOSER, [part], layout)
        jobs.append(dict(stem=f"Halation_LeadSheet_{tag}", xml=xml, spatium=1.9,
                         chords=[chord_seq(lead_changes, spec.get("transpose"))],
                         kind="lead"))
    return jobs


def chord_seq(changes, transpose):
    seq = []
    for bar in changes:
        for c in bar:
            cc = c.transposed(*transpose) if transpose else c
            seq.append((cc.tpc(), MSCORE_NAME[cc.suffix], cc.text()))
    return seq


def solo_jobs(changes, tpt, gtr):
    jobs = []
    for k in (1, 2):
        sl = slice(32 * (k - 1), 32 * k)
        ch = shifted(changes, 32 * (k - 1))
        t_bars, g_bars = tpt[sl], gtr[sl]
        rehearsal = {0: "A", 8: "B", 16: "A'", 24: "C"}
        score_layout = Layout(system_breaks=list(range(0, 32, 4)), page_breaks=[16],
                              rehearsal=rehearsal, double_bars=[7, 15, 23],
                              tempo_text=TEMPO_TEXT if k == 1 else f"{TEMPO_TEXT} (chorus 2)",
                              tempo_bpm=TEMPO)
        part_layout = Layout(system_breaks=list(range(0, 32, 4)), rehearsal=rehearsal,
                             double_bars=[7, 15, 23], tempo_text=score_layout.tempo_text,
                             tempo_bpm=TEMPO)
        variants = [
            ("Score_Concert", "concert score", [("T", TRUMPET_C, True), ("G", GUITAR, True)], score_layout, 1.75),
            ("Score_Bb", "transposed score (B♭ trumpet)", [("T", TRUMPET_BB, True), ("G", GUITAR, True)],
             score_layout, 1.75),
            ("Trumpet_Bb", "B♭ trumpet part", [("T", TRUMPET_BB, True)], part_layout, 1.85),
            ("Trumpet_Concert", "trumpet part in concert pitch", [("T", TRUMPET_C, True)], part_layout, 1.85),
            ("Guitar", "guitar part", [("G", GUITAR, True)], part_layout, 1.85),
        ]
        for suffix, label, members, layout, spatium in variants:
            parts, seqs = [], []
            for i, (who, spec, show) in enumerate(members):
                bars = t_bars if who == "T" else g_bars
                parts.append(PartSpec(f"P{i + 1}", bars=bars, chords=ch, show_chords=show, **spec))
                seqs.append(chord_seq(ch, spec.get("transpose")) if show else None)
            sub = f"Trumpet + guitar duo solo — chorus {k} of 2 — {label}"
            xml = build_musicxml(TITLE, sub, COMPOSER, parts, layout)
            jobs.append(dict(stem=f"Halation_Solo_Chorus{k}_{suffix}", xml=xml, spatium=spatium,
                             chords=seqs, kind="score" if len(parts) > 1 else "part"))
    # both choruses in one file, for playback / study
    ch2 = changes + shifted(changes, 32)
    layout = Layout(system_breaks=list(range(0, 64, 4)), page_breaks=[16, 32, 48],
                    rehearsal={0: "A", 8: "B", 16: "A'", 24: "C", 32: "A", 40: "B", 48: "A'", 56: "C"},
                    double_bars=[7, 15, 23, 31, 39, 47, 55], tempo_text=TEMPO_TEXT, tempo_bpm=TEMPO,
                    top_texts={32: ["Chorus 2"]})
    for suffix, tspec in [("Concert", TRUMPET_C), ("Bb", TRUMPET_BB)]:
        parts = [PartSpec("P1", bars=tpt, chords=ch2, **tspec), PartSpec("P2", bars=gtr, chords=ch2, **GUITAR)]
        xml = build_musicxml(TITLE, f"Trumpet + guitar duo solo — both choruses — "
                             f"{'concert' if suffix == 'Concert' else 'transposed'} score", COMPOSER, parts, layout)
        jobs.append(dict(stem=f"Halation_Solo_BothChoruses_Score_{suffix}", xml=xml, spatium=1.7,
                         chords=[chord_seq(ch2, tspec.get("transpose")), chord_seq(ch2, None)], kind="score"))
    return jobs


# ------------------------------------------------------------ MuseScore steps

def run_mscore_jobs(pairs, label):
    """pairs: list of (input path, [output paths]) run in one MuseScore batch."""
    job = [{"in": str(i), "out": [str(o) for o in outs]} for i, outs in pairs]
    jf = BUILD / f"job_{label}.json"
    jf.write_text(json.dumps(job, indent=1))
    res = subprocess.run([MSCORE, "-j", str(jf)], capture_output=True, text=True)
    missing = [str(o) for _, outs in pairs for o in outs if not Path(o).exists()]
    if missing:
        print(res.stdout[-3000:], res.stderr[-3000:])
        raise SystemExit(f"MuseScore did not produce: {missing}")


def jazz_style_children():
    tree = ET.parse(JAZZ_TEMPLATE)
    return list(tree.getroot().find("Score/Style"))


STYLE_OVERRIDES = {
    "pageWidth": "8.5", "pageHeight": "11", "pagePrintableWidth": "7.5",
    "pageEvenLeftMargin": "0.5", "pageOddLeftMargin": "0.5", "pageEvenTopMargin": "0.45",
    "pageEvenBottomMargin": "0.5", "pageOddTopMargin": "0.45", "pageOddBottomMargin": "0.5",
    "pageTwosided": "0", "showMeasureNumber": "1", "showMeasureNumberOne": "0",
    "measureNumberSystem": "1", "swingUnit": "eighth", "swingRatio": "62",
    "lastSystemFillLimit": "0", "enableIndentationOnFirstSystem": "0",
    "chordSymbolAFontSize": "14", "chordSymbolBFontSize": "12",
    "createMultiMeasureRests": "0", "hideInstrumentNameIfOneInstrument": "1",
    "concertPitch": "0", "rehearsalMarkFontSize": "13", "subTitleFontSize": "13",
    "composerFontSize": "11", "titleFontSize": "30",
}


def patch_mscx(path: Path, spatium: float, chord_lists, kind: str):
    tree = ET.parse(path)
    score = tree.getroot().find("Score")
    style = score.find("Style")
    existing = {c.tag: c for c in style}
    for child in jazz_style_children():
        if child.tag in existing:
            style.remove(existing[child.tag])
        style.append(child)
    overrides = dict(STYLE_OVERRIDES, Spatium=f"{spatium}")
    if kind == "score":
        overrides.update({"staffDistance": "5.5", "akkoladeDistance": "5.5",
                          "minSystemDistance": "7", "maxSystemDistance": "14"})
    else:
        overrides.update({"minSystemDistance": "6", "maxSystemDistance": "12"})
    existing = {c.tag: c for c in style}
    for tag, val in overrides.items():
        el = existing.get(tag)
        if el is None:
            el = ET.SubElement(style, tag)
        el.text = val
    # exact chord spellings
    staves = score.findall("Staff")
    for si, staff in enumerate(staves):
        harms = staff.findall(".//Harmony")
        want = chord_lists[si] if si < len(chord_lists) else None
        if want is None:
            if harms:
                raise SystemExit(f"{path.name}: staff {si + 1} has unexpected chord symbols")
            continue
        if len(harms) != len(want):
            raise SystemExit(f"{path.name}: staff {si + 1} has {len(harms)} chords, expected {len(want)}")
        for h, (tpc, name, _) in zip(harms, want):
            got = int(h.findtext("root"))
            if got != tpc:
                raise SystemExit(f"{path.name}: chord root {got} != expected {tpc} ({name})")
            for tag in ("name", "base"):
                old = h.find(tag)
                if old is not None:
                    h.remove(old)
            n = ET.Element("name")
            n.text = name
            h.insert(list(h).index(h.find("root")) + 1, n)
    tree.write(path, encoding="UTF-8", xml_declaration=True)


# ------------------------------------------------------------ iReal Pro

IREAL_QUALITY = {"maj7#11": "^7#11", "maj7#5": "^7#5", "7sus(b9)": "7b9sus", "7alt": "7alt",
                 "m9": "-9", "13sus": "13sus", "m7": "-7", "7": "7", "7(b9)": "7b9",
                 "m7b5": "h7", "m(maj7)": "-^7", "9(#11)": "9#11", "7(#11)": "7#11"}


def ireal(changes):
    marks = {0: "*A", 8: "*B", 16: "*A", 24: "*C"}
    cells = []
    for bi, bar in enumerate(changes):
        prefix = ""
        if bi in marks:
            prefix = ("[" if bi == 0 else "[") + marks[bi] + ("T44" if bi == 0 else "")
        chords = [c.root_name() + IREAL_QUALITY[c.suffix] for c in bar]
        body = chords[0] + "   " if len(chords) == 1 else " ".join(chords) + " "
        end = "|"
        if bi in (7, 15, 23):
            end = "]"
        elif bi == 31:
            end = "Z"
        cells.append(prefix + body + end)
    prog = "".join(cells)
    raw = f"{TITLE}=Claude=Medium Up Swing=F=n={prog}"
    url = "irealbook://" + urllib.parse.quote(raw, safe="=")
    return raw, prog, url


def write_ireal(changes):
    raw, prog, url = ireal(changes)
    OUT["ireal"].mkdir(exist_ok=True)
    (OUT["ireal"] / "Halation_iReal_link.txt").write_text(url + "\n")
    rows = []
    for i in range(0, 32, 4):
        cells = []
        for bar in changes[i:i + 4]:
            cells.append("<td>" + " &nbsp; ".join(c.text() for c in bar) + "</td>")
        label = {0: "A", 8: "B", 16: "A'", 24: "C"}.get(i, "")
        rows.append(f"<tr><th>{label}</th>{''.join(cells)}</tr>")
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Halation iReal Pro</title>
<style>
 body {{ font-family: -apple-system, Helvetica, Arial, sans-serif; max-width: 760px; margin: 2em auto;
        padding: 0 16px; line-height: 1.45; color: #1d1d1f; background: #fff; }}
 a.button {{ display: inline-block; padding: .6em 1.1em; background: #1d4ed8; color: #fff;
            border-radius: 8px; text-decoration: none; font-weight: 600; }}
 table {{ border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 15px; }}
 td, th {{ border: 1px solid #ccc; padding: .45em .5em; }}
 th {{ width: 2.2em; background: #f2f2f2; }}
 code {{ word-break: break-all; font-size: 12px; }}
</style></head><body>
<h1>Halation &mdash; iReal Pro chart</h1>
<p>Open this page on the Mac or iPhone/iPad that has iReal Pro, then tap the button.
iReal Pro will offer to import the song (style: Medium Up Swing, key of F, 32 bars, ABA'C).</p>
<p><a class="button" href="{url}">Import &ldquo;Halation&rdquo; into iReal Pro</a></p>
<table>{''.join(rows)}</table>
<p>Head: play once in, solos over the form, head out; last time end on Fmaj7#11 (the
turnaround in bars 31&ndash;32 is the Lady Bird turnaround with every chord lydian).</p>
<p>Chart text (iReal Pro syntax):</p>
<p><code>{prog}</code></p>
</body></html>
"""
    (OUT["ireal"] / "Halation_iReal.html").write_text(html)
    return url


# ------------------------------------------------------------ main

def main():
    for d in [BUILD, *OUT.values()]:
        d.mkdir(exist_ok=True)
    changes, lead, lead_changes, tpt, gtr = load()
    jobs = lead_sheet_jobs(lead, lead_changes) + solo_jobs(changes, tpt, gtr)
    only = sys.argv[1] if len(sys.argv) > 1 else None
    if only:
        jobs = [j for j in jobs if only in j["stem"]]
    for j in jobs:
        (BUILD / f"{j['stem']}.musicxml").write_text(j["xml"])
    run_mscore_jobs([(BUILD / f"{j['stem']}.musicxml", [BUILD / f"{j['stem']}.mscx"]) for j in jobs],
                    "import")
    for j in jobs:
        patch_mscx(BUILD / f"{j['stem']}.mscx", j["spatium"], j["chords"], j["kind"])
    exports = []
    for j in jobs:
        s = j["stem"]
        outs = [OUT["pdf"] / f"{s}.pdf", OUT["mscz"] / f"{s}.mscz", OUT["xml"] / f"{s}.musicxml"]
        exports.append((BUILD / f"{s}.mscx", outs))
    run_mscore_jobs(exports, "export")
    url = write_ireal(changes)
    print(f"built {len(jobs)} scores; iReal link {len(url)} chars")


if __name__ == "__main__":
    main()
