# Project Memory

## Gig Packet / Sheet Music PDF Workflow

- Source sheet music lives primarily under `/Users/yosemite/Dropbox/sheet_music/kay_house_itsawonderfulband_music/`.
- For the Real Book Fifth Edition scan at `The Real Book vol 1.pdf`, the printed tune page maps to PDF page `printed page + 13`. The first tune page is PDF page 14.
- Useful local tools for sheet packet assembly:
  - `pdfinfo` for page counts and metadata.
  - `pdftoppm` for visual spot checks.
  - `pdfunite` for final merged packets.
  - `pdflatex` with `pdfpages`, `graphicx`, and `eso-pic` for extracting pages and adding cue text.
- Avoid relying on OCR for this Real Book PDF; it is a scan with no useful text layer. Use the index pages visually to map printed page numbers.
- For Boox/Preview annotation packets, create both:
  - `00_<gig>_full_set.pdf` as a single ordered packet.
  - `01_...pdf`, `02_...pdf`, etc. as per-tune ordered files.
- For cue notes, use a dedicated top text band where possible, especially on image/photo pages. Overlays can land unexpectedly when images are rotated or pages have mixed orientation.
- Keep cue text short, high-contrast, and about 9pt. Smaller bottom notes were too easy to miss during rehearsal/gig use.
- For the Nell's birthday packet, the working generator was created at `/private/tmp/nells_build/make_packet.py`; final output went to `/Users/yosemite/Dropbox/sheet_music/kay_house_itsawonderfulband_music/nells_birthday/`.
- Nica's Dream: a cleaner two-page PDF source was found from University of Rochester score-alignment examples and saved as `nicas_dream_rochester_source.pdf` in the Nell's birthday folder.

## Music Sites

- GTD Trio is a separate nested Git repo at `gtd-trio/`, remote `daaronr/gtd-trio`, published by GitHub Pages from `main` `/` at `https://daaronr.github.io/gtd-trio/`.
- Kay House Trio scaffold lives in `K-house/` in this repo. The `music` GitHub Pages workflow builds `blues-app` and copies `K-house/` into `blues-app/dist/`, so after push/deploy it should publish at `https://daaronr.github.io/music/K-house/`.
