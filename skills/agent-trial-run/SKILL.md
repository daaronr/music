---
name: agent-trial-run
description: Run a matched, unattended AI model trial - give a new model (or the same model on a new brief) exactly the prompts and starting state an earlier run had, in a clean copy of the repo, headless, logged, then audit the log for leaks and record the conditions. Use whenever David wants to "run the same prompt on <model>", "do an independent trial", "match the conditions of the earlier run", "queue a headless run", or compare a new model against earlier AI music or writing runs. Pairs with agent-trial-page for publishing the results.
---

# Matched agent trial runs

Worked example and runbook: `~/githubs/music/ai_jazz_trial/next_runs/README.md` (Fable 5.2 on
both jazz rounds; Opus 5.5 on TV-theme contrafacts). Precedent with a full conditions record:
`~/githubs/music/ai_jazz_trial/waltz_prompts/` (GPT-6 Astra on the Tenebrae brief).

## Method

1. **Reconstruct the starting state.** Find from git history and the earlier session's log
   what the original run could see: which commit, which untracked files, which skills and memory.
   Build a clean copy outside the repo (`git archive <commit> | tar -x`), add only those files,
   and `git init` it with one commit so `git status` later shows exactly what the run made.
   Nothing in the copy should mention later results; grep it for later tune or run names.
2. **Match the prompts verbatim**, typos included, as files. Same order, same session for
   follow-ups, no answers or feedback mid-run. If the model stops to ask, it gets no reply.
3. **Run headless**: `scripts/run_headless.sh <copy> <prompt> <model> <effort> <log-stem>
   [session-id-to-resume]`. It runs from inside the copy (also on resume: resuming from another
   folder silently changes the working directory), logs stream-json, the session id and
   start/end times. `EXTRA_ARGS="--disable-slash-commands"` hides skills when the original run had
   none. Launch with the Bash tool's `run_in_background`; don't poll.
4. **Check the CLI first**: a one-line Haiku smoke run in a throwaway copy. An expired login
   fails in a second with `authentication_failed`; David must run `claude auth login` himself.
5. **Audit** with `scripts/audit_claude_log.py <log> <copy> --forbid <names it must not see>`:
   models used, tokens, cost, every command, paths outside the copy, web use, skills, name hits.
   Read the flagged lines; report what was actually opened, not just listed.
6. **Record conditions** in a `RUN_RECORD.md`: setup, model and effort per prompt, times, tokens,
   audit findings, every deviation, and the differences that can't be removed (harness, global
   instructions grown since, memory).
7. **Treat outputs equally afterwards.** Any post-hoc fix (mix, packet layout) is applied to every
   entry in the round, and noted.

## Rules

- Keep logs out of public repos: they hold the system prompt with private global instructions.
- Keep judging blind: names of models stay off listening cards and videos.
- Ask David before adding a run to a public page or vote.
