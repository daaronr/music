"""Parse Glory_of_the_pumpkin.mscx: per-measure chords, melody notes and lyrics."""
import json
import sys
import xml.etree.ElementTree as ET
from fractions import Fraction

TPC = {9: "Db", 10: "Ab", 11: "Eb", 12: "Bb", 13: "F", 14: "C", 15: "G", 16: "D",
       17: "A", 18: "E", 19: "B", 20: "F#", 21: "C#", 22: "G#"}
DUR = {"whole": Fraction(4), "half": Fraction(2), "quarter": Fraction(1), "eighth": Fraction(1, 2),
       "16th": Fraction(1, 4), "32nd": Fraction(1, 8)}

root = ET.parse(sys.argv[1]).getroot()
staff = root.find(".//Score/Staff")
measures = []
for m in staff.findall("Measure"):
    voice = m.find("voice")
    pos = Fraction(0)
    events = []
    chords = []
    tuplet = None
    for el in list(voice):
        if el.tag == "Tuplet":
            tuplet = Fraction(int(el.findtext("normalNotes")), int(el.findtext("actualNotes")))
        elif el.tag == "endTuplet":
            tuplet = None
        elif el.tag == "Harmony":
            r = int(el.findtext("root"))
            chords.append((float(pos), TPC[r] + (el.findtext("name") or "")))
        elif el.tag in ("Chord", "Rest"):
            d = DUR.get(el.findtext("durationType"), None)
            if d is None:  # measure rest
                d = Fraction(4)
            if el.find("dots") is not None:
                d = d * Fraction(3, 2)
            if tuplet:
                d = d * tuplet
            if el.tag == "Chord":
                pitch = int(el.find("Note").findtext("pitch"))
                tie = el.find("Note/Spanner[@type='Tie']/next") is not None
                lyr = el.findtext("Lyrics/text")
                events.append(dict(pos=float(pos), dur=float(d), pitch=pitch, lyric=lyr, tie=tie))
            pos += d
    measures.append(dict(chords=chords, notes=events, length=float(pos)))

json.dump(measures, open(sys.argv[2], "w"), indent=1)
for i, m in enumerate(measures):
    ch = " ".join(f"{c}@{p:g}" for p, c in m["chords"])
    ly = " ".join((n["lyric"] or "~") for n in m["notes"])
    ps = " ".join(str(n["pitch"]) for n in m["notes"])
    print(f"{i+1:2d} [{m['length']:g}] {ch:28s} | {ly} | {ps}")
