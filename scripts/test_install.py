import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
T = Path(tempfile.mkdtemp())
env = {k: v for k, v in os.environ.items() if not k.startswith("AODD_")}
REA_LOG = T / "rea.log"                                                          # stub REA launcher: never npx/network
(T / "rea").write_text(f'#!/bin/sh\necho "$@" >> "{REA_LOG}"\n'); (T / "rea").chmod(0o755)
env.update(CLAUDE_HOME=str(T / "claude"), CODEX_HOME=str(T / "codex"), AODD_SCHEDULES_DRY_RUN="1", AODD_REA_CMD=str(T / "rea"))


def run(*flags, extra=None, home=None):
    p = subprocess.run(["bash", str(ROOT / "install.sh"), *flags], capture_output=True, text=True, stdin=subprocess.DEVNULL,
                       env={**env, **(extra or {})})
    assert p.returncode == 0, p.stderr
    return p.stdout


out = run("--dry-run", "--codex")
assert "AGENTS" in out and "would register" in out and not (T / "codex").exists() and not (T / "claude").exists()

(T / "codex").mkdir()
(T / "codex/AGENTS.md").write_text("# mine\n")
(T / "claude/hooks").mkdir(parents=True)
mine = T / "claude/hooks/my-own-hook.py"; mine.write_text("x"); mine.chmod(0o644)
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
assert set(hooks) == {"Stop", "PreToolUse", "PostToolUse"} and len(hooks["Stop"]) == 5   # theirs + four of ours (graphify-guard, skill-capture, done-gate, work-log), once
assert (T / "codex/skills/ai-sdlc/SKILL.md").is_file() and (T / "codex/agents/auditor.md").is_file()
assert (T / "codex/hooks/done-gate.py").is_file() and (T / "claude/settings.json").is_file()   # --codex is in addition to the Claude install
assert (T / "claude/skills/ai-sdlc/phases/phase1-interview.md").is_file() and not (T / "claude/rules/ai-sdlc").exists()   # phase files are on-demand: under the skill, never under rules/ (Claude Code auto-loads rules/)
assert (T / "claude/hooks/_aodd_paths.py").is_file() and (T / "codex/hooks/_aodd_paths.py").is_file()   # the shared resolver rides along
assert (mine.stat().st_mode & 0o777) == 0o644, "install must not chmod the host's own files"
assert os.access(T / "claude/hooks/done-gate.py", os.X_OK)                 # its own hooks stay executable
assert not (T / "claude/scripts/git-hooks").exists(), "repo git hooks are never installed (they would clobber the host's own)"

# --- optional modules --------------------------------------------------------------------------
assert not (T / "claude/hooks/memory-recall.py").exists() and not (T / "claude/scripts/install-schedules.py").exists()   # core only by default
assert (T / "claude/hooks/secret-read-guard.py").is_file() and (T / "claude/hooks/_aodd_secrets.py").is_file()
out = run("--dry-run", "--all")
assert "modules core agent-memory schedules" in out and "rea     setup --client claude_code --dry-run" in out and "schedule agent-ops" in out and "delegation" not in out
bad = subprocess.run(["bash", str(ROOT / "install.sh"), "--with", "nope"], capture_output=True, text=True, env=env)
assert bad.returncode == 2 and "unknown module" in bad.stderr
M = T / "m"
menv = {"CLAUDE_HOME": str(M / "c"), "AODD_HOME": str(M / "a"), "AODD_LAUNCHAGENTS_DIR": str(M / "la")}
out = run("--with", "agent-memory", extra=menv)
for f in ("hooks/memory-recall.py", "hooks/memory-write-scan.py", "hooks/session-start-recent.py"):
    assert (M / "c" / f).is_file(), f
assert not (M / "c/scripts/install-schedules.py").exists()                       # schedules not chosen -> not installed
st = json.loads((M / "c/settings.json").read_text())
assert {"UserPromptSubmit", "SessionStart"} <= set(st["hooks"]) and st["env"] == {"AODD_HOME": str(M / "a")}
run("--with", "agent-memory,schedules", extra=menv)                            # add a module later
assert (M / "c/scripts/install-schedules.py").is_file() and (M / "c/schedules/jobs.json").is_file() and (M / "c/scripts/aodd_job.py").is_file()
snap = {p: p.read_bytes() for p in (M / "c").rglob("*") if p.is_file()}
second = run("--all", extra=menv)                                                # idempotent: nothing changes, no new .aodd-bak
assert snap == {p: p.read_bytes() for p in (M / "c").rglob("*") if p.is_file()}, "second run changed files"
assert "UPDATE" not in second and "would register" not in second
assert not list((M / "la").glob("*")), "schedules installer must not write launch agents under AODD_SCHEDULES_DRY_RUN"
assert (M / "c/skills/reverse-engineer-anything/SKILL.md").is_file()             # rea is core: skill copied and setup run even with no module chosen
assert "setup --client claude_code --yes" in REA_LOG.read_text()
# a user's own env value is kept, and no env is written when nothing is set
run("--core-only", extra={"CLAUDE_HOME": str(M / "c2")})
assert "env" not in json.loads((M / "c2/settings.json").read_text())
json.dump({"env": {"AODD_HOME": "/mine"}}, open(M / "c2/settings.json", "w"))
assert "kept" in run("--core-only", extra={"CLAUDE_HOME": str(M / "c2"), "AODD_HOME": str(M / "other")})
assert json.loads((M / "c2/settings.json").read_text())["env"]["AODD_HOME"] == "/mine"
print("ok")

# --- --no-backup: an UPDATE over differing files leaves no .aodd-bak anywhere ---------------------
N = T / "nb"
nenv = {"CLAUDE_HOME": str(N / "c"), "CODEX_HOME": str(N / "x"), "AGY_HOME": str(N / "g/antigravity-cli")}
for f in ("c/skills/ai-sdlc/SKILL.md", "c/settings.json", "x/AGENTS.md", "x/hooks.json", "g/AGENTS.md", "g/antigravity-cli/skills/ai-sdlc/SKILL.md"):
    (N / f).parent.mkdir(parents=True, exist_ok=True); (N / f).write_text("{}" if f.endswith(".json") else "mine\n")
out = run("--no-backup", "--codex", "--agy", extra=nenv)
assert "UPDATE" in out and not list(N.rglob("*.aodd-bak")), list(N.rglob("*.aodd-bak"))
print("ok - install self-test passed (incl. --no-backup)")

# agent detection: a fake PATH and HOME decide what is found; a non-terminal run never adds a target by itself
fake = T / "fakebin"; fake.mkdir()
for b in ("codex", "hermes", "opencode"):
    (fake / b).write_text("#!/bin/sh\n"); (fake / b).chmod(0o755)
(T / "fakehome/.cursor").mkdir(parents=True)
det = {"PATH": f"{fake}:/usr/bin:/bin", "HOME": str(T / "fakehome")}
out = run("--detect", extra=det)
assert "found: codex cursor opencode hermes" in out, out
assert "no installer yet for: cursor opencode hermes" in out and "warn    no agy" not in out
assert "install into" not in out  # --detect only prints
out = run("--dry-run", "--core-only", extra=det)
assert "add --codex" in out and "(codex)" not in out, out
out = run("--detect", extra={"PATH": "/usr/bin:/bin", "HOME": str(T / "fakehome")})
assert "warn    no agy or codex CLI" in out, out
