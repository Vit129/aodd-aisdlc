#!/usr/bin/env python3
"""search-guard (file name kept so existing hook registrations keep working): tool-neutral code-search hook.

Agents search code with `project_search` (one call returns text and graph hits; MCP tool
`mcp__memory__project_search` or any server exposing a tool of that name); rg + Read is the primary
method and any graph backend is optional. The hook is active only when a search backend is configured:
`AODD_INDEX_CMD` (a command, `{root}` is replaced by the project root) or, if that file exists,
`<claude home>/scripts/lib/project_search.py index <root>`. Without one every mode is a silent no-op
and grep is never touched.

  pre   (PreToolUse  Bash|Grep|Read|Glob)  advice, never a block: the first raw search or source-file
        read of a session, before `project_search` was consulted, gets ONE line of context.
  post  (PostToolUse Bash|mcp__.*)  records that search was consulted: any tool named `project_search`
        (also `mcp__<server>__project_search`), or a Bash call to the backend CLI (`project_search.py`,
        or a command named in `AODD_SEARCH_CLI`, comma separated).
  stop  (Stop) opt-in: with AODD_INDEX_ON_STOP=1 it runs the index command when a code file changed since
        the last index run (once per turn). Off by default: a backend with its own file watcher keeps itself fresh.

Fails open on any error. Disable with AODD_SEARCH_GUARD=0. State markers: `AODD_SEARCH_GUARD_STATE`.
"""
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

RAW_SEARCH = {"grep", "egrep", "fgrep", "rg", "ripgrep", "ag", "ack", "fd", "find"}
CODE_EXT = {
    ".py", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".swift", ".go", ".rs", ".java", ".kt", ".kts",
    ".c", ".h", ".m", ".mm", ".cpp", ".cc", ".cxx", ".hpp", ".cs", ".rb", ".php", ".gd", ".sh", ".lua",
    ".dart", ".scala", ".vue", ".svelte",
}
GATE_MSG = (
    "search-first (advice, not a block): prefer `project_search` (text + graph hits in one call) "
    "before raw code search. Shown once per session."
)
NUDGE_MSG = (
    "A code-search backend is configured: use `project_search` to explore; read a file when you "
    "need to edit specific lines."
)


# ---- helpers ---------------------------------------------------------------------------------
def find_root(cwd):
    """Nearest ancestor that is a git checkout, else None."""
    p = Path(cwd).resolve()
    for d in [p, *p.parents]:
        if (d / ".git").exists():
            return d
    return None


def _claude_home():
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import _aodd_paths
    return _aodd_paths.claude_home()


def index_cmd(root):
    """Argv of the configured index command, or None when no backend is configured."""
    custom = os.environ.get("AODD_INDEX_CMD", "").strip()
    if custom:
        return [w.replace("{root}", str(root)) for w in shlex.split(custom)]
    script = _claude_home() / "scripts" / "lib" / "project_search.py"
    if script.is_file():
        return ["python3", str(script), "index", str(root)]
    return None


def _segments(command):
    return [s.strip() for s in re.split(r"&&|\|\||;|\n", command) if s.strip()]


def _first_words(segment):
    """Command words of a segment up to its first pipe, minus env assignments / sudo-style prefixes."""
    head = segment.split("|", 1)[0]
    try:
        words = shlex.split(head)
    except ValueError:
        words = head.split()
    while words and (re.match(r"^\w+=", words[0]) or os.path.basename(words[0]) in {"sudo", "time", "command", "nohup", "env"}):
        words = words[1:]
    return words


def non_code_targets(words, cwd):
    """Conservatively recognize explicit file targets; ambiguous shell/options stay gated."""
    name, args = os.path.basename(words[0]), words[1:]
    paths, pattern, options = [], name == "find", True
    takes_value = {"-e", "--regexp", "-f", "--file", "-g", "--glob", "--iglob", "-t", "--type",
                   "-T", "--type-not", "-A", "-B", "-C", "--after-context", "--before-context",
                   "--context", "-m", "--max-count", "--include", "--exclude", "--exclude-dir"}
    flags = {"--fixed-strings", "--ignore-case", "--line-number", "--recursive", "--hidden",
             "--files-with-matches", "--files-without-match", "--word-regexp", "--no-heading"}
    i = 0
    while i < len(args):
        arg = args[i]
        if name == "find" and arg.startswith(("-", "(", "!")):
            break  # find's expression follows its starting paths
        if options and arg == "--":
            options = False
        elif options and arg.startswith("-"):
            option = arg.split("=", 1)[0]
            if option in takes_value:
                if "=" not in arg:
                    i += 1
                    if i >= len(args):
                        return False
                if option in {"-e", "--regexp", "-f", "--file"}:
                    pattern = True
            elif arg not in flags and not re.fullmatch(r"-[nrilLhHvscqwoEFIPaUbz]+", arg):
                return False
        elif not pattern:
            pattern = True
        else:
            paths.append(arg)
        i += 1
    return bool(paths) and all(
        not re.search(r"[*?\[\]${}`<>]", p)
        and (Path(cwd) / p).is_file() and Path(p).suffix.lower() not in CODE_EXT
        for p in paths
    )


def is_raw_search(command, cwd=None):
    return any(w and os.path.basename(w[0]) in RAW_SEARCH and not non_code_targets(w, cwd or os.getcwd())
               for w in map(_first_words, _segments(command)))


def uses_search(command):
    """True for a Bash call to the search backend CLI (not an index run)."""
    names = {n.strip() for n in os.environ.get("AODD_SEARCH_CLI", "").split(",") if n.strip()}
    for w in map(_first_words, _segments(command)):
        if not w:
            continue
        head = os.path.basename(w[0])
        if head in names and not (len(w) >= 2 and w[1] == "index"):
            return True
        if head.startswith("python") and len(w) >= 3 and os.path.basename(w[1]) == "project_search.py" and w[2] != "index":
            return True
    return False


def _state_dir():
    if os.environ.get("AODD_SEARCH_GUARD_STATE"):
        return Path(os.environ["AODD_SEARCH_GUARD_STATE"])
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import _aodd_paths
    return _aodd_paths.state() / "search-guard"


def _marker(session_id, root, kind):
    key = hashlib.sha1(str(root).encode()).hexdigest()[:10]
    return _state_dir() / f"{session_id}-{key}.{kind}"


def _touch(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()


def _hso(**kw):
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", **kw}}


# ---- pre -------------------------------------------------------------------------------------
def decide_pre(payload):
    if os.environ.get("AODD_SEARCH_GUARD") == "0":
        return None
    root = find_root(payload.get("cwd") or os.getcwd())
    if root is None or (index_cmd(root) is None and not os.environ.get("AODD_SEARCH_CLI")):
        return None  # no backend configured: never interfere with grep
    tool, inp, sid = payload.get("tool_name"), payload.get("tool_input") or {}, payload.get("session_id")
    if not sid:  # cannot throttle without a session -> stay silent rather than repeat on every call
        return None
    if tool == "Grep" or (tool == "Bash" and is_raw_search(str(inp.get("command", "")), payload.get("cwd") or os.getcwd())):
        msg = GATE_MSG
    elif tool in ("Read", "Glob"):
        target = str(inp.get("file_path") or inp.get("pattern") or "")
        if Path(target).suffix.lower() not in CODE_EXT:
            return None
        msg = NUDGE_MSG
    else:
        return None
    nudged = _marker(sid, root, "nudged")  # one advice line per session, whichever tool comes first
    if nudged.exists() or _marker(sid, root, "used").exists():
        return None
    _touch(nudged)
    return _hso(additionalContext=msg)


# ---- post ------------------------------------------------------------------------------------
def record_post(payload):
    root = find_root(payload.get("cwd") or os.getcwd())
    sid = payload.get("session_id")
    if root is None or not sid:
        return
    tool = str(payload.get("tool_name") or "")
    if tool == "project_search" or tool.endswith("__project_search") or (
        tool == "Bash" and uses_search(str((payload.get("tool_input") or {}).get("command", "")))
    ):
        _touch(_marker(sid, root, "used"))


# ---- stop ------------------------------------------------------------------------------------
def _index_marker(root):
    return _state_dir() / f"index-{hashlib.sha1(str(root).encode()).hexdigest()[:10]}"


def changed_since_index(root):
    """Code files changed (git status) since the last index run; all of them when it never ran."""
    marker = _index_marker(root)
    try:
        built = marker.stat().st_mtime if marker.exists() else 0
        out = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain", "-z"], capture_output=True, text=True, timeout=10
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if out.returncode != 0:
        return []
    changed, entries, i = [], out.stdout.split("\0"), 0
    while i < len(entries):
        e = entries[i]
        i += 1
        if len(e) < 4:
            continue
        status, path = e[:2], e[3:]
        if status[0] in "RC":
            i += 1  # the next entry is the original path
        if Path(path).suffix.lower() not in CODE_EXT:
            continue
        f = root / path
        if "D" in status or (f.is_file() and f.stat().st_mtime > built + 0.5):
            changed.append(path)
    return sorted(set(changed))


def run_index(root, cmd):
    try:
        r = subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=150)
    except subprocess.TimeoutExpired:
        return 124, "timed out after 150s"
    except OSError as exc:
        return 127, str(exc)
    tail = " ".join((r.stdout + r.stderr).strip().splitlines()[-2:])
    return r.returncode, tail[:240]


def decide_stop(payload):
    if payload.get("stop_hook_active") or os.environ.get("AODD_SEARCH_GUARD") == "0":
        return None
    if os.environ.get("AODD_INDEX_ON_STOP") != "1":
        return None  # opt-in: one reindex path, the backend's own watcher
    root = find_root(payload.get("cwd") or os.getcwd())
    cmd = index_cmd(root) if root else None
    if root is None or cmd is None:
        return None  # no backend configured: nothing to refresh, stay silent
    changed = changed_since_index(root)
    if not changed:
        return None
    rc, tail = run_index(root, cmd)
    if rc == 0:
        _touch(_index_marker(root))
        return {"systemMessage": f"search index refreshed ({len(changed)} changed file(s))"}
    return {"systemMessage": f"search index update failed (exit {rc}): {tail}"}


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        payload = json.load(sys.stdin)
        if mode == "pre":
            out = decide_pre(payload)
        elif mode == "post":
            record_post(payload)
            out = None
        elif mode == "stop":
            out = decide_stop(payload)
        else:
            out = None
    except Exception:
        return  # fail open
    if out:
        print(json.dumps(out))


if __name__ == "__main__":
    main()
