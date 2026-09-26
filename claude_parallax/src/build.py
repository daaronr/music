"""Build every Parallax output: MusicXML, MuseScore (.mscz) and PDF.

Run:  python3 src/build.py            (writes to output/)
"""

from __future__ import annotations

import os
import subprocess
import sys

import check
import tune
from musicxml import PartSpec, ScoreSpec, write_score
from notation import Measure, link_ties, parse_chords, parse_measure

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output")
MSCORE = "/Applications/MuseScore 3.app/Contents/MacOS/mscore"
BB = (1, 2)   # Bb trumpet: written a major 2nd above concert


def build_measures(chords, lines, where, bars_per_system=4, rehearsals=None, texts=None,
                   section_ends=()):
    out = []
    for i, (ch, line) in enumerate(zip(chords, lines)):
        m = Measure(parse_measure(line, f"{where} bar {i + 1}"), parse_chords(ch))
        m.new_system = i % bars_per_system == 0
        if rehearsals and i in rehearsals:
            m.rehearsal = rehearsals[i]
        if texts and i in texts:
            m.texts.append((0, texts[i], "first"))
        if i in section_ends:
            m.barline = "light-light"
        out.append(m)
    return out


def lead_sheet_measures():
    intro = build_measures(tune.INTRO_CHORDS, tune.INTRO, "intro",
                           texts={0: "Intro — guitar alone (trumpet tacet)"},
                           section_ends=(3,))
    head = build_measures(tune.FORM, tune.HEAD, "head", rehearsals=tune.SECTIONS,
                          texts={0: "Head — then solos on the 32-bar form"},
                          section_ends=(7, 15, 23, 31))
    coda = build_measures(tune.CODA_CHORDS, tune.CODA, "coda", rehearsals={0: "Coda"},
                          texts={0: "After the last head: tag bars 31–32, then"})
    coda[-1].barline = "light-heavy"
    for m in intro:
        m.implicit = True
    ms = intro + head + coda
    link_ties(ms)
    return ms


# Page numbers go to the footer (the header number collided with rehearsal marks).
STYLE_PATCH = ("<showHeader>0</showHeader><footerFirstPage>0</footerFirstPage>"
               "<oddFooterC>$p</oddFooterC><evenFooterC>$p</evenFooterC>")


def _mscore(src, dest):
    res = subprocess.run([MSCORE, "-o", dest, src], capture_output=True, text=True)
    if res.returncode != 0 or not os.path.exists(dest):
        print(res.stdout[-2000:], res.stderr[-2000:])
        raise SystemExit(f"MuseScore failed: {src} -> {dest}")


def _patch_style(src_mscz, dest_mscz):
    import zipfile
    with zipfile.ZipFile(src_mscz) as zin:
        items = [(info, zin.read(info.filename)) for info in zin.infolist()]
    with zipfile.ZipFile(dest_mscz, "w", zipfile.ZIP_DEFLATED) as zout:
        for info, data in items:
            if info.filename.endswith(".mscx"):
                text = data.decode("utf-8")
                if "</Style>" not in text:
                    raise SystemExit(f"no <Style> block in {src_mscz}")
                data = text.replace("</Style>", STYLE_PATCH + "</Style>", 1).encode("utf-8")
            zout.writestr(info, data)


def render(xml_path, formats=("pdf", "mscz")):
    """MusicXML -> MuseScore import -> style patch -> .mscz and/or .pdf."""
    base = os.path.splitext(xml_path)[0]
    name = os.path.basename(base)
    raw = os.path.join(ROOT, "build", name + "_raw.mscz")
    styled = f"{base}.mscz" if "mscz" in formats else os.path.join(ROOT, "build",
                                                                   name + "_styled.mscz")
    _mscore(xml_path, raw)
    _patch_style(raw, styled)
    if "mscz" in formats:
        print("  wrote", os.path.relpath(styled, ROOT))
    if "pdf" in formats:
        _mscore(styled, f"{base}.pdf")
        print("  wrote", os.path.relpath(f"{base}.pdf", ROOT))


def build_lead_sheets(do_render=True):
    footer = ("Form: Intro (guitar, 4) – Head AABA (32) – duo solo, 2 choruses "
              "– Head – Coda")
    for label, transpose, fname, left in [
        ("concert", None, "Parallax_lead_sheet_concert", "Concert pitch (C)"),
        ("Bb", BB, "Parallax_lead_sheet_Bb_trumpet", "Trumpet in B♭"),
    ]:
        part = PartSpec("P1", "Melody" if not transpose else "Trumpet in Bb",
                        "Mel." if not transpose else "Tpt.", lead_sheet_measures(),
                        transpose=transpose, simplify=bool(transpose))
        score = ScoreSpec(tune.TITLE, [part], subtitle=tune.SUBTITLE, composer=tune.COMPOSER,
                          left_label=left, tempo_text=tune.TEMPO_TEXT, bpm=tune.BPM,
                          credits_extra=[(footer, 0.5, -75, 8, "center")], staff_mm=6.1,
                          system_distance=90)
        path = os.path.join(OUT, fname + ".musicxml")
        write_score(score, path)
        print("  wrote", os.path.relpath(path, ROOT))
        if do_render:
            render(path)


def solo_measures(instrument, bars_per_system=4, page_per_chorus=False):
    import solo_ch1
    import solo_ch2
    lines = (solo_ch1.TPT + solo_ch2.TPT) if instrument == "tpt" else \
        (solo_ch1.GTR + solo_ch2.GTR)
    chords = tune.FORM + tune.FORM
    rehearsals = {0: "1A", 8: "1A", 16: "1B", 24: "1A", 32: "2A", 40: "2A", 48: "2B", 56: "2A"}
    ms = build_measures(chords, lines, f"solo-{instrument}", bars_per_system,
                        rehearsals=rehearsals,
                        texts={0: "Chorus 1", 32: "Chorus 2"},
                        section_ends=(7, 15, 23, 31, 39, 47, 55))
    ms[31].barline = "light-light"
    ms[-1].barline = "light-heavy"
    if page_per_chorus:
        ms[32].new_page = True
    link_ties(ms)
    return ms


def run_checks():
    print("Head check (flags = notes outside the implied chord scale):")
    head = build_measures(tune.FORM, tune.HEAD, "head")
    check.check(head, "head")
    lo, hi = check.span(head)
    print(f"  head range MIDI {lo}-{hi}")
    tpt, gtr = solo_measures("tpt"), solo_measures("gtr")
    print("Solo check, trumpet:")
    check.check(tpt, "tpt")
    print("Solo check, guitar:")
    check.check(gtr, "gtr", instrument="guitar")
    print("Counterpoint (unisons and minor 2nd/9th rubs between the players):")
    check.counterpoint(tpt, gtr)
    for name, ms in (("tpt", tpt), ("gtr", gtr)):
        lo, hi = check.span(ms)
        print(f"  {name} range MIDI {lo}-{hi}")


SOLO_TITLE = "Parallax — duo solo"
SOLO_SUB = "trumpet & guitar, 2 choruses on the 32-bar form (AABA)"


def build_solos(do_render=True):
    jobs = []
    # study score: both players in concert pitch, analysis notes printed
    tpt = PartSpec("P1", "Trumpet (concert)", "Tpt.", solo_measures("tpt", page_per_chorus=True))
    gtr = PartSpec("P2", "Guitar", "Gtr.", solo_measures("gtr", page_per_chorus=True),
                   clef="treble8vb", program=27, show_chords=False)
    jobs.append(("Parallax_duo_solo_score_concert",
                 ScoreSpec(SOLO_TITLE, [tpt, gtr], subtitle=SOLO_SUB, composer=tune.COMPOSER,
                           left_label="Score in C",
                           tempo_text=tune.TEMPO_TEXT, bpm=tune.BPM, annotations=True,
                           credits_extra=[("Small purple notes under the staves name the "
                                           "device in use.", 0.5, -75, 8, "center")],
                           staff_mm=5.8),
                 ("pdf",)))
    # transposing score for MuseScore (toggle Concert Pitch there; parts extract cleanly)
    tpt_bb = PartSpec("P1", "Trumpet in Bb", "Tpt.", solo_measures("tpt"), transpose=BB,
                      simplify=True)
    gtr_plain = PartSpec("P2", "Guitar", "Gtr.", solo_measures("gtr"), clef="treble8vb",
                         program=27)
    jobs.append(("Parallax_duo_solo_MuseScore",
                 ScoreSpec(SOLO_TITLE, [tpt_bb, gtr_plain], subtitle=SOLO_SUB,
                           composer=tune.COMPOSER, tempo_text=tune.TEMPO_TEXT, bpm=tune.BPM),
                 ("mscz",)))
    # individual parts, one chorus per page
    for fname, label, part in [
        ("Parallax_solo_trumpet_concert", "Trumpet — concert pitch",
         PartSpec("P1", "Trumpet (concert)", "Tpt.", solo_measures("tpt", page_per_chorus=True))),
        ("Parallax_solo_trumpet_Bb", "Trumpet in B♭",
         PartSpec("P1", "Trumpet in Bb", "Tpt.", solo_measures("tpt", page_per_chorus=True),
                  transpose=BB, simplify=True)),
        ("Parallax_solo_guitar", "Guitar (sounds 8vb)",
         PartSpec("P1", "Guitar", "Gtr.", solo_measures("gtr", page_per_chorus=True),
                  clef="treble8vb", program=27)),
    ]:
        jobs.append((fname, ScoreSpec(SOLO_TITLE, [part], subtitle=SOLO_SUB,
                                      composer=tune.COMPOSER, left_label=label,
                                      tempo_text=tune.TEMPO_TEXT, bpm=tune.BPM),
                     ("pdf", "mscz")))
    for fname, score, formats in jobs:
        path = os.path.join(OUT, fname + ".musicxml")
        write_score(score, path)
        print("  wrote", os.path.relpath(path, ROOT))
        if do_render:
            render(path, formats)


if __name__ == "__main__":
    run_checks()
    render_on = "--no-render" not in sys.argv
    if "--solos-only" not in sys.argv:
        build_lead_sheets(do_render=render_on)
    build_solos(do_render=render_on)
