import os, sys, tempfile
from pathlib import Path
for k in ("AODD_HOME", "AODD_REPORTS", "AODD_STATE", "AODD_PLANS"):
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
print("ok")
