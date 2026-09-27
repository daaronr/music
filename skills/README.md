# Claude Code skills from the AI jazz tune trial

Master copies of four skills. The working copies Claude Code actually loads are in
`~/.claude/skills/<name>/`; after editing here, reinstall with:

```bash
cp -R ~/githubs/music/skills/jazz-chart-notation ~/.claude/skills/
```

(same for the others).

| Skill | What it does |
|---|---|
| `jazz-chart-notation` | Text notation to MusicXML to MuseScore 3 PDF/.mscz: lead sheets, solos, B-flat and guitar parts, harmony and counterpoint checks |
| `ireal-pro-chart` | Plain-text chord chart to an iReal Pro import link and click-to-import HTML page |
| `jazz-composition` | Method for original tunes and written duo solos, with a chord-by-chord device map |
| `agent-trial-page` | Prompt chains from Claude Code and Codex logs, checking what gets published, and a listen/vote/results page on Netlify |
