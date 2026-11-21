#!/usr/bin/env python3
"""Check the generated MusicXML.

  python3 verify.py [path/to/musicxml.xsd]

1. Re-reads every file and confirms each bar of each part adds up to 4 beats and
   that the pitches equal the source music (after the stated transposition).
2. If an XSD path is given, validates each file against it with xmllint.
"""
import subprocess
import sys
import xml.etree.ElementTree as ET
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import engine as E  # noqa: E402
import music_head as H  # noqa: E402
import music_solo as S  # noqa: E402

XML = Path(__file__).resolve().parent.parent / "musicxml"


def read_part(part):
    """-> (list of bar lengths in quarters, list of sounding-as-written midi numbers, n harmonies)"""
    div, lengths, pitches, nharm = None, [], [], 0
    for meas in part.findall("measure"):
        pos = F(0)
        for el in meas:
            if el.tag == "attributes" and el.find("divisions") is not None:
                div = int(el.find("divisions").text)
            elif el.tag == "harmony":
                nharm += 1
            elif el.tag == "backup":
                pos -= F(int(el.find("duration").text), div)
            elif el.tag == "forward":
                pos += F(int(el.find("duration").text), div)
            elif el.tag == "note":
                if el.find("chord") is None:
                    pos += F(int(el.find("duration").text), div)
                p = el.find("pitch")
                tied_in = any(t.get("type") == "stop" for t in el.findall("tie"))
                if p is not None and not tied_in:
                    alter = int(p.find("alter").text) if p.find("alter") is not None else 0
                    pitches.append(12 * (int(p.find("octave").text) + 1)
                                   + E.STEP_PC[p.find("step").text] + alter)
        lengths.append(pos)
    return lengths, pitches, nharm


def source_pitches(bars, semis=0):
    return [E.midi(p) + semis for evs in bars for e in evs for p in e.pitches if not e.tied_in]


def main():
    head, tpt, gtr = E.parse_part(H.HEAD), E.parse_part(S.TRUMPET), E.parse_part(S.GUITAR)
    nch = sum(len(b.split()) for b in H.CHANGES)
    expect = {
        "Brightwork_01_lead_sheet_concert": [(head, 0, nch)],
        "Brightwork_02_lead_sheet_Bb": [(head, 2, nch)],
        "Brightwork_03_duo_solo_score_concert": [(tpt, 0, 2 * nch), (gtr, 0, 0)],
        "Brightwork_04_trumpet_solo_concert": [(tpt, 0, 2 * nch)],
        "Brightwork_05_trumpet_solo_Bb": [(tpt, 2, 2 * nch)],
        "Brightwork_06_guitar_solo": [(gtr, 0, 2 * nch)],
    }
    ok = True
    for stem, parts in expect.items():
        path = XML / f"{stem}.musicxml"
        root = ET.parse(path).getroot()
        xml_parts = root.findall("part")
        assert len(xml_parts) == len(parts), stem
        for xp, (bars, semis, nharm) in zip(xml_parts, parts):
            lengths, pitches, got_harm = read_part(xp)
            good = (len(lengths) == len(bars) and all(x == 4 for x in lengths)
                    and pitches == source_pitches(bars, semis) and got_harm == nharm)
            ok &= good
            print(f"{'ok ' if good else 'BAD'} {stem} part {xp.get('id')}: {len(lengths)} bars, "
                  f"{len(pitches)} notes, {got_harm} chord symbols")
        if len(sys.argv) > 1:
            r = subprocess.run(["xmllint", "--noout", "--nonet", "--schema", sys.argv[1], str(path)],
                               capture_output=True, text=True)
            good = r.returncode == 0
            ok &= good
            print(f"{'ok ' if good else 'BAD'} {stem}: MusicXML 3.1 schema {r.stderr.strip()[-60:]}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
