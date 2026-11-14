#!/bin/bash
# Run one unattended Claude Code turn for a matched AI trial, logging everything.
#   bash run_headless.sh <workdir> <prompt-file> <model> <effort> <log-stem> [resume-session-id]
#
# - Runs from inside <workdir> (also when resuming: a resumed run must start in the same clean
#   copy, or it lands in whatever folder the shell is in).
# - Prompt text is passed verbatim on stdin.
# - Permissions bypassed (unattended, nobody to answer); hooks and global CLAUDE.md still load,
#   as they did for the original sessions.
# - Writes <log-stem>.jsonl (stream-json transcript), <log-stem>.session (session id),
#   <log-stem>.meta (model, effort, start/end times, exit code). Keep logs out of public repos:
#   they contain the system prompt, which includes private global instructions.
set -uo pipefail
workdir="$1"; prompt="$2"; model="$3"; effort="$4"; stem="$5"; resume="${6:-}"
cd "$workdir" || exit 1
if [ -n "$resume" ]; then
  sid="$resume"; how=(--resume "$sid")
else
  sid="$(uuidgen | tr 'A-Z' 'a-z')"; how=(--session-id "$sid")
fi
echo "$sid" > "$stem.session"
{
  echo "workdir: $workdir"; echo "prompt: $prompt"; echo "model: $model"; echo "effort: $effort"
  echo "session: $sid"; echo "resume: ${resume:-no}"; echo "start: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > "$stem.meta"
# Extra flags for this run only, e.g. EXTRA_ARGS="--disable-slash-commands" to hide skills.
read -r -a extra <<< "${EXTRA_ARGS:-}"
echo "extra: ${EXTRA_ARGS:-none}" >> "$stem.meta"
claude -p "${how[@]}" --model "$model" --effort "$effort" --dangerously-skip-permissions \
  "${extra[@]}" --output-format stream-json --verbose < "$prompt" > "$stem.jsonl" 2> "$stem.stderr.txt"
code=$?
{ echo "end: $(date '+%Y-%m-%d %H:%M:%S %Z')"; echo "exit: $code"; } >> "$stem.meta"
exit $code
