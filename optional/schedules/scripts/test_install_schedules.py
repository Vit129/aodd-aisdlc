import importlib.util, os, plistlib, stat, sys, tempfile
from pathlib import Path

T = Path(tempfile.mkdtemp()).resolve()
os.environ.update(AODD_HOME=str(T / "aodd"), AODD_LAUNCHAGENTS_DIR=str(T / "la"), CLAUDE_HOME=str(T / "ch"))
for k in ("AODD_STATE", "AODD_REPORTS"):
    os.environ.pop(k, None)
claude = T / "bin/claude"; claude.parent.mkdir(); claude.write_text("#!/bin/sh\n"); claude.chmod(0o755)
os.environ["CLAUDE_BIN"] = str(claude)
spec = importlib.util.spec_from_file_location("s", Path(__file__).with_name("install-schedules.py"))
s = importlib.util.module_from_spec(spec); spec.loader.exec_module(s)

# time parsing
assert s.parse_time("08:30", "mon 09:00") == (1, 8, 30) and s.parse_time("fri 17:05", "mon 09:00") == (5, 17, 5)
assert s.parse_time("daily 7:00", "mon 09:00") == (None, 7, 0) and s.parse_time("22:00", "daily 08:45") == (None, 22, 0)
for bad in ("25:00", "9", "funday 09:00"):
    try: s.parse_time(bad, "daily 09:00"); raise SystemExit("accepted " + bad)
    except ValueError: pass

# launchd: dry run writes nothing; real run writes absolute-path plists; second run is a no-op
assert s.main(["--platform", "launchd", "--dry-run", "--modules", "agent-memory"]) == 0 and not (T / "la").exists()
assert s.main(["--platform", "launchd", "--modules", "agent-memory", "--set", "agent-ops=tue 10:30", "--set", "housekeeping=off"]) == 0
plists = sorted((T / "la").glob("*.plist"))
assert [p.name for p in plists] == ["com.aodd.agent-ops.plist", "com.aodd.memory-backup.plist", "com.aodd.pending-work.plist"], plists
p = plistlib.loads(plists[0].read_bytes())
assert p["StartCalendarInterval"] == {"Hour": 10, "Minute": 30, "Weekday": 2}
assert os.path.isabs(p["ProgramArguments"][0]) and p["ProgramArguments"][2] == "agent-ops"
assert p["EnvironmentVariables"]["CLAUDE_BIN"] == str(claude) and p["EnvironmentVariables"]["AODD_HOME"] == str(T / "aodd")
assert "AODD_REPORTS" not in p["EnvironmentVariables"] and p["StandardOutPath"].endswith("logs/agent-ops.log")
before = {q: q.stat().st_mtime_ns for q in plists}
assert s.main(["--platform", "launchd", "--modules", "agent-memory", "--set", "agent-ops=tue 10:30", "--set", "housekeeping=off"]) == 0
assert before == {q: q.stat().st_mtime_ns for q in plists}
# without the agent-memory module the backup job is skipped
assert s.main(["--platform", "launchd", "--modules", "", "--only", "memory-backup", "--dry-run"]) == 0
assert s.main(["--platform", "launchd", "--uninstall"]) == 0 and not list((T / "la").glob("*.plist"))

# cron through a fake crontab binary that keeps its table in a file
tab = T / "tab"; tab.write_text("MAILTO=me\n0 1 * * * mine\n")
fake = T / "bin/crontab"
fake.write_text(f'#!/bin/sh\nif [ "$1" = "-l" ]; then cat {tab}; else cat > {tab}; fi\n'); fake.chmod(0o755)
os.environ["AODD_CRONTAB"] = str(fake)
assert s.main(["--platform", "cron", "--modules", "agent-memory"]) == 0
txt = tab.read_text()
assert "0 1 * * * mine" in txt and txt.count("# aodd:begin") == 1 and "0 9 * * 1 env" in txt and "45 8 * * * env" in txt
assert f"CLAUDE_BIN={claude}" in txt and "/aodd_job.py agent-ops" in txt and "logs/agent-ops.log" in txt
assert s.main(["--platform", "cron", "--modules", "agent-memory"]) == 0 and tab.read_text() == txt   # idempotent
assert s.main(["--platform", "cron", "--modules", "agent-memory", "--set", "agent-ops=wed 06:00"]) == 0
assert tab.read_text().count("# aodd:begin") == 1 and "0 6 * * 3 env" in tab.read_text()
assert s.main(["--platform", "cron", "--uninstall"]) == 0 and tab.read_text() == "MAILTO=me\n0 1 * * * mine\n"

# no claude: model jobs are skipped with a warning, not an error
os.environ["CLAUDE_BIN"] = ""
os.environ["PATH"] = str(T / "nowhere")
assert s.main(["--platform", "launchd", "--modules", "", "--dry-run"]) == 0
print("ok")
