"""Print the structure of a MusicXML file: parts, transposition, clefs, measures
with marks/repeats/endings, and sounding-pitch range per part."""
import sys
import xml.etree.ElementTree as ET

STEP = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def main(path):
    root = ET.parse(path).getroot()
    names = {sp.get("id"): (sp.findtext("part-name") or "") for sp in root.iter("score-part")}
    print(path)
    for part in root.findall("part"):
        pid = part.get("id")
        measures = part.findall("measure")
        trans = None
        clef_oct = None
        lo, hi, n = 999, -1, 0
        marks = []
        for mi, m in enumerate(measures):
            for t in m.iter("transpose"):
                trans = (t.findtext("diatonic"), t.findtext("chromatic"), t.findtext("octave-change"))
            for c in m.iter("clef"):
                clef_oct = c.findtext("clef-octave-change")
            for r in m.iter("rehearsal"):
                marks.append(f"m{mi + 1}:[{r.text}]")
            for w in m.iter("words"):
                if w.text and w.text.strip():
                    marks.append(f"m{mi + 1}:'{w.text.strip()[:30]}'")
            for b in m.iter("barline"):
                rep = b.find("repeat")
                end = b.find("ending")
                if rep is not None:
                    marks.append(f"m{mi + 1}:repeat-{rep.get('direction')}")
                if end is not None:
                    marks.append(f"m{mi + 1}:ending{end.get('number')}-{end.get('type')}")
            for s in m.iter("segno"):
                marks.append(f"m{mi + 1}:segno")
            for s in m.iter("coda"):
                marks.append(f"m{mi + 1}:coda")
            for note in m.iter("note"):
                p = note.find("pitch")
                if p is None:
                    continue
                midi = 12 * (int(p.findtext("octave")) + 1) + STEP[p.findtext("step")] + int(float(p.findtext("alter") or 0))
                lo, hi, n = min(lo, midi), max(hi, midi), n + 1
        print(f"  part {pid} '{names.get(pid)}' measures={len(measures)} transpose={trans} "
              f"clef-oct={clef_oct} written range {lo}-{hi} notes={n}")
        print("   ", " ".join(marks)[:1500])


for p in sys.argv[1:]:
    main(p)
