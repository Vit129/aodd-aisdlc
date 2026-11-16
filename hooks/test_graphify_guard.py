import importlib.util, json, os, pathlib, subprocess, tempfile, time

spec = importlib.util.spec_from_file_location("g", os.path.join(os.path.dirname(os.path.abspath(__file__)), "graphify-guard.py"))
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)

# ---- command classification -------------------------------------------------------------
raw = g.is_raw_search
assert raw("grep -rn foo src") and raw("rg foo") and raw("find . -name '*.py'") and raw("cd x && grep a b")
assert raw("FOO=1 rg bar") and raw("sudo find /") and raw("ls; fd pattern")
assert not raw("git log | grep fix")                       # filter after a pipe, not a codebase search
assert not raw("graphify grep foo") and not raw("graphify query 'where is grep'")
assert not raw("npm test") and not raw("git grep-ish") and not raw("echo find") and not raw("cat graphify-out/x | rg a")
assert not raw("rg foo graphify-out/GRAPH_REPORT.md")
assert g.uses_graphify("graphify query 'x'") and g.uses_graphify("cd p && graphify explain Foo") and g.uses_graphify("graphify affected X")
assert g.uses_graphify("graphify grep foo") and g.uses_graphify("graphify flow f --param p")
assert not g.uses_graphify("graphify update .") and not g.uses_graphify("echo graphify query")

# ---- fixtures: a project with a graph, a project without -------------------------------
tmp = pathlib.Path(tempfile.mkdtemp()).resolve()
proj = tmp / "proj"; (proj / "graphify-out").mkdir(parents=True); (proj / "sub" / "deep").mkdir(parents=True)
(proj / "graphify-out" / "graph.json").write_text("{}")
plain = tmp / "plain"; plain.mkdir()
os.environ["GRAPHIFY_GUARD_STATE"] = str(tmp / "state")       # keep markers out of the real tmp

assert g.find_root(proj / "sub" / "deep") == proj              # walks up
assert g.find_root(plain) is None

def pre(tool, inp, cwd=proj, sid="s1"):
    return g.decide_pre({"tool_name": tool, "tool_input": inp, "cwd": str(cwd), "session_id": sid})

# [TS-TOKEN-02][BE-UT] Only explicit non-code files bypass the Bash gate.
(proj / "rules").mkdir()
for name in ("rules/foo.md", "rules/other file.txt", "rules/config.json", "rules/source.py"):
    (proj / name).write_text("x")
(proj / "rules/looks.md").mkdir()
for cmd in (
    "grep -n x rules/foo.md", "rg x rules/foo.md rules/config.json",
    "grep -e x -- rules/foo.md", "rg --regexp x 'rules/other file.txt'",
    "grep -A 2 x rules/foo.md", "rg --glob '*.py' x rules/foo.md",
    "grep x rules/foo.md && rg y rules/config.json",
    "find rules/foo.md -name '*.md'", "fd x rules/foo.md",
):
    assert pre("Bash", {"command": cmd}, sid="docs") is None, cmd
def advice(out):
    """A PreToolUse result that only adds context: never a permission decision."""
    assert out and "permissionDecision" not in out["hookSpecificOutput"], out
    return out["hookSpecificOutput"]["additionalContext"]

for i, cmd in enumerate((
    "rg x", "grep -n x rules", "grep x rules/foo.md rules/source.py",
    "rg x rules/looks.md", "find rules -name '*.md'",
    "grep x rules/foo.md; rg x rules/source.py", "grep -f rules/foo.md",
    "rg -g '*.md' x", "grep x rules/*.md", "grep x missing.md",
)):
    assert advice(pre("Bash", {"command": cmd}, sid=f"code{i}")) == g.GATE_MSG, cmd   # code search: advice only
assert len(g.GATE_MSG) <= 200 and "\n" not in g.GATE_MSG
assert g.GATE_MSG.index("graphify query") < g.GATE_MSG.index("mcp__graphify__*")

# ---- allow by default: a raw search is never refused, it gets one line of advice per session ----
assert "graphify query" in advice(pre("Bash", {"command": "grep -rn load_session ."}))
assert pre("Grep", {"pattern": "foo"}) is None                                 # same session: already advised
assert pre("Bash", {"command": "rg x"}) is None and pre("Read", {"file_path": str(proj / "a.py")}) is None
assert advice(pre("Grep", {"pattern": "foo"}, sid="grep")) == g.GATE_MSG
assert pre("Bash", {"command": "grep x y"}, cwd=plain) is None                 # no graph -> never interferes
assert pre("Bash", {"command": "npm test"}) is None                            # not a search
assert pre("Bash", {"command": "graphify grep foo"}) is None
advice(pre("Bash", {"command": "graphify grep x; rg y"}, sid="compound2"))

g.record_post({"tool_name": "mcp__graphify__search_text", "tool_input": {}, "cwd": str(proj), "session_id": "s2"})
assert pre("Bash", {"command": "rg x"}, sid="s2") is None                      # graphify consulted first -> silent
g.record_post({"tool_name": "Bash", "tool_input": {"command": "graphify update ."}, "cwd": str(proj), "session_id": "s3"})
advice(pre("Bash", {"command": "rg x"}, sid="s3"))                             # update is not a lookup -> still advised once
assert pre("Bash", {"command": "rg x"}, sid=None) is None                      # no session id: cannot throttle -> silent
assert pre("Bash", {"command": "rg x"}, cwd=tmp / "missing", sid="gone") is None   # missing cwd: fail open

os.environ["GRAPHIFY_GUARD"] = "0"
assert pre("Bash", {"command": "rg x"}, sid="s9") is None                      # explicit escape hatch
del os.environ["GRAPHIFY_GUARD"]

# ---- Read/Glob of source files: one nudge per session, never a block --------------------
assert advice(pre("Read", {"file_path": str(proj / "a.py")}, sid="n1")) == g.NUDGE_MSG
assert pre("Read", {"file_path": str(proj / "b.py")}, sid="n1") is None        # already nudged
assert pre("Read", {"file_path": str(proj / "notes.png")}, sid="n2") is None   # not source
assert pre("Read", {"file_path": str(proj / "graphify-out" / "GRAPH_REPORT.md")}, sid="n3") is None

# ---- stop: refresh the graph only when code changed since it was built -------------------
def git(*a):
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", *a], cwd=proj, check=True, capture_output=True)
git("init", "-q"); (proj / "a.py").write_text("x = 1\n"); (proj / ".gitignore").write_text("")
git("add", "-A"); git("commit", "-q", "-m", "i")
time.sleep(1.1)
(proj / "graphify-out" / "graph.json").write_text("{}")                        # graph built after the commit
assert g.changed_since_graph(proj) == []
time.sleep(1.1)
(proj / "a.py").write_text("x = 2\n")
assert g.changed_since_graph(proj) == ["a.py"]
(proj / "notes.md").write_text("doc"); (proj / "graphify-out" / "extra.json").write_text("{}")
assert g.changed_since_graph(proj) == ["a.py"]                                  # docs and graphify-out never count
calls = []
g.run_update = lambda root: (calls.append(root) or (0, ""))                     # no real graphify in unit tests
g.shutil.which = lambda name: "/fake/graphify" if name == "graphify" else None  # stub availability too
out = g.decide_stop({"cwd": str(proj), "session_id": "s1"})
assert calls == [proj] and "refreshed" in out["systemMessage"]
assert g.decide_stop({"cwd": str(proj), "stop_hook_active": True}) is None and calls == [proj]
assert g.decide_stop({"cwd": str(plain)}) is None
g.run_update = lambda root: (1, "boom")
assert "failed" in g.decide_stop({"cwd": str(proj)})["systemMessage"]
(proj / "graphify-out" / "graph.json").write_text("{}")                        # refreshed -> nothing to do
g.run_update = lambda root: (_ for _ in ()).throw(AssertionError("must not run"))
assert g.decide_stop({"cwd": str(proj)}) is None
print("ok")
