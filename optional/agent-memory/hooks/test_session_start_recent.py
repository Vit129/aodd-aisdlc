#!/usr/bin/env python3
"""Self-test for session-start-recent.py's Agent Ops pointer: python3 hooks/test_session_start_recent.py"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HOOK = Path(__file__).with_name("session-start-recent.py")
with tempfile.TemporaryDirectory() as home:
    reports = Path(home, "aodd/pending-reports")
    reports.mkdir(parents=True)
    ws = Path(home, "claude"); ws.mkdir()
    env = {k: v for k, v in os.environ.items() if not k.startswith("AODD_")}
    env.update(HOME=home, AODD_HOME=str(Path(home, "aodd")), CLAUDE_HOME=str(ws))
    run = lambda cwd=None, e=None: subprocess.run([sys.executable, str(HOOK)], input=json.dumps({"cwd": str(cwd or ws)}),
                                          capture_output=True, text=True, env={**env, **(e or {})}).stdout
    proj = Path(home, "work/proj"); proj.mkdir(parents=True)
    assert run() == ""                                   # no report -> silent
    (reports / "agent-ops-2026-10-20.md").write_text("x")
    assert "agent-ops-2026-10-20.md" in run()            # new report -> pointer
    assert run() == ""                                   # shown once only
    (reports / "housekeeping-2026-10-20.md").write_text("x")
    assert run(proj) == ""                               # a project session never sees the central queue
    out = run()
    assert "housekeeping-2026-10-20.md" in out and "agent-ops" not in out  # each kind, only the new one
    (reports / "agy-proposal-2026-10-20-thin.md").write_text("- **What:** .claude/skills/x/SKILL.md\nlooks useful")
    out = run()
    assert "auto-rejected" in out and "agy-proposal-2026-10-20-thin.md" in out    # no evidence -> filed, CEO not asked
    assert (reports / "done/agy-proposal-2026-10-20-thin.md").is_file() and "Auto-rejected" in (reports / "done/agy-proposal-2026-10-20-thin.md").read_text()
    repo = Path(home, "repo"); repo.mkdir()
    g = lambda *a: subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True).stdout.strip()
    g("init", "-q"); (repo / "f").write_text("1"); g("add", "."); g("-c", "core.hooksPath=/dev/null", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x")
    sha = g("rev-parse", "HEAD")
    good = "\n".join(f"- **{k}:** {v}" for k, v in [
        ("Project", "demo"), ("Repo", str(repo)), ("What", ".claude/skills/x/SKILL.md"),
        ("Analysis", "root cause A, recurs on B, global because C"), ("Code", "src/a.py:10"),
        ("Test", "pytest -> 1 failed"), ("Fix", "guard the None case"), ("Verified", "pytest -> 3 passed"),
        ("Commit", sha), ("Proposed change", "+ add pitfall line")])
    (reports / "agy-proposal-2026-10-20-x.md").write_text(good)
    assert "agy-proposal-2026-10-20-x.md" in run() and "agy-proposal-2026-10-20-x.md" in run()  # with evidence: shown until decided
    assert "agy-proposal" not in run(proj)               # ...but only in the workspace
    (reports / "agy-proposal-2026-10-20-x.md").rename(reports / "done/agy-proposal-2026-10-20-x.md")
    assert "agy-proposal" not in run()                   # moved to done/ -> quiet
    # audits: PASS is silent; FAIL shows in the workspace and in the audited repo, not in other projects
    (reports / "audit-2026-10-20-aaaa.md").write_text(f"---\nrepo: {proj}\nverdict: PASS\n---\n")
    assert "audit-" not in run(proj) and (reports / "audit-2026-10-20-aaaa.md").is_file()  # project session: untouched
    assert "audit-" not in run() and (reports / "done/audit-2026-10-20-aaaa.md").is_file()  # workspace: PASS filed to done/
    (reports / "audit-2026-10-20-bbbb.md").write_text(f"---\nrepo: {proj}\nverdict: FAIL\n---\n")
    assert "audit-2026-10-20-bbbb.md: verdict: FAIL" in run() and "bbbb" in run(proj) and "bbbb" in run(proj / "src")
    other = Path(home, "work/other"); other.mkdir()
    assert "audit-" not in run(other)
    # AODD_WORKSPACE moves the workspace: a project dir listed there sees the queue, the Claude home no longer does
    (reports / "agent-ops-2026-10-27.md").write_text("x")
    assert "agent-ops-2026-10-27" not in run(proj) and "agent-ops-2026-10-27" not in run(ws, {"AODD_WORKSPACE": str(proj)})
    assert "agent-ops-2026-10-27" in run(proj, {"AODD_WORKSPACE": str(proj)})
    # the project's session digest comes from $AODD_MEMORY/<project>/SESSION-TOPICS.md
    Path(home, "aodd/memory/proj").mkdir(parents=True)
    Path(home, "aodd/memory/proj/SESSION-TOPICS.md").write_text("# T\n## 2026-01 first\nold\n## 2026-02 second\nlast one")
    assert "last one" in run(proj) and "2026-01 first" not in run(proj)
    # digest template + alias, and extra report kinds
    Path(home, "digests/other").mkdir(parents=True)
    Path(home, "digests/other/SESSION-TOPICS.md").write_text("## x\naliased digest")
    assert "aliased digest" not in run(proj)
    tpl = {"AODD_DIGEST": str(Path(home, "digests/{project}/SESSION-TOPICS.md"))}
    assert "aliased digest" not in run(proj, tpl)
    assert "aliased digest" in run(proj, {**tpl, "AODD_PROJECT_ALIASES": "x=y,proj=other"})
    (reports / "memory-consolidation-2026-10-30.md").write_text("x")
    assert "memory-consolidation" not in run()
    assert "memory-consolidation-2026-10-30" in run(None, {"AODD_REPORT_KINDS": "agent-ops, memory-consolidation"})
    # unfinished progress files of this project are pointed at, first open box only
    pl = {"AODD_PLANS": str(Path(home, "plans/{project}"))}
    f = Path(home, "plans/proj/login/ai-sdlc-task-progress.md"); f.parent.mkdir(parents=True)
    f.write_text("- [x] design\n- [ ] write tests\n- [ ] ship\n")
    out = run(proj, pl)
    assert "login" in out and "write tests" in out and "ship" not in out, out
    Path(home, "plans/proj/done-one").mkdir(); Path(home, "plans/proj/done-one/ai-sdlc-task-progress.md").write_text("- [x] a\n")
    assert "done-one" not in run(proj, pl)                       # all ticked -> not listed
    loc = proj / "agent-memory/plans/2026SP21/pbi-7/qa-task-progress.md"; loc.parent.mkdir(parents=True)
    loc.write_text("- [ ] Phase 2.1\n")
    assert "pbi-7" in run(proj)                                  # repo-local agent-memory/plans (legacy name) too
    loc.write_text("Moved to: 2026SP22/pbi-7\n- [ ] Phase 2.1\n")
    assert "pbi-7" not in run(proj)                              # carried over -> the old file is not live
print("ok - session-start-recent self-test passed")
