#!/usr/bin/env python3
"""Run: python3 hooks/test_dirty_branch_switch_guard.py  (asserts, no framework)"""
import itertools, json, subprocess, tempfile, os
HOOK = os.path.join(os.path.dirname(__file__), "dirty-branch-switch-guard.py")
ENV = {k: v for k, v in os.environ.items() if not k.startswith("AODD_") and k != "BRANCH_SWITCH_GUARD"}
ENV["AODD_HOME"] = tempfile.mkdtemp()
_n = itertools.count()


def run(cmd, cwd, sid=None, stdin=None):
    """Fresh session id per call unless one is given. Returns (returncode, stdout)."""
    payload = {"tool_name": "Bash", "tool_input": {"command": cmd}, "session_id": sid or f"s{next(_n)}"}
    r = subprocess.run(["python3", HOOK], input=stdin if stdin is not None else json.dumps(payload),
                       text=True, cwd=cwd, capture_output=True, env=ENV)
    return r.returncode, r.stdout


def advised(cmd, cwd, sid=None):
    """True when the hook added context; asserts it never blocks or denies."""
    rc, out = run(cmd, cwd, sid)
    assert rc == 0, (cmd, rc)
    if not out:
        return False
    o = json.loads(out)["hookSpecificOutput"]
    assert "permissionDecision" not in o and "additionalContext" in o and "advice, not a block" in o["additionalContext"], out
    return True


d = tempfile.mkdtemp()
g = lambda *a: subprocess.run(["git", *a], cwd=d, check=True, capture_output=True)
g("init", "-q"); g("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "i")
open(f"{d}/f", "w").write("a"); g("add", "f"); g("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "f")
open(f"{d}/f", "a").write("b")
assert advised("git checkout -b feat/x", d) and advised("git switch other", d)    # dirty: advice, never a block
assert not advised("git checkout -- f", d) and not advised("git status", d)       # restore / non-switch: silent
g("checkout", "-q", "--", "f")
assert not advised("git checkout -b feat/y", d)                                   # clean: silent
assert not advised('git commit -m "docs: mention git worktree add and git checkout -b x"', d)   # prose in quotes is not a command
assert not advised("cat <<'EOF'\ngit worktree add x\nEOF", d)                                 # nor is a heredoc body
# new worktree while the tree is dirty: advice; clean: silent
open(f"{d}/f", "a").write("c")
assert advised(f"git -C {d} worktree add -b t2 {d}-wt", d)
g("checkout", "-q", "--", "f")
assert not advised(f"git -C {d} worktree add -b t2 {d}-wt", d)
# -C <repo> is honoured even when the hook's cwd is elsewhere; generated graphify-out/ changes never count
open(f"{d}/f", "a").write("d")
assert advised(f"git -C {d} checkout -b t3", os.path.expanduser("~"))
g("checkout", "-q", "--", "f")
os.makedirs(f"{d}/graphify-out"); open(f"{d}/graphify-out/graph.json", "w").write("1")
g("add", "-f", "graphify-out/graph.json"); g("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "go")
open(f"{d}/graphify-out/graph.json", "w").write("2")
assert not advised(f"git -C {d} checkout -b t4", os.path.expanduser("~"))
# a `git stash` earlier in the same command cleans the tree before the switch; stash list/show does not
open(f"{d}/f", "a").write("e")
assert not advised("git stash push -q -- f && git switch -c t5 && git stash pop", d)
assert not advised("git stash && git checkout -b t6", d)
assert not advised(f"git stash -q && git -C {d} worktree add -b t7 {d}-wt7", d)
assert advised("git stash list && git switch -c t8", d)
assert advised("git switch -c t9 && git stash", d)                                  # stash AFTER the switch: still advised
# once per session: the same advice again is silent, a new session hears it again; no session id -> silent
assert advised("git switch -c a1", d, sid="once") and not advised("git switch -c a1", d, sid="once")
assert advised("git switch -c a1", d, sid="other")
rc, out = run("git switch -c a1", d, stdin=json.dumps({"tool_name": "Bash", "tool_input": {"command": "git switch -c a1"}}))
assert rc == 0 and out == ""
# garbage and empty input fail open
for junk in ("not json", "{}", ""):
    assert run("x", d, stdin=junk) == (0, ""), junk
print("dirty-branch-switch-guard OK")
