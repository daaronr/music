# "Can AI write a modern jazz tune?" trial page

Live: **https://ai-jazz-tune-trial.netlify.app** (Netlify site `ai-jazz-tune-trial`, team slug
`daaronr`). An earlier private version is at https://claude.ai/artifact/D5b7ZMj3QG2P2cT7xGagUn;
it now points to the Netlify page.

The page presents the three runs of the same prompt (`../claude_halation`, `../claude_parallax`,
`../codex_glass_meridian`): recordings first, then a vote, the tunes and their files, and the
prompt chains.

## Update and redeploy

```bash
bash ai_jazz_trial/deploy.sh "what changed"
```

That runs `build_site.py` (copies the PDFs, MP3s and zips out of the three run folders into
`web/public/`, fills the templates) and deploys to production with the Netlify CLI.

| File | Role |
|---|---|
| `trial_data.py` | Runs, sheets, file bundles, chord changes, prompt timelines (verbatim prompts) |
| `site_data.py` | Recordings per tune (headline + alternates, with notes), pending notes, tooltip glossary |
| `web_src/` | `index.html` and `results.html` templates, `style.css`, `app.js`, `results.js` |
| `build_site.py` | Builds `web/public/`; `[[term]]` in templates becomes a tooltip from the glossary |
| `web/netlify/functions/vote.mjs` | `POST /api/vote`: one vote per browser id, stored in Netlify Blobs store `votes` |
| `web/netlify/functions/results.mjs` | `GET /api/results?voter=id`: aggregates, only for ids that have voted; comments never returned |
| `deploy.sh`, `votes.sh` | Deploy; list, read or delete votes (`bash ai_jazz_trial/votes.sh list`) |
| `build_page.py`, `template.html`, `site/` | The earlier claude.ai artifact version |

Votes hold a random browser id, the favourite, optional 1-5 ratings, what the voter did,
an optional instrument and a private comment. No names or IPs. Voter ids starting `test-` are
stored but left out of the results, so the API can be checked without skewing the tallies.

## Open items (27 September 2026)

- Parallax recording: being made from the same audio request Halation got, plus the audio brief
  the Codex session wrote (`codex_glass_meridian/audio/share/`).
- Fairness: render all three tunes through that same pipeline and settings, and show those as
  the headline recordings, keeping each run's own recordings as alternates.
