#!/bin/bash
# Build and deploy the trial page to Netlify (site: ai-jazz-tune-trial, team slug: daaronr).
#   bash ai_jazz_trial/deploy.sh "message"          # rebuild + production deploy
#   bash ai_jazz_trial/deploy.sh --create "message" # first deploy: creates the site
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
python3 "$HERE/build_site.py"
cd "$HERE/web"
if [ "${1:-}" = "--create" ]; then
  shift
  netlify deploy --create-site ai-jazz-tune-trial --team daaronr --prod --no-build \
    --dir public --functions netlify/functions --message "${1:-first deploy}"
else
  netlify deploy --prod --no-build --dir public --functions netlify/functions \
    --message "${1:-update}"
fi
