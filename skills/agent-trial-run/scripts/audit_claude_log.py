"""Audit a headless Claude Code run (stream-json log) for a matched trial.

    python3 audit_claude_log.py <log.jsonl> <allowed-dir> [--forbid NAME ...]

Prints: model(s) used, turns, duration, token totals, every Bash command, every file path a
tool touched outside <allowed-dir> (and outside system/tool locations), web fetches, skills
invoked, and any line mentioning a --forbid name (e.g. another run's tune title). Read the
flagged lines yourself; a path listed is not proof the run read another attempt's work.
"""

import json
import re
import sys

SYSTEM_PREFIXES = ("/Applications/", "/opt/homebrew/", "/usr/", "/System/", "/Library/",
                   "/private/tmp/", "/tmp/", "/dev/", "/Users/yosemite/.claude/skills/",
                   "/Users/yosemite/Library/", "/var/folders/")
PATH_RE = re.compile(r"(/(?:Users|private|tmp|opt|Applications)[^\s'\"`;|&<>)]*)")


def walk_strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from walk_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk_strings(v)


def main():
    path, allowed = sys.argv[1], sys.argv[2].rstrip("/")
    forbid = sys.argv[sys.argv.index("--forbid") + 1:] if "--forbid" in sys.argv else []
    models, bash, outside, web, skills, hits = set(), [], set(), [], [], []
    result = None
    for line in open(path, encoding="utf-8"):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("type") == "result":
            result = d
        msg = d.get("message") if isinstance(d.get("message"), dict) else {}
        if d.get("type") == "assistant":
            models.add(msg.get("model"))
            for c in msg.get("content") or []:
                if not isinstance(c, dict) or c.get("type") != "tool_use":
                    continue
                name, inp = c.get("name"), c.get("input") or {}
                if name == "Bash":
                    bash.append(inp.get("command", ""))
                if name in ("WebFetch", "WebSearch"):
                    web.append(inp.get("url") or inp.get("query"))
                if name == "Skill":
                    skills.append(inp.get("skill"))
                for s in walk_strings(inp):
                    for p in PATH_RE.findall(s):
                        if not p.startswith(allowed) and not p.startswith(SYSTEM_PREFIXES):
                            outside.add(p)
        for s in walk_strings(d):
            for f in forbid:
                if f.lower() in s.lower():
                    hits.append((d.get("type"), f, s[:200].replace("\n", " ")))
    print("models:", sorted(m for m in models if m))
    if result:
        print("turns:", result.get("num_turns"), "| duration min:",
              round((result.get("duration_ms") or 0) / 60000, 1), "| cost usd:",
              result.get("total_cost_usd"), "| is_error:", result.get("is_error"))
        print("usage:", json.dumps(result.get("usage", {}))[:400])
    print(f"\nbash commands ({len(bash)}):")
    for b in bash:
        print("  $", b[:220].replace("\n", " "))
    print(f"\npaths outside {allowed} ({len(outside)}):")
    for p in sorted(outside):
        print("  ", p)
    print("\nweb:", web)
    print("skills:", skills)
    print(f"\nforbidden-name hits ({len(hits)}):")
    for h in hits[:50]:
        print("  ", h)


if __name__ == "__main__":
    main()
