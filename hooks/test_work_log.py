import json,importlib.util,tempfile,pathlib,os
spec=importlib.util.spec_from_file_location("w",os.path.join(os.path.dirname(os.path.abspath(__file__)),"work-log.py"));w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
d=pathlib.Path(tempfile.mkdtemp());w.LOG_DIR=d
t=d/"t.jsonl"
t.write_text("\n".join([
    json.dumps({"type":"assistant","message":{"usage":{"input_tokens":100,"output_tokens":50},"content":[{"type":"tool_use","name":"Bash","input":{}}]}}),
    json.dumps({"type":"user","message":{"content":"ไม่ใช่ ทำใหม่"}}),
]))
e=w.entry({"session_id":"s1","transcript_path":str(t),"cwd":"/x/proj"})
assert e["tokens"]==150 and e["tool_calls"]==1 and e["owner"]=="proj" and e["signals"],e
assert w.entry({"session_id":"","transcript_path":str(t)}) is None
(d/"2026-10.jsonl").write_text(json.dumps({**e,"tokens":10})+"\n"+json.dumps(e)+"\n")
r=w.report("2026-10"); assert "| proj | 1 | 150 | 1 |" in r,r   # last line per session wins
print("ok")

# AODD_WORKLOG_SKIP globs (empty by default) keep matching sessions out of the log
import os as _os
home = _os.path.expanduser("~")
assert w.project_of(home + "/work/private/x") == "x"
_os.environ["AODD_WORKLOG_SKIP"] = _os.pathsep.join([home + "/work/private/*", home + "/.scratch*"])
assert w.project_of(home + "/work/private/x") is None and w.project_of(home + "/.scratch/y") is None
assert w.project_of(home + "/work/public/x") == "x"

# unreachable $AODD_WORKLOG parent -> entry goes to $AODD_STATE/work-log with a note; default dir is untouched
w.FALLBACK_DIR = d / "state/work-log"; w.LOG_DIR = d / "missing/central/work-log"
e2 = {"ts": "2026-10-02T00:00:00", "session": "s2"}
assert w.log_dir(e2) == w.LOG_DIR and "note" not in e2         # env unset: default behaviour
_os.environ["AODD_WORKLOG"] = str(w.LOG_DIR)
assert w.log_dir(e2) == w.FALLBACK_DIR and "missing" in e2["note"]
w.LOG_DIR = d / "wl2"; assert w.log_dir({}) == w.LOG_DIR     # parent exists: no fallback
_os.environ.pop("AODD_WORKLOG")
