#!/usr/bin/env python3
"""delegation-nudge: PostToolUse(Read|Grep|Glob|Bash|Agent|Task; Codex exec|spawn_agent|followup_task) reminder to hand mechanical work to a cheap model.

The model split in rules/ai-sdlc-workflow.md is text only; in practice the main session keeps doing lookups itself.
This hook watches the MAIN session (Claude tool calls carrying `agent_id`, and Codex threads whose rollout
says `source.subagent`, are ignored). Codex gets the same rule with its tiers (Sol/Terra/Luna = Opus/Sonnet/Haiku):

- one tool output over MAX_BYTES or MAX_LINES (a dump that now rides along in every later turn), or
- STREAK lookups in a row (Read/Grep/Glob/Bash) without an Agent/Task call,

adds one line of context asking to send that kind of work to a Haiku subagent. At most once per
COOLDOWN tool calls. State: $AODD_STATE/delegation-nudge/<session_id> (JSON counters).
Fails open on any error. Disable with AODD_DELEGATION_NUDGE=0.
"""
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _aodd_paths  # noqa: E402

MAX_BYTES = 40_000   # same threshold as rules/ai-sdlc-workflow.md "Big data stays out of main context"
MAX_LINES = 300
STREAK = 8
COOLDOWN = 10
LOOKUP = {"Read", "Grep", "Glob", "Bash", "exec"}
DELEGATE = {"Agent", "Task", "spawn_agent", "followup_task"}   # Claude, then Codex
# Same tiers on both tools: Claude Opus/Sonnet/Haiku == Codex Sol/Terra/Luna
TIER = {
    "claude": 'a Haiku subagent (Agent model: "haiku")',
    "codex": 'a luna subagent (spawn_agent with model luna; terra for code, sol stays the main session)',
}
MSG = (
    "[delegation-nudge] {why}. Per rules/ai-sdlc-workflow.md (cheap-model delegation): send the next search, file sweep, "
    "log read or test run to {tier} that returns paths and a short excerpt, "
    "and keep the main session for code, decisions and review. Ignore if the next step is one short command."
)


def _codex_meta(transcript):
    """(is_codex, is_subagent) from a Codex rollout's first record; Claude transcripts -> (False, False)."""
    if not transcript or "rollout-" not in os.path.basename(transcript):
        return False, False
    try:
        with open(transcript, encoding="utf-8") as fh:
            src = (json.loads(fh.readline()).get("payload") or {}).get("source")
    except (OSError, ValueError, AttributeError):
        return True, False
    return True, isinstance(src, dict) and "subagent" in src


def _size(resp):
    text = resp if isinstance(resp, str) else json.dumps(resp, ensure_ascii=False)
    # json.dumps escapes newlines; count both real and escaped ones
    return len(text.encode()), text.count("\n") + len(re.findall(r"\\n", text))


def decide(payload, state_dir=None):
    if os.environ.get("AODD_DELEGATION_NUDGE") == "0" or payload.get("agent_id"):
        return None
    tool, sid = payload.get("tool_name"), payload.get("session_id")
    if not sid or (tool not in LOOKUP and tool not in DELEGATE):
        return None
    codex, sub = _codex_meta(payload.get("transcript_path"))
    if sub:
        return None
    d = Path(state_dir or _aodd_paths.state() / "delegation-nudge")
    f = d / re.sub(r"[^\w.-]", "_", sid)
    try:
        st = json.loads(f.read_text())
    except (OSError, ValueError):
        st = {}
    calls, streak, last = st.get("calls", 0) + 1, st.get("streak", 0), st.get("last", -COOLDOWN)
    why = None
    if tool in DELEGATE:
        streak = 0
    else:
        streak += 1
        nbytes, nlines = _size(payload.get("tool_response", ""))
        if nbytes > MAX_BYTES or nlines > MAX_LINES:
            why = f"{tool} returned a large output ({nbytes // 1000} KB, {nlines} lines) into the main context"
        elif streak >= STREAK:
            why = f"{streak} lookups in a row in the main session without delegating"
    if why and calls - last < COOLDOWN:
        why = None
    if why:
        streak, last = 0, calls
    d.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps({"calls": calls, "streak": streak, "last": last, "nudges": st.get("nudges", 0) + bool(why)}))
    return MSG.format(why=why, tier=TIER["codex" if codex else "claude"]) if why else None


def main():
    try:
        msg = decide(json.loads(sys.stdin.read() or "{}"))
        if msg:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": msg}}))
    except Exception:
        pass  # fail open: a broken nudge must never block or spam the session
    sys.exit(0)


if __name__ == "__main__":
    main()
