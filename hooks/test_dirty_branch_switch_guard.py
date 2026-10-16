#!/usr/bin/env python3
"""Run: python3 hooks/test_dirty_branch_switch_guard.py  (asserts, no framework)"""
import json, subprocess, tempfile, os
HOOK = os.path.join(os.path.dirname(__file__), "dirty-branch-switch-guard.py")

def rc(cmd, cwd, tool="Bash", ti=None):
    return subprocess.run(["python3", HOOK], input=json.dumps({"tool_name": tool, "tool_input": ti or {"command": cmd}}),
                          text=True, cwd=cwd, capture_output=True).returncode

d = tempfile.mkdtemp()
g = lambda *a: subprocess.run(["git", *a], cwd=d, check=True, capture_output=True)
g("init", "-q"); g("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "i")
open(f"{d}/f", "w").write("a"); g("add", "f"); g("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "f")
open(f"{d}/f", "a").write("b")
assert rc("git checkout -b feat/x", d) == 2 and rc("git switch other", d) == 2   # dirty: blocked
assert rc("git checkout -- f", d) == 0 and rc("git status", d) == 0               # restore / non-switch: allowed
g("checkout", "-q", "--", "f")
assert rc("git checkout -b feat/y", d) == 0                                       # clean: allowed
assert rc('git commit -m "docs: mention git worktree add and git checkout -b x"', d) == 0   # prose in quotes is not a command
assert rc("cat <<'EOF'\ngit worktree add x\nEOF", d) == 0                                 # nor is a heredoc body
# new worktree while the tree is dirty: blocked; clean: allowed
open(f"{d}/f", "a").write("c")
assert rc(f"git -C {d} worktree add -b t2 {d}-wt", d) == 2
g("checkout", "-q", "--", "f")
assert rc(f"git -C {d} worktree add -b t2 {d}-wt", d) == 0
# -C <repo> is honoured even when the hook's cwd is elsewhere; generated graphify-out/ changes never count
open(f"{d}/f", "a").write("d")
assert rc(f"git -C {d} checkout -b t3", os.path.expanduser("~")) == 2
g("checkout", "-q", "--", "f")
os.makedirs(f"{d}/graphify-out"); open(f"{d}/graphify-out/graph.json", "w").write("1")
g("add", "-f", "graphify-out/graph.json"); g("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "go")
open(f"{d}/graphify-out/graph.json", "w").write("2")
assert rc(f"git -C {d} checkout -b t4", os.path.expanduser("~")) == 0
# a `git stash` earlier in the same command cleans the tree before the switch; stash list/show does not
open(f"{d}/f", "a").write("e")
assert rc("git stash push -q -- f && git switch -c t5 && git stash pop", d) == 0
assert rc("git stash && git checkout -b t6", d) == 0
assert rc(f"git stash -q && git -C {d} worktree add -b t7 {d}-wt7", d) == 0
assert rc("git stash list && git switch -c t8", d) == 2
assert rc("git switch -c t9 && git stash", d) == 2                                  # stash AFTER the switch: still blocked
print("dirty-branch-switch-guard OK")
