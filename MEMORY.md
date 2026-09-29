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
- K-House site lives in `K-house/` in this repo. The one live copy is https://kay-house.netlify.app (Netlify site `kay-house`, which holds the bandmate form submissions); `K-house/.netlify/state.json` links there. Deploy with `netlify deploy --prod --dir K-house` from the repo root, or `--site kay-house`.
- **One live version per site (Sep 2026).** The `music` GitHub Pages workflow still tests and builds `blues-app`, but it now publishes only `pages_redirect/index.html` (as index and 404), which sends `daaronr.github.io/music/...` to blues-flow.netlify.app and `/music/K-house/...` to kay-house.netlify.app. The old duplicate Netlify sites `k-house-jazz`, `delicate-taffy-42ae49` and `benevolent-maamoul-de8109` were collapsed: the last was renamed to `jazz-practice-hub` (the Jazz Practice Hub, source `jazz_hub/index.html`), and the other two now 301 to the canonical copies. Don't redeploy to the redirect sites.

## Blues Flow app (blues-app/)

- Live at https://blues-flow.netlify.app (daaronr.github.io/music/ now only redirects there). Chart data lives only in `blues-app/src/music/progressions.ts`, transcribed from `blues_variations_in_F.JPG`; forms 9-18 were wrong before Sep 2026 because they came from `blues_variations_wrong.md`. The root `blues_variations.md`, `blues_flowchart*.md` and `index.html` still carry old errors.
- The only copy is https://blues-flow.netlify.app (Netlify site `blues-flow`, `bash blues-app/deploy-netlify.sh`); it hosts the vote/feedback/usage functions. Read results with `node blues-app/netlify/stats.mjs [notes|votes]`.
- `npm run render:tour` rebuilds the narrated 18-form MP3 in `blues-app/public/audio/` with the app's own arranger. It borrows the Kokoro venv from `claude_code_misc_work/brass_playing_next_step/`.

## Notation and audio pipeline (claude_halation/)

- `claude_halation/` holds Claude's original tune "Halation" plus a written trumpet/guitar duo solo (a parallel GPT attempt lives in a different subfolder). Rebuild steps are in its README.
- Text notation → MusicXML → MuseScore 3 CLI → patched .mscx → PDF/.mscz. MuseScore's MusicXML import mangles chord names such as `7alt` and `13sus`, and `-S` style files are ignored on import, so `src/build.py` rewrites `<Harmony><name>` and `<Style>` in the .mscx.
- Realistic audio without a DAW: `src/audio/` renders Apple GarageBand EXS instruments (Steinway, Upright Jazz Bass, Alto Sax, SoCal kit) with its own EXS parser (consolidated CAFs aren't loadable by AVAudioUnitSampler), plus University of Iowa solo-trumpet samples. EXS fine-tune adds to pitch; the upright bass is mapped an octave up.

## AI jazz tune trial (26 Sep 2026)

- Three runs of one prompt: `claude_halation/`, `claude_parallax/` (both Claude Opus 5.5 max) and `codex_glass_meridian/` (GPT-6 Astra in Codex). `claude_parallax/src/` has a reusable text-notation → MusicXML library with harmony and counterpoint checks.
- Public page with recordings and a vote: https://ai-jazz-tune-trial.netlify.app, built from `ai_jazz_trial/` (`bash ai_jazz_trial/deploy.sh "msg"`). Votes live in Netlify Blobs store `votes` (`bash ai_jazz_trial/votes.sh list`); results are shown only to browsers that voted. See `ai_jazz_trial/README.md`.
- Artifacts can't carry .zip/.mscz/.mid files or XML with a DOCTYPE, which is why the shareable page moved to Netlify.
