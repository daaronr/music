---
name: agent-trial-page
description: Build and publish a shareable web page for an informal trial or bake-off in which several AI agent sessions (Claude Code, Codex or others) got the same task - showing each run's outputs, the exact prompt chains pulled from local session logs, the setup, caveats, recordings or demos first, and a vote with results revealed after voting. Use this whenever David says he ran the same prompt in Claude and Codex (or in several sessions) and wants to show, compare, write up, share or collect votes on the results, even if he just says "make a page for this trial" or "link all the outputs".
---

# Agent trial page

A working example to copy: `~/githubs/music/ai_jazz_trial/` (live at
https://ai-jazz-tune-trial.netlify.app): data files, templates, a builder, two Netlify
Functions for voting, and deploy/vote scripts. Its README explains each file.

## 1. Inventory the runs

List each run's folder and its deliverables. Don't edit another run's outputs; if the host
needs a change (e.g. stripping a DOCTYPE), make a copy and say so on the page.

## 2. Get the prompt chains from the logs, not from memory

```bash
python3 scripts/extract_prompts.py find <folder-name-or-phrase> --date YYYY-MM-DD
python3 scripts/extract_prompts.py claude ~/.claude/projects/<slug>/<session>.jsonl
python3 scripts/extract_prompts.py codex ~/.codex/sessions/YYYY/MM/DD/rollout-....jsonl
```

- Prompts typed while a Claude session is busy are logged as `queued_command` attachments;
  the script catches them. Codex logs a `turn_context` (model and reasoning effort) per turn.
- Quote prompts verbatim, typos included, in folds. Summarise them in short labels.
- Report models and effort as the logs show them. If David calls a run something different
  (e.g. "high" when the log says xhigh for the key turn), say what the log shows and tell him.
- Re-run the extraction before each update; sessions keep going after the page goes up.

## 3. Look at everything you publish

- PDFs: Read them (pages) and check they are what the file names say.
- MusicXML, MuseScore, HTML: `python3 scripts/scan_text.py --brief <files>` lists every
  human-readable string (titles, credits, directions, links) so nothing private rides along.
- Audio: `ffprobe` for duration and tags; read the run's README for sources and licences.

## 4. Write the page

- Use the david-writing-style skill: David's first person, plain, no ranking of the runs unless
  he asks. Say early that it is informal (one attempt per setup, different follow-ups, no
  blind rating) and keep caveats visible.
- Order: a short framing header; the thing people want first (recordings, demos); the vote;
  what this is plus caveats; one card per run (model and setup, key facts, preview, folds for
  files); then folds for what was asked (summary lines with the exact words as tooltips, plus
  the full prompt), prompts in order per run, side-by-side comparisons, and setup.
- Style: David's workshop pages. Warm paper `#f8f6f1`, slate header gradient
  `#2c3e50 -> #1a252f`, Source Serif 4 headings, DM Sans body, sage `#5a7a5a` and brown
  `#8b5e3c` accents, white cards. Light only; he dislikes "night mode" pages. Use folds and
  tooltips generously for jargon and secondary detail.
- Fairness: if the runs got different follow-ups, show that. For recordings, the headline
  version of each should come from the same instructions (ideally one shared rendering
  pipeline), with each run's own versions kept as labelled alternates.
- Shuffle the order of the entries per visitor (stored in localStorage) so position doesn't
  bias listening or votes, and offer a blind path (listen and vote before the model names).

## 5. Host it

**Netlify (default for sharing).** Copy the example's `web/`, `web_src/`, `build_site.py`,
`deploy.sh`, `votes.sh`. Votes go through `POST /api/vote` into a Netlify Blobs store (one
record per random browser id, no names or IPs); `GET /api/results?voter=<id>` returns tallies
only for ids that have voted, and never returns comments. Deploy with the CLI from inside
`web/` (the team slug for David's account is `daaronr`, not the display name). After the first
deploy, test: results before voting -> 403; a vote from a `test-...` id -> ok; results -> 200
with the test excluded; then delete the test record (`votes.sh delete <id>`). This avoids
Netlify Forms and its silent-drop trap.

**claude.ai artifact (private or quick).** Works for a read-only page, with limits learned the
hard way: .zip, .docx, .mscz and .mid can't be attached; XML with a DOCTYPE is refused; files
can only be saved through the `downloads` capability (pdf, zip, txt, json, md, html, png and a
few more; not mp3), so zips have to be built in the page (JSZip from cdnjs) from published
files; audio plays inline; custom-scheme links such as `irealbook://` need a copy button.

## 6. Keep it current

Record the live URL, deploy command and open items in the project README and memory. When a
run adds outputs (a new recording, a README), re-read them, update the data files, and redeploy.
