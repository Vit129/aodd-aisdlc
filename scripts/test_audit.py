import os as _o, tempfile as _t
[_o.environ.pop(k, None) for k in ("AODD_REPORTS", "AODD_STATE", "AODD_PLANS")]
_o.environ["AODD_HOME"] = _t.mkdtemp()  # tests never touch the real AODD_HOME
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Sandboxed runners cannot read ~/.gitconfig, so every git call here fails there
# (found in practice). Inherited by the test's git calls and by audit.git().
os.environ["GIT_CONFIG_GLOBAL"] = "/dev/null"
spec = importlib.util.spec_from_file_location("audit", Path(__file__).with_name("audit.py"))
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)

# cross-family pick (installed = any existing binary)
os.environ.pop("AODD_AUDITOR_PICK", None)
a.CODEX = sys.executable                                                   # codex installed but never auto-picked
a.AGY = sys.executable
assert a.pick_auditor("claude-opus") == "agy" and a.pick_auditor("claude-fable") == "agy"
assert a.pick_auditor("codex") == "claude-opus"
assert a.pick_auditor("claude-sonnet") == "claude-opus" and a.pick_auditor("claude-haiku") == "claude-opus"
a.AGY = "definitely-not-installed-agy"                                     # agy missing -> same-family Opus, even with codex present
assert a.pick_auditor("claude-opus") == "claude-opus" and a.pick_auditor("claude-fable") == "claude-opus"
for choice in ("agy", "codex", "claude-opus"):                            # explicit selector wins over detection
    os.environ["AODD_AUDITOR_PICK"] = choice
    assert a.pick_auditor("claude-opus") == choice and a.pick_auditor("claude-sonnet") == choice
os.environ["AODD_AUDITOR_PICK"] = "bogus"                                 # invalid value is ignored
assert a.pick_auditor("claude-opus") == "claude-opus"
os.environ.pop("AODD_AUDITOR_PICK")

d = Path(tempfile.mkdtemp())
tr = d / "s.jsonl"
rows = [{"type": "user", "timestamp": "2000-01-01T08:00:00Z", "message": {"role": "user", "content": "แก้ทุกข้อ"}},
        {"type": "assistant", "message": {"model": "claude-sonnet-5-5", "content": [{"type": "text", "text": "ok"}]}},
        {"type": "user", "message": {"content": [{"type": "tool_result", "content": "x"}]}},          # not a user ask
        {"type": "user", "message": {"content": "<command-name>/x</command-name>"}},                    # harness noise
        {"type": "user", "isSidechain": True, "message": {"content": "subagent prompt"}}]               # not the CEO
tr.write_text("\n".join(map(json.dumps, rows)))
users, worker, ts = a.read_transcript(tr)
assert users == ["แก้ทุกข้อ"], users
assert worker == "claude-sonnet" and ts == "2000-01-01T08:00:00Z"
crows = [{"timestamp": "t0", "type": "session_meta", "payload": {"id": "x"}},
         {"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "# AGENTS.md instructions"}]}},
         {"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "<environment_context>"}]}},
         {"type": "turn_context", "payload": {"model": "gpt-x"}},
         {"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "ตรวจให้หน่อย"}]}},
         {"type": "response_item", "payload": {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "ok"}]}}]
tr.write_text("\n".join(map(json.dumps, crows)))
assert a.read_transcript(tr) == (["ตรวจให้หน่อย"], "codex", "t0")

assert a.verdict("OVERALL: PASS\n|...") == "PASS"
assert a.verdict("**OVERALL: fail**") == "FAIL"
assert a.verdict("looks good to me") == "UNVERIFIABLE"            # no verdict line -> not a pass
assert a.verdict("OVERALL: PASS|FAIL|UNVERIFIABLE\n") == "UNVERIFIABLE"  # echoed template is not a verdict
assert a.verdict("| x |\nOVERALL: PASS\n") == "PASS"
a.CLAUDE = a.CODEX = a.AGY = "/bin/false"
assert a.run_model("claude-opus", "---\nname: x", Path(".")).startswith("OVERALL: UNVERIFIABLE")  # failed run
assert a.run_model("codex", "---\nname: x", Path(".")).startswith("OVERALL: UNVERIFIABLE")
r = a.run_model("agy", "---\nname: x", Path("."))
assert r.startswith("OVERALL: UNVERIFIABLE\nagy run failed")
assert a.combine("PASS", "PASS") == "PASS" and a.combine("FAIL", "FAIL") == "FAIL"
assert a.combine("PASS", "FAIL") == "FAIL"                          # verifier found more
assert a.combine("FAIL", "PASS") == "DISPUTED"                      # Claude may not clear codex's FAIL alone
assert a.combine("UNVERIFIABLE", "PASS") == "UNVERIFIABLE"

# [TS-0104] [BE-UT] Codex may write test outputs only in an isolated scratch root.
from unittest.mock import patch
seen = {}
def fake_run(cmd, **kwargs):
    seen.update(cmd=cmd, env=kwargs["env"], prompt=kwargs["input"])
    scratch = Path(cmd[cmd.index("-C") + 1])
    assert scratch.is_dir() and scratch != Path(".").resolve()
    assert kwargs["env"]["TMPDIR"] == str(scratch)
    return subprocess.CompletedProcess(cmd, 0, stdout="OVERALL: PASS", stderr="")
with patch.object(a.subprocess, "run", fake_run):
    assert a.run_model("codex", "check", Path(".")) == "OVERALL: PASS"
assert seen["cmd"][seen["cmd"].index("-s") + 1] == "workspace-write"
assert not Path(seen["env"]["TMPDIR"]).exists()
assert str(Path(".").resolve()) in seen["prompt"]

# agy argv: prompt is the VALUE of -p, read-only --sandbox, no stdin, no --effort (rejected with an effort-suffixed model id)
seen = {}
def fake_agy(cmd, **kwargs):
    seen.update(cmd=cmd, input=kwargs.get("input"), stdin=kwargs.get("stdin"))
    return subprocess.CompletedProcess(cmd, 0, stdout="OVERALL: PASS", stderr="")
a.AGY = "agy-bin"
with patch.object(a.subprocess, "run", fake_agy):
    assert a.run_model("agy", "---\nthe prompt", Path(".")) == "OVERALL: PASS"
c = seen["cmd"]
assert c[0] == "agy-bin" and c[c.index("-p") + 1] == "---\nthe prompt" and c[-2:] == ["-p", "---\nthe prompt"]
assert "--sandbox" in c and "--effort" not in c and c[c.index("--model") + 1] == "gemini-4-neon-medium"
assert seen["input"] is None and seen["stdin"] == subprocess.DEVNULL
os.environ["AODD_AUDITOR_MODEL"] = "m"                                    # env override read at import time
spec2 = importlib.util.spec_from_file_location("audit2", Path(__file__).with_name("audit.py"))
a2 = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(a2)
assert a2.AGY_MODEL == "m"
os.environ.pop("AODD_AUDITOR_MODEL")

# [TS-0101] [BE-UT] infrastructure failure can fall back without clearing a real failed audit.
assert a.combine("UNVERIFIABLE", "PASS", infra_failure=True) == "PASS"
assert a.combine("UNVERIFIABLE", "FAIL", infra_failure=True) == "FAIL"
assert a.combine("FAIL", "PASS", infra_failure=True) == "DISPUTED"

# end to end with stub models: codex audits, opus verifies and overturns; repo change voids the audit
repo = d / "r"; repo.mkdir()
g = lambda *c: subprocess.run(["git", "-C", str(repo), *c], capture_output=True)
g("init", "-q", "-b", "main"); (repo / "f").write_text("1"); g("add", ".")
g("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "-c", "core.hooksPath=/dev/null", "commit", "-qm", "x").check_returncode()
tr.write_text(json.dumps(rows[0]) + "\n" + json.dumps({"message": {"model": "claude-opus-5-5"}}))
(repo / "new.py").write_text("print('new')\n")
(repo / "f").write_text("x" * (a.MAX_DIFF + 5000))
sc = a.scope(repo, "HEAD", None)[1]
assert "print('new')" in sc and "new.py (untracked)" in sc and "1 file changed" in sc  # stat & untracked survive >MAX_DIFF patch
(repo / "f").write_text("edited-line\n")                            # the reverse: a big new file must not hide the edit
(repo / "new.py").write_text("y" * (a.MAX_DIFF + 5000))
sc = a.scope(repo, "HEAD", None)[1]
assert "+edited-line" in sc and len(sc) < a.MAX_DIFF + 2000, len(sc)
(repo / "f").write_text("1")
(repo / "new.py").unlink()
calls = []
a.REPORTS = d / "reports"
a.CODEX = a.AGY = sys.executable  # existing binaries, so the cross-family path is taken
a.run_model = lambda who, prompt, r: (calls.append((who, prompt)) or
                                      ("OVERALL: PASS" if who == "agy" else "OVERALL: FAIL\nOverturned codex rows: 1"))
n = len(calls)
assert a.main(["--transcript", str(tr), "--repo", str(repo)]) == 2 and len(calls) == n  # no user yes -> no model runs
assert a.main(["--transcript", str(tr), "--repo", str(repo), "--confirmed"]) == 1
assert "verdict: FAIL" in next((d / "reports").glob("audit-*-s.md")).read_text()
calls.clear()
a.run_model = lambda who, prompt, r: (calls.append((who, prompt)) or
                                      ("OVERALL: FAIL" if who == "agy" else "OVERALL: PASS\nOverturned codex rows: 1"))
assert a.main(["--transcript", str(tr), "--repo", str(repo), "--confirmed"]) == 1
assert [c[0] for c in calls] == ["agy", "claude-opus"] and "แก้ทุกข้อ" in calls[0][1]
assert "OVERALL: FAIL" in calls[1][1]                               # verifier sees codex's audit
rep = next(a.REPORTS.glob("audit-*-s.md")).read_text()
assert "verdict: DISPUTED" in rep and "auditor: agy" in rep and "agy's original audit" in rep
assert any("verdict: FAIL" in f.read_text() for f in (a.REPORTS / "done").glob("audit-*-*-s.md"))  # same-day re-audit kept the FAIL

calls.clear()
a.run_model = lambda who, prompt, r: ((repo / "f").write_text("tampered") and "OVERALL: PASS")
assert a.main(["--transcript", str(tr), "--repo", str(repo), "--confirmed", "--auditor", "claude-opus"]) == 1
assert "Audit void" in next(a.REPORTS.glob("audit-*-s.md")).read_text()
a.run_model = lambda who, prompt, r: ((a.REPORTS / "stray-x.md").write_text("x") and "OVERALL: PASS")
assert a.main(["--transcript", str(tr), "--repo", str(repo), "--confirmed", "--auditor", "claude-opus"]) == 1
assert "stray-x.md" in next(a.REPORTS.glob("audit-*-s.md")).read_text()   # wrote outside the repo
# agy not installed -> same-family Opus audits and the report says so
for f in a.REPORTS.glob("audit-*"):
    f.unlink()
a.AGY = "definitely-not-installed-agy"
calls.clear()
a.run_model = lambda who, prompt, r: (calls.append(who) or "OVERALL: PASS")
assert a.main(["--transcript", str(tr), "--repo", str(repo), "--confirmed"]) == 0
assert calls == ["claude-opus"]
assert "auditor: claude-opus (agy not installed, same-family)" in next(a.REPORTS.glob("audit-*-s.md")).read_text()

# AODD_AUDITOR_PICK=codex: codex audits a Claude Opus worker, then a cold Opus verifies; codex FAIL + opus PASS = DISPUTED
for f in a.REPORTS.glob("audit-*"):
    f.unlink()
a.CODEX = sys.executable
os.environ["AODD_AUDITOR_PICK"] = "codex"
calls.clear()
a.run_model = lambda who, prompt, r: (calls.append(who) or ("OVERALL: FAIL" if who == "codex" else "OVERALL: PASS"))
assert a.main(["--transcript", str(tr), "--repo", str(repo), "--confirmed"]) == 1
assert calls == ["codex", "claude-opus"]
rep = next(a.REPORTS.glob("audit-*-s.md")).read_text()
assert "verdict: DISPUTED" in rep and "auditor: codex" in rep and "verifier: claude-opus" in rep and "codex's original audit" in rep
# [TS-0103] [BE-IT] infrastructure fallback is labelled and preserves the original error.
a.run_model = lambda who, prompt, r: ("OVERALL: UNVERIFIABLE\ncodex run failed (exit 1): EPERM" if who == "codex" else "OVERALL: PASS")
assert a.main(["--transcript", str(tr), "--repo", str(repo), "--confirmed"]) == 0
rep = next(a.REPORTS.glob("audit-*-s.md")).read_text()
assert "verdict: PASS" in rep and "same-family" in rep and "EPERM" in rep

os.environ.pop("AODD_AUDITOR_PICK")
# agy infrastructure failure (e.g. usage limit) keeps its error and falls back to the verifier, labelled same-family
a.AGY = sys.executable
a.run_model = lambda who, prompt, r: ("OVERALL: UNVERIFIABLE\nagy run failed (exit 1): QUOTA" if who == "agy" else "OVERALL: PASS")
assert a.main(["--transcript", str(tr), "--repo", str(repo), "--confirmed"]) == 0
rep = next(a.REPORTS.glob("audit-*-s.md")).read_text()
assert "same-family" in rep and "QUOTA" in rep

# a codex worker is audited by Opus alone (no verifier step)
tr.write_text("\n".join(map(json.dumps, crows)))
calls.clear()
a.run_model = lambda who, prompt, r: (calls.append(who) or "OVERALL: PASS")
assert a.main(["--transcript", str(tr), "--repo", str(repo), "--confirmed"]) == 0 and calls == ["claude-opus"]
assert "worker: codex" in next(a.REPORTS.glob("audit-*-s.md")).read_text()
print("ok")
