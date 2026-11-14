# Next runs: Fable 5.2 on both rounds, and Opus 5.5 on two TV themes

Runbook for a fresh session to carry out. Set up 14 Nov 2026 by the Parallax session. The
generic method is the `agent-trial-run` skill (`../../skills/agent-trial-run/`).

## The five runs

| Run | Model, effort | Prompt(s), verbatim | Clean copy (`make_clean_copy.sh`) | Recording |
|---|---|---|---|---|
| `fable_bright` | `claude-fable-5-2`, max | `prompts/bright_01_compose.txt` (round 1's Claude prompt) | `bright` | Shared round-1 pipeline, afterwards |
| `fable_dark` | `claude-fable-5-2`, max; then high | `../waltz_prompts/01_compose.txt`, then `02_recording.txt` in the same session | `dark` | Its own, from prompt 2 (as Tenebrae and Noctilucent) |
| `opus_threes_company` | `claude-opus-5-5`, max | `prompts/tv_threes_company_01_compose.txt` | `tv` | Shared round-1 pipeline, afterwards (private) |
| `opus_all_in_the_family` | `claude-opus-5-5`, max | `prompts/tv_all_in_the_family_01_compose.txt` | `tv` | Shared round-1 pipeline, afterwards (private) |

All five are independent: separate clean copies under `~/githubs/music_trial_runs/<run>/`,
unattended, no questions answered, no feedback between prompts. They can run in parallel.

## Before starting

1. **Log the CLI in.** On 14 Nov the CLI's login had expired ("OAuth session expired"). David
   runs `claude auth login` (or `claude` then `/login`) in a terminal once. Check with a cheap
   smoke run (Haiku, low effort) before launching the real ones.
2. Confirm the model id `claude-fable-5-2` is accepted (`claude -p --model claude-fable-5-2
   "say ok"` in an empty folder).
3. `git -C ~/githubs/music pull`.

## Running

```bash
K=/Users/yosemite/githubs/music/ai_jazz_trial/next_runs
R=/Users/yosemite/githubs/music/skills/agent-trial-run/scripts/run_headless.sh
L=/Users/yosemite/githubs/music_trial_runs/logs
bash $K/make_clean_copy.sh fable_bright bright
bash $R /Users/yosemite/githubs/music_trial_runs/fable_bright $K/prompts/bright_01_compose.txt claude-fable-5-2 max $L/fable_bright_01
```

Same pattern for the others. For `fable_dark`, after prompt 1 finishes, resume the same session
**from inside the same clean copy** (the Astra run's one deviation came from resuming elsewhere):

```bash
bash $R /Users/yosemite/githubs/music_trial_runs/fable_dark /Users/yosemite/githubs/music/ai_jazz_trial/waltz_prompts/02_recording.txt claude-fable-5-2 high $L/fable_dark_02 <session id from fable_dark_01.session>
```

Launch each with the Bash tool's `run_in_background: true`; you're notified when it exits.
Don't poll. Composition runs took 25-55 min before; budget an hour each.

## What each clean copy contains, and why

- `bright`: the repo as round 1's sessions found it (commit 571918a, the untracked files already
  there, the pre-trial `MEMORY.md`). No trial folders, skills or recording engine. Round 1's
  sessions also had no jazz skills, but the four jazz skills are now installed globally, so run
  `fable_bright` with skills hidden: prefix its command with
  `EXTRA_ARGS="--disable-slash-commands"`. That also hides unrelated skills round 1 had; note it.
- `dark`: the repo as Tenebrae's session found it (commit d2eb8d2: round-1 folders, `skills/`,
  the recording engine before the groove changes, the git-ignored sample caches), minus the
  page and videos, plus the two waltz prompt files. Matches the Astra copy's recipe
  (`../waltz_prompts/HANDOFF_codex_astra.md`).
- `tv`: the same base as `dark`, without the waltz prompts or caches.

New folder paths start with empty Claude auto-memory, as round 1's sessions did. Tenebrae had
a short memory note about round 1; Fable dark gets none (Astra got Codex's own memory instead).
Global `~/.claude/CLAUDE.md` has grown since September; that can't be undone, so note it.

## After each run

1. Audit: `python3 .../agent-trial-run/scripts/audit_claude_log.py $L/<stem>.jsonl
   ~/githubs/music_trial_runs/<run> --forbid Tenebrae Noctilucent Halation Parallax "Glass Meridian"`
   (drop the names a run was allowed to see: `dark` and `tv` copies contain round 1). Read every
   path outside the copy and every forbidden-name hit; record what it means.
2. Write `RUN_RECORD.md` next to the logs, in the style of
   `../waltz_prompts/astra_logs/RUN_RECORD.md`: setup, times, tokens, cost, session ids, audit
   findings, any deviation.
3. `git -C <copy> status` shows what the run made. Copy a Fable run's output subfolder into
   `~/githubs/music/` as `fable_<name>/`. Leave the TV runs' outputs where they are (see the
   last section): render their recordings by pointing the shared pipeline at the copy, writing
   output inside `~/githubs/music_trial_runs/`.
4. Keep the `.jsonl` logs out of the public repo: they contain the system prompt with David's
   private global instructions. `~/githubs/music_trial_runs/` is outside the repo; leave them there.

## Recordings

- `fable_bright`, both TV tunes: render with the shared pipeline in `~/githubs/music/trial_recordings/`
  (read its README; add each tune to `tunes.py` the way Parallax and Glass Meridian were added,
  check with `check_inputs.py`, render with `engine/render.py <key>`), including the current
  `engine/groove.py` mix, so they sound like round 1's current recordings.
- `fable_dark`: its own recording from prompt 2. Then apply exactly the post-hoc fixes Tenebrae and
  Noctilucent got (bass +4.5 dB with 500-1500 Hz presence; the shared `groove.py` drums, bass and
  comping), as recorded in `../waltz_prompts/astra_logs/RUN_RECORD.md`. Keep the pre-fix MP3.

## Things to ask David before publishing anything

- Whether Fable's tunes join the existing blind rounds on https://ai-jazz-tune-trial.netlify.app
  (round 1 with four tunes, round 2 with three) or get a separate section, and whether they enter
  the vote (`vote.mjs`/`results.mjs` TUNES, `app.js` ROUNDS).
- Whether the TV-theme pieces become a round 3 on the page, and whether they go on YouTube.
- Keep blind judging: listen cards and videos never name the model; models appear only on tune
  cards and in a SPOILER line in YouTube descriptions.

## The TV themes are arrangements of copyrighted songs: keep them private

David asked (14 Nov) for arrangements that use the themes' actual melodies, not contrafacts. Both
songs are under copyright, so the arrangements, sheets and recordings stay private:

- Don't commit the TV outputs to `~/githubs/music` (a **public** GitHub repo). Keep them in
  `~/githubs/music_trial_runs/` (outside any repo) or a private repo, and don't push their
  renders anywhere public.
- Don't put them on the public page, YouTube or other public sites. Publishing an arrangement or a
  recording of it needs a licence (arrangement permission from the publisher, plus a mechanical
  or sync licence for a recording or video). Tell David this before he decides on a round 3.
- No lyrics in any output (the prompts say so); check the sheets and READMEs for stray lyric text.
- Only the Fable runs' outputs (original tunes) may go into the public repo and page as before.
