#!/bin/bash
# Launch run_headless.sh the way a plain terminal would, from inside another Claude session.
#   [EXTRA_ARGS="..."] bash launch_clean_env.sh <workdir> <prompt> <model> <effort> <log-stem> [session-id]
#
# Two things found on 14 Nov 2026, before the first run:
# 1. A shell started by the Claude desktop app carries that session's variables
#    (CLAUDE_EFFORT=xhigh, CLAUDE_CODE_CHILD_SESSION, CLAUDE_CODE_SESSION_ID, messaging socket...).
#    A nested `claude -p` inherits them, so they are removed here.
# 2. The `claude` on PATH was 2.1.300, which does not know claude-fable-5-2: it prints
#    "unrecognized_model", still gets answers from that model, but gives it a 200k context
#    window. The desktop app's bundled 2.1.325 recognises it (1M window, list pricing). All
#    five runs use 2.1.325 through a wrapper put first on PATH; run_headless.sh is unchanged.
set -uo pipefail
CLI="/Users/yosemite/Library/Application Support/Claude/claude-code/2.1.325/485fdac4332e/claude.app/Contents/MacOS/claude"
RUNNER=/Users/yosemite/githubs/music/skills/agent-trial-run/scripts/run_headless.sh
BIN=/Users/yosemite/githubs/music_trial_runs/bin
if [ ! -x "$CLI" ]; then echo "missing CLI: $CLI" >&2; exit 3; fi
for v in $(compgen -v | grep -E '^(CLAUDE|MCP_|ANTHROPIC_)'); do unset "$v"; done
if [ ! -x "$BIN/claude" ]; then
  mkdir -p "$BIN"
  printf '#!/bin/bash\nexec "%s" "$@"\n' "$CLI" > "$BIN/claude.tmp.$$"
  chmod +x "$BIN/claude.tmp.$$"
  mv "$BIN/claude.tmp.$$" "$BIN/claude"
fi
export PATH="$BIN:$PATH"
# caffeinate stops idle sleep while the run is alive. It cannot stop lid-close sleep: the first
# attempt (14 Nov, 16:45) died when the network dropped and the lid was then closed on battery.
exec caffeinate -i -s bash "$RUNNER" "$@"
