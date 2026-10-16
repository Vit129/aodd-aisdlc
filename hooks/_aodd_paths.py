"""Where AODD keeps its files. Standard library only; every variable is optional.

AODD_HOME     ~/.aodd
AODD_REPORTS  $AODD_HOME/pending-reports   audit reports, agent-ops reports, agy proposals (decided ones in done/)
AODD_STATE    $AODD_HOME/state             hook state (one marker per session)
AODD_PLANS    $AODD_HOME/plans             briefs, ai-sdlc progress files, handoffs; may contain {project}
AODD_WORKLOG  $AODD_HOME/work-log          one JSONL file per month, written by hooks/work-log.py
AODD_MEMORY   $AODD_HOME/memory            agent-memory module: knowledge/*.md, <project>/SESSION-TOPICS.md
AODD_WORKSPACE  <claude home>              agent-memory module: dirs (os.pathsep list) where the central report
                                           queue is shown at session start; default CLAUDE_HOME or ~/.claude
AODD_WORKLOG_SKIP  (empty)                 path globs (os.pathsep list) of session dirs the Work Log skips

{project} = folder name of the git repo that holds the session's working directory (the directory
itself when there is no .git above it). Shell: python3 hooks/_aodd_paths.py reports|state|plans [cwd]
"""
import os
import sys
from pathlib import Path


def home() -> Path:
    return Path(os.environ.get("AODD_HOME") or Path.home() / ".aodd").expanduser()


def reports() -> Path:
    return Path(os.environ.get("AODD_REPORTS") or home() / "pending-reports").expanduser()


def state() -> Path:
    return Path(os.environ.get("AODD_STATE") or home() / "state").expanduser()


def worklog() -> Path:
    return Path(os.environ.get("AODD_WORKLOG") or home() / "work-log").expanduser()


def memory() -> Path:
    return Path(os.environ.get("AODD_MEMORY") or home() / "memory").expanduser()


def claude_home() -> Path:
    return Path(os.environ.get("CLAUDE_HOME") or Path.home() / ".claude").expanduser()


def workspace_dirs() -> list:
    raw = os.environ.get("AODD_WORKSPACE")
    dirs = [d for d in raw.split(os.pathsep) if d] if raw else [str(claude_home())]
    return [Path(d).expanduser().resolve() for d in dirs]


def project(cwd=None) -> str:
    start = Path(cwd or os.getcwd()).expanduser().resolve()
    for d in (start, *start.parents):
        if (d / ".git").exists():
            return d.name
    return start.name


def plans(cwd=None) -> Path:
    tpl = os.environ.get("AODD_PLANS") or str(home() / "plans")
    return Path(tpl.replace("{project}", project(cwd)) if "{project}" in tpl else tpl).expanduser()


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else ""
    if what in ("home", "reports", "state", "worklog", "memory", "claude_home"):
        print(globals()[what]())
    elif what == "plans":
        print(plans(sys.argv[2] if len(sys.argv) > 2 else None))
    else:
        sys.exit("usage: _aodd_paths.py home|reports|state|worklog|memory|claude_home|plans [cwd]")
