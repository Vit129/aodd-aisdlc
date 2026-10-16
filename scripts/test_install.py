import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
T = Path(tempfile.mkdtemp())
env = {**os.environ, "CLAUDE_HOME": str(T / "claude"), "CODEX_HOME": str(T / "codex")}


def run(*flags):
    p = subprocess.run(["bash", str(ROOT / "install.sh"), *flags], capture_output=True, text=True, env=env)
    assert p.returncode == 0, p.stderr
    return p.stdout


out = run("--dry-run", "--codex")
assert "AGENTS" in out and "would register" in out and not (T / "codex").exists() and not (T / "claude").exists()

(T / "codex").mkdir()
(T / "codex/AGENTS.md").write_text("# mine\n")
(T / "codex/hooks.json").write_text(json.dumps({"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "echo mine"}]}]}}))
run("--codex")
first = (T / "codex/AGENTS.md").read_text()
run("--codex")
assert (T / "codex/AGENTS.md").read_text() == first, "second run must not change AGENTS.md"
assert first.startswith("# mine\n") and first.count("<!-- aodd:begin -->") == 1 and first.count("<!-- aodd:end -->") == 1
assert (T / "codex/AGENTS.md.aodd-bak").read_text() == "# mine\n" and (T / "codex/hooks.json.aodd-bak").is_file()
(T / "codex/AGENTS.md").write_text(first.replace("AODD", "AODD-EDITED", 1))   # a changed block is replaced, not duplicated
run("--codex")
assert (T / "codex/AGENTS.md").read_text() == first
hooks = json.loads((T / "codex/hooks.json").read_text())["hooks"]
assert set(hooks) == {"Stop", "PreToolUse", "PostToolUse"} and len(hooks["Stop"]) == 3   # theirs + two of ours, once
assert (T / "codex/skills/ai-sdlc/SKILL.md").is_file() and (T / "codex/agents/auditor.md").is_file()
assert (T / "codex/hooks/done-gate.py").is_file() and (T / "claude/settings.json").is_file()   # --codex is in addition to the Claude install
assert (T / "claude/hooks/_aodd_paths.py").is_file() and (T / "codex/hooks/_aodd_paths.py").is_file()   # the shared resolver rides along
assert not (T / "claude/scripts/git-hooks").exists(), "repo git hooks are never installed (they would clobber the host's own)"
print("ok")
