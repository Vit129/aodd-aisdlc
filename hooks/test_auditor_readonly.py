import importlib.util
import os
from pathlib import Path

spec = importlib.util.spec_from_file_location("h", Path(__file__).with_name("auditor-readonly.py"))
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)

bash = lambda c: {"tool_name": "Bash", "tool_input": {"command": c}}
os.environ.pop("AODD_AUDITOR", None)
assert h.decide({"tool_name": "Write"}) is None                    # normal sessions untouched
os.environ["AODD_AUDITOR"] = "1"
assert h.decide({"tool_name": "Write"}) and h.decide({"tool_name": "Edit"})
for c in ["echo x > f", "cat a >> b", "sed -i '' s/a/b/ f", "rm -rf x", "git commit -m x", "git push", "tee out",
          "gh pr merge 1"]:
    assert h.decide(bash(c)), c
for c in ["pytest -q 2>&1 | tail", "git diff HEAD~1", "git log --oneline", "python3 -m py_compile x.py",
          "make test >/dev/null", "grep -n foo f", "git status --porcelain", "bash -n s.sh"]:
    assert h.decide(bash(c)) is None, c
# Codex, as dumped from a live PreToolUse: edits are apply_patch {command: <patch>}, shell is Bash {command}
assert h.decide({"tool_name": "apply_patch", "tool_input": {"command": "*** Begin Patch\n*** Add File: a\n+x\n*** End Patch"}})
assert h.decide(bash("echo hi > hello.txt")) and h.decide(bash("ls")) is None
assert h.decide({"tool_name": "Read"}) is None
print("ok")
