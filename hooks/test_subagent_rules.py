import importlib.util, os, pathlib, tempfile

spec = importlib.util.spec_from_file_location("s", os.path.join(os.path.dirname(os.path.abspath(__file__)), "subagent-rules.py"))
s = importlib.util.module_from_spec(spec); spec.loader.exec_module(s)
CH = pathlib.Path(tempfile.mkdtemp()); os.environ["CLAUDE_HOME"] = str(CH)
for k in ("SUBAGENT_RULES", "SUBAGENT_RULES_MATCH"):
    os.environ.pop(k, None)

ctx = lambda p: s.decide(p)["hookSpecificOutput"]["additionalContext"]
out = s.decide({"agent_type": "general-purpose"})
assert out["hookSpecificOutput"]["hookEventName"] == "SubagentStart"
assert "shortcut:" in ctx({}) and "coding.md" not in ctx({})          # no rules file installed: digest only
(CH / "rules").mkdir(); (CH / "rules/coding.md").write_text("x")
assert str(CH / "rules/coding.md") in ctx({})
os.environ["SUBAGENT_RULES_MATCH"] = "general|explore"
assert s.decide({"agent_type": "Explore"}) and s.decide({"agent_type": "auditor"}) is None
os.environ["SUBAGENT_RULES_MATCH"] = "(("                              # bad regex fails open
assert s.decide({"agent_type": "auditor"})
os.environ["SUBAGENT_RULES"] = "0"
assert s.decide({}) is None
print("ok")
