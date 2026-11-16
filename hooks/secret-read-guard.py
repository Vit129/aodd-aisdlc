#!/usr/bin/env python3
"""secret-read-guard: secret files may be READ only masked, so their values never reach the session
output. The one hook here that still denies; everything else is advice.

  pre  (PreToolUse Read|Bash|Edit|Write|MultiEdit)
       DENY (hard secret file): the Read tool, or a Bash command that prints the file (cat/head/tail/
         less/more/bat/sed/awk/grep without -c/-l/-q, jq without `keys`, git diff|show|blame|grep|
         cat-file|log, ...). Hard = a name like .env*, *.pem/*.key/*.p12/*.keystore, .netrc/.npmrc/
         .pypirc, a non-code file named *secret*/*credential*, or a config file holding a real token
         shape (_aodd_secrets.py SECRET_PATTERNS). The reason names the masked view:
         `python3 <hooks dir>/secret-read-guard.py --show <file>` (structure kept, values ***).
       ADVICE only (once per session per text, never a block): reading a config file whose only signal
         is a secret-like key (pat, token, password, ...); any edit or write of a secret file (do not echo
         real values); a recursive grep/rg for a secret word (it may print values: add -l or exclude .env).
       Not a read: cp, mv, git add/status/rm/check-ignore, and heredoc bodies.
  --show FILE   print FILE with every secret value masked.

Why the deny stays: a cat/sed on a secret file puts its values into the transcript and the model
provider's logs, and the key then has to be rotated; that cannot be undone. Fails open on any error.
Disable with SECRET_READ_GUARD=0.

ponytail: Bash detection is a heuristic over the command text. Known ceiling, not caught: interpreter
reads (python -c "open('.env').read()"), `source .env && echo $KEY`, `env`/`printenv`, command
substitution / xargs (`cat $(echo .env)`), and secrets
in files with no config extension. Upgrade path: a PostToolUse scan of tool output for token shapes.
"""
import hashlib
import json
import os
import re
import shlex
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _aodd_secrets import SECRET_PATTERNS  # noqa: E402
import _aodd_paths  # noqa: E402
TOKEN_SHAPES = [p for _, p in SECRET_PATTERNS]

NAME = re.compile(r"(^\.env(\..*)?$|secret|credential|\.pem$|\.key$|\.p12$|\.keystore$|^\.netrc$|^\.npmrc$|^\.pypirc$)", re.I)
TEMPLATE = re.compile(r"\.(example|sample|template|dist)$", re.I)  # checked by content instead
CODE_EXT = re.compile(r"\.(py|pyi|js|jsx|mjs|cjs|ts|tsx|go|rs|swift|java|kt|rb|php|c|h|cs|sh|zsh|md|txt|html|css)$", re.I)  # source/docs: name says nothing
CONFIG_EXT = re.compile(r"\.(json|ya?ml|toml|ini|env|properties|conf|cfg|example|sample|template|dist)$", re.I)
_WORD = r"(?:pats?|tokens?|api[_-]?keys?|secrets?|passw(?:or)?ds?|private[_-]?keys?|access[_-]?keys?|credentials?)\d*"
KEY = rf"(?:[\w-]*[_.-])?{_WORD}(?:[_.-][\w-]*)?"
# key/value anywhere on a line (minified JSON has many per line); value = quoted string, list, or bare word
KV = re.compile(rf"""(?ix)(["']?\b{KEY}\b["']?\s*[:=]\s*)("(?:\\.|[^"\\])*"|'[^']*'|\[[^\]]*\]|[^\s,}}\]]+)""")
READERS = {"cat", "head", "tail", "less", "more", "bat", "sed", "awk", "grep", "rg", "jq", "yq", "strings", "xxd", "od",
           "nl", "base64", "hexdump", "diff", "git", "scp", "rsync", "openssl", "column", "sort", "uniq", "cut"}
WRITE = re.compile(r"\bsed\s+(?:-\w*\s+)*-i|\bperl\s+-\w*i|\btee\b|>>?")
GIT_READS = {"diff", "show", "blame", "grep", "cat-file", "log"}  # other git subcommands never print file content
HEREDOC = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?([^\n]*)\n.*?\n\s*\1\b", re.S)
SHOW = f"python3 {HERE / 'secret-read-guard.py'} --show"


def secret_level(path):
    """"hard" (secret by name, or holds a real token shape), "soft" (a secret-like key only), or None."""
    p = Path(os.path.expanduser(path))
    if NAME.search(p.name) and not TEMPLATE.search(p.name) and not CODE_EXT.search(p.name):
        return "hard"
    if "graphify-out" in p.parts:  # generated code graph, never real secrets; may quote this file's own examples
        return None
    if not (p.is_file() and CONFIG_EXT.search(p.name)) or p.stat().st_size > 2_000_000:
        return None
    text = p.read_text(errors="ignore")
    if any(t.search(text) for t in TOKEN_SHAPES):
        return "hard"
    return "soft" if any(not _benign(m) for m in KV.finditer(text)) else None


def is_secret(path):
    return secret_level(path) is not None


def _placeholder(value):
    v = value.strip().strip("\"'[]").strip().strip("\"'")
    return v in ("", "null", "true", "false", "{") or v.startswith(("${", "<", "$"))


def _call_arg(m):
    """An unquoted `key=` right after `(` or `,` is a function argument in a template
    (git-cliff/Tera `split(pat="\n")`), not a config key. Quoted JSON keys stay suspect."""
    key = m.group(1).lstrip()
    return "=" in key and not key.startswith(("\"", "'")) and m.string[:m.start(1)].rstrip()[-1:] in ("(", ",")


def _benign(m):
    """Placeholder, a number on a token-count key (max_tokens: 4096), or a template call argument - not a secret."""
    v = m.group(2).strip("\"'")
    return (_placeholder(m.group(2)) or _call_arg(m)
            or (re.fullmatch(r"\d+", v) is not None and re.search(r"tokens?\b", m.group(1), re.I) is not None))


def _mask_value(m):
    v = m.group(2)
    if _benign(m):
        return m.group(0)
    if v.startswith("["):
        return m.group(1) + re.sub(r'"(?:\\.|[^"\\])*"|\'[^\']*\'', '"***"', v)
    q = v[0] if v[0] in "\"'" else ""
    return f"{m.group(1)}{q}***{q}"


def mask(text):
    text = KV.sub(_mask_value, text)
    for t in TOKEN_SHAPES:
        text = t.sub("***", text)
    return text


def _git_sub(words):
    """The git subcommand of an argv (skipping -C <dir> and -c <k=v>)."""
    it = iter(words[1:])
    for w in it:
        if w in ("-C", "-c"):
            next(it, None)
        elif not w.startswith("-"):
            return w
    return ""


def bash_targets(cmd):
    """(reads, writes, greps) of secret files in a Bash command, per pipeline segment. reads are
    (file, level) pairs; greps are recursive greps for a secret word (advice only)."""
    reads, writes, greps = [], [], []
    # a heredoc body is text, not a command, unless a shell reads it (`bash <<EOF`, `ssh host <<EOF`)
    cmd = HEREDOC.sub(lambda m: m.group(0) if re.search(r"\b(?:bash|sh|zsh|ssh)\b", cmd[cmd.rfind("\n", 0, m.start()) + 1:m.start()])
                      else m.group(2), cmd)
    for seg in re.split(r"&&|\|\|?|;|\n", cmd):
        try:
            words = shlex.split(seg, comments=True)
        except ValueError:
            words = seg.split()
        if not words or "secret-read-guard.py --show" in seg:
            continue
        args = [g for w in words[1:] if not w.startswith("-") and ("/" in w or "." in w) for g in _expand(w)]
        if os.path.basename(words[0]) == "git":  # branch/ref names look like paths; only real files count
            args = [a for a in args if os.path.isfile(os.path.expanduser(a))]
            if _git_sub(words) not in GIT_READS:
                args = []  # git add/status/rm/check-ignore/mv name the file without printing it
        if os.path.basename(words[0]) in ("cp", "mv", "scp", "rsync", "install", "ln"):
            if words[0] in ("cp", "mv") and words[-1] in ("/dev/stdout", "/dev/stderr", "/dev/tty", "-"):
                reads += [(f, secret_level(f)) for f in args[:-1] if is_secret(f)]  # copying to the terminal prints it
            if args and is_secret(args[-1]):
                writes.append(args[-1])  # overwriting a secret file is an edit
            args = args[:-1]  # the destination is written, not printed; only a secret source leaks
        files = [w for w in args if is_secret(w)]
        redirect = re.findall(r">>?\s*([^\s|;&]+)", seg)
        writes += [f for f in redirect if is_secret(f)]
        if files and words[0] in ("sed", "perl", "tee") and (words[0] == "tee" or WRITE.search(seg)):
            writes += files
            continue
        prog, flags = os.path.basename(words[0]), " ".join(w for w in words if w.startswith("-"))
        if prog in ("grep", "rg") and re.search(r"-\w*[clqL]", flags):
            continue
        if prog in ("jq", "yq") and any(re.fullmatch(r"\.?\s*keys(_unsorted)?|\.?\s*\|?\s*keys", w.strip("'\"")) for w in words[1:]):
            continue
        if prog in READERS:
            reads += [(f, secret_level(f)) for f in files]
        recursive = prog == "rg" or (prog == "grep" and re.search(r"-\w*[rR]|--recursive", flags))
        if recursive and not re.search(r"-\w*[clqL]", flags) and re.search(_WORD, seg, re.I):
            greps.append(seg.strip())
    return reads, writes, greps


def _expand(word):
    """A glob like .e* names the files it matches (cat .e* would print .env)."""
    w = os.path.expanduser(word)
    if any(c in w for c in "*?["):
        import glob
        return glob.glob(w) or [word]
    return [word]


def deny(reason):
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                   "permissionDecisionReason": reason}}


def advise(text):
    """Advice only: context for the model, the call goes through. Once per session per text."""
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": text}}


def read_msg(f):
    return (f"secret-read-guard: {f} holds secrets - its values must never appear in this session. "
            f"Read it masked instead: `{SHOW} {f}` (full structure, values ***).")


def soft_msg(f):
    return (f"secret-read-guard (advice, not a block): {f} has secret-like keys; its values may land in this "
            f"session. A masked view keeps the structure: `{SHOW} {f}`.")


def edit_msg(f):
    return (f"secret-read-guard (advice, not a block): {f} holds secrets - do not echo real values into "
            f"commands or files. If a value must change, give the user the file path and the exact command "
            f"with a placeholder like <NEW_VALUE>.")


def grep_msg(seg):
    return (f"secret-read-guard (advice, not a block): `{seg}` may print secret values; add -l or exclude "
            f".env and key files.")


def _once(sid, text):
    """True the first time this session sees this text; no session id -> False (stay silent)."""
    if not sid:
        return False
    d = _aodd_paths.state() / "secret-read-guard"
    f = d / re.sub(r"[^\w.-]", "_", str(sid))
    digest = hashlib.sha1(text.encode()).hexdigest()
    seen = f.read_text().split() if f.is_file() else []
    if digest in seen:
        return False
    d.mkdir(parents=True, exist_ok=True)
    f.write_text("\n".join(seen + [digest]))
    return True


def _advice(sid, text):
    return advise(text) if _once(sid, text) else None


def decide(payload):
    if os.environ.get("SECRET_READ_GUARD") == "0":
        return None
    tool, inp, sid = payload.get("tool_name"), payload.get("tool_input") or {}, payload.get("session_id")
    if tool in ("Read", "Edit", "Write", "MultiEdit"):
        f = inp.get("file_path", "")
        level = secret_level(f)
        if not level:
            return None
        if tool != "Read":
            return _advice(sid, edit_msg(f))
        return deny(read_msg(f)) if level == "hard" else _advice(sid, soft_msg(f))
    if tool == "Bash":
        reads, writes, greps = bash_targets(str(inp.get("command", "")))
        hard = [f for f, lvl in reads if lvl == "hard"]
        if hard:
            return deny(read_msg(hard[0]))
        text = (edit_msg(writes[0]) if writes else soft_msg(reads[0][0]) if reads else grep_msg(greps[0]) if greps else None)
        return _advice(sid, text) if text else None
    return None


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "--show":
        try:
            print(mask(Path(os.path.expanduser(sys.argv[2])).read_text(errors="ignore")))
        except OSError as e:
            print(f"secret-read-guard --show: cannot read {sys.argv[2]}: {e.strerror}", file=sys.stderr)
            sys.exit(1)
        return
    try:
        out = decide(json.load(sys.stdin))
    except Exception:
        return  # fail open
    if out:
        print(json.dumps(out))


if __name__ == "__main__":
    main()
