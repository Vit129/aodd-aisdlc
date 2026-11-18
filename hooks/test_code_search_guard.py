import importlib.util, json, os, pathlib, subprocess, tempfile, time

spec = importlib.util.spec_from_file_location("g", os.path.join(os.path.dirname(os.path.abspath(__file__)), "code-search-guard.py"))
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)

# ---- command classification -------------------------------------------------------------
raw = g.is_raw_search
assert raw("grep -rn foo src") and raw("rg foo") and raw("find . -name '*.py'") and raw("cd x && grep a b")
assert raw("FOO=1 rg bar") and raw("sudo find /") and raw("ls; fd pattern")
assert not raw("git log | grep fix")                       # filter after a pipe, not a codebase search
assert not raw("npm test") and not raw("git grep-ish") and not raw("echo find")
os.environ["AODD_SEARCH_CLI"] = "mysearch"
assert g.uses_search("python3 ~/x/project_search.py query foo") and g.uses_search("mysearch find foo")
assert g.uses_search("cd p && mysearch callers Foo")
assert not g.uses_search("python3 project_search.py index .") and not g.uses_search("mysearch index .")
assert not g.uses_search("echo mysearch find") and not g.uses_search("rg foo")
del os.environ["AODD_SEARCH_CLI"]

# ---- fixtures: a git project with a configured backend, one without ----------------------
tmp = pathlib.Path(tempfile.mkdtemp()).resolve()
proj = tmp / "proj"; (proj / "sub" / "deep").mkdir(parents=True)
plain = tmp / "plain"; plain.mkdir()
os.environ["AODD_SEARCH_GUARD_STATE"] = str(tmp / "state")    # keep markers out of the real tmp
os.environ["AODD_HOME"] = str(tmp / "home")                   # no default backend under the test home
os.environ["CLAUDE_HOME"] = str(tmp / "claude")
os.environ["AODD_INDEX_CMD"] = "python3 -c pass {root}"       # a configured backend (stubbed below)
def git(*a):
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", *a], cwd=proj, check=True, capture_output=True)
git("init", "-q")
(plain / ".git").mkdir()

assert g.find_root(proj / "sub" / "deep") == proj              # walks up
assert g.find_root(tmp / "nowhere") is None
assert g.index_cmd(proj)[-1] == str(proj)                      # {root} substituted
del os.environ["AODD_INDEX_CMD"]
assert g.index_cmd(proj) is None                               # nothing configured, no default script
sc = tmp / "claude" / "scripts" / "lib"; sc.mkdir(parents=True); (sc / "project_search.py").write_text("")
assert g.index_cmd(proj)[1:] == [str(sc / "project_search.py"), "index", str(proj)]   # default when the file exists
(sc / "project_search.py").unlink()
os.environ["AODD_INDEX_CMD"] = "python3 -c pass {root}"

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
assert "project_search" in g.GATE_MSG

# ---- allow by default: a raw search is never refused, it gets one line of advice per session ----
assert "project_search" in advice(pre("Bash", {"command": "grep -rn load_session ."}))
assert pre("Grep", {"pattern": "foo"}) is None                                 # same session: already advised
assert pre("Bash", {"command": "rg x"}) is None and pre("Read", {"file_path": str(proj / "a.py")}) is None
assert advice(pre("Grep", {"pattern": "foo"}, sid="grep")) == g.GATE_MSG
assert pre("Bash", {"command": "npm test"}) is None             # not a search
g.record_post({"tool_name": "mcp__memory__project_search", "tool_input": {}, "cwd": str(proj), "session_id": "s2"})
assert pre("Bash", {"command": "rg x"}, sid="s2") is None                      # searched first -> silent
g.record_post({"tool_name": "Bash", "tool_input": {"command": "python3 project_search.py index ."}, "cwd": str(proj), "session_id": "s3"})
advice(pre("Bash", {"command": "rg x"}, sid="s3"))                             # index is not a lookup -> still advised once
assert pre("Bash", {"command": "rg x"}, sid=None) is None                      # no session id: cannot throttle -> silent
assert pre("Bash", {"command": "rg x"}, cwd=tmp / "missing", sid="gone") is None   # missing cwd: fail open

# no backend configured: grep is never touched
del os.environ["AODD_INDEX_CMD"]
assert pre("Bash", {"command": "grep -rn x ."}, sid="nb") is None and pre("Grep", {"pattern": "x"}, sid="nb") is None
os.environ["AODD_INDEX_CMD"] = "python3 -c pass {root}"

os.environ["AODD_SEARCH_GUARD"] = "0"
assert pre("Bash", {"command": "rg x"}, sid="s9") is None                      # explicit escape hatch
del os.environ["AODD_SEARCH_GUARD"]

# ---- Read/Glob of source files: one nudge per session, never a block --------------------
assert advice(pre("Read", {"file_path": str(proj / "a.py")}, sid="n1")) == g.NUDGE_MSG
assert pre("Read", {"file_path": str(proj / "b.py")}, sid="n1") is None        # already nudged
assert pre("Read", {"file_path": str(proj / "notes.png")}, sid="n2") is None   # not source

# ---- stop: run the index command only when code changed since the last run ---------------
(proj / "a.py").write_text("x = 1\n"); (proj / ".gitignore").write_text("")
git("add", "-A"); git("commit", "-q", "-m", "i")
assert g.changed_since_index(proj) == []                                       # committed, clean
(proj / "a.py").write_text("x = 2\n")
assert g.changed_since_index(proj) == ["a.py"]
(proj / "notes.md").write_text("doc")
assert g.changed_since_index(proj) == ["a.py"]                                 # docs never count
calls = []
g.run_index = lambda root, cmd: (calls.append((root, cmd)) or (0, ""))         # no real backend in unit tests
out = g.decide_stop({"cwd": str(proj), "session_id": "s1"})
assert len(calls) == 1 and calls[0][0] == proj and "refreshed" in out["systemMessage"]
assert g.decide_stop({"cwd": str(proj)}) is None and len(calls) == 1           # marker is newer than a.py now
time.sleep(1.1); (proj / "a.py").write_text("x = 3\n")
g.run_index = lambda root, cmd: (1, "boom")
assert "failed" in g.decide_stop({"cwd": str(proj)})["systemMessage"]
assert g.decide_stop({"cwd": str(proj), "stop_hook_active": True}) is None
assert g.decide_stop({"cwd": str(plain)}) is None                      # plain has no changes
del os.environ["AODD_INDEX_CMD"]
g.run_index = lambda root, cmd: (_ for _ in ()).throw(AssertionError("must not run without a backend"))
assert g.decide_stop({"cwd": str(proj)}) is None                               # no backend: silent no-op
print("ok")
