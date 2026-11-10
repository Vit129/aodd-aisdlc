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
