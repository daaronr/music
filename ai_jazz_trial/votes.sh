#!/bin/bash
# Inspect or tidy the vote store of the ai-jazz-tune-trial Netlify site.
#   bash ai_jazz_trial/votes.sh list            # list voter keys
#   bash ai_jazz_trial/votes.sh get <key>       # one vote (includes the private comment)
#   bash ai_jazz_trial/votes.sh delete <key>    # remove one vote (e.g. a test vote)
set -euo pipefail
cd "$(cd "$(dirname "$0")" && pwd)/web"
case "${1:-list}" in
  list)   netlify blobs:list votes ;;
  get)    netlify blobs:get votes "$2" ;;
  delete) netlify blobs:delete votes "$2" --force ;;
  *)      echo "usage: votes.sh list|get <key>|delete <key>" >&2; exit 2 ;;
esac
