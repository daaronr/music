#!/bin/bash
# Build Blues Flow for the site root and deploy it, with its functions, to
# Netlify (site: blues-flow, team slug: daaronr). The GitHub Pages copy at
# daaronr.github.io/music/ is deployed separately by the repo's workflow and
# talks to the same functions.
#   bash blues-app/deploy-netlify.sh "message"
#   bash blues-app/deploy-netlify.sh --create "message"   # first time only
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
npm test
BASE=/ npx vite build --outDir dist-netlify --emptyOutDir
cd "$HERE/netlify"
[ -d node_modules ] || npm install
if [ "${1:-}" = "--create" ]; then
  shift
  netlify deploy --create-site blues-flow --team daaronr --prod --no-build \
    --dir ../dist-netlify --functions functions --message "${1:-first deploy}"
else
  netlify deploy --prod --no-build --dir ../dist-netlify --functions functions --message "${1:-update}"
fi
