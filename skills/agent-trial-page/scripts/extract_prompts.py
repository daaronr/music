"""Pull the prompt chain (what the human typed, when, to which model and effort) from local
Claude Code and Codex session logs.

  python3 extract_prompts.py find <keyword> [--date 2026-09-26]   # which logs mention it
  python3 extract_prompts.py claude <session.jsonl> [--json]
  python3 extract_prompts.py codex <rollout.jsonl> [--json]

Claude Code logs: ~/.claude/projects/<project-slug>/<session-id>.jsonl
  - first prompt: {"type": "user", "message": {"content": ...}} without tool_result items
  - prompts typed while the agent was working: {"type": "attachment", "attachment":
    {"type": "queued_command", "prompt": ..., "origin": {"kind": "human"}}}
  - model: {"type": "assistant", "message": {"model": ...}}
Codex logs: ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl
  - {"type": "turn_context", "payload": {"model", "effort"}} precedes each turn
  - {"type": "response_item", "payload": {"type": "message", "role": "user", "content": [...]}}
    (skip injected blocks: AGENTS.md, <environment_context>, <permissions>, plugin lists)
Times are printed in local time. Prompts are verbatim; don't tidy them if you quote them.
"""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import re

INJECTED = ("<environment_context>", "# AGENTS.md", "<user_instructions>", "<permissions",
            "<recommended_plugins>", "<system-reminder>")


def local(ts: str | None) -> str:
    if not ts:
        return "?"
    t = dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone()
    return t.strftime("%Y-%m-%d %H:%M")


def text_of(content) -> str:
    if isinstance(content, str):
        return content
    return "\n".join(c.get("text", "") for c in content or []
                     if isinstance(c, dict) and c.get("type") in ("text", "input_text"))


def claude(path):
    turns, models = [], set()
    for line in open(path, encoding="utf-8"):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        kind = d.get("type")
        if kind == "assistant":
            models.add((d.get("message") or {}).get("model"))
        elif kind == "attachment":
            att = d.get("attachment") or {}
            if att.get("type") == "queued_command" and (att.get("origin") or {}).get("kind") == "human":
                turns.append({"time": local(d.get("timestamp")), "mid_turn": True,
                              "text": str(att.get("prompt", ""))})
        elif kind == "user" and not d.get("isMeta"):
            content = (d.get("message") or {}).get("content")
            if isinstance(content, list) and any(isinstance(c, dict) and c.get("type") == "tool_result"
                                                 for c in content):
                continue
            t = re.sub(r"</?pasted_content[^>]*>\s*", "", text_of(content)).strip()
            if t and not t.startswith(INJECTED):
                turns.append({"time": local(d.get("timestamp")), "mid_turn": False, "text": t})
    return {"kind": "claude", "models": sorted(m for m in models if m), "turns": turns}


def codex(path):
    turns, meta, ctx = [], {}, {}
    for line in open(path, encoding="utf-8"):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        p = d.get("payload") or {}
        if d.get("type") == "session_meta":
            meta = {k: p.get(k) for k in ("cwd", "originator", "cli_version", "model_provider")}
        elif d.get("type") == "turn_context":
            ctx = {"model": p.get("model"), "effort": p.get("effort")}
        elif d.get("type") == "response_item" and p.get("type") == "message" and p.get("role") == "user":
            t = text_of(p.get("content")).strip().replace("&#x20;", " ")
            if t and not t.startswith(INJECTED):
                turns.append({"time": local(d.get("timestamp")), **ctx, "text": t})
    return {"kind": "codex", "meta": meta, "turns": turns}


def find(keyword, date=None):
    home = os.path.expanduser("~")
    pats = [f"{home}/.claude/projects/*/*.jsonl"]
    if date:
        y, m, dd = date.split("-")
        pats.append(f"{home}/.codex/sessions/{y}/{m}/{dd}/*.jsonl")
    else:
        pats.append(f"{home}/.codex/sessions/*/*/*/*.jsonl")
    for pat in pats:
        for path in sorted(glob.glob(pat), key=os.path.getmtime):
            if date and ".claude" in path:
                mdate = dt.datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d")
                if mdate < date:
                    continue
            try:
                with open(path, encoding="utf-8", errors="ignore") as fh:
                    if keyword.lower() in fh.read().lower():
                        print(path)
            except OSError:
                pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["find", "claude", "codex"])
    ap.add_argument("target")
    ap.add_argument("--date")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.mode == "find":
        find(args.target, args.date)
        return
    out = claude(args.target) if args.mode == "claude" else codex(args.target)
    if args.json:
        print(json.dumps(out, indent=1, ensure_ascii=False))
        return
    print(out.get("models") or out.get("meta"))
    for t in out["turns"]:
        extra = f" [{t.get('model')}, effort {t.get('effort')}]" if out["kind"] == "codex" else \
            (" [typed mid-turn]" if t.get("mid_turn") else "")
        print(f"\n=== {t['time']}{extra}\n{t['text'][:3000]}")


if __name__ == "__main__":
    main()
