import importlib.util, os, subprocess, sys, tempfile
from pathlib import Path

T = Path(tempfile.mkdtemp()).resolve()
os.environ.update(AODD_HOME=str(T / "aodd"), CLAUDE_HOME=str(T / "claude"), CODEX_HOME=str(T / "none"), AODD_REPOS=str(T / "repos"))
for k in ("AODD_REPORTS", "AODD_STATE", "AODD_MEMORY"):
    os.environ.pop(k, None)
spec = importlib.util.spec_from_file_location("j", Path(__file__).with_name("aodd_job.py"))
j = importlib.util.module_from_spec(spec); spec.loader.exec_module(j)
reports = T / "aodd/pending-reports"

# stub claude: records its argv and stdin, answers with a report
stub = T / "claude-stub"
stub.write_text(f'#!/bin/sh\necho "$@" > {T}/argv\ncat > {T}/stdin\necho "# Stub report"\n')
stub.chmod(0o755)
os.environ["CLAUDE_BIN"] = str(stub)

(T / "claude/skills/demo").mkdir(parents=True)
(T / "claude/skills/demo/SKILL.md").write_text("---\nname: demo\n---\n")
assert j.main(["agent-ops", "--days", "3"]) == 0
rep = next(reports.glob("agent-ops-*.md"))
assert rep.read_text().startswith("# Stub report")
assert (T / "argv").read_text().split() == ["-p", "--model", "haiku", "--tools", ""] or (T / "argv").read_text().split() == ["-p", "--model", "haiku", "--tools"]
sent = (T / "stdin").read_text()
assert "last 3 days" in sent and "--- DATA ---" in sent and "demo" in sent and "{{" not in sent   # prompt on stdin, filled in

old = T / "claude/projects/p/old.jsonl"; old.parent.mkdir(parents=True); old.write_text("x" * 100)
os.utime(old, (1, 1))
assert j.main(["housekeeping"]) == 0 and next(reports.glob("housekeeping-*.md"))
assert "transcripts older than 30 days: 1 file(s)" in (T / "stdin").read_text()
assert old.exists()   # the scan never deletes

# a failing model call writes no report and exits 1
for f in reports.glob("*.md"):
    f.unlink()
stub.write_text("#!/bin/sh\ncat >/dev/null\nexit 3\n")
assert j.main(["agent-ops"]) == 1 and not list(reports.glob("*.md"))
stub.write_text("#!/bin/sh\ncat >/dev/null\n")   # exit 0 but empty answer is a failure too
assert j.main(["housekeeping"]) == 1 and not list(reports.glob("*.md"))

# pending-work: no model; only written when something is pending
g = lambda r, *a: subprocess.run(["git", "-C", str(r), "-c", "user.name=t", "-c", "user.email=t@t", *a], capture_output=True, text=True)
repo = T / "repos/app"; repo.mkdir(parents=True)
g(repo, "init", "-q", "-b", "main"); (repo / "f").write_text("1"); g(repo, "add", "."); g(repo, "commit", "-qm", "i")
assert j.main(["pending-work"]) == 0 and not list(reports.glob("pending-work-*.md"))
g(repo, "checkout", "-qb", "feat/x"); (repo / "g").write_text("2"); g(repo, "add", "."); g(repo, "commit", "-qm", "g")
(repo / "f").write_text("dirty")
assert j.main(["pending-work"]) == 0
text = next(reports.glob("pending-work-*.md")).read_text()
assert "## app" in text and "uncommitted" in text and "feat/x" in text

# memory-backup: not a repo -> skip; repo -> commit; second run -> no new commit
mem = T / "aodd/memory"; mem.mkdir(parents=True); (mem / "k.md").write_text("a")
assert j.main(["memory-backup"]) == 0 and not (mem / ".git").exists()
g(mem, "init", "-q"); assert j.main(["memory-backup"]) == 0
n = g(mem, "rev-list", "--count", "HEAD").stdout.strip()
assert n == "1" and j.main(["memory-backup"]) == 0 and g(mem, "rev-list", "--count", "HEAD").stdout.strip() == "1"
assert j.main(["nope"]) == 2
print("ok")
