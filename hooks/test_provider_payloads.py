#!/usr/bin/env python3
"""Security hooks behave the same for every provider and for main and subagent sessions: Claude main,
Claude subagent (agent_id / agent_type), Codex (extra turn fields) and Antigravity (via the adapter).
Run: python3 hooks/test_provider_payloads.py"""
import importlib.util, json, os, subprocess, sys, tempfile
from pathlib import Path

HOOKS = Path(__file__).resolve().parent
T = Path(tempfile.mkdtemp()).resolve()
env = T / ".env"; env.write_text('KEY="sk-abcdefghijklmnopqrstuvwx"\n')
(T / "graphify-out").mkdir(); (T / "graphify-out" / "graph.json").write_text("{}")
ENV = {k: v for k, v in os.environ.items() if not k.startswith("AODD_")}
ENV.update(AODD_HOME=str(T / "home"), AODD_STATE=str(T / "state"), GRAPHIFY_GUARD_STATE=str(T / "gstate"), HOME=str(T))


def run(script, payload, *args):
    p = subprocess.run([sys.executable, str(HOOKS / script), *args], input=json.dumps(payload), capture_output=True, text=True, env=ENV, timeout=30)
    assert p.returncode == 0, (script, p.stderr)
    return json.loads(p.stdout) if p.stdout.strip() else None


def load_adapter():
    spec = importlib.util.spec_from_file_location("ad", HOOKS.parent / "adapters" / "antigravity-hook-adapter.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


base = {"cwd": str(T), "tool_name": "Bash", "tool_input": {"command": f"cat {env}"}}
shapes = {
    "claude-main": {**base, "session_id": "m1"},
    "claude-subagent": {**base, "session_id": "m2", "agent_id": "a1", "agent_type": "general-purpose"},
    "codex": {**base, "session_id": "m3", "turn_id": "t1", "model": "gpt-5", "hook_event_name": "PreToolUse"},
}
agy = load_adapter().to_claude_payload({"session_id": "m4", "workspacePaths": [str(T)],
                                        "toolCall": {"name": "run_command", "args": {"CommandLine": f"cat {env}"}}})
assert agy["tool_name"] == "Bash"
shapes["agy"] = agy

for name, pl in shapes.items():
    out = run("secret-read-guard.py", pl)
    assert out and out["hookSpecificOutput"]["permissionDecision"] == "deny", name   # hard-safety set: every provider
    safe = {**pl, "session_id": pl["session_id"] + "x", "tool_input": {"command": "ls"}}
    assert run("secret-read-guard.py", safe) is None, name
    # graphify-guard nudges once per session and never blocks, whoever the caller is
    raw = {**pl, "session_id": pl["session_id"] + "g", "tool_input": {"command": "grep -rn foo src"}}
    out = run("graphify-guard.py", raw, "pre")
    assert out and "permissionDecision" not in out["hookSpecificOutput"], name
    assert run("graphify-guard.py", raw, "pre") is None, name
print("ok")
