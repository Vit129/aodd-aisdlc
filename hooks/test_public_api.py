"""The names other tools (adapters, session-start hooks) import from these files. Removing or renaming one is a breaking change."""
import importlib.util, inspect, os, tempfile
os.environ["AODD_HOME"] = tempfile.mkdtemp()
here = os.path.dirname(os.path.abspath(__file__))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


n = load("n", os.path.join(here, "skill-capture-nudge.py"))
for name in ("CORRECTION", "DOC", "FIX_COMMIT", "FIX_NOTE", "INTERVAL", "MIN_TOOL_CALLS", "SKILL_BASH_WRITE",
             "SKILL_FILE", "SKILL_MD", "skill_path", "_text", "scan", "decide", "STATE_DIR"):
    assert hasattr(n, name), f"skill-capture-nudge.{name} is public API"

g = load("g", os.path.join(here, "done-gate.py"))
assert "reports" in inspect.signature(g.decide).parameters, "done-gate.decide(payload, reports=...)"
assert callable(g.scan) and callable(g.audit_report)

c = load("c", os.path.join(here, "..", "scripts", "check_agy_proposal.py"))
assert len(inspect.signature(c.problems).parameters) == 1, "check_agy_proposal.problems(text)"
print("ok")
