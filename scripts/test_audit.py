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

# Sandboxed runners (agy --sandbox) cannot read ~/.gitconfig, so every git call here fails there
# (found in practice). Inherited by the test's git calls and by audit.git().
os.environ["GIT_CONFIG_GLOBAL"] = "/dev/null"
spec = importlib.util.spec_from_file_location("audit", Path(__file__).with_name("audit.py"))
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)

# cross-family pick (installed = any existing binary)
a.AGY = a.CODEX = sys.executable
assert a.pick_auditor("claude-opus") == "agy" and a.pick_auditor("claude-fable") == "agy"
assert a.pick_auditor("agy") == "claude-opus" and a.pick_auditor("codex") == "claude-opus"
assert a.pick_auditor("claude-sonnet") == "claude-opus" and a.pick_auditor("claude-haiku") == "claude-opus"
a.AGY = "definitely-not-installed-agy"                                     # agy missing, codex present -> codex
assert a.pick_auditor("claude-opus") == "codex" and a.pick_auditor("claude-fable") == "codex"
a.CODEX = "definitely-not-installed-codex"                                 # neither -> same-family Opus
assert a.pick_auditor("claude-opus") == "claude-opus"

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
tr.write_text(json.dumps({"type": "USER_INPUT", "content": "fix it"}))
assert a.read_transcript(tr)[:2] == (["fix it"], "agy")
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
a.CLAUDE = a.CODEX = "/bin/false"
assert a.run_model("claude-opus", "---\nname: x", Path(".")).startswith("OVERALL: UNVERIFIABLE")  # failed run
assert a.run_model("codex", "---\nname: x", Path(".")).startswith("OVERALL: UNVERIFIABLE")
assert a.combine("PASS", "PASS") == "PASS" and a.combine("FAIL", "FAIL") == "FAIL"
assert a.combine("PASS", "FAIL") == "FAIL"                          # verifier found more
assert a.combine("FAIL", "PASS") == "DISPUTED"                      # Claude may not clear agy's FAIL alone
assert a.combine("UNVERIFIABLE", "PASS") == "UNVERIFIABLE"

# end to end with stub models: agy audits, opus verifies and overturns; repo change voids the audit
repo = d / "r"; repo.mkdir()
g = lambda *c: subprocess.run(["git", "-C", str(repo), *c], capture_output=True)
g("init", "-q", "-b", "main"); (repo / "f").write_text("1"); g("add", "."); g("-c", "core.hooksPath=/dev/null", "commit", "-qm", "x")
tr.write_text(json.dumps(rows[0]) + "\n" + json.dumps({"message": {"model": "claude-opus-5-5"}}))
(repo / "new.py").write_text("print('new')\n")
assert "print('new')" in a.scope(repo, "HEAD", None)[1]              # untracked files are in scope
(repo / "new.py").unlink()
calls = []
a.REPORTS = d / "reports"
a.AGY = sys.executable  # an existing binary, so the agy path is taken
a.run_model = lambda who, prompt, r: (calls.append((who, prompt)) or
                                      ("OVERALL: PASS" if who == "agy" else "OVERALL: FAIL\nOverturned agy rows: 1"))
assert a.main(["--transcript", str(tr), "--repo", str(repo)]) == 1
assert "verdict: FAIL" in next((d / "reports").glob("audit-*-s.md")).read_text()
calls.clear()
a.run_model = lambda who, prompt, r: (calls.append((who, prompt)) or
                                      ("OVERALL: FAIL" if who == "agy" else "OVERALL: PASS\nOverturned agy rows: 1"))
assert a.main(["--transcript", str(tr), "--repo", str(repo)]) == 1
assert [c[0] for c in calls] == ["agy", "claude-opus"] and "แก้ทุกข้อ" in calls[0][1]
assert "OVERALL: FAIL" in calls[1][1]                               # verifier sees agy's audit
rep = next(a.REPORTS.glob("audit-*-s.md")).read_text()
assert "verdict: DISPUTED" in rep and "auditor: agy" in rep and "agy's original audit" in rep

calls.clear()
a.run_model = lambda who, prompt, r: ((repo / "f").write_text("tampered") and "OVERALL: PASS")
assert a.main(["--transcript", str(tr), "--repo", str(repo), "--auditor", "claude-opus"]) == 1
assert "Audit void" in next(a.REPORTS.glob("audit-*-s.md")).read_text()
a.run_model = lambda who, prompt, r: ((a.REPORTS / "agy-proposal-x.md").write_text("x") and "OVERALL: PASS")
assert a.main(["--transcript", str(tr), "--repo", str(repo), "--auditor", "claude-opus"]) == 1
assert "agy-proposal-x.md" in next(a.REPORTS.glob("audit-*-s.md")).read_text()   # wrote outside the repo
# agy not installed -> same-family Opus audits and the report says so
for f in a.REPORTS.glob("audit-*"):
    f.unlink()
a.AGY = "definitely-not-installed-agy"
calls.clear()
a.run_model = lambda who, prompt, r: (calls.append(who) or "OVERALL: PASS")
assert a.main(["--transcript", str(tr), "--repo", str(repo)]) == 0
assert calls == ["claude-opus"]
assert "auditor: claude-opus (agy/codex not installed, same-family)" in next(a.REPORTS.glob("audit-*-s.md")).read_text()

# agy missing, codex installed: codex audits a Claude Opus worker, then a cold Opus verifies; codex FAIL + opus PASS = DISPUTED
for f in a.REPORTS.glob("audit-*"):
    f.unlink()
a.CODEX = sys.executable
calls.clear()
a.run_model = lambda who, prompt, r: (calls.append(who) or ("OVERALL: FAIL" if who == "codex" else "OVERALL: PASS"))
assert a.main(["--transcript", str(tr), "--repo", str(repo)]) == 1
assert calls == ["codex", "claude-opus"]
rep = next(a.REPORTS.glob("audit-*-s.md")).read_text()
assert "verdict: DISPUTED" in rep and "auditor: codex" in rep and "verifier: claude-opus" in rep and "codex's original audit" in rep
# a codex worker is audited by Opus alone (no verifier step)
tr.write_text("\n".join(map(json.dumps, crows)))
calls.clear()
a.run_model = lambda who, prompt, r: (calls.append(who) or "OVERALL: PASS")
assert a.main(["--transcript", str(tr), "--repo", str(repo)]) == 0 and calls == ["claude-opus"]
assert "worker: codex" in next(a.REPORTS.glob("audit-*-s.md")).read_text()
print("ok")
