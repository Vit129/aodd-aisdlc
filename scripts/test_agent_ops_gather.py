import importlib.util, os, pathlib, tempfile
spec = importlib.util.spec_from_file_location("g", os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent_ops_gather.py"))
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
d = pathlib.Path(tempfile.mkdtemp())
(d / "1.jsonl").write_text("read skills/graphify/SKILL.md")
(d / "2.jsonl").write_text("more graphify talk")
(d / "claude.jsonl").write_text('skills list: graphify, agent-ops ... {"skill":"agent-ops"}')
n, use = g.skill_usage(["graphify", "agent-ops", "fitness"], [d / "1.jsonl", d / "2.jsonl", d / "claude.jsonl"])
assert n == 3, n
assert use == {"graphify": 1, "agent-ops": 1, "fitness": 0}, use   # bare name mention is not a use
import subprocess, sys, os
out = d / "out.md"
env = {**os.environ, "CLAUDE_HOME": str(d / "c"), "CODEX_HOME": str(d / "none"), "AODD_HOME": str(d / "aodd")}
(d / "c/skills/foo").mkdir(parents=True); (d / "c/skills/foo/SKILL.md").write_text("---\nname: foo\n---\n")
r = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent_ops_gather.py"), str(out)], env=env, capture_output=True, text=True)
assert r.returncode == 0, r.stderr
txt = out.read_text()
assert "# Agent: claude" in txt and "foo: 0" in txt and "UNUSED" in txt and "# Agent: codex" not in txt and "Skill learning loop" in txt
print("ok")
