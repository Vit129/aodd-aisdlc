import importlib.util, json, os, pathlib, tempfile
spec = importlib.util.spec_from_file_location("h", os.path.join(os.path.dirname(os.path.abspath(__file__)), "secret-read-guard.py"))
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
d = pathlib.Path(tempfile.mkdtemp())
env = d / ".env"; env.write_text('export DEEPSEEK_API_KEY="sk-abcdefghijklmnopqrstuvwx"\nDEBUG=1\n')
cfg = d / "config.json"; cfg.write_text('{\n  "org": "x",\n  "pat": "abc123realvalue",\n  "token": ""\n}\n')
plain = d / "app.json"; plain.write_text('{"name": "x", "token": ""}\n')
code = d / "main.py"; code.write_text("print(1)\n")
dec = lambda tool, **i: h.decide({"tool_name": tool, "tool_input": i})
denied = lambda r: r and r["hookSpecificOutput"]["permissionDecision"] == "deny"
# reads: masked view only (an .env file, a config.json with a pat)
assert denied(dec("Read", file_path=str(env))) and "--show" in json.dumps(dec("Read", file_path=str(cfg)))
assert denied(dec("Bash", command=f"cat {cfg}")) and denied(dec("Bash", command=f"sed 's/KEY=.*//' {env}"))
assert denied(dec("Bash", command=f"cd x && grep KEY {env}"))
# allowed: key-only / existence checks, the masked view, ordinary files, empty-value configs
for c in (f"grep -c KEY {env}", f"jq 'keys' {cfg}", f"test -f {env}", f"python3 hooks/secret-read-guard.py --show {cfg}", f"cat {code}"):
    assert dec("Bash", command=c) is None, c
assert dec("Read", file_path=str(plain)) is None and dec("Read", file_path=str(code)) is None
# edits: never by the agent
assert "path" in json.dumps(dec("Edit", file_path=str(env))) and denied(dec("Write", file_path=str(cfg)))
assert denied(dec("Bash", command=f"sed -i '' 's/a/b/' {env}")) and denied(dec("Bash", command=f"echo X=1 >> {env}"))
# masked view keeps structure, drops values
m = h.mask(cfg.read_text() + env.read_text())
assert "abc123realvalue" not in m and "sk-abc" not in m and '"pat": "***"' in m and "DEBUG=1" in m and '"org": "x"' in m
# auditor round 1: minified JSON, tee in a pipe, keys loophole, over-broad key names, more printers, globs
one = d / "one.json"; one.write_text('{"pats":["X1FAKE"],"auth":{"pat":"NESTEDFAKE777"}}')
assert denied(dec("Read", file_path=str(one))) and "NESTEDFAKE777" not in h.mask(one.read_text()) and "X1FAKE" not in h.mask(one.read_text())
assert denied(dec("Bash", command=f"echo x | tee {env}")) and denied(dec("Bash", command=f"jq '.pat, keys' {cfg}"))
py = d / "pyproject.toml"; py.write_text('[deps]\nauthlib = "1.2"\npatch-package = "8"\n')
assert dec("Read", file_path=str(py)) is None
for c in (f"base64 {env}", f"git diff {env}", f"cp {env} /tmp/x", f"cat {d}/.e*"):
    assert denied(dec("Bash", command=c)), c
ex = d / ".env.example"; ex.write_text("DEEPSEEK_API_KEY=<your-key>\n")
assert dec("Read", file_path=str(ex)) is None and dec("Bash", command=f"cat {ex}") is None   # template: readable
assert denied(dec("Bash", command=f"cp {ex} {d}/.env.new"))   # creating a real .env is the user's edit
# auditor round 2: digit-suffixed keys, cp/mv over a secret, recursive grep for key names
c2 = d / "c2.json"; c2.write_text('{\n  "pat2": "qqqqFAKE"\n}\n')
assert "qqqqFAKE" not in h.mask(c2.read_text()) and denied(dec("Read", file_path=str(c2)))
assert denied(dec("Bash", command=f"cp /tmp/y {env}")) and denied(dec("Bash", command=f"mv /tmp/y {env}"))
assert denied(dec("Bash", command="grep -r pat .")) and denied(dec("Bash", command="rg -i api_key src"))
assert dec("Bash", command="grep -rl token .") is None and dec("Bash", command="grep -r TODO src") is None
# false positives: code files named *secret*, token counts, branch names
src = d / "secret_manager.py"; src.write_text("token = os.environ['T']\n")
assert dec("Read", file_path=str(src)) is None and dec("Edit", file_path=str(src)) is None
llm = d / "llm.yaml"; llm.write_text("model: x\nmax_tokens: 4096\n")
assert dec("Read", file_path=str(llm)) is None and "4096" in h.mask(llm.read_text())
pw = d / "db.yaml"; pw.write_text("password: 123456\n")
assert denied(dec("Read", file_path=str(pw)))   # numeric passwords still count
assert dec("Bash", command="git checkout -b fix/secret-read-guard origin/main") is None
tera = d / "cliff.toml"; tera.write_text('body = """{{ version | trim_start_matches(pat="v") }} {{ m | split(pat="x") }}"""\n')
assert not h.is_secret(str(tera))                                  # template call args are not secrets
mini = d / "m.json"; mini.write_text('{"a":1,"pat":"ghp_realvalue123"}')
assert h.is_secret(str(mini))                                      # minified JSON key after "," still caught
print("ok")
