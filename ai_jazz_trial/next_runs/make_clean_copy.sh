#!/bin/bash
# Make a clean copy of the music repo as a given round's composers found it, outside the repo.
#   bash make_clean_copy.sh <run-name> bright|dark|tv
#
# bright: the repo as the round-1 sessions saw it on 26 Sep (commit 571918a, plus the
#         untracked files that were already there, and the pre-trial MEMORY.md). No trial
#         folders, no skills/, no recording engine.
# dark:   the repo as the Tenebrae session saw it on 27 Sep (commit d2eb8d2: round-1 folders,
#         skills/, trial_recordings/ engine), without the page (ai_jazz_trial/) or the videos,
#         plus the two waltz prompt files and the git-ignored sample caches the engine reads.
# tv:     same base as dark, without the waltz prompts or sample caches (TV-theme recordings
#         are rendered afterwards by the shared pipeline in the main repo).
# Each copy gets a fresh one-commit git repo, so `git status` afterwards shows exactly what
# the run made.
set -euo pipefail
REPO=/Users/yosemite/githubs/music
ROOT=/Users/yosemite/githubs/music_trial_runs
HERE="$(cd "$(dirname "$0")" && pwd)"
name="$1"; kind="$2"
dest="$ROOT/$name"
if [ -e "$dest" ]; then echo "already exists: $dest" >&2; exit 1; fi
mkdir -p "$dest" "$ROOT/logs"

case "$kind" in
  bright)
    git -C "$REPO" archive 571918a | tar -x -C "$dest"
    git -C "$REPO" archive d2eb8d2 K-house modal_tune Exeter_Eugenios_Gangs_iReal_import.html \
      handwritten_to_irealpro_chart.md handwritten_to_irealpro_chart.musicxml mostlymodal.txt \
      transcribe.py | tar -x -C "$dest"
    cp "$REPO/modal_tune/mostly modal tune - 17_01_2026, 23.11.mp3" "$dest/modal_tune/"
    cp "$HERE/pre_trial_MEMORY.md" "$dest/MEMORY.md"
    ;;
  dark|tv)
    git -C "$REPO" archive d2eb8d2 | tar -x -C "$dest" --exclude 'ai_jazz_trial' \
      --exclude 'trial_recordings/video'
    if [ "$kind" = dark ]; then
      mkdir -p "$dest/ai_jazz_trial/waltz_prompts"
      cp "$REPO/ai_jazz_trial/waltz_prompts/01_compose.txt" \
         "$REPO/ai_jazz_trial/waltz_prompts/02_recording.txt" "$dest/ai_jazz_trial/waltz_prompts/"
      mkdir -p "$dest/trial_recordings/cache" "$dest/claude_halation/build"
      cp -R "$REPO/trial_recordings/cache/." "$dest/trial_recordings/cache/"
      cp -R "$REPO/claude_halation/build/." "$dest/claude_halation/build/"
    fi
    ;;
  *) echo "kind must be bright, dark or tv" >&2; exit 2 ;;
esac

git -C "$dest" init -q
git -C "$dest" add -A
git -C "$dest" commit -q -m "Clean copy for trial run $name ($kind)"
echo "made $dest"
