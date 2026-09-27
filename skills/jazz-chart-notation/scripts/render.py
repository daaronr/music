"""Render MusicXML through the MuseScore 3 command line.

    python3 render.py score.musicxml                 # -> score.mscz + score.pdf next to it
    python3 render.py score.musicxml --formats pdf,mid --png

Import -> patch the MuseScore style (page numbers to the footer, so they never collide
with rehearsal marks) -> export from the patched .mscz. `--png` also writes page images
with pdftoppm for a quick visual check (Read the PNGs; don't trust the XML alone).
"""

from __future__ import annotations

import argparse
import os
import subprocess
import tempfile
import zipfile

MSCORE = os.environ.get("MSCORE", "/Applications/MuseScore 3.app/Contents/MacOS/mscore")
STYLE_PATCH = ("<showHeader>0</showHeader><footerFirstPage>0</footerFirstPage>"
               "<oddFooterC>$p</oddFooterC><evenFooterC>$p</evenFooterC>")


def mscore(src: str, dest: str) -> None:
    """Convert with MuseScore; the libjack warnings it prints on macOS are harmless."""
    res = subprocess.run([MSCORE, "-o", dest, src], capture_output=True, text=True)
    if res.returncode != 0 or not os.path.exists(dest):
        raise SystemExit(f"MuseScore failed: {src} -> {dest}\n{res.stdout[-1500:]}\n{res.stderr[-1500:]}")


def patch_style(src_mscz: str, dest_mscz: str, extra: str = "") -> None:
    """Insert style tags into the .mscx inside a .mscz (e.g. extra='<Spatium>1.6</Spatium>')."""
    with zipfile.ZipFile(src_mscz) as zin:
        items = [(info, zin.read(info.filename)) for info in zin.infolist()]
    with zipfile.ZipFile(dest_mscz, "w", zipfile.ZIP_DEFLATED) as zout:
        for info, data in items:
            if info.filename.endswith(".mscx"):
                text = data.decode("utf-8")
                data = text.replace("</Style>", STYLE_PATCH + extra + "</Style>", 1).encode("utf-8")
            zout.writestr(info, data)


def render(xml_path: str, formats=("pdf", "mscz"), png: bool = False, dpi: int = 90) -> list:
    base = os.path.splitext(xml_path)[0]
    written = []
    with tempfile.TemporaryDirectory() as tmp:
        raw = os.path.join(tmp, "raw.mscz")
        mscore(xml_path, raw)
        styled = f"{base}.mscz" if "mscz" in formats else os.path.join(tmp, "styled.mscz")
        patch_style(raw, styled)
        if "mscz" in formats:
            written.append(styled)
        for fmt in formats:
            if fmt == "mscz":
                continue
            dest = f"{base}.{fmt}"
            mscore(styled, dest)
            written.append(dest)
    if png and os.path.exists(f"{base}.pdf"):
        subprocess.run(["pdftoppm", "-r", str(dpi), "-png", f"{base}.pdf", f"{base}-page"],
                       check=True)
        written.append(f"{base}-page-*.png")
    return written


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("musicxml")
    ap.add_argument("--formats", default="pdf,mscz", help="comma list: pdf, mscz, mid, mp3, png")
    ap.add_argument("--png", action="store_true", help="also rasterize the PDF for checking")
    args = ap.parse_args()
    for path in render(args.musicxml, tuple(args.formats.split(",")), png=args.png):
        print("wrote", path)
