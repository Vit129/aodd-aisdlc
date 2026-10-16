import os as _o, tempfile as _t
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
assert r and "skill-learning.md" in r and "skill-capture: nothing" in r and "fine answer" in r
assert run("b",reads(24)+[sig]+reads(1)) is None                                 # not again until INTERVAL more calls
assert run("b",reads(24)+[sig]+reads(1)+reads(45)) is None                       # interval passed but no NEW signal
assert run("b",reads(24)+[sig]+reads(1)+reads(45)+[sig])                     # interval passed + new signal -> again
assert run("c",reads(25)+[sig],stop_hook_active=True) is None
assert run("d",reads(25)+[sig]+[use("Edit",{"file_path":"/u/.claude/skills/x/SKILL.md"})]) is None              # skill already patched
assert run("d2",reads(25)+[sig]+[use("Write",{"file_path":"/p/.claude/skills/x/references/t.md"})]) is None     # references count too
assert run("d3",reads(25)+[sig]+[use("Edit",{"file_path":"/w/notes/lessons.md"})])                      # a loose notes file does not count
(h.STATE_DIR/"legacy").write_text("")                                       # old empty marker = already nudged
assert run("legacy",reads(80)+[sig]) is None

# loaded skills are named as first patch targets, with a path
(d/".claude/skills/proj").mkdir(parents=True); (d/".claude/skills/proj/SKILL.md").write_text("x")
r=run("e",reads(25)+[sig,use("Skill",{"skill":"proj"}),use("Read",{"file_path":"/u/.claude/skills/glob/SKILL.md"}),use("Skill",{"skill":"pl:other"})])
assert "proj: "+str(d/".claude/skills/proj/SKILL.md") in r and "glob: /u/.claude/skills/glob/SKILL.md" in r and "other: (plugin" in r
r=run("f",reads(25)+[use("Bash",{"command":'git commit -m "fix(x): y"'})])  # fix commit alone fires, with the fix note
assert h.FIX_NOTE in r
r=run("g",reads(25)+[{"type":"user","message":{"content":"ยาวไป เอาสั้นๆ"}}])   # style correction is a signal
assert "user correction" in r
assert h.post_tool({"tool_input":{"command":'git commit -m "fix: z"'}})==h.MID_FLIGHT
assert h.post_tool({"tool_input":{"command":'git commit -m "feat: z"'}}) is None
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
assert "1 user correction" in run("i",recs)
assert not h.CORRECTION.search("อย่าลืมรัน test นะ ไม่ต้องรีบ")              # everyday Thai is not a correction
print("ok")
