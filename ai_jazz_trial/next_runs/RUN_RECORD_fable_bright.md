# Fable 5.2, round-1 prompt: "Brightwork" (21 Nov 2026)

Attempt 3, after the two failed attempts in `RUN_RECORD_fable_attempts.md`. Output copied to
`../../fable_brightwork/`; recording in `../../trial_recordings/output/Brightwork_band_trumpet_alto.mp3`.

- **Setup.** Clean copy `~/githubs/music_trial_runs/fable_bright` (`make_clean_copy.sh ... bright`:
  the repo as round 1 found it, untouched since the earlier attempts; an empty folder from
  attempt 2 was removed first). `launch_clean_env.sh` with the desktop app's bundled CLI 2.1.330
  (2.1.325 had been removed by an app update), model `claude-fable-5-2`, effort `max`,
  `--disable-slash-commands` (round 1 had no jazz skills), permissions bypassed, unattended.
- **Part 1.** `prompts/bright_01_compose.txt` verbatim. Session `09137b2f-8be5-4349-95e6-4f9eda3eea0b`.
  Started 16:37 EST; ended 17:30 (53.7 min, 38 turns) on "You've hit your 5-hour limit".
  $16.60 at list price; 307k output tokens, 284k of them thinking. By then it had written the
  lead sheets (concert and B-flat) and the solo source code.
- **Deviation: one resume prompt.** After the 6:10 pm reset, David chose to resume the same session
  rather than start over. It got the single prompt `Continue.` (`prompts/resume_continue.txt`),
  same model, effort and flags, run from inside the clean copy. Started 18:28; finished 18:57
  (18.6 min, 111 turns, exit 0). $37.79 at list price (mostly 20.8M cached input re-reads);
  90k output tokens, 54k thinking. No other input either time.
- **Total.** About 72 min of model time, $54.39 at list price, two 5-hour windows.
- **What it made.** Six sheets as PDF and MusicXML (lead sheet concert and B-flat, duo score,
  trumpet concert and B-flat, guitar), a combined 12-page PDF, an iReal Pro import page, LilyPond
  sources, a README with analysis, and an unrequested General-MIDI mock-up (`audio/`). It engraved
  with LilyPond, not MuseScore (MuseScore 2 and 3 are Intel builds and no longer run on this Mac),
  so there are no `.mscz` files; the MusicXML imports into MuseScore. It validated the MusicXML
  against the 3.1 schema and read it back with `musicxml2ly`. It committed its work in the copy's
  local git.
- **Audit** (`audit_claude_log.py`, forbidding the other tunes' names). No mention of Halation,
  Parallax, Glass Meridian, Tenebrae or Noctilucent; no web access; no skills. Outside its copy
  it ran `ls /Applications`, `ls ~/Applications` and `ls -la ~/githubs/music_trial_runs`. That
  last listing showed the sibling folder names (fable_dark, opus_threes_company,
  opus_all_in_the_family, private_recordings, logs); it opened none of them. It also used `/tmp`
  for previews and downloaded the MusicXML schema from GitHub with `curl`.
- **Recording.** Rendered with the shared round-1 recipe (`trial_recordings/engine/render.py
  brightwork`, default settings, current groove): head in, two duo choruses, head out ending on bar
  31 as its README says; tempo 160 as marked. The alto took the guitar line up an octave in bars
  9, 15, 17, 24 and 38 (below the alto's range), as the recipe does. Length 3:23.
- **Differences from round 1 that remain.** Global `~/.claude/CLAUDE.md` has grown since
  September; `--disable-slash-commands` also hid unrelated skills round 1 had; the resume prompt;
  and the copy-folder listing above.
