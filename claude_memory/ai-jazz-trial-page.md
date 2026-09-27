---
name: ai-jazz-trial-page
description: "Where the \"Can AI write a modern jazz tune?\" trial page, its vote store and deploy scripts live, and what is still pending"
metadata:
  node_type: memory
  type: project
  originSessionId: 4bb3bcc9-304c-47f0-988c-7c6cc219f2a5
  modified: 2026-09-26T23:41:01.077Z
---

David's informal 26 Sep 2026 trial: one composition prompt (post-bop tune + two-chorus trumpet/guitar duo solo, PDF + MuseScore + iReal) given to two Claude Opus 5.5 max sessions (`claude_halation/`, `claude_parallax/`) and one GPT-6 Astra Codex session (`codex_glass_meridian/`) in `~/githubs/music`.

Public page: https://ai-jazz-tune-trial.netlify.app (Netlify site `ai-jazz-tune-trial`, team slug `daaronr`, source `ai_jazz_trial/`, deploy with `bash ai_jazz_trial/deploy.sh "msg"`). Votes: Netlify Blobs store `votes`, one per browser id; `bash ai_jazz_trial/votes.sh list|get|delete`. Results only visible to browsers that have voted; comments private.

**Why:** David wants to share it widely and keep iterating, in his usual light workshop-page style (warm paper, slate header, Source Serif 4 + DM Sans, sage/brown), with folds and tooltips, recordings first.

**How to apply:** For fairness he wants every tune's headline recording made from the same audio instructions; runs' own recordings stay as labelled alternates (Glass Meridian v3 had three extra feedback rounds). Done 27 Sep: `~/githubs/music/trial_recordings/` applies the Halation recording's instructions unchanged to all three (Halation not re-rendered; it is the model). Keep the per-visitor shuffle of the listening order as is: he confirmed he wants it fully shuffled. Keep the page's facts tied to the session logs (Codex effort was xhigh for the composition turn even though David calls it "high"). Related: [[jazz-chart-notation]], [[ireal-pro-chart]].
