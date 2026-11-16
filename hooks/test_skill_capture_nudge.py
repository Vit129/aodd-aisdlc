import os as _o, tempfile as _t
[_o.environ.pop(k, None) for k in ("AODD_REPORTS", "AODD_STATE", "AODD_PLANS")]
_o.environ["AODD_HOME"] = _t.mkdtemp()  # tests never touch the real AODD_HOME
import os as _os
_os.environ.pop("CLAUDE_SKILL_CAPTURE", None)  # audit.py sets it to 0 for auditors; this test needs the nudge on
import json,importlib.util,tempfile,pathlib,os
spec=importlib.util.spec_from_file_location("h",os.path.join(os.path.dirname(os.path.abspath(__file__)),"skill-capture-nudge.py"));h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
d=pathlib.Path(tempfile.mkdtemp());h.STATE_DIR=d/"state"
use=lambda name,inp: {"message":{"content":[{"type":"tool_use","name":name,"input":inp}]}}
err={"message":{"content":[{"type":"tool_result","is_error":True}]}}
sig={"type":"user","message":{"content":"ไม่ใช่ ทำผิดแล้ว"}}   # a user correction: the signal
def tr(recs,tag):
    p=d/f"{tag}.jsonl"; p.write_text("\n".join(json.dumps(r) for r in recs)); return str(p)
reads=lambda n: [use("Read",{"file_path":"/x/a.py"})]*n
run=lambda sid,recs,**kw: h.decide({"session_id":sid,"transcript_path":tr(recs,sid),"cwd":str(d),**kw})

assert run("a",reads(5)+[sig]) is None                                  # too small
assert run("a0",reads(25)) is None                                          # no learning signal
assert run("a1",reads(25)+[err,err,err]) is None                           # tool errors alone are not a lesson
r=run("b",reads(24)+[sig]+reads(1))                                              # one signal is enough now
assert r and "skill-learning.md" in r and "user correction" in r and "\n" not in r   # a one-line note
assert run("b",reads(24)+[sig]+reads(1)) is None                                 # said once
assert run("b",reads(24)+[sig]+reads(1)+reads(45)) is None                       # nothing refires ...
assert run("b",reads(24)+[sig]+reads(1)+reads(45)+[sig]) is None                 # ... not even on a new signal after INTERVAL
assert run("c",reads(25)+[sig],stop_hook_active=True) is None
assert run("d",reads(25)+[sig]+[use("Edit",{"file_path":"/u/.claude/skills/x/SKILL.md"})]) is None              # skill already patched
assert run("d2",reads(25)+[sig]+[use("Write",{"file_path":"/p/.claude/skills/x/references/t.md"})]) is None     # references count too
assert run("d3",reads(25)+[sig]+[use("Edit",{"file_path":"/w/notes/lessons.md"})])                      # a loose notes file does not count
(h.STATE_DIR/"legacy").write_text("")                                       # old empty marker = already nudged
assert run("legacy",reads(80)+[sig]) is None

# loaded skills are named in the note
r=run("e",reads(25)+[sig,use("Skill",{"skill":"proj"}),use("Read",{"file_path":"/u/.claude/skills/glob/SKILL.md"}),use("Skill",{"skill":"pl:other"})])
assert "proj" in r and "glob" in r and "other" in r
r=run("f",reads(25)+[use("Bash",{"command":'git commit -m "fix(x): y"'})])  # fix commit alone fires
assert "fix commit" in r
r=run("g",reads(25)+[{"type":"user","message":{"content":"ยาวไป เอาสั้นๆ"}}])   # style correction is a signal
assert "user correction" in r
pt=lambda sid,c: h.post_tool({"session_id":sid,"tool_input":{"command":c}})
assert pt("p1",'git commit -m "fix: z"')==h.MID_FLIGHT
assert pt("p1",'git commit -m "fix: z"') is None                            # once per session
assert pt("p2",'git commit -m "feat: z"') is None
assert pt("","git commit -m \"fix: z\"") is None                           # no session id -> silent
# Bash: reads/stderr redirects are not skill writes; real writes (relative path, cp, open w) are
assert not h.SKILL_BASH_WRITE.search("grep x ~/.claude/skills/a/SKILL.md 2>/dev/null")
assert not h.SKILL_BASH_WRITE.search("cat skills/a/SKILL.md > /tmp/x")
for c in ("sed -i '' s/a/b/ skills/a/SKILL.md", "cp /tmp/x skills/a/references/t.md", "echo x >> ~/.claude/skills/a/SKILL.md",
          "python3 -c \"open('skills/a/SKILL.md','w')\""):
    assert h.SKILL_BASH_WRITE.search(c), c
assert run("h",reads(25)+[sig,use("Bash",{"command":"cat ~/.claude/skills/a/SKILL.md 2>/dev/null"})])   # a read does not silence the nudge
# a correction typed right after a nudge counts toward the next one; the nudge text itself does not
recs=reads(24)+[sig]+reads(1); assert run("i",recs)
recs+= [{"type":"user","message":{"content":"Stop hook feedback: [skill-capture] ... wrong rules"}},{"type":"user","message":{"content":"ไม่ใช่ ทำแบบนี้"}}]+reads(45)
assert run("i",recs) is None                                                # said once: no refire on a new correction
assert not h.CORRECTION.search("อย่าลืมรัน test นะ ไม่ต้องรีบ")              # everyday Thai is not a correction
# Codex rollout records
def cxcall(cmd): return {"type":"response_item","payload":{"type":"function_call","name":"exec_command","arguments":json.dumps({"cmd":cmd}),"call_id":"c"}}
cxuser=lambda t: {"type":"response_item","payload":{"type":"message","role":"user","content":[{"type":"input_text","text":t}]}}
cxreads=lambda n: [cxcall("ls")]*n
inj=cxuser("<environment_context>wrong</environment_context>")
assert run("x1",cxreads(25)+[inj]) is None                                  # injected context is not a correction
assert "user correction" in run("x2",cxreads(24)+[cxuser("ไม่ใช่ ทำผิดแล้ว")]+cxreads(1))
assert "fix commit" in run("x3",cxreads(25)+[cxcall('git commit -m "fix(x): y"')])
assert run("x4",cxreads(25)+[cxuser("wrong"),{"type":"response_item","payload":{"type":"custom_tool_call","name":"apply_patch",
    "input":"*** Begin Patch\n*** Update File: /u/skills/x/SKILL.md\n@@\n-a\n+b\n*** End Patch"}}]) is None   # skill patched via apply_patch
print("ok")
# a shell loop variable or glob is not a loaded skill name
_r=run("var",reads(25)+[sig]+[use("Bash",{"command":"for s in a b; do diff x ~/.claude/skills/$s/SKILL.md; cat /h/.claude/skills/*/SKILL.md; done; cat /h/.claude/skills/ai-sdlc/SKILL.md"})])
assert _r and "$s" not in _r and "*" not in _r and "ai-sdlc" in _r, _r
print("ok - shell variable is not a skill name")
# CLI: the Stop note is a systemMessage, never a block
import subprocess, sys
env={**os.environ,"AODD_STATE":str(d/"clistate"),"AODD_HOME":str(d/"clihome")}; env.pop("CLAUDE_SKILL_CAPTURE",None)
hook=os.path.join(os.path.dirname(os.path.abspath(__file__)),"skill-capture-nudge.py")
payload=json.dumps({"session_id":"cli1","transcript_path":tr(reads(25)+[sig],"cli1"),"cwd":str(d)})
r1=subprocess.run([sys.executable,hook],input=payload,capture_output=True,text=True,env=env); o=json.loads(r1.stdout)
assert r1.returncode==0 and "systemMessage" in o and "decision" not in o, r1.stdout
assert subprocess.run([sys.executable,hook],input=payload,capture_output=True,text=True,env=env).stdout==""   # once
for junk in ("garbage","{}",""):
    r=subprocess.run([sys.executable,hook],input=junk,capture_output=True,text=True,env=env); assert r.returncode==0 and r.stdout=="",junk
print("ok - CLI systemMessage")
