#!/usr/bin/env python3
"""Run: python3 optional/agent-memory/hooks/test_memory_recall.py  (asserts, no framework)"""
import importlib.util, json, os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp()
os.environ.update(AODD_HOME=TMP + "/aodd", CLAUDE_HOME=TMP + "/claude")
os.environ.pop("AODD_MEMORY", None)
os.makedirs(TMP + "/aodd/memory/knowledge")
open(TMP + "/aodd/memory/knowledge/hooks.md", "w").write(
    "# Hooks\n\n## Missing hook file\n\nA hook registered as python3 whose file is missing blocks every tool call.\n"
    "**How to apply:** register hooks with a fail-open command.\n")
spec = importlib.util.spec_from_file_location("mr", os.path.join(HERE, "memory-recall.py"))
mr = importlib.util.module_from_spec(spec); spec.loader.exec_module(mr)

assert mr.keywords("Fix the something today in settings.json") == ["settings.json"]    # stopwords/short tokens dropped
assert mr.keywords("สวัสดี ช่วยหน่อย") == []                                            # Thai greeting/filler: nothing usable
assert "พอร์ตการลงทุน" in mr.keywords("วิเคราะห์พอร์ตการลงทุน")                           # Thai compound term
assert mr.keywords("ช่วยดูเรื่อง กำไร ขาดทุน หน่อย") == ["กำไร", "ขาดทุน"]               # Thai domain keywords extracted
assert mr.recall("สวัสดี", TMP) == []
hits = mr.recall("hook registered as python3 but the file is missing blocks every tool call", TMP)
assert any("hooks" in str(p) for _, p, _, _ in hits), hits                              # finds knowledge/hooks.md
import tempfile; LOG = os.path.join(tempfile.mkdtemp(), "hits.jsonl")
run = lambda payload, env=None: subprocess.run([sys.executable, os.path.join(HERE, "memory-recall.py")], input=json.dumps(payload),
                                               text=True, capture_output=True, env={**os.environ, "MEMORY_RECALL_LOG": LOG, **(env or {})})
out = run({"prompt": "hook registered as python3 but the file is missing blocks every tool call", "cwd": str(TMP)})
ctx = json.loads(out.stdout)["hookSpecificOutput"]["additionalContext"]
assert out.returncode == 0 and "knowledge/hooks.md" in ctx and len(ctx) < 2600           # small: pointers + one gist line each
assert json.loads(open(LOG).readline())["files"]                                       # surfaced files are logged
assert run({"prompt": "run the tests again", "cwd": str(TMP)}).stdout == ""            # no match -> silent
assert run({"prompt": "hook file missing", "cwd": str(TMP)}, {"MEMORY_RECALL": "0"}).stdout == ""
assert run("not json").returncode == 0                                                    # fails open
# machine text / pasted walls of text must not trigger recall, even when they contain matching terms
body = "hook registered as python3 but the file is missing blocks every tool call"
for tag in ("<system-reminder>", "<task-notification>", "  <system-reminder>"):
    assert run({"prompt": f"{tag}\n{body}", "cwd": str(TMP)}).stdout == "", tag
long_prompt = body + " " + " ".join(f"extraterm{i}" for i in range(16))          # >15 distinct keywords
assert mr.is_machine_or_pasted(long_prompt) and not mr.is_machine_or_pasted(body)
assert run({"prompt": long_prompt, "cwd": str(TMP)}).stdout == ""
assert run({"prompt": body, "cwd": str(TMP)}).stdout != ""                    # a normal question still recalls
note = "---\nname: x\ndescription: d\n---\n\nSome fact.\n\n**Why:** because.\n**How to apply:** do the thing.\n"
assert mr.gist(mr.Path("n.md"), note, "d") == "do the thing."                          # gist prefers How to apply
assert mr.gist(mr.Path("n.md"), "---\ndescription: d\n---\nOnly a fact.\n", "d") == "Only a fact."
assert "gist:" in ctx
print("memory-recall OK")
