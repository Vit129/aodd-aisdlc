#!/usr/bin/env python3
"""Antigravity Lifecycle Hook Adapter.

Bridges Antigravity's lifecycle events (PreToolUse, PostToolUse, Stop) to
Claude Code's hardened guardrails and AODD gates:
- auditor-readonly.py (PreToolUse)
- done-gate.py (Stop)
- skill-capture-nudge.py (Stop)
And, only if present in the installed hooks directory:
- secret-read-guard.py (PreToolUse)
- coding-rules-gate.py (PreToolUse, PostToolUse)
- dirty-branch-switch-guard.py (PreToolUse)
- work-log.py (Stop)

Antigravity contract:
- PreToolUse: stdin -> {"toolCall": {"name": "...", "args": {...}}, ...}
              stdout -> {"decision": "allow"|"deny", "reason": "..."}
- PostToolUse: stdin -> {"toolCall": {...}, ...}
               stdout -> {}
- Stop: stdin -> {"terminationReason": "...", "transcriptPath": "...", ...}
        stdout -> {"decision": "continue", "reason": "..."} (to block stop) or {"decision": "allow"}

Usage:
  python3 adapters/antigravity-hook-adapter.py pre
  python3 adapters/antigravity-hook-adapter.py post
  python3 adapters/antigravity-hook-adapter.py stop
"""
import importlib.util
import json
import os

for _k, _v in list(os.environ.items()):  # settings "env" values arrive unexpanded (see hooks/_aodd_paths.py)
    if _k.startswith("AODD_") or _k == "CLAUDE_HOME":
        os.environ[_k] = os.path.expanduser(os.path.expandvars(_v))
import re
import sys
from datetime import datetime
from pathlib import Path


def get_hooks_dir() -> Path:
    if os.environ.get("AODD_HOOKS_DIR"):
        return Path(os.environ["AODD_HOOKS_DIR"]).expanduser()
    if os.environ.get("CLAUDE_HOME"):
        return Path(os.environ["CLAUDE_HOME"]).expanduser() / "hooks"
    return Path.home() / ".claude" / "hooks"


def _load_module(name: str, path: Path):
    if not path.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        if not spec or not spec.loader:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None


def load_hooks(hooks_dir: Path | None = None) -> dict:
    hdir = hooks_dir if hooks_dir is not None else get_hooks_dir()
    if str(hdir) not in sys.path:
        sys.path.insert(0, str(hdir))
    for shared in ("_aodd_paths", "_aodd_secrets"):
        sys.modules.pop(shared, None)
    return {
        "aro": _load_module("auditor_readonly", hdir / "auditor-readonly.py"),
        "dg": _load_module("done_gate", hdir / "done-gate.py"),
        "scn": _load_module("skill_capture_nudge", hdir / "skill-capture-nudge.py"),
        "srg": _load_module("secret_read_guard", hdir / "secret-read-guard.py"),
        "crg": _load_module("coding_rules_gate", hdir / "coding-rules-gate.py"),
        "dbs": _load_module("dirty_branch_switch_guard", hdir / "dirty-branch-switch-guard.py"),
        "gg": _load_module("graphify_guard", hdir / "graphify-guard.py"),
        "wl": _load_module("work_log", hdir / "work-log.py"),
    }


_current_hooks_dir = get_hooks_dir()
HOOKS = load_hooks(_current_hooks_dir)
aro = HOOKS["aro"]
dg = HOOKS["dg"]
scn = HOOKS["scn"]
srg = HOOKS["srg"]
crg = HOOKS["crg"]
dbs = HOOKS["dbs"]
gg = HOOKS["gg"]
wl = HOOKS["wl"]


def get_hook(name: str):
    global HOOKS, _current_hooks_dir, aro, dg, scn, srg, crg, dbs, gg, wl
    hdir = get_hooks_dir()
    if _current_hooks_dir != hdir:
        _current_hooks_dir = hdir
        HOOKS = load_hooks(hdir)
        aro = HOOKS["aro"]
        dg = HOOKS["dg"]
        scn = HOOKS["scn"]
        srg = HOOKS["srg"]
        crg = HOOKS["crg"]
        dbs = HOOKS["dbs"]
        gg = HOOKS["gg"]
        wl = HOOKS["wl"]
    return HOOKS.get(name)


def to_claude_payload(agy_data: dict) -> dict:
    """Translate Antigravity's JSON contract to Claude Code hook payload format."""
    tool_call = agy_data.get("toolCall") or {}
    name = tool_call.get("name", "")
    args = tool_call.get("args") or {}
    tool_name = name or agy_data.get("tool_name", "")
    tool_input = dict(args) if args else dict(agy_data.get("tool_input") or {})

    if name == "run_command":
        tool_name = "Bash"
        tool_input = {"command": args.get("CommandLine", "")}
    elif name == "view_file":
        tool_name = "Read"
        tool_input = {"file_path": args.get("AbsolutePath", "")}
    elif name == "write_to_file":
        tool_name = "Write"
        tool_input = {"file_path": args.get("TargetFile", ""), "content": args.get("CodeContent", "")}
    elif name == "replace_file_content":
        tool_name = "Edit"
        tool_input = {"file_path": args.get("TargetFile", "")}

    ws = agy_data.get("workspacePaths") or []
    cwd = agy_data.get("cwd") or (ws[0] if ws else os.getcwd())

    sid = agy_data.get("session_id") or agy_data.get("conversationId") or ""
    tpath = agy_data.get("transcript_path") or agy_data.get("transcriptPath") or ""

    return {
        "session_id": sid,
        "conversationId": sid,
        "transcript_path": tpath,
        "transcriptPath": tpath,
        "cwd": cwd,
        "workspacePaths": ws,
        "tool_name": tool_name,
        "tool_input": tool_input,
        "stop_hook_active": agy_data.get("stop_hook_active", False),
    }


def handle_pre(agy_data: dict) -> dict:
    try:
        cp = to_claude_payload(agy_data)

        # 1. auditor-readonly (AODD_AUDITOR=1: prevent writes)
        h_aro = get_hook("aro")
        if h_aro and hasattr(h_aro, "decide"):
            try:
                reason = h_aro.decide(cp)
                if reason:
                    return {"decision": "deny", "reason": reason}
            except Exception:
                pass

        # 2. secret-read-guard (if installed)
        h_srg = get_hook("srg")
        if h_srg and hasattr(h_srg, "decide"):
            try:
                res = h_srg.decide(cp)
                if res:
                    reason = res.get("hookSpecificOutput", {}).get("permissionDecisionReason", "secret access denied")
                    return {"decision": "deny", "reason": reason}
            except Exception:
                pass

        # 3. coding-rules-gate (if installed)
        h_crg = get_hook("crg")
        if h_crg and hasattr(h_crg, "decide_pre"):
            try:
                res = h_crg.decide_pre(cp)
                if res:
                    out = res.get("hookSpecificOutput", {})
                    if out.get("permissionDecision") == "deny":
                        return {"decision": "deny", "reason": out.get("permissionDecisionReason", "coding rules unread")}
            except Exception:
                pass

        # 4. dirty-branch-switch-guard (if installed)
        h_dbs = get_hook("dbs")
        if cp.get("tool_name") == "Bash" and h_dbs and hasattr(h_dbs, "decide"):
            try:
                msg, blocking, _ = h_dbs.decide(cp)
                if blocking and msg:
                    return {"decision": "deny", "reason": msg}
            except Exception:
                pass

        # 5. graphify-guard (if installed)
        h_gg = get_hook("gg")
        if h_gg and hasattr(h_gg, "decide_pre"):
            try:
                res = h_gg.decide_pre(cp)
                if res:
                    out = res.get("hookSpecificOutput", {})
                    if out.get("permissionDecision") == "deny":
                        return {"decision": "deny", "reason": out.get("permissionDecisionReason", "graphify lookup required")}
            except Exception:
                pass
    except Exception:
        pass

    return {"decision": "allow"}


def handle_post(agy_data: dict) -> dict:
    try:
        cp = to_claude_payload(agy_data)
        h_crg = get_hook("crg")
        if h_crg and hasattr(h_crg, "record_post"):
            try:
                h_crg.record_post(cp)
            except Exception:
                pass
        h_gg = get_hook("gg")
        if h_gg and hasattr(h_gg, "record_post"):
            try:
                h_gg.record_post(cp)
            except Exception:
                pass
    except Exception:
        pass
    return {}


EXIT_CODE_RE = re.compile(r"exited with code (-?[1-9]\d*)")
EDIT_TOOLS = {"write_to_file", "replace_file_content", "multi_replace_file_content", "Write", "Edit", "MultiEdit"}

AGY_SKILL_PASS = """[skill-capture] This session had a learning signal ({sig}; {n} tool calls). Most sessions teach nothing new: "skill-capture: nothing" is a fine answer, and one solid lesson beats three thin ones. Procedure: {doc}.
{loaded}
Analyse first, then pick ONE place:
  - Lesson about THIS project (its code, data, domain): add one line to that project's AGENTS.md on the branch you are working on, commit it there. No proposal.
  - Lesson about the central agent home (a skill, rule, hook, script): raise an agy-proposal. Do NOT edit skills directly (Antigravity copies are synced read-only).
  - Not verified, or would not recur: nothing.
An agy-proposal is checked by scripts/check_agy_proposal.py and auto-rejected unless every section below is filled with real evidence from this session:
  $AODD_REPORTS/agy-proposal-<YYYY-MM-DD>-<project>-<slug>.md
  - **Project:** repo folder name
  - **Repo:** absolute path of the repo the evidence commits are in
  - **What:** target file (loaded skill above > existing skill > references/ file > new skill)
  - **Analysis:** root cause, why it will recur, why it belongs in the global agent config and not the project
  - **Code:** file:line of the code involved
  - **Test:** the test command that failed before the fix, with its output
  - **Fix:** what changed
  - **Verified:** the command re-run after the fix, with its passing output
  - **Commit:** the hash of the commit holding the fix (must exist in Repo)
  - **Proposed change:** diff or exact text for the target file
Never claim "fixed" or "verified" without the command and output. Generalize (placeholders, not this session's values). If a rule caused the mistake, propose rewriting or deleting it. No secrets or company identifiers.
Then tell the user in one line what you wrote, or "skill-capture: nothing"{fix_note}."""


def scan_transcript(transcript: Path, since: int = 0):
    """Scan Antigravity or Claude transcript for tool calls and learning signals."""
    n = errors = corrections = fixes = 0
    written = False
    loaded = {}

    h_scn = get_hook("scn")
    if not h_scn:
        return 0, False, [], {}

    with transcript.open() as f:
        for line in f:
            try:
                rec = json.loads(line)
            except (json.JSONDecodeError, TypeError):
                continue

            after = n > since

            # User input / correction
            content = rec.get("content")
            if rec.get("type") in ("USER_INPUT", "user") or rec.get("source") == "USER_EXPLICIT":
                said = ""
                if isinstance(content, str):
                    said = content
                elif isinstance(rec.get("message", {}).get("content"), (str, list)):
                    said = h_scn._text(rec["message"]["content"])
                if n >= since and "[skill-capture]" not in said and h_scn.CORRECTION.search(said[:400]):
                    corrections += 1

            # Tool errors:
            # Claude format:
            msg_content = (rec.get("message") or {}).get("content")
            if isinstance(msg_content, list):
                for b in msg_content:
                    if isinstance(b, dict):
                        if b.get("type") == "tool_result" and b.get("is_error") and after:
                            errors += 1
                        elif b.get("type") == "tool_use":
                            n += 1
                            name = b.get("name")
                            inp = b.get("input") or {}
                            path = str(inp.get("file_path", ""))
                            cmd = str(inp.get("command", ""))
                            if name == "Skill" and inp.get("skill"):
                                loaded.setdefault(str(inp["skill"]).split(":")[-1], "")
                            for m in h_scn.SKILL_MD.finditer(path if name == "Read" else cmd if name == "Bash" else ""):
                                loaded[m.group(2)] = m.group(1)
                            if n > since:
                                if name in ("Write", "Edit", "MultiEdit"):
                                    written |= bool(h_scn.SKILL_FILE.search(path) or "agy-proposal" in path)
                                elif name == "Bash":
                                    if h_scn.FIX_COMMIT.search(cmd):
                                        fixes += 1
                                    written |= bool(h_scn.SKILL_BASH_WRITE.search(cmd))

            # Antigravity tool errors (result lines):
            if after and rec.get("type") not in ("USER_INPUT", "user", "PLANNER_RESPONSE") and rec.get("source") != "USER_EXPLICIT":
                has_err = (rec.get("status") == "ERROR" or
                           rec.get("type") == "ERROR_MESSAGE" or
                           bool(rec.get("error")))
                if not has_err and isinstance(content, str) and EXIT_CODE_RE.search(content):
                    has_err = True
                if has_err:
                    errors += 1

            # Antigravity tool calls:
            for tc in rec.get("tool_calls") or []:
                n += 1
                name = tc.get("name")
                args = tc.get("args") or {}
                fp = str(args.get("TargetFile") or args.get("AbsolutePath") or args.get("file_path") or "")
                cmd = str(args.get("CommandLine") or args.get("command") or "")

                if name == "Skill" and args.get("skill"):
                    loaded.setdefault(str(args["skill"]).split(":")[-1], "")
                for target_str in (fp, cmd):
                    if target_str:
                        for m in h_scn.SKILL_MD.finditer(target_str):
                            loaded[m.group(2)] = m.group(1)

                if n > since:
                    if name in EDIT_TOOLS:
                        if fp:
                            written |= bool(h_scn.SKILL_FILE.search(fp) or "agy-proposal" in fp)
                    elif name in ("run_command", "Bash"):
                        if h_scn.FIX_COMMIT.search(cmd):
                            fixes += 1
                        written |= bool(h_scn.SKILL_BASH_WRITE.search(cmd))

    signals = []
    if corrections:
        signals.append(f"{corrections} user correction(s)")
    if fixes:
        signals.append("fix commit")

    return n, written, signals, loaded


def decide_skill_capture(cp: dict):
    """Antigravity stop decision for skill-learning nudge (Hermes-style)."""
    if os.environ.get("CLAUDE_SKILL_CAPTURE") == "0" or cp.get("stop_hook_active"):
        return None
    sid = cp.get("session_id") or ""
    transcript = Path(cp.get("transcript_path") or "")
    h_scn = get_hook("scn")
    if not sid or not transcript.is_file() or not h_scn:
        return None

    state_dir = getattr(h_scn, "STATE_DIR", None)
    if state_dir is None:
        state_dir = Path(os.environ.get("AODD_STATE") or (Path(os.environ.get("AODD_HOME") or (Path.home() / ".aodd")) / "state")).expanduser() / "skill-capture"
    marker = state_dir / sid
    last = None
    if marker.exists():
        raw = marker.read_text().strip()
        last = int(raw) if raw.isdigit() else 10**9

    n, written, signals, loaded = scan_transcript(transcript, since=last or 0)
    if n < (h_scn.MIN_TOOL_CALLS if last is None else last + h_scn.INTERVAL) or written or not signals:
        return None

    state_dir.mkdir(parents=True, exist_ok=True)
    marker.write_text(str(n))
    cwd = Path(cp.get("cwd") or os.getcwd())
    loaded_txt = ("Skills loaded this session (propose changes to these first):\n" +
                  "\n".join(f"  - {k}: {h_scn.skill_path(k, v, cwd)}" for k, v in loaded.items())) if loaded else \
        "No skill was loaded this session."
    return AGY_SKILL_PASS.format(n=n, sig=", ".join(signals), doc=h_scn.DOC, loaded=loaded_txt,
                                 fix_note=h_scn.FIX_NOTE if "fix commit" in signals else "")


def handle_stop(agy_data: dict) -> dict:
    try:
        cp = to_claude_payload(agy_data)

        # 1. done-gate (checks progress files and auditor run)
        h_dg = get_hook("dg")
        if h_dg and hasattr(h_dg, "decide"):
            try:
                reason = h_dg.decide(cp)
                if reason:
                    return {"decision": "continue", "reason": reason}
            except Exception:
                pass

        # 2. skill-capture-nudge (prompts for agy-proposal if learning signals found)
        h_scn = get_hook("scn")
        if h_scn:
            try:
                reason = decide_skill_capture(cp)
                if reason:
                    return {"decision": "continue", "reason": reason}
            except Exception:
                pass

        # 3. graphify-guard stop refresh (if installed)
        h_gg = get_hook("gg")
        if h_gg and hasattr(h_gg, "decide_stop"):
            try:
                h_gg.decide_stop(cp)
            except Exception:
                pass

        # 4. work-log (records session, if installed)
        h_wl = get_hook("wl")
        if h_wl and hasattr(h_wl, "entry") and os.environ.get("CLAUDE_WORK_LOG") != "0":
            try:
                e = h_wl.entry(cp)
                d = h_wl.log_dir(e) if (e and hasattr(h_wl, "log_dir")) else (getattr(h_wl, "LOG_DIR", None) if e else None)
                if e and d:
                    d.mkdir(parents=True, exist_ok=True)
                    with (d / f"{e['ts'][:7]}.jsonl").open("a") as f:
                        f.write(json.dumps(e, ensure_ascii=False) + "\n")
            except Exception:
                pass
    except Exception:
        pass

    return {"decision": "allow"}


def main():
    event = sys.argv[1].lower() if len(sys.argv) > 1 else "pre"
    try:
        raw = sys.stdin.read().strip()
        data = json.loads(raw) if raw else {}
    except Exception:
        data = {}

    try:
        if "pre" in event:
            out = handle_pre(data)
        elif "post" in event:
            out = handle_post(data)
        elif "stop" in event:
            out = handle_stop(data)
        else:
            out = {"decision": "allow"}
    except Exception:
        out = {} if "post" in event else {"decision": "allow"}

    print(json.dumps(out))


if __name__ == "__main__":
    main()
