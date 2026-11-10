#!/usr/bin/env python3
"""Stop hook: don't end a turn claiming Done while a touched ai-sdlc progress file
still has unchecked boxes. Only checks progress files this session actually
wrote to (so an unrelated old plan never blocks). Blocks at most once per
stop cycle (stop_hook_active), fails open on any error.

The audit is on demand: the user asks for it, or the worker proposes it for risky work (rules/aodd.md),
so this hook never asks for one. "Audited" = scripts/audit.py wrote $AODD_REPORTS/audit-*-<sid8>.md for this
session. When a tracked or AODD "medium" session (MEDIUM_FILES+ files via Edit/Write/MultiEdit, Codex apply_patch;
scratch files never count) has a FAIL/DISPUTED/UNVERIFIABLE verdict -> block once per report: the worker relays
it, then may stop. Disable with DONE_GATE_AUDIT=0; DONE_GATE_ITEMS=0 turns off the open-items reminder.

Known limit: edits made through Bash are not counted."""
import hashlib
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _aodd_paths  # noqa: E402
REPORTS = _aodd_paths.reports()
VERDICT = re.compile(r"^verdict:\s*(\w+)", re.M)
PROGRESS = re.compile(r"(ai-sdlc|dev|qa)-task-progress\.md$")
MEDIUM_FILES = 5  # below this a non-PASS report does not gate
NOT_WORK = re.compile(r"(/agent-memory[^/]*/|/memory/|/\.aodd/|/\.claude/plans/|/scratchpad/|^/tmp/|^/private/(tmp|var)/)")  # notes/scratch, not deliverables
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "write_to_file", "replace_file_content", "multi_replace_file_content"}
PATCH_FILE = re.compile(r"^\*\*\* (?:Add|Update|Delete) File: (.+?)\s*$", re.M)  # Codex apply_patch headers


def scan(transcript: Path):
    """(progress files written this session, whether an auditor subagent ran, files edited)."""
    paths, audited, edited = set(), False, {}
    for line in transcript.open():
        if "task-progress" not in line and "auditor" not in line and "apply_patch" not in line and not any(t in line for t in EDIT_TOOLS):
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = str(data.get("timestamp") or "")
        # Claude Code format:
        content = data.get("message", {}).get("content") or []
        for b in content:
            if isinstance(b, dict) and b.get("type") == "tool_use":
                inp = b.get("input") or {}
                audited = audited or inp.get("subagent_type") == "auditor"
                fp = str(inp.get("file_path", ""))
                if b.get("name") in EDIT_TOOLS and fp and not NOT_WORK.search(fp):
                    edited[fp] = ts
                if PROGRESS.search(fp):
                    paths.add(Path(fp))
        # Codex rollout: {type: response_item, payload: {type: custom_tool_call, name: apply_patch, input: "<patch text>"}}
        pl = data.get("payload")
        if isinstance(pl, dict) and pl.get("name") == "apply_patch":
            for fp in PATCH_FILE.findall(str(pl.get("input") or "")):
                if not NOT_WORK.search(fp):
                    edited[fp] = ts
                if PROGRESS.search(fp):
                    paths.add(Path(fp))
        # Antigravity format:
        for tc in data.get("tool_calls") or []:
            name = tc.get("name")
            args = tc.get("args") or {}
            if name == "invoke_subagent":
                subs = args.get("Subagents") or []
                if any(s.get("TypeName") == "auditor" or s.get("Role") == "Independent Auditor" for s in subs):
                    audited = True
            fp = str(args.get("TargetFile") or args.get("AbsolutePath") or "")
            if name in EDIT_TOOLS and fp and not NOT_WORK.search(fp):
                edited[fp] = ts
            if PROGRESS.search(fp):
                paths.add(Path(fp))
    return paths, audited, edited


def audit_report(transcript: Path, reports: Path = REPORTS):
    """(report path, verdict) of the newest audit for this session, or (None, None)."""
    # done/ too: a PASS may be filed there, and a resumed session must still count as audited
    pat = f"audit-*-{_aodd_paths.session_id(transcript)}.md"
    found = sorted([*reports.glob(pat), *(reports / "done").glob(pat)], key=lambda p: (p.name.split("-", 1)[1][:10], p.stat().st_mtime)) if reports.is_dir() else []  # audit date in the name first: annotating an old report must not make it "newest"
    if not found:
        return None, None
    m = VERDICT.search(found[-1].read_text(errors="ignore"))
    return found[-1], (m.group(1).upper() if m else "UNVERIFIABLE")


def already_raised(transcript: Path, report: "Path | None" = None, kind: str = "raised", text: str = "") -> bool:
    """True if this exact report (or open-items text) was already put to the worker; records it otherwise."""
    mark = _aodd_paths.state() / f"done-gate-{kind}-{_aodd_paths.session_id(transcript)}"
    digest = hashlib.sha1(report.read_bytes() if report else text.encode()).hexdigest()
    try:
        if mark.read_text() == digest:
            return True
    except OSError:
        pass
    mark.parent.mkdir(parents=True, exist_ok=True)
    mark.write_text(digest)
    return False


def decide(payload: dict, reports: Path = REPORTS):
    if payload.get("stop_hook_active"):
        return None
    transcript = Path(payload.get("transcript_path") or payload.get("transcriptPath") or "")
    if not transcript.is_file():
        return None
    paths, _, edited = scan(transcript)
    report, verdict = audit_report(transcript, reports)
    audited = report is not None
    medium_session = len(edited) >= MEDIUM_FILES
    audit_on = os.environ.get("DONE_GATE_AUDIT") != "0"
    paths = [p for p in sorted(paths) if p.is_file()]
    open_items = []
    for p in paths:
        open_items += [f"{p}: {l.strip()}" for l in p.read_text().splitlines() if l.lstrip().startswith("- [ ]")]
    if not open_items and audited and verdict != "PASS" and audit_on and (paths or medium_session) and not already_raised(transcript, report):
        return (f"[done-gate] The independent audit says {verdict}: {report}. Do not report Done. Either fix the "
                "failed rows and re-run the audit, or tell the user plainly it is " + ("DISPUTED (the other-family auditor found a failure the "
                "verifier rejected: the CEO decides)" if verdict == "DISPUTED" else "FAILED") + ", quoting the report's table.")
    # Same list as last time -> the worker already relayed it; repeating it every stop only adds noise.
    if not open_items or os.environ.get("DONE_GATE_ITEMS") == "0" or already_raised(transcript, kind="items", text="\n".join(open_items)):
        return None
    shown = "\n".join(open_items[:8])
    return ("[done-gate] Progress file(s) touched this session still have unchecked items:\n" + shown +
            "\n\nEither finish/verify them and tick the boxes, or tell the user explicitly that the feature is NOT done "
            "and which items remain. Do not claim Done.")


def main():
    try:
        reason = decide(json.load(sys.stdin))
    except Exception:
        return
    if reason:
        print(json.dumps({"decision": "block", "reason": reason}))


if __name__ == "__main__":
    main()
