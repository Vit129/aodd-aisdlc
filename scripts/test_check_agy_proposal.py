import importlib.util
import subprocess
import tempfile
from pathlib import Path

spec = importlib.util.spec_from_file_location("c", Path(__file__).with_name("check_agy_proposal.py"))
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)

repo = Path(tempfile.mkdtemp())
g = lambda *a: subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True).stdout.strip()
g("init", "-q", "-b", "main"); (repo / "f").write_text("1"); g("add", "."); g("-c", "core.hooksPath=/dev/null", "commit", "-qm", "fix")
sha = g("rev-parse", "--short", "HEAD")

good = f"""# agy-proposal: x
- **Project:** demo
- **Repo:** {repo}
- **What:** ~/.claude/skills/git-safety/SKILL.md
- **Analysis:** root cause is X; recurs whenever Y; belongs in ~/.claude because every repo does Y
- **Code:** scripts/x.py:12
- **Test:** `python3 t.py` -> AssertionError line 4
- **Fix:** set GIT_CONFIG_GLOBAL in the test env
- **Verified:** `python3 t.py` -> ok (exit 0)
- **Commit:** {sha}
- **Proposed change:**
  ```diff
  + a new pitfall line
  ```
"""
assert c.problems(good) == [], c.problems(good)
assert any("Analysis" in p for p in c.problems(good.replace("- **Analysis:** root cause is X; recurs whenever Y; belongs in ~/.claude because every repo does Y\n", "")))
assert any("Commit" in p for p in c.problems(good.replace(sha, "deadbee")))               # hash must exist
assert any("hash" in p for p in c.problems(good.replace(f"- **Commit:** {sha}", "- **Commit:** pushed it")))
assert any("AGENTS.md" in p for p in c.problems(good.replace("~/.claude/skills/git-safety/SKILL.md", "src/app.js")))
assert any("not a git repo" in p for p in c.problems(good.replace(str(repo), "/nonexistent")))
same = good.replace("`python3 t.py` -> ok (exit 0)", "`python3 t.py` -> AssertionError line 4")
assert any("repeats" in p for p in c.problems(same))
assert any("Test" in p for p in c.problems(good.replace("`python3 t.py` -> AssertionError line 4", "n/a")))  # placeholder
assert c.main([]) == 0
print("ok")
