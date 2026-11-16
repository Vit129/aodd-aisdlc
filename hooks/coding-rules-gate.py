#!/usr/bin/env python3
"""coding-rules-gate: remind a session once to read `rules/coding.md` before it edits code. Never blocks.

  pre   (PreToolUse  Edit|Write|MultiEdit|NotebookEdit|Bash)  on a code-file write (Edit/Write tool,
        or a Bash command that writes a code file: sed -i, perl -i, redirect/tee, open(...,"w"),
        write_text, git apply, patch) while this session has no "read" marker, add ONE line of context
        naming the file to read. The same for the edited project's root ARCHITECTURE.md (if it has one),
        once per project. The edit itself always goes through.
  post  (PostToolUse Read|Bash)  sets a marker when rules/coding.md or ARCHITECTURE.md is read (Read
        tool, or a Bash cat/sed/head/less/nl/grep/rg on it).

Why: "read the coding rules once per session" is plain text; a session that edits only through Bash
(auto mode) skips it. The reminder only applies when `rules/coding.md` exists in the Claude home
(or at $AODD_CODING_RULES). Bash detection is a heuristic, which is why it only advises: a wrong guess
costs one line of context, never a refused command.
Fails open on any error. Disable with CODING_RULES_GATE=0.
"""
import hashlib
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _aodd_paths  # noqa: E402

CODE_EXT = (
    "py|js|jsx|mjs|cjs|ts|tsx|swift|go|rs|java|kt|kts|c|h|m|mm|cpp|cc|cxx|hpp|hh|cs|rb|php|gd|sh|lua|dart|scala|vue|svelte"
)
CODE_PATH = re.compile(rf"[\w./+~$-]+\.(?:{CODE_EXT})\b")
# Shell-level writes: matched only outside quotes and non-interpreter heredocs, so a commit message
# or PR body that merely mentions `sed -i` is not an edit.
SHELL_WRITE = re.compile(r"\bsed\s+(?:-\w*\s+)*-i|\bperl\s+-\w*i|\btee\b|>>?\s*[\w./+~$-]+\.(?:" + CODE_EXT + r")\b")
# Interpreter writes: live inside a heredoc or `-c "..."`, so matched on the quoted text.
PY_WRITE = re.compile(r"open\([^)]*['\"][wa]\+?['\"]|\.write_text\(")
# The same writes when their target is a string literal: open("x", "w") / Path("x").write_text(
PY_TARGET = re.compile(r"open\(\s*[rbfu]*['\"]([^'\"]+)['\"]\s*,[^)]*['\"][wa]\+?['\"]|Path\(\s*['\"]([^'\"]+)['\"]\s*\)\.write_text\(")
HEREDOC = re.compile(r"^(?P<head>[^\n]*?)<<-?\s*['\"]?(?P<tag>\w+)['\"]?[^\n]*\n.*?^\s*(?P=tag)\s*$", re.M | re.S)
# An interpreter as the command that reads the heredoc, not a word inside a path (`cat > /x/swift/notes.md`)
INTERPRETER = re.compile(r"(?:^|[|;&(]|\b(?:sudo|env|time|command|exec)\b)\s*(?:\w+=\S*\s+)*(?:[\w./~$-]*/)?"
                         r"(?:python3?|node|ruby|perl|bash|sh|zsh|swift|deno|bun)\b")
QUOTED = re.compile(r"'[^']*'|\"(?:\\.|[^\"\\])*\"")
PATCH = re.compile(r"\bgit\s+apply\b|\bpatch\s+-")  # writes code without naming a code file
RULE = "rules/coding.md"
ARCH = "ARCHITECTURE.md"
READERS = {"cat", "sed", "head", "tail", "less", "more", "bat", "nl", "awk", "grep", "rg", "rtk"}
MSG = "coding-rules-gate (advice, not a block): this session has not read {path}; read it before more code edits."


def rule_file():
    """The coding rules file, or None when this install has none (then the rule gate stays off)."""
    f = Path(os.environ.get("AODD_CODING_RULES") or _aodd_paths.claude_home() / RULE).expanduser()
    return f if f.is_file() else None
ARCH_MSG = "coding-rules-gate (advice, not a block): this project has {path}; read it before more code edits here."


def _marker(sid, kind="read"):
    d = Path(os.environ.get("CODING_RULES_GATE_STATE") or _aodd_paths.state() / "coding-rules-gate")
    return d / f"{sid}.{kind}"


def is_code_write(tool, inp):
    if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        path = str(inp.get("file_path") or inp.get("notebook_path") or "")
        return bool(CODE_PATH.fullmatch(path.rsplit("/", 1)[-1])) or path.endswith(".ipynb")
    if tool == "Bash":
        cmd = str(inp.get("command", ""))
        return bool(write_texts(cmd)) or any(PATCH.search(s) for s in _segments(_bare(cmd)))
    return False


def _segments(cmd):
    # Same `&&`/`||` segment only: `sed -i x.md && git add y.py` is not a code write. Not split on
    # `;`/newlines, which would cut a python heredoc's path from its open(...,"w").
    return re.split(r"&&|\|\|", cmd)


def _drop_data_heredocs(cmd):
    """Heredoc bodies fed to an interpreter are code (kept); any other body (git commit -F -, cat >
    file) is data, so dropped. `cat > x.py <<EOF` still counts: the redirect is on the head line."""
    return HEREDOC.sub(lambda m: m.group(0) if INTERPRETER.search(m.group("head")) else m.group("head"), cmd)


def _bare(cmd):
    return QUOTED.sub("", _drop_data_heredocs(cmd))


def write_texts(cmd):
    """Text of each segment that writes a code file, searched for its path. Shell writes are judged
    on the bare command (`sed -i 's|x.sh|y|' AGENTS.md` edits the .md); interpreter writes on the
    quoted text, since their path is a string literal."""
    out = [s for s in _segments(_bare(cmd)) if SHELL_WRITE.search(s) and CODE_PATH.search(s)]
    out += [t for t in map(_py_write_paths, _segments(_drop_data_heredocs(cmd))) if t]
    return out


def _py_write_paths(text):
    """Code paths an interpreter snippet writes, space-joined. A literal target decides alone
    (`open("report.md", "w")` is not a code write, whatever paths the text it writes mentions);
    only a write through a variable falls back to every code path in the snippet."""
    writes = PY_WRITE.findall(text)
    if not writes:
        return ""
    literal = [a or b for a, b in PY_TARGET.findall(text)]
    paths = literal if len(literal) >= len(writes) else [m.group() for m in CODE_PATH.finditer(text)]
    return " ".join(p for p in paths if CODE_PATH.search(p))


def reads_file(tool, inp, name):
    if tool == "Read":
        return str(inp.get("file_path", "")).endswith(name)
    if tool == "Bash":
        cmd = str(inp.get("command", ""))
        return name in cmd and any(re.search(rf"(?:^|[;&|(\s'\"]){w}\s", cmd) for w in READERS)
    return False


def find_arch(start):
    """Dir holding the project's root ARCHITECTURE.md, walking up from `start` and stopping at the
    repo root (.git), so a repo without one never inherits a parent dir's."""
    p = Path(start).expanduser().resolve()
    for d in [p, *p.parents]:
        if (d / ARCH).is_file():
            return d
        if (d / ".git").exists():
            return None
    return None


def bash_target(cmd):
    """First absolute (or ~) code path in a Bash command: the shell's cwd is often another project
    (`cd`/absolute paths), so the file decides whose ARCHITECTURE.md applies. Relative -> None (cwd)."""
    # Write segments first; then the whole command, since a `&&` inside a heredoc string can split a
    # script's `p="/abs/x.py"` from its `open(p,"w")`.
    for text in (" ".join(write_texts(cmd)), _py_write_paths(_drop_data_heredocs(cmd))):
        for m in CODE_PATH.finditer(text):
            if m.group().startswith(("/", "~", "$HOME/")):
                return m.group().replace("$HOME", "~", 1)
    return None


def _arch_key(root):
    return "arch-" + hashlib.sha1(str(root).encode()).hexdigest()[:10]


def _touch(m):
    m.parent.mkdir(parents=True, exist_ok=True)
    m.touch()


def _first_time(m):
    """True once per marker: each reminder is said one time per session, never on every edit."""
    if m.exists():
        return False
    _touch(m)
    return True


def decide_pre(payload):
    if os.environ.get("CODING_RULES_GATE") == "0":
        return None
    tool, inp, sid = payload.get("tool_name"), payload.get("tool_input") or {}, payload.get("session_id")
    if not is_code_write(tool, inp):
        return None
    target = inp.get("file_path") or inp.get("notebook_path") or bash_target(str(inp.get("command", "")))
    arch = find_arch(Path(target).expanduser().parent if target else payload.get("cwd") or os.getcwd())
    if not sid:  # cannot throttle without a session -> stay silent rather than repeat on every edit
        return None
    missing = []
    rule = rule_file()
    if rule and not _marker(sid).exists() and _first_time(_marker(sid, "advised")):
        missing.append(MSG.format(path=rule))
    if arch and not _marker(sid, _arch_key(arch)).exists() and _first_time(_marker(sid, _arch_key(arch) + "-advised")):
        missing.append(ARCH_MSG.format(path=arch / ARCH))
    if not missing:
        return None
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": " ".join(missing)}}


def record_post(payload):
    sid, tool, inp = payload.get("session_id"), payload.get("tool_name"), payload.get("tool_input") or {}
    if not sid:
        return
    if reads_file(tool, inp, "coding.md"):
        _touch(_marker(sid))
    if reads_file(tool, inp, ARCH):
        # Read gives the exact file; for Bash, the project is the one the shell is in.
        start = Path(inp["file_path"]).parent if tool == "Read" else payload.get("cwd") or os.getcwd()
        arch = find_arch(start)
        if arch:
            _touch(_marker(sid, _arch_key(arch)))


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        payload = json.load(sys.stdin)
        out = decide_pre(payload) if mode == "pre" else record_post(payload) if mode == "post" else None
    except Exception:
        return  # fail open
    if out:
        print(json.dumps(out))


if __name__ == "__main__":
    main()
