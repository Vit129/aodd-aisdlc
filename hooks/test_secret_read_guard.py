import importlib.util, itertools, json, os, pathlib, subprocess, sys, tempfile
os.environ["AODD_STATE"] = tempfile.mkdtemp()
spec = importlib.util.spec_from_file_location("h", os.path.join(os.path.dirname(os.path.abspath(__file__)), "secret-read-guard.py"))
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
d = pathlib.Path(tempfile.mkdtemp())
env = d / ".env"; env.write_text('export DEEPSEEK_API_KEY="sk-abcdefghijklmnopqrstuvwx"\nDEBUG=1\n')
cfg = d / "config.json"; cfg.write_text('{\n  "org": "x",\n  "pat": "abc123realvalue",\n  "token": ""\n}\n')
plain = d / "app.json"; plain.write_text('{"name": "x", "token": ""}\n')
code = d / "main.py"; code.write_text("print(1)\n")
_n = itertools.count()
dec = lambda tool, sid=None, **i: h.decide({"tool_name": tool, "tool_input": i, "session_id": sid or f"s{next(_n)}"})  # fresh session per call
denied = lambda r: bool(r) and r["hookSpecificOutput"].get("permissionDecision") == "deny"
advised = lambda r: bool(r) and "permissionDecision" not in r["hookSpecificOutput"] and bool(r["hookSpecificOutput"]["additionalContext"])
real = d / "tok.json"; real.write_text('{"x": "ghp_' + "a1B2" * 9 + '"}\n')   # a real token shape in a config file
# reads: masked view only (an .env file, a config.json with a pat)
assert denied(dec("Read", file_path=str(env))) and denied(dec("Read", file_path=str(real)))
assert "--show" in json.dumps(dec("Read", file_path=str(env)))
assert denied(dec("Bash", command=f"cat {real}")) and denied(dec("Bash", command=f"sed 's/KEY=.*//' {env}"))
assert denied(dec("Bash", command=f"cd x && grep KEY {env}")) and denied(dec("Bash", command=f"head {env}"))
for ext in (".pem", ".key"):
    k = d / f"id{ext}"; k.write_text("x"); assert denied(dec("Read", file_path=str(k))) and denied(dec("Bash", command=f"cat {k}"))
# soft: only a secret-like key in a config file -> advice naming the masked view, not a deny
assert advised(dec("Read", file_path=str(cfg))) and "--show" in json.dumps(dec("Read", file_path=str(cfg)))
assert advised(dec("Bash", command=f"cat {cfg}")) and not denied(dec("Bash", command=f"cat {cfg}"))
# allowed: key-only / existence checks, the masked view, ordinary files, empty-value configs
for c in (f"grep -c KEY {env}", f"jq 'keys' {cfg}", f"test -f {env}", f"python3 hooks/secret-read-guard.py --show {cfg}", f"cat {code}"):
    assert dec("Bash", command=c) is None, c
assert dec("Read", file_path=str(plain)) is None and dec("Read", file_path=str(code)) is None
# edits: never by the agent
# edits: advice only, never a deny
assert advised(dec("Edit", file_path=str(env))) and advised(dec("Write", file_path=str(cfg))) and advised(dec("Write", file_path=str(env)))
assert advised(dec("Bash", command=f"sed -i '' 's/a/b/' {env}")) and advised(dec("Bash", command=f"echo X=1 >> {env}"))
assert not denied(dec("Edit", file_path=str(env))) and not denied(dec("Bash", command=f"echo X=1 >> {env}"))
# once per session per text; no session id -> silent
r = h.decide({"tool_name": "Edit", "tool_input": {"file_path": str(env)}, "session_id": "same"})
assert advised(r) and h.decide({"tool_name": "Edit", "tool_input": {"file_path": str(env)}, "session_id": "same"}) is None
assert h.decide({"tool_name": "Edit", "tool_input": {"file_path": str(env)}}) is None
# more non-reads: no read, no advice
for c in (f"git add {env}", f"git status {env}", f"git check-ignore {env}", f"cp {env} {env}.bak", "grep -rn password src",
          f"cat > {d}/notes.md <<'EOF'\ncat {env}\nEOF"):
    r = dec("Bash", command=c)
    assert not denied(r), c
assert dec("Bash", command=f"git add {env}") is None and dec("Bash", command=f"git status {env}") is None
assert dec("Bash", command=f"cat > {d}/notes.md <<'EOF'\ncat {env}\nEOF") is None
assert advised(dec("Bash", command="grep -rn password src")) and advised(dec("Bash", command="rg token"))
assert denied(dec("Bash", command=f"git diff {env}")) and denied(dec("Bash", command=f"git -C {d} log -p {env}"))
assert denied(dec("Bash", command=f"bash <<EOF\ncat {env}\nEOF")) and denied(dec("Bash", command=f"cp {env} /dev/stdout"))
assert denied(dec("Bash", command=f"mv {env} /dev/tty"))
# garbage / empty payloads fail open
for junk in ("{}", "garbage", ""):
    r = subprocess.run([sys.executable, h.__file__], input=junk, capture_output=True, text=True, env={**os.environ})
    assert r.returncode == 0 and r.stdout == "", junk
assert h.decide({}) is None
# masked view keeps structure, drops values
m = h.mask(cfg.read_text() + env.read_text())
assert "abc123realvalue" not in m and "sk-abc" not in m and '"pat": "***"' in m and "DEBUG=1" in m and '"org": "x"' in m
# auditor round 1: minified JSON, tee in a pipe, keys loophole, over-broad key names, more printers, globs
one = d / "one.json"; one.write_text('{"pats":["X1FAKE"],"auth":{"pat":"NESTEDFAKE777"}}')
assert advised(dec("Read", file_path=str(one))) and "NESTEDFAKE777" not in h.mask(one.read_text()) and "X1FAKE" not in h.mask(one.read_text())
assert advised(dec("Bash", command=f"echo x | tee {env}")) and advised(dec("Bash", command=f"jq '.pat, keys' {cfg}"))
py = d / "pyproject.toml"; py.write_text('[deps]\nauthlib = "1.2"\npatch-package = "8"\n')
assert dec("Read", file_path=str(py)) is None
for c in (f"base64 {env}", f"git diff {env}", f"cat {d}/.e*"):
    assert denied(dec("Bash", command=c)), c
ex = d / ".env.example"; ex.write_text("DEEPSEEK_API_KEY=<your-key>\n")
assert dec("Read", file_path=str(ex)) is None and dec("Bash", command=f"cat {ex}") is None   # template: readable
assert advised(dec("Bash", command=f"cp {ex} {d}/.env.new"))   # creating a real .env is an edit: advice
# auditor round 2: digit-suffixed keys, cp/mv over a secret, recursive grep for key names
c2 = d / "c2.json"; c2.write_text('{\n  "pat2": "qqqqFAKE"\n}\n')
assert "qqqqFAKE" not in h.mask(c2.read_text()) and advised(dec("Read", file_path=str(c2)))
assert advised(dec("Bash", command=f"cp /tmp/y {env}")) and advised(dec("Bash", command=f"mv /tmp/y {env}"))
assert advised(dec("Bash", command="grep -r pat .")) and advised(dec("Bash", command="rg -i api_key src"))
assert dec("Bash", command="grep -rl token .") is None and dec("Bash", command="grep -r TODO src") is None
# false positives: code files named *secret*, token counts, branch names
src = d / "secret_manager.py"; src.write_text("token = os.environ['T']\n")
assert dec("Read", file_path=str(src)) is None and dec("Edit", file_path=str(src)) is None
llm = d / "llm.yaml"; llm.write_text("model: x\nmax_tokens: 4096\n")
assert dec("Read", file_path=str(llm)) is None and "4096" in h.mask(llm.read_text())
pw = d / "db.yaml"; pw.write_text("password: 123456\n")
assert advised(dec("Read", file_path=str(pw))) and h.is_secret(str(pw))   # numeric passwords still count (advice)
assert dec("Bash", command="git checkout -b fix/secret-read-guard origin/main") is None
tera = d / "cliff.toml"; tera.write_text('body = """{{ version | trim_start_matches(pat="v") }} {{ m | split(pat="x") }}"""\n')
assert not h.is_secret(str(tera))                                  # template call args are not secrets
mini = d / "m.json"; mini.write_text('{"a":1,"pat":"ghp_realvalue123"}')
assert h.is_secret(str(mini))                                      # minified JSON key after "," still caught
gdir = d / "graphify-out"; gdir.mkdir()
gg = gdir / "graph.json"; gg.write_text('{"label": "max_tokens: x", "pat": "ghp_realvalue123", "api_key": "sk-abcdefghijklmnopqrstuvwx"}\n')
assert dec("Read", file_path=str(gg)) is None and dec("Bash", command=f"cat {gg}") is None   # generated graph: allowed
assert dec("Bash", command="grep -n foo graphify-out/graph.json") is None
ge = gdir / ".env"; ge.write_text('export DEEPSEEK_API_KEY="sk-abcdefghijklmnopqrstuvwx"\n')
assert denied(dec("Read", file_path=str(ge)))   # name-based secret under graphify-out stays blocked
ge2 = d / "other" / "graph.json"; ge2.parent.mkdir(); ge2.write_text(gg.read_text())
assert denied(dec("Read", file_path=str(ge2)))   # same content (real token shape) outside graphify-out stays blocked
assert denied(dec("Read", file_path=str(env)))   # real .env unchanged
print("ok")
