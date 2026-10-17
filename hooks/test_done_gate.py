import os as _o, tempfile as _t
[_o.environ.pop(k, None) for k in ("AODD_REPORTS", "AODD_STATE", "AODD_PLANS")]
_o.environ["AODD_HOME"] = _t.mkdtemp()  # tests never touch the real AODD_HOME
import json, importlib.util, tempfile, pathlib, os
spec = importlib.util.spec_from_file_location("h", os.path.join(os.path.dirname(os.path.abspath(__file__)), "done-gate.py"))
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
d = pathlib.Path(tempfile.mkdtemp())
rep = d / "reports"; rep.mkdir()
decide = lambda **kw: h.decide({"transcript_path": str(tr), **kw}, reports=rep)
prog = d / "ai-sdlc-task-progress.md"
tr = d / "abcdef12-session.jsonl"
audit = lambda v: (rep / "audit-2000-01-01-abcdef12.md").write_text(f"---\nverdict: {v}\n---\n")
unaudit = lambda: [p.unlink() for p in rep.glob("*") if p.is_file()]
tr.write_text(json.dumps({"message": {"content": [{"type": "tool_use", "name": "Edit", "input": {"file_path": str(prog)}}]}}))
prog.write_text("- [x] a\n- [ ] b\n")
assert "- [ ] b" in decide()                                       # open item -> block
assert decide(stop_hook_active=True) is None
prog.write_text("- [x] a\n- [x] b\n")
assert "audit.py" in decide()                                      # all done, not audited -> block
sub = {"message": {"content": [{"type": "tool_use", "name": "Agent", "input": {"subagent_type": "auditor"}}]}}
tr.write_text(tr.read_text() + "\n" + json.dumps(sub))
assert "audit.py" in decide()                                      # a worker-briefed subagent no longer counts
audit("PASS"); assert decide() is None                             # independent PASS -> allow
(rep / "done").mkdir(); (rep / "audit-2000-01-01-abcdef12.md").rename(rep / "done/audit-2000-01-01-abcdef12.md")
assert decide() is None                                            # PASS filed to done/ still counts (resumed session)
(rep / "done/audit-2000-01-01-abcdef12.md").unlink()
audit("FAIL"); assert "FAIL" in decide()                           # FAIL -> must not claim Done
audit("DISPUTED"); assert "CEO decides" in decide()
audit("UNVERIFIABLE"); assert "UNVERIFIABLE" in decide()
unaudit()
tr.write_text("{}")
assert decide() is None                                            # untouched -> allow
# medium: 5+ files edited without a tracked plan -> audit required
ed = lambda f: json.dumps({"message": {"content": [{"type": "tool_use", "name": "Edit", "input": {"file_path": f}}]}})
tr.write_text(ed("/x/a.py"))
assert decide() is None                                            # one file -> small
tr.write_text("\n".join(ed(f"/x/{i}.py") for i in range(4)))
assert decide() is None                                            # 4 files -> self-check is enough
audit("FAIL"); assert decide() is None; unaudit()                  # small work: a FAIL report does not gate
tr.write_text("\n".join(ed(f"/x/{i}.py") for i in range(5)))
assert "audit.py" in decide()                                      # 5 files -> medium, not audited
audit("PASS"); assert decide() is None; unaudit()                  # audited -> allow
tr.write_text(ed("/h/notes/agent-memory/x/lessons.md") + "\n" + ed("/h/.claude/projects/p/memory/n.md"))
assert decide() is None                                            # notes only -> not medium
# Codex rollout: apply_patch custom_tool_call, files from patch headers
cx = lambda *fs: json.dumps({"timestamp": "t", "type": "response_item", "payload": {"type": "custom_tool_call", "name": "apply_patch",
    "input": "*** Begin Patch\n" + "".join(f"*** Update File: {f}\n@@\n-a\n+b\n" for f in fs) + "*** End Patch"}})
tr.write_text("\n".join(cx(f"/x/{i}.py") for i in range(4)))
assert decide() is None                                            # 4 patched files -> small
tr.write_text(cx(*[f"/x/{i}.py" for i in range(5)]))
assert "audit.py" in decide()                                      # 5 patched files (one patch) -> medium
tr.write_text(cx(str(prog)) ); prog.write_text("- [ ] z\n")
assert "- [ ] z" in decide()                                       # Codex-touched progress file with open box -> block
# the audit date in the file name wins over mtime: annotating an older FAIL report later must not override a newer PASS
import time
(rep / "done").mkdir(exist_ok=True)
(rep / "audit-2000-01-02-abcdef12.md").write_text("---\nverdict: PASS\n---\n")
old = rep / "done/audit-2000-01-01-abcdef12.md"; time.sleep(0.05); old.write_text("---\nverdict: FAIL\n---\nsuperseded\n")
tr.write_text("\n".join(ed(f"/x/{i}.py") for i in range(5)))
assert decide() is None, decide()                                  # newer-dated PASS counts
old.unlink(); (rep / "audit-2000-01-02-abcdef12.md").unlink()
print("ok")
