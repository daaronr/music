# Fable 5.2 attempts (14-15 Nov 2026): none finished

These runs followed `README.md` in this folder: clean copies in `~/githubs/music_trial_runs/`,
prompts verbatim, unattended, `claude -p` with stream-json logs. The logs stay outside the repo,
because they contain private global instructions. None of the runs got as far as writing music.

| Attempt | Run | Start (GMT) | Length | Turns | Cost (list) | How it ended |
|---|---|---|---|---|---|---|
| 1 | Fable bright, `bright_01_compose.txt`, effort max | 14 Nov 16:45 | 11.7 min | 16 | $1.42 | `ENOTFOUND`: the network dropped at 16:54 |
| 1 | Fable dark, `waltz_prompts/01_compose.txt`, effort max | 14 Nov 16:45 | ~58 min wall | 28 + 3 | $4.91 | `ENOTFOUND` twice: the network dropped, then the lid was closed on battery at 17:01 (`pmset -g log`) |
| 2 | Fable bright, as above | 15 Nov 01:30 | 71.3 min | 36 | $11.98 | "You've hit your 5-hour limit" (5-hour window at 100%, weekly at 72%) |

- **Setup for both attempts**
  - CLI 2.1.325, the desktop app's bundled build. The `claude` on PATH, 2.1.300, does not
    recognise `claude-fable-5-2` and gives it only a 200k context window.
  - Launched through `launch_clean_env.sh`, which strips the desktop session's
    environment variables and, from attempt 2 on, holds off idle sleep. Model
    `claude-fable-5-2`, effort `max`.
- **Attempt 2.** The run read the copy and the skills and planned at length: more than 117k
  thinking tokens. It wrote no files before the 5-hour window ran out. `git status` in the copy
  was clean afterwards, so the copy is still unused.
- **Cost.** One unfinished max-effort compose step took a whole 5-hour window and about 7-9% of
  the weekly allowance. Extra usage is off on this account.
- **Decision (David, 15 Nov).**
  - Fable dark is dropped as too expensive.
  - Fable bright is on hold. It could be re-run after the weekly reset (Tue 12:00), or at a
    lower effort, which would no longer match the earlier runs.
- **Lessons for the runbook.**
  - Keep the Mac on mains power with the lid open. `caffeinate` cannot stop lid-close sleep.
  - Run one job at a time.
  - Check `rate_limit_event` lines in the log before starting a long max-effort run.
