"""List every human-readable text string in MusicXML / MuseScore / HTML files.

Notes, rests and layout numbers are skipped; titles, credits, directions, metadata,
instrument names, link targets and similar text are printed (deduplicated per file).
"""

import re
import sys
import zipfile
from xml.etree import ElementTree as ET

SKIP_TAGS = {"step", "octave", "alter", "duration", "type", "voice", "stem", "beam",
             "divisions", "fifths", "beats", "beat-type", "sign", "line", "staff",
             "accidental", "dot", "tie", "tied", "pitch", "tpc", "tpc2", "durationType",
             "track", "velocity", "lid", "subtype", "direction", "pos", "offset",
             "placement", "normal-notes", "actual-notes", "normal-type", "degree-value",
             "degree-alter", "degree-type", "root-step", "root-alter", "bass-step",
             "bass-alter", "midi-channel", "midi-program", "volume", "pan", "chromatic",
             "diatonic", "octave-change", "per-minute", "beat-unit", "tenths",
             "millimeters", "page-height", "page-width", "left-margin", "right-margin",
             "top-margin", "bottom-margin", "system-distance", "top-system-distance",
             "staff-distance", "BarLine", "Spatium", "fret", "string"}


def texts_from_xml(data: bytes):
    out = set()
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        return {f"<<parse error {exc}>>"}
    for el in root.iter():
        tag = el.tag.split("}")[-1]
        if tag in SKIP_TAGS:
            continue
        t = (el.text or "").strip()
        if t and not re.fullmatch(r"[-\d.\s]+", t):
            out.add(f"{tag}: {t[:160]}")
        for k, v in el.attrib.items():
            if k in ("text", "name", "href", "value") and v and not re.fullmatch(r"[-\d.]+", v):
                out.add(f"{tag}@{k}: {v[:160]}")
    return out


def scan(path):
    print("#", path)
    if path.endswith(".mscz"):
        with zipfile.ZipFile(path) as z:
            print("  members:", z.namelist())
            for name in z.namelist():
                if name.endswith(".mscx"):
                    for t in sorted(texts_from_xml(z.read(name))):
                        print("  ", t)
    elif path.endswith((".musicxml", ".xml", ".mscx")):
        for t in sorted(texts_from_xml(open(path, "rb").read())):
            print("  ", t)
    else:
        text = open(path, encoding="utf-8", errors="replace").read()
        body = re.sub(r"<[^>]+>", " ", text)
        print("  TEXT:", " ".join(body.split())[:3000])
        for href in re.findall(r'href="([^"]+)"', text):
            print("  HREF:", href[:300])


BRIEF = {"credit-words", "words", "creator", "rights", "software", "metaTag", "text",
         "rehearsal", "lyric", "movement-title", "work-title", "part-name", "longName",
         "instrument-name", "source", "encoder"}

if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--brief":
        args = args[1:]
        _orig = texts_from_xml

        def texts_from_xml(data):  # noqa: F811 - brief filter
            return {t for t in _orig(data) if t.split(":")[0].split("@")[0] in BRIEF}
    for p in args:
        scan(p)
