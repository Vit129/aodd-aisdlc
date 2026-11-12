#!/usr/bin/env python3
"""skill_trigger_eval: counts how often a fresh session opens the expected skill, using a stub CLI."""
import importlib.util, json, os, pathlib, sys, tempfile

here = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ste", here / "skill_trigger_eval.py")
ste = importlib.util.module_from_spec(spec); spec.loader.exec_module(ste)

with tempfile.TemporaryDirectory() as d:
    d = pathlib.Path(d)
    # Stub CLI: opens git-safety only when the prompt says "branch".
    stub = d / "stub.py"
    stub.write_text(
        "import json,sys\np=sys.argv[-1]\n"
        "if 'branch' in p:\n"
        "  print(json.dumps({'type':'assistant','message':{'content':[{'type':'tool_use','name':'Skill','input':{'skill':'git-safety'}}]}}))\n"
        "print(json.dumps({'type':'result','result':'done'}))\n")
    os.environ["AODD_TRIGGER_CMD"] = f"{sys.executable} {stub}"

    assert ste.skills_opened('{"type":"system","message":"plain string"}\n') == set()
    assert ste.skills_opened('{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Skill","input":{"skill":"a:b"}}]}}\nnot json\n') == {"a:b"}

    cases = d / "cases.json"
    cases.write_text(json.dumps({"git-safety": ["delete the old branch", "is this merged yet", "clean up feature work", "remove branch x"]}))
    res = ste.run(json.loads(cases.read_text()), rounds=1)
    assert res["git-safety"]["hits"] == 2 and res["git-safety"]["runs"] == 4, res
    out = ste.report(res)
    assert "git-safety" in out and "2/4" in out and "make it user-invoked" not in out, out

    res2 = ste.run({"git-safety": ["is this merged yet", "clean up feature work", "x"]}, rounds=2)
    assert res2["git-safety"]["hits"] == 0 and res2["git-safety"]["runs"] == 6
    assert "make it user-invoked" in ste.report(res2)

    # A case that contains the skill's own name is a leaked exam question.
    assert ste.leaks("git-safety", "use git-safety here") and not ste.leaks("git-safety", "is it merged")
print("ok - skill_trigger_eval")
