#!/usr/bin/env python3
"""Allow by default: no hook may block. Every hook CLI, in every registered mode, fed `{}`, garbage and a
plain `ls` payload, exits 0 and prints nothing or JSON without a deny / block. The hard-safety set (a secret
file read, a memory token, an auditor write) is covered in each hook's own test.
Run: python3 hooks/test_allow_by_default.py"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HOOKS = Path(__file__).resolve().parent
ROOT = HOOKS.parent
CLI = [  # (script, modes); "" = no argument
    (HOOKS / "auditor-readonly.py", [""]),
    (HOOKS / "secret-read-guard.py", [""]),
    (HOOKS / "coding-rules-gate.py", ["pre", "post"]),
    (HOOKS / "dirty-branch-switch-guard.py", [""]),
    (HOOKS / "code-search-guard.py", ["pre", "post", "stop"]),
    (HOOKS / "skill-capture-nudge.py", ["", "post"]),
    (HOOKS / "done-gate.py", [""]),
    (HOOKS / "delegation-nudge.py", [""]),
    (ROOT / "optional/agent-memory/hooks/memory-write-scan.py", [""]),
]
ADAPTER = ROOT / "adapters/antigravity-hook-adapter.py"
T = tempfile.mkdtemp()
ENV = {k: v for k, v in os.environ.items() if not k.startswith("AODD_") and k not in ("AODD_AUDITOR", "CLAUDE_SKILL_CAPTURE", "DONE_GATE_AUDIT")}
ENV.update(AODD_HOME=T, HOME=T)
LS = {"session_id": "allow-1", "tool_name": "Bash", "tool_input": {"command": "ls"}, "cwd": T, "transcript_path": f"{T}/none.jsonl"}
INPUTS = ["{}", "not json at all", "", json.dumps(LS)]


def blocks(out):
    try:
        o = json.loads(out)
    except ValueError:
        return True  # stdout that is not JSON could be read as a verdict
    hs = o.get("hookSpecificOutput") or {}
    return hs.get("permissionDecision") == "deny" or o.get("decision") in ("block", "deny", "continue")


for script, modes in CLI:
    for mode in modes:
        for text in INPUTS:
            r = subprocess.run([sys.executable, str(script), *([mode] if mode else [])], input=text, capture_output=True, text=True,
                               env=ENV, cwd=T)
            assert r.returncode == 0, (script.name, mode, text[:20], r.returncode, r.stderr[-200:])
            assert not r.stdout.strip() or not blocks(r.stdout), (script.name, mode, text[:20], r.stdout[:200])
for mode in ("pre", "post", "stop"):  # the agy adapter: allow, never deny/continue
    for text in INPUTS:
        r = subprocess.run([sys.executable, str(ADAPTER), mode], input=text, capture_output=True, text=True, env=ENV, cwd=T)
        assert r.returncode == 0 and not blocks(r.stdout), (mode, text[:20], r.stdout[:200])
print("ok - every hook allows by default")
