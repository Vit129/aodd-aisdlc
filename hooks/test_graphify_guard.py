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

# ---- the gate: raw search is refused until graphify was consulted this session ----------
d = pre("Bash", {"command": "grep -rn load_session ."})
assert d["hookSpecificOutput"]["permissionDecision"] == "deny"
assert "graphify query" in d["hookSpecificOutput"]["permissionDecisionReason"]
assert pre("Grep", {"pattern": "foo"})["hookSpecificOutput"]["permissionDecision"] == "deny"
assert pre("Bash", {"command": "grep x y"}, cwd=plain) is None                 # no graph -> never interferes
assert pre("Bash", {"command": "npm test"}) is None                            # not a search
assert pre("Bash", {"command": "graphify grep foo"}) is None

g.record_post({"tool_name": "Bash", "tool_input": {"command": "graphify query 'x'"}, "cwd": str(proj), "session_id": "s1"})
assert pre("Bash", {"command": "grep -rn load_session ."}) is None             # consulted -> allowed
assert pre("Grep", {"pattern": "foo"}) is None
d2 = pre("Bash", {"command": "grep -rn x ."}, sid="s2")                        # another session is still gated
assert d2["hookSpecificOutput"]["permissionDecision"] == "deny"
g.record_post({"tool_name": "mcp__graphify__search_text", "tool_input": {}, "cwd": str(proj), "session_id": "s2"})
assert pre("Bash", {"command": "rg x"}, sid="s2") is None                      # MCP use counts too
g.record_post({"tool_name": "Bash", "tool_input": {"command": "graphify update ."}, "cwd": str(proj), "session_id": "s3"})
assert pre("Bash", {"command": "rg x"}, sid="s3")["hookSpecificOutput"]["permissionDecision"] == "deny"  # update is not a lookup
assert "additionalContext" in pre("Bash", {"command": "rg x"}, sid=None)["hookSpecificOutput"]  # no session id -> nudge, never deny

os.environ["GRAPHIFY_GUARD"] = "0"
assert pre("Bash", {"command": "rg x"}, sid="s9") is None                      # explicit escape hatch
del os.environ["GRAPHIFY_GUARD"]

# ---- Read/Glob of source files: one nudge per session, never a block --------------------
n1 = pre("Read", {"file_path": str(proj / "a.py")}, sid="n1")
assert n1 and "permissionDecision" not in n1["hookSpecificOutput"] and "graphify" in n1["hookSpecificOutput"]["additionalContext"]
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
