import os, sys, tempfile
from pathlib import Path
for k in ("AODD_HOME", "AODD_REPORTS", "AODD_STATE", "AODD_PLANS", "AODD_WORKLOG", "AODD_MEMORY", "AODD_WORKSPACE", "CLAUDE_HOME"):
    os.environ.pop(k, None)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _aodd_paths as p

assert p.home() == Path.home() / ".aodd" and p.reports() == p.home() / "pending-reports"
assert p.state() == p.home() / "state" and p.plans("/") == p.home() / "plans"
t = Path(tempfile.mkdtemp()).resolve()
os.environ["AODD_HOME"] = str(t / "h")
assert p.reports() == t / "h/pending-reports" and p.state() == t / "h/state"
os.environ["AODD_REPORTS"] = str(t / "r"); os.environ["AODD_STATE"] = str(t / "s")
assert p.reports() == t / "r" and p.state() == t / "s"
# {project} = git repo folder name of cwd, found from a subfolder; no .git -> the cwd folder itself
repo = t / "myrepo"; (repo / ".git").mkdir(parents=True); (repo / "a/b").mkdir(parents=True)
(t / "plain").mkdir()
assert p.project(repo / "a/b") == "myrepo" and p.project(t / "plain") == "plain"
os.environ["AODD_PLANS"] = str(t / "{project}/plans")
assert p.plans(repo / "a/b") == t / "myrepo/plans" and p.plans(t / "plain") == t / "plain/plans"
os.environ["AODD_PLANS"] = str(t / "fixed")
assert p.plans(repo) == t / "fixed"
os.environ.pop("AODD_REPORTS"); os.environ.pop("AODD_STATE")
assert p.worklog() == t / "h/work-log" and p.memory() == t / "h/memory"
os.environ["AODD_WORKLOG"] = str(t / "wl"); assert p.worklog() == t / "wl"
os.environ.pop("CLAUDE_HOME", None)
assert p.workspace_dirs() == [(Path.home() / ".claude").resolve()]
os.environ["AODD_WORKSPACE"] = f"{t}{os.pathsep}{t / 'h'}"
assert p.workspace_dirs() == [t.resolve(), (t / "h").resolve()]
os.environ["AODD_MEMORY"] = f"{t / 'm1'}{os.pathsep}{t / 'm2'}"
assert p.memory() == t / "m1" and p.memory_dirs() == [t / "m1", t / "m2"]
os.environ.pop("AODD_MEMORY"); assert p.memory_dirs() == [t / "h/memory"]
# settings.json "env" is not shell-expanded: "$HOME/x" must still resolve under the real home
import subprocess, sys
out = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, %r); import _aodd_paths as a; print(a.reports())" % str(Path(__file__).parent)],
                     env={**os.environ, "AODD_REPORTS": "$HOME/aodd-x", "HOME": "/tmp/h"}, capture_output=True, text=True).stdout.strip()
assert out == "/tmp/h/aodd-x", out
assert p.session_id("/x/abcdef12-3456.jsonl") == "abcdef12"
assert p.session_id("/x/brain/c040dfd2-31ad-4f81/.system_generated/logs/transcript.jsonl") == "c040dfd2"
assert p.session_id("/x/sessions/rollout-2026-10-17T09-00-00-019299ab-112233445566.jsonl") == "33445566"
print("ok")
