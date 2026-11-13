import importlib.util, json, os, subprocess, sys, tempfile
from pathlib import Path

os.environ.pop("AODD_DELEGATION_NUDGE", None)
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("d", HERE / "delegation-nudge.py")
d = importlib.util.module_from_spec(spec); spec.loader.exec_module(d)
state = Path(tempfile.mkdtemp())


def call(tool, out="ok", sid="s1", **extra):
    p = {"session_id": sid, "tool_name": tool, "tool_input": {"command": "x"}, "tool_response": out, **extra}
    return d.decide(p, state_dir=state)


# a short streak of lookups stays quiet
for _ in range(d.STREAK - 1):
    assert call("Read") is None
# the STREAK-th lookup in a row without delegating fires once
msg = call("Grep")
assert msg and "[delegation-nudge]" in msg and "Haiku" in msg
assert "rules/ai-sdlc/delegation.md" in msg and "ai-sdlc-workflow.md" not in msg   # points at the file that holds the rule
assert "effort `low`" in msg and "announce" in msg and "yes" in msg      # effort + announce-once rule rides along
assert all(len(m) <= 600 for m in (msg, call("Bash", out="x" * (d.MAX_BYTES + 1), sid="len-c", transcript_path=str(Path(tempfile.mkdtemp()) / "rollout-x.jsonl"))))
# cooldown: the next lookups do not fire again right away
for _ in range(d.STREAK - 1):
    assert call("Bash") is None

# a delegation resets the streak
s2 = "s2"
for _ in range(d.STREAK - 1):
    assert call("Read", sid=s2) is None
assert call("Agent", sid=s2) is None
assert call("Read", sid=s2) is None

# one big output fires at once (fresh session)
assert call("Bash", out="line\n" * (d.MAX_LINES + 1), sid="s3")
assert call("Read", out="x" * (d.MAX_BYTES + 1), sid="s4")
assert call("Read", out={"file": {"content": "y\n" * (d.MAX_LINES + 1)}}, sid="s5")   # dict response measured too

# tool calls made inside a subagent are never counted
for _ in range(d.STREAK * 2):
    assert call("Read", sid="s6", agent_id="a1", out="z" * (d.MAX_BYTES + 1)) is None

# ---- Codex: same rule, Codex tool names and tiers (Sol=Opus, Terra=Sonnet, Luna=Haiku) ----
tmpc = Path(tempfile.mkdtemp())
main_ro = tmpc / "rollout-main.jsonl"; main_ro.write_text(json.dumps({"type": "session_meta", "payload": {"source": "vscode"}}) + "\n")
sub_ro = tmpc / "rollout-sub.jsonl"; sub_ro.write_text(json.dumps({"type": "session_meta", "payload": {"source": {"subagent": {"thread_spawn": {"parent_thread_id": "p"}}}}}) + "\n")
for _ in range(d.STREAK - 1):
    assert call("Bash", sid="c1", transcript_path=str(main_ro)) is None
assert call("spawn_agent", sid="c1", transcript_path=str(main_ro)) is None        # Codex delegation resets the streak
assert call("Bash", sid="c1", transcript_path=str(main_ro)) is None
m = call("Bash", out="x" * (d.MAX_BYTES + 1), sid="c2", transcript_path=str(main_ro))
assert m and "luna" in m and "Haiku" not in m                                    # Codex wording names its own tier
for _ in range(d.STREAK * 2):                                                    # a Codex subagent thread is never nudged
    assert call("Bash", sid="c3", transcript_path=str(sub_ro), out="z" * (d.MAX_BYTES + 1)) is None
assert call("Bash", sid="c4", transcript_path=str(tmpc / "rollout-missing.jsonl"), out="z" * (d.MAX_BYTES + 1))   # unreadable rollout -> treated as main

# switch off
os.environ["AODD_DELEGATION_NUDGE"] = "0"
assert call("Bash", out="x" * (d.MAX_BYTES + 1), sid="s7") is None
os.environ.pop("AODD_DELEGATION_NUDGE")

# fail open: garbage stdin, empty payload -> exit 0, no output
env = {**os.environ, "AODD_STATE": str(state)}
for stdin in ("not json", "{}", ""):
    r = subprocess.run([sys.executable, str(HERE / "delegation-nudge.py")], input=stdin, capture_output=True, text=True, env=env)
    assert r.returncode == 0 and r.stdout == "", (stdin, r)
# real run emits PostToolUse additionalContext
big = json.dumps({"session_id": "s8", "tool_name": "Bash", "tool_response": "x" * (d.MAX_BYTES + 1)})
r = subprocess.run([sys.executable, str(HERE / "delegation-nudge.py")], input=big, capture_output=True, text=True, env=env)
out = json.loads(r.stdout)["hookSpecificOutput"]
assert out["hookEventName"] == "PostToolUse" and "[delegation-nudge]" in out["additionalContext"]
print("ok")
