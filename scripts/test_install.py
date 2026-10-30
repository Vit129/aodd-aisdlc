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

# --- project mode: the same files under one repository's .claude/, nothing machine-wide ----------
def repo(name, files):
    r = T / "projects" / name
    r.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(r)], check=True)
    for rel, text in files.items():
        (r / rel).parent.mkdir(parents=True, exist_ok=True)
        (r / rel).write_text(text)
    return r


def tree(*roots):  # every file in the repos (not .git): equal before and after means nothing changed
    return {p: p.read_bytes() for r in roots for p in r.rglob("*") if p.is_file() and ".git" not in p.relative_to(r).parts}


SKILL_HOOK = {"UserPromptSubmit": [{"hooks": [{"type": "command", "command": "python3 .claude/hooks/skill-trigger.py"}]}]}
alpha = repo("alpha", {".claude/settings.json": json.dumps({"hooks": SKILL_HOOK}), "AGENTS.md": "# mine\n", "CLAUDE.md": "@AGENTS.md\n"})
beta = repo("beta", {".claude/aidlc.json": '{"artifactPath": "agent-memory/plans"}\n'})
gamma = repo("gamma", {"CLAUDE.md": "# guidelines\n"})
REPOS = [alpha, beta, gamma]
flags = [f for r in REPOS for f in ("--project", str(r))]
LA = {"AODD_LAUNCHAGENTS_DIR": str(T / "la-proj")}
global_before = {p: p.read_bytes() for p in (T / "claude").rglob("*") if p.is_file()}
out = run(*flags, extra=LA)
assert "skip    schedules and rea" in out and not list((T / "la-proj").glob("*"))
assert {p: p.read_bytes() for p in (T / "claude").rglob("*") if p.is_file()} == global_before, "the Claude home is read, never written"

settings = (alpha / ".claude/settings.json").read_text()
ours = [h["command"] for ev in json.loads(settings)["hooks"].values() for g in ev for h in g["hooks"] if "$CLAUDE_PROJECT_DIR" in h["command"]]
assert len(ours) == 16 and all('CLAUDE_HOME="$CLAUDE_PROJECT_DIR/.claude"' in c for c in ours), ours   # core (12) + subagent-rules + agent-memory (3): the same set in every repo
assert "skill-trigger.py" in settings                                                                    # the repo's own hook stays
assert "done-gate" in settings and "coding-rules-gate" in settings
assert str(T) not in settings                                                                            # committable: no machine path
smoke = next(c for c in ours if "memory-recall.py" in c)
assert subprocess.run(["sh", "-c", smoke], env={**env, "CLAUDE_PROJECT_DIR": str(gamma)}, input="{}", capture_output=True, text=True).returncode == 0
no_dir = {k: v for k, v in env.items() if k != "CLAUDE_PROJECT_DIR"}
assert subprocess.run(["sh", "-c", smoke], env=no_dir, input="{}", capture_output=True, text=True).returncode == 0, "no project dir: fail-open"

assert (beta / ".claude/aidlc.json").read_text() == '{"artifactPath": "agent-memory/plans"}\n'         # a repo's own files are not touched
assert (beta / ".claude/hooks/done-gate.py").is_file() and (gamma / ".claude/skills/ai-sdlc/SKILL.md").is_file()
assert (gamma / "CLAUDE.md").read_text() == "# guidelines\n@AGENTS.md\n"          # the import is appended, the guidelines kept
assert (alpha / "CLAUDE.md").read_text() == "@AGENTS.md\n" and (beta / "CLAUDE.md").read_text() == "@AGENTS.md\n"   # already imported / created
ag = (alpha / "AGENTS.md").read_text()
assert ag.startswith("# mine\n") and ag.count("<!-- aodd:begin -->") == 1 and "this repo's .claude/ folder" in ag
assert (alpha / ".gitignore").read_text() == "__pycache__/\n" and (gamma / ".gitignore").read_text() == "__pycache__/\n"
assert not list((T / "projects").rglob("*.aodd-bak")), "git is the backup: no .aodd-bak inside a repo"
snap = tree(*REPOS)
second = run(*flags, extra=LA)
assert tree(*REPOS) == snap and ": registered" not in second and "UPDATE" not in second, second

fresh = repo("fresh", {"AGENTS.md": "# fresh\n"})
run("--dry-run", "--project", str(fresh))
assert tree(fresh) == {fresh / "AGENTS.md": b"# fresh\n"} and not (fresh / ".claude").exists()

lite = repo("lite", {})
run("--project", str(lite), "--core-only")
assert not (lite / ".claude/hooks/memory-recall.py").exists() and (lite / ".claude/hooks/done-gate.py").is_file()
out = run("--project", str(lite), "--with", "schedules", extra=LA)
assert "skip    schedules" in out and not (lite / ".claude/scripts/install-schedules.py").exists() and not list((T / "la-proj").glob("*"))

home = T / "home"
(home / "work").mkdir(parents=True)
subprocess.run(["git", "init", "-q", str(home / "work/acme")], check=True)
COMPANY = {"AODD_COMPANY_PATHS": str((home / "work").resolve()) + "/*"}
company = subprocess.run(["bash", str(ROOT / "install.sh"), "--project", str(home / "work/acme")], capture_output=True, text=True, env={**env, **COMPANY})
assert company.returncode == 2 and "company work" in company.stderr and not (home / "work/acme/.claude").exists()
run("--project", str(home / "work/acme"), extra={**COMPANY, "AODD_ALLOW_COMPANY": "1"})   # explicit override
assert (home / "work/acme/.claude/hooks/done-gate.py").is_file()
plain = T / "plain"
plain.mkdir()
notgit = subprocess.run(["bash", str(ROOT / "install.sh"), "--project", str(plain)], capture_output=True, text=True, env=env)
assert notgit.returncode == 2 and "not a git repository" in notgit.stderr and not (plain / ".claude").exists()
