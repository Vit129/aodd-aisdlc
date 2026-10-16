#!/usr/bin/env python3
"""Scheduled AODD jobs. Run by cron / launchd (see install-schedules.py), or by hand:

  aodd_job.py agent-ops [--days N]   gather inputs, have Haiku (no tools) write the weekly team review
  aodd_job.py housekeeping           read-only scan of the Claude home and AODD state, Haiku writes the report
  aodd_job.py pending-work           uncommitted / unpushed / unmerged work in $AODD_REPOS (no model)
  aodd_job.py memory-backup          commit (and push, if a remote exists) $AODD_MEMORY (no model)

Rules for unattended runs: the shell side gathers inputs and writes the output file; the model only sees
the data on stdin (`claude -p --model haiku --tools ""`), so it has no permission to write anything. A
failed model call (non-zero exit or empty answer) writes NO report and exits 1 so the next tick retries and
the failure is visible in the log. Binaries: CLAUDE_BIN (default: `claude` on PATH). Reports go to
$AODD_REPORTS (hooks/_aodd_paths.py). Exit 0 = done or nothing to do, 1 = failed, 2 = bad usage.
"""
import os
import shutil
import subprocess
import sys
import time
from datetime import date, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _d in (HERE.parent / "hooks", HERE.parents[2] / "hooks"):  # installed: <home>/hooks; in the repo: hooks/
    sys.path.append(str(_d))
import _aodd_paths as paths  # noqa: E402

# installed: <home>/schedules next to scripts/; in the repo: optional/schedules/schedules
TEMPLATES = HERE.parent / "schedules"
GATHER = next((d / "agent_ops_gather.py" for d in (HERE, HERE.parents[2] / "scripts") if (d / "agent_ops_gather.py").is_file()),
              HERE / "agent_ops_gather.py")
MODEL_TIMEOUT = 900


def log(msg):
    print(f"{datetime.now().isoformat(timespec='seconds')} {msg}", flush=True)


def ask_model(prompt: str):
    exe = os.environ.get("CLAUDE_BIN") or shutil.which("claude")
    if not exe:
        log("claude not found (set CLAUDE_BIN)")
        return None
    try:
        # prompt on stdin, not argv: a prompt that starts with "-" would be parsed as an option
        r = subprocess.run([exe, "-p", "--model", "haiku", "--tools", ""], input=prompt,
                           capture_output=True, text=True, timeout=MODEL_TIMEOUT)
    except (OSError, subprocess.TimeoutExpired) as e:
        log(f"model call failed: {e}")
        return None
    if r.returncode != 0 or not r.stdout.strip():
        log(f"model call failed (exit {r.returncode}): {r.stderr.strip()[:300]}")
        return None
    return r.stdout.strip() + "\n"


def write_report(name: str, text: str) -> Path:
    out = paths.reports() / f"{name}-{date.today().isoformat()}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    log(f"wrote {out}")
    return out


def template(name: str, **subs) -> str:
    text = (TEMPLATES / name).read_text()
    for k, v in subs.items():
        text = text.replace("{{" + k + "}}", str(v))
    return text


def sop() -> str:
    f = paths.claude_home() / "skills/agent-ops/SKILL.md"
    try:
        text = f.read_text()
        a, b = text.index("## SOP"), text.find("## Self-Update")
        return text[a:b if b > a else None].strip()
    except (OSError, ValueError):
        return "Find projects with the most rework, skills never used, corrections that recur; propose at most 5 changes, each with its Why."


def job_agent_ops(days=7) -> int:
    data = Path(os.environ.get("TMPDIR") or "/tmp") / f"aodd-agent-ops-{os.getpid()}.md"
    try:
        subprocess.run([sys.executable, str(GATHER), str(data), "--days", str(days)], check=True, timeout=600)
        prompt = template("agent-ops.prompt.md", DAYS=days, SOP=sop()) + "\n--- DATA ---\n" + data.read_text()
    finally:
        data.unlink(missing_ok=True)
    answer = ask_model(prompt)
    if not answer:
        return 1
    write_report("agent-ops", answer)
    return 0


def _size(paths_):
    n = total = 0
    for p in paths_:
        try:
            total += p.stat().st_size
            n += 1
        except OSError:
            pass
    return n, total


def housekeeping_scan(now=None, transcript_days=30, state_days=14) -> str:
    now = now or time.time()
    home, state = paths.claude_home(), paths.state()

    def older(files, days):
        return [f for f in files if f.is_file() and now - f.stat().st_mtime > days * 86400]

    rows = [("transcripts older than %d days" % transcript_days, older(home.glob("projects/*/*.jsonl"), transcript_days)),
            ("hook state files older than %d days" % state_days, older(state.rglob("*") if state.is_dir() else [], state_days)),
            ("*.aodd-bak files from the installer", [f for f in home.rglob("*.aodd-bak") if f.is_file()]),
            ("archived skills (.archive)", [f for f in home.glob("skills/.archive/*/SKILL.md")])]
    lines = [f"scan of {home} and {state} (read-only)"]
    for label, files in rows:
        n, total = _size(files)
        lines.append(f"- {label}: {n} file(s), {total / 1e6:.1f} MB")
    return "\n".join(lines)


def job_housekeeping() -> int:
    prompt = template("housekeeping.prompt.md", DATE=date.today().isoformat()) + "\n--- DATA ---\n" + housekeeping_scan()
    answer = ask_model(prompt)
    if not answer:
        return 1
    write_report("housekeeping", answer)
    return 0


def git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=30)
    return r.returncode, r.stdout.strip()


def repo_list():
    out = []
    for base in (d for d in os.environ.get("AODD_REPOS", "").split(os.pathsep) if d):
        b = Path(base).expanduser()
        out += [b] if (b / ".git").exists() else [p for p in sorted(b.glob("*")) if (p / ".git").exists()]
    return out


def pending_work(repos) -> str:
    sections = []
    for repo in repos:
        items = []
        rc, dirty = git(repo, "status", "--porcelain", "--untracked-files=no")
        if dirty:
            items.append(f"{len(dirty.splitlines())} file(s) with uncommitted changes")
        rc, ahead = git(repo, "rev-list", "--count", "@{u}..HEAD")
        if rc == 0 and ahead not in ("", "0"):
            items.append(f"{ahead} commit(s) not pushed")
        base = next((b for b in ("main", "master") if git(repo, "rev-parse", "--verify", "-q", b)[0] == 0), None)
        if base:
            rc, out = git(repo, "branch", "--no-merged", base, "--format=%(refname:short)")
            names = [n for n in out.splitlines() if n]
            if names:
                items.append(f"{len(names)} branch(es) not merged into {base}: " + ", ".join(names[:5]) + (" ..." if len(names) > 5 else ""))
        if items:
            sections.append(f"## {repo.name}\n" + "\n".join(f"- {i}" for i in items))
    return "\n\n".join(sections)


def job_pending_work() -> int:
    repos = repo_list()
    if not repos:
        log("AODD_REPOS not set or holds no git repo: nothing to scan")
        return 0
    body = pending_work(repos)
    if not body:
        log("nothing pending")
        return 0
    write_report("pending-work", f"# Pending work {date.today().isoformat()}\n\n{body}\n")
    return 0


def job_memory_backup() -> int:
    mem = paths.memory()
    if not (mem / ".git").exists():
        log(f"{mem} is not a git repo: nothing to back up (git init it, add a remote to push)")
        return 0
    git(mem, "add", "-A")
    if git(mem, "diff", "--cached", "--quiet")[0] != 0:
        rc, out = git(mem, "-c", "user.name=aodd", "-c", "user.email=aodd@localhost", "commit", "-q", "-m",
                      "sync: " + datetime.now().isoformat(timespec="seconds"))
        if rc != 0:
            log(f"commit failed: {out[:200]}")
            return 1
        log("committed")
    else:
        log("no changes")
    if git(mem, "remote")[1]:  # push whatever is on HEAD: an earlier push may have failed
        rc, out = git(mem, "push", "-q")
        if rc != 0:
            log("push failed (will retry next run)")
            return 1
        log("pushed")
    return 0


JOBS = {"agent-ops": job_agent_ops, "housekeeping": job_housekeeping, "pending-work": job_pending_work,
        "memory-backup": job_memory_backup}


def main(argv):
    if not argv or argv[0] not in JOBS:
        print(__doc__, file=sys.stderr)
        return 2
    kw = {"days": int(argv[argv.index("--days") + 1])} if argv[0] == "agent-ops" and "--days" in argv else {}
    try:
        return JOBS[argv[0]](**kw)
    except Exception as e:  # a failed job must be visible in the log, not silent
        log(f"{argv[0]} failed: {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
