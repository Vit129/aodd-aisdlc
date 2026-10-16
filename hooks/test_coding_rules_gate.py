import importlib.util, os, pathlib, tempfile

spec = importlib.util.spec_from_file_location("g", os.path.join(os.path.dirname(os.path.abspath(__file__)), "coding-rules-gate.py"))
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
os.environ["CODING_RULES_GATE_STATE"] = tempfile.mkdtemp()
CH = pathlib.Path(tempfile.mkdtemp()); os.environ["CLAUDE_HOME"] = str(CH)
TMP = pathlib.Path(tempfile.mkdtemp()).resolve()
plain = TMP / "plain"; (plain / ".git").mkdir(parents=True)                       # repo without ARCHITECTURE.md
proj = TMP / "proj"; (proj / ".git").mkdir(parents=True); (proj / "src").mkdir()
(proj / "ARCHITECTURE.md").write_text("x")

w = lambda cmd: g.is_code_write("Bash", {"command": cmd})
# the forms this session actually used to edit code without reading the rule
assert w("sed -i '' -E 's/a/b/' Packages/X/Foo+Bar.swift")
assert w("python3 - <<'EOF'\np='src/a.swift'\nopen(p,\"w\").write(s)\nEOF")
assert w("cat > hooks/x.py <<'EOF'\nprint(1)\nEOF") and w("echo x >> lib/a.ts") and w("printf x | tee src/a.go")
assert w("perl -pi -e 's/a/b/' a.rs") and w("git apply fix.patch && swift build x.swift") is True
# reads, builds, and non-code writes are not edits
# text that only mentions a write: commit-message heredoc, quoted PR body
assert not w("git add a.py && git commit -q -F - <<'EOF'\nfix: sed -i on x.sh\nEOF")
assert not w("gh pr create --body \"$(printf 'run sed -i s/a/b/ x.py first')\"")
assert w("cat > hooks/y.py <<'EOF'\nprint(1)\nEOF")                                  # redirect on the head line
assert w("python3 - <<'EOF'\nopen('a.py','w').write('')\nEOF") and w("python3 -c \"open('a.py','w')\"")
assert not w("sed -i '' 's|^graphify update . && ~/.claude/scripts/x.sh .$|graphify update .|' AGENTS.md")  # .sh only in the sed script
assert g.bash_target("sed -i '' 's|~/.claude/x.sh|y|' /r/AGENTS.md") is None
assert g.bash_target("python3 - <<'EOF'\np='/r/t.py'; s='a && b'\nopen(p,'w')\nEOF") == "/r/t.py"
assert not w("sed -i '' s/a/b/ rules/core.md && git add hooks/x.py")
assert not w("cat Sources/a.swift") and not w("sed -n 1,20p a.swift") and not w("swift test --filter X")
assert not w("grep -rn foo src/a.py") and not w("echo hi > notes.md") and not w("node Tests/a.test.mjs")
assert g.is_code_write("Edit", {"file_path": "/r/MobileBridgeServer+Connection.swift"})
assert g.is_code_write("Write", {"file_path": "/r/hooks/x.py"})
assert not g.is_code_write("Edit", {"file_path": "/r/README.md"}) and not g.is_code_write("Write", {"file_path": "/r/a.json"})

# no rules/coding.md installed: the rule gate stays off (nothing to read)
assert g.decide_pre({"tool_name": "Edit", "tool_input": {"file_path": str(plain / "a.swift")}, "session_id": "s0", "cwd": str(plain)}) is None
(CH / "rules").mkdir(); (CH / "rules/coding.md").write_text("rules")
pre = lambda tool, inp, sid="s1", cwd=plain: g.decide_pre({"tool_name": tool, "tool_input": inp, "session_id": sid, "cwd": str(cwd)})
A, P = str(plain / "a.swift"), str(proj / "src" / "a.swift")
d = pre("Edit", {"file_path": A})
assert d["hookSpecificOutput"]["permissionDecision"] == "deny" and "rules/coding.md" in d["hookSpecificOutput"]["permissionDecisionReason"]
assert "permissionDecision" not in pre("Edit", {"file_path": A}, sid=None)["hookSpecificOutput"]  # no session -> remind only
assert pre("Edit", {"file_path": str(plain / "a.md")}) is None

# reading the rule (Read tool or Bash cat) unlocks the session, and only that session
assert not g.reads_file("Bash", {"command": "echo rules/coding.md"}, g.RULE)
g.record_post({"tool_name": "Bash", "tool_input": {"command": "cat ~/.claude/rules/coding.md; ls"}, "session_id": "s1"})
assert pre("Edit", {"file_path": A}) is None
assert pre("Edit", {"file_path": A}, sid="s2")["hookSpecificOutput"]["permissionDecision"] == "deny"
g.record_post({"tool_name": "Read", "tool_input": {"file_path": "/srv/u/.claude/rules/coding.md"}, "session_id": "s2"})
assert pre("Bash", {"command": "sed -i '' s/a/b/ a.swift"}, sid="s2") is None

# a project with ARCHITECTURE.md also needs that file read, per project
assert g.find_arch(proj / "src") == proj and g.find_arch(plain) is None
r = pre("Edit", {"file_path": P})["hookSpecificOutput"]["permissionDecisionReason"]     # s1 read coding.md only
assert "ARCHITECTURE.md" in r and "rules/coding.md" not in r
assert "rules/coding.md" in pre("Edit", {"file_path": P}, sid="s9")["hookSpecificOutput"]["permissionDecisionReason"]
g.record_post({"tool_name": "Bash", "tool_input": {"command": "cat ARCHITECTURE.md"}, "cwd": str(proj), "session_id": "s1"})
assert pre("Edit", {"file_path": P}) is None
assert pre("Bash", {"command": "sed -i '' s/a/b/ src/a.swift"}, cwd=proj) is None
g.record_post({"tool_name": "Read", "tool_input": {"file_path": str(proj / "ARCHITECTURE.md")}, "session_id": "s2"})
assert pre("Edit", {"file_path": P}, sid="s2") is None

# Bash run from another project's cwd: an absolute path decides the project, not the cwd
assert pre("Bash", {"command": f"sed -i '' s/a/b/ {P}"}, sid="s3", cwd=plain)["hookSpecificOutput"]["permissionDecision"] == "deny"
g.record_post({"tool_name": "Read", "tool_input": {"file_path": "/x/rules/coding.md"}, "session_id": "s3"})
assert "ARCHITECTURE.md" in pre("Bash", {"command": f"sed -i '' s/a/b/ {P}"}, sid="s3", cwd=plain)["hookSpecificOutput"]["permissionDecisionReason"]
assert pre("Bash", {"command": f"sed -i '' s/a/b/ {A}"}, sid="s3", cwd=proj) is None
assert g.bash_target("cd x && sed -i s/a/b/ src/a.swift") is None
assert g.bash_target("f=\"$HOME/.claude/hooks/x.py\"; open(f,\"w\")") == "~/.claude/hooks/x.py"

os.environ["CODING_RULES_GATE"] = "0"
assert pre("Edit", {"file_path": P}, sid="s4") is None
print("coding-rules-gate: ok")
