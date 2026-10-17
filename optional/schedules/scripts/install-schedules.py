#!/usr/bin/env python3
"""Install (or remove) the AODD scheduled jobs as cron lines (Linux) or launchd agents (macOS).

  install-schedules.py [--dry-run] [--set JOB="mon 09:00" ...] [--only JOB,JOB] [--modules agent-memory,...]
  install-schedules.py --uninstall [--dry-run]
  install-schedules.py --list                      job<TAB>default time<TAB>what it produces

Times are "HH:MM" (keeps the job's default day) or "<day> HH:MM" with day = daily|mon|tue|wed|thu|fri|sat|sun;
`--set JOB=off` skips a job. Jobs come from schedules/jobs.json and run `aodd_job.py JOB`. Absolute paths of
python3 and claude are resolved NOW and written into the entry, because cron and launchd have no shell rc.
Output goes to $AODD_STATE/logs/<job>.log. Re-running replaces the entries in place (idempotent). A job whose
module is not installed (jobs.json "requires"), or that needs claude when claude is not found, is skipped
with a warning. Only AODD_*/CLAUDE_HOME variables you have set are baked into the entry.

Platform: launchd on macOS (agents in ~/Library/LaunchAgents, or $AODD_LAUNCHAGENTS_DIR), cron elsewhere
(managed block between `# aodd:begin` / `# aodd:end`; crontab binary: $AODD_CRONTAB or PATH).
--platform cron|launchd forces one. Nothing is written with --dry-run.
"""
import argparse
import json
import os
import plistlib
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _d in (HERE.parent / "hooks", HERE.parents[2] / "hooks"):
    sys.path.append(str(_d))
import _aodd_paths as paths  # noqa: E402

JOBS_FILE = HERE.parent / "schedules" / "jobs.json"
RUNNER = HERE / "aodd_job.py"
DAYS = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]   # index = cron/launchd weekday (0 = Sunday)
LABEL = "com.aodd.{}"
BAKE = ("AODD_HOME", "AODD_REPORTS", "AODD_STATE", "AODD_PLANS", "AODD_WORKLOG", "AODD_MEMORY", "AODD_REPOS",
        "AODD_WORKSPACE", "AODD_WORKLOG_SKIP", "CLAUDE_HOME", "CODEX_HOME")


def load_jobs():
    return json.loads(JOBS_FILE.read_text())["jobs"]


def parse_time(spec: str, default: str):
    """-> (weekday or None for daily, hour, minute). A bare HH:MM keeps the default's day."""
    spec = spec.strip().lower()
    day = None if default.split()[0] == "daily" else DAYS.index(default.split()[0][:3])
    parts = spec.split()
    if len(parts) == 2:
        if parts[0] != "daily" and parts[0][:3] not in DAYS:
            raise ValueError(f"unknown day {parts[0]!r}")
        day, spec = (None if parts[0] == "daily" else DAYS.index(parts[0][:3])), parts[1]
    m = re.fullmatch(r"([01]?\d|2[0-3]):([0-5]\d)", spec)
    if not m:
        raise ValueError(f"bad time {spec!r}: use HH:MM, optionally preceded by daily|mon..sun")
    return day, int(m.group(1)), int(m.group(2))


def describe(t) -> str:
    return f"{'daily' if t[0] is None else DAYS[t[0]]} {t[1]:02d}:{t[2]:02d}"


def baked_env(claude):
    env = {k: os.environ[k] for k in BAKE if os.environ.get(k)}
    dirs = [str(Path(p).parent) for p in (claude, shutil.which("git"), shutil.which("python3")) if p]
    env["PATH"] = os.pathsep.join(dict.fromkeys(dirs + ["/usr/local/bin", "/usr/bin", "/bin"]))
    if claude:
        env["CLAUDE_BIN"] = claude
    return env


def argv(job, python):
    return [python, str(RUNNER), job]


def cron_block(entries, env, logdir):
    lines = ["# aodd:begin (managed by install-schedules.py; edit with --set / --uninstall)"]
    for job, t in entries:
        when = f"{t[2]} {t[1]} * * {'*' if t[0] is None else t[0]}"
        envs = " ".join(f"{k}={shlex.quote(v)}" for k, v in sorted(env.items()))
        cmd = " ".join(shlex.quote(a) for a in argv(job, env["_PY"]))
        lines.append(f"{when} env {envs} {cmd} >> {shlex.quote(str(logdir / (job + '.log')))} 2>&1")
    return "\n".join(lines + ["# aodd:end"]) + "\n"


def merge_cron(current: str, block: str) -> str:
    pat = re.compile(r"# aodd:begin.*?# aodd:end\n?", re.S)
    if pat.search(current):
        return pat.sub(lambda _: block, current)
    return current + ("" if not current or current.endswith("\n") else "\n") + block


def plist_for(job, t, env, logdir):
    cal = {"Hour": t[1], "Minute": t[2]}
    if t[0] is not None:
        cal["Weekday"] = t[0]
    return plistlib.dumps({
        "Label": LABEL.format(job), "ProgramArguments": argv(job, env["_PY"]),
        "EnvironmentVariables": {k: v for k, v in env.items() if k != "_PY"},
        "StartCalendarInterval": cal,
        "StandardOutPath": str(logdir / f"{job}.log"), "StandardErrorPath": str(logdir / f"{job}.log"),
    })


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def crontab_bin():
    return os.environ.get("AODD_CRONTAB") or shutil.which("crontab")


def main(a=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--uninstall", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--set", action="append", default=[], metavar="JOB=TIME")
    ap.add_argument("--only", default="")
    ap.add_argument("--modules", default=None, help="comma list of installed modules (default: detect)")
    ap.add_argument("--platform", choices=["cron", "launchd"], default=None)
    ap.add_argument("--no-load", action="store_true", help="launchd: write plists but do not load them")
    args = ap.parse_args(a)
    jobs = load_jobs()
    if args.list:
        for j in jobs:
            print(f"{j['name']}\t{j['default']}\t{j['label']}: {j['produces']}")
        return 0
    platform = args.platform or ("launchd" if sys.platform == "darwin" else "cron")
    dry = args.dry_run
    tag = "[dry-run] " if dry else ""
    logdir = paths.state() / "logs"
    laDir = Path(os.environ.get("AODD_LAUNCHAGENTS_DIR") or Path.home() / "Library/LaunchAgents")

    if args.uninstall:
        return uninstall(jobs, platform, laDir, dry, tag)

    sets = dict(s.split("=", 1) for s in args.set if "=" in s)
    only = {x for x in args.only.split(",") if x}
    mods = set(args.modules.split(",")) if args.modules is not None else \
        ({"agent-memory"} if (paths.claude_home() / "hooks/memory-recall.py").is_file() else set())
    claude = os.environ.get("CLAUDE_BIN") or shutil.which("claude")
    python = shutil.which("python3") or sys.executable
    entries = []
    for j in jobs:
        name = j["name"]
        if only and name not in only:
            continue
        if sets.get(name, "").lower() == "off":
            print(f"skip    {name}: switched off")
            continue
        if j.get("requires") and j["requires"] not in mods:
            print(f"skip    {name}: needs the {j['requires']} module (./install.sh --with {j['requires']})")
            continue
        if j.get("model") and not claude:
            print(f"warn    {name}: claude not found on PATH (set CLAUDE_BIN); not scheduled")
            continue
        try:
            entries.append((name, parse_time(sets.get(name, j["default"]), j["default"])))
        except ValueError as e:
            print(f"error   {name}: {e}", file=sys.stderr)
            return 2
    if not entries:
        print("nothing to schedule")
        return 0
    env = {**baked_env(claude), "_PY": python}
    for name, t in entries:
        print(f"{tag}schedule {name:<14}{describe(t)}")
    print(f"{tag}logs    {logdir}")
    if not dry:
        logdir.mkdir(parents=True, exist_ok=True)

    if platform == "cron":
        exe = crontab_bin()
        if not exe:
            print("warn    crontab not found; nothing scheduled", file=sys.stderr)
            return 0
        cur = run([exe, "-l"])
        new = merge_cron(cur.stdout if cur.returncode == 0 else "", cron_block(entries, env, logdir))
        if cur.returncode == 0 and new == cur.stdout:
            print("cron    unchanged")
        elif not dry:
            r = run([exe, "-"], input=new)
            print("cron    updated" if r.returncode == 0 else f"error   crontab: {r.stderr.strip()}")
            return r.returncode
        else:
            print("[dry-run] cron block:\n" + cron_block(entries, env, logdir))
        return 0

    for name, t in entries:
        f = laDir / f"{LABEL.format(name)}.plist"
        data = plist_for(name, t, env, logdir)
        if f.is_file() and f.read_bytes() == data:
            print(f"launchd {f.name}: unchanged")
            continue
        print(f"{tag}launchd {f.name}")
        if dry:
            continue
        laDir.mkdir(parents=True, exist_ok=True)
        f.write_bytes(data)
        if not args.no_load and not os.environ.get("AODD_LAUNCHAGENTS_DIR"):
            uid = str(os.getuid())
            run(["launchctl", "bootout", f"gui/{uid}/{LABEL.format(name)}"])
            r = run(["launchctl", "bootstrap", f"gui/{uid}", str(f)])
            if r.returncode != 0:
                print(f"warn    launchctl bootstrap {f.name}: {r.stderr.strip()}")
    return 0


def uninstall(jobs, platform, laDir, dry, tag):
    if platform == "cron":
        exe = crontab_bin()
        cur = run([exe, "-l"]) if exe else None
        if not cur or cur.returncode != 0 or "# aodd:begin" not in cur.stdout:
            print("cron    nothing to remove")
            return 0
        new = re.sub(r"# aodd:begin.*?# aodd:end\n?", "", cur.stdout, flags=re.S)
        print(f"{tag}cron    removing the aodd block")
        if not dry:
            run([exe, "-"], input=new)
        return 0
    for j in jobs:
        f = laDir / f"{LABEL.format(j['name'])}.plist"
        if f.is_file():
            print(f"{tag}remove  {f}")
            if not dry:
                if not os.environ.get("AODD_LAUNCHAGENTS_DIR"):
                    run(["launchctl", "bootout", f"gui/{os.getuid()}/{LABEL.format(j['name'])}"])
                f.unlink()
    return 0


if __name__ == "__main__":
    sys.exit(main())
