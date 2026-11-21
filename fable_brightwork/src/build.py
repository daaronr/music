#!/usr/bin/env python3
"""Build every Brightwork deliverable: MusicXML, LilyPond -> PDF, iReal Pro chart.

Usage: python3 build.py [--no-pdf]
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import engine as E  # noqa: E402
import music_head as H  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
XML, PDF, LY = ROOT / "musicxml", ROOT / "pdf", ROOT / "lilypond"
LILYPOND = "/opt/homebrew/bin/lilypond"


def part(pid, name, abbr, bars, changes, fifths=0, clef="G", transpose=None, program=57):
    return dict(id=pid, name=name, abbr=abbr, bars=bars, chords=changes, fifths=fifths, clef=clef,
                transpose=transpose, midi_program=program)


def emit(stem, parts, sections, subtitle, poet="", **ly_opts):
    """Write <stem>.musicxml and <stem>.ly; return the .ly path."""
    XML.mkdir(exist_ok=True)
    LY.mkdir(exist_ok=True)
    xml = E.musicxml(H.TITLE, H.COMPOSER, parts, sections, H.TEMPO, H.TEMPO_TEXT, subtitle=subtitle)
    (XML / f"{stem}.musicxml").write_text(xml, encoding="utf-8")
    ly = E.lilypond(H.TITLE, H.COMPOSER, parts, sections, H.TEMPO, H.TEMPO_TEXT, subtitle=subtitle,
                    poet=poet, **ly_opts)
    path = LY / f"{stem}.ly"
    path.write_text(ly, encoding="utf-8")
    return path


def main():
    jobs = []
    head = E.parse_part(H.HEAD)
    ch_c = E.parse_changes(H.CHANGES)
    ch_bb = E.parse_changes(H.CHANGES, 1, 2)
    head_bb = E.transpose_part(head, 1, 2)

    jobs.append(emit("Brightwork_01_lead_sheet_concert",
                     [part("P1", "Lead (concert)", "C", head, ch_c)], H.SECTIONS,
                     "Lead sheet - concert pitch", staffsize=20, sysdist=15))
    jobs.append(emit("Brightwork_02_lead_sheet_Bb",
                     [part("P1", "Trumpet in Bb", "Bb Tpt.", head_bb, ch_bb, fifths=2, transpose=(-1, -2))],
                     H.SECTIONS, "Lead sheet - B-flat instruments", staffsize=20, sysdist=15))

    try:
        import music_solo as S
    except ImportError:
        S = None
    if S is not None:
        import solo_jobs
        jobs += solo_jobs.build(E, H, S, part, emit, ch_c, ch_bb)

    import ireal
    music, _ = ireal.write_chart(ROOT / "ireal", H.TITLE, "Claude (AI)", "Medium Up Swing", "F", H.TEMPO,
                                 H.CHANGES, H.SECTIONS, E.QUAL, E.parse_chord, E.root_name)
    print("iReal chart:", music)

    if "--no-pdf" in sys.argv:
        return
    PDF.mkdir(exist_ok=True)
    for ly in jobs:
        r = subprocess.run([LILYPOND, "--loglevel=WARNING", "-o", str(PDF / ly.stem), str(ly)],
                           capture_output=True, text=True)
        if r.returncode or r.stderr.strip():
            print(f"--- lilypond {ly.name}\n{r.stderr}")
        print("built", ly.stem + ".pdf")
    pdfs = [str(PDF / (ly.stem + ".pdf")) for ly in jobs]
    subprocess.run(["/opt/homebrew/bin/pdfunite", *pdfs, str(ROOT / "Brightwork_complete.pdf")], check=True)
    print("built Brightwork_complete.pdf")


if __name__ == "__main__":
    main()
