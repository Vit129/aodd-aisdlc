#!/usr/bin/env python3
"""Stop hook: a one-line note to the user, once per session, that a skill patch may be worth making.

Procedure to follow when the user agrees: docs/agents/skill-learning.md. Lessons go into skills
(patch a loaded skill > patch an existing umbrella > add a references/ file > new skill),
never into a loose lessons file.

Fires once per session, when it has >= MIN_TOOL_CALLS tool calls and at least one learning signal
(a user correction or a `fix` commit; tool errors are counted but no longer a signal), and no
skill file was written. The note goes out as `systemMessage` (for the user); it never blocks the
stop and never refires (INTERVAL is kept for the adapters that import it). With the `post` argument
it runs as PostToolUse(Bash) and, once per session, right after a fix commit, adds one line of context.
Fails open (any error -> allow stop). Disable with CLAUDE_SKILL_CAPTURE=0.
"""
import json
import os
import re
import sys
from pathlib import Path

MIN_TOOL_CALLS = 20  # Known limit: raw tool-call count as "complex"; swap for a smarter signal if it fires on grind-y but trivial sessions
INTERVAL = 40        # kept for the public API; nothing refires any more (one note per session)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _aodd_paths  # noqa: E402
STATE_DIR = _aodd_paths.state() / "skill-capture"
CORRECTION = re.compile(r"ไม่ใช่|ทำผิด|ผิดแล้ว|อย่าทำ|ไม่ต้องทำแบบ|ยาวไป|สั้นๆ|\b(no[,.]|wrong|that'?s not|too (long|verbose)|stop doing)\b", re.I)
FIX_COMMIT = re.compile(r"git commit[\s\S]{0,80}?\b(fix|revert)(\(|:)", re.I)  # conventional-commit subject only
SKILL_FILE = re.compile(r"(?:^|[\s/'\"])skills/[^/\s]+/(SKILL\.md|references/|scripts/|templates/)")
# a Bash write INTO a skill dir: redirect (not 2>/&>), sed -i/tee/cp/mv/install, or python open(..., "w"/"a")
SKILL_BASH_WRITE = re.compile(r"(?<![0-9&])>>?\s*['\"]?\S*skills/[^/\s]+/"
                              r"|\b(sed\s+-i|tee|cp|mv|install)\b[^|;&]*skills/[^/\s]+/"
                              r"|open\([^)]*skills/[^)]*,\s*['\"][wa]")
SKILL_MD = re.compile(r"(/[^\s'\"$*?{}]*/skills/([A-Za-z0-9][\w.:-]*)/SKILL\.md)")  # a shell $var or glob is not a skill
PATCH_FILE = re.compile(r"^\*\*\* (?:Add|Update|Delete) File: (.+?)\s*$", re.M)  # Codex apply_patch headers
DOC = "docs/skill-learning.md (under your Claude home)"

SKILL_PASS = "[skill-capture] learning signal this session ({sig}; {n} tool calls): a skill patch may be worth it, see {doc}.{loaded}"

FIX_NOTE = ""  # kept for the public API

MID_FLIGHT = "[skill-capture] a fix was committed: the skill that governs this code may deserve a pitfall note, see " + DOC + "."


def _text(content) -> str:
    if isinstance(content, str):
        return content
    return " ".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")


def scan(transcript: Path, since: int = 0):
    """Return (tool_calls, skill_written_since, signals_since, loaded_skills). `since` = tool-call count at last nudge."""
    n = errors = corrections = fixes = 0
    written = False
    loaded = {}
    with transcript.open() as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(rec.get("payload"), dict):  # Codex rollout
                n, corrections, fixes, written = _codex(rec, n, since, corrections, fixes, written, loaded)
                continue
            content = (rec.get("message") or {}).get("content") or []
            after = n > since
            said = _text(content)
            # a correction typed right after a nudge (before the next tool call) still counts; the nudge itself does not
            if (rec.get("type") == "user" and n >= since and "[skill-capture]" not in said
                    and CORRECTION.search(said[:400])):
                corrections += 1
            if isinstance(content, str):
                continue
            for block in content:
                if not isinstance(block, dict):
                    continue
                kind = block.get("type")
                if kind == "tool_result" and block.get("is_error") and after:
                    errors += 1
                elif kind == "tool_use":
                    n += 1
                    name, inp = block.get("name"), block.get("input") or {}
                    path = str(inp.get("file_path", ""))
                    cmd = str(inp.get("command", ""))
                    if name == "Skill" and inp.get("skill"):
                        loaded.setdefault(str(inp["skill"]).split(":")[-1], "")
                    for m in SKILL_MD.finditer(path if name == "Read" else cmd if name == "Bash" else ""):
                        loaded[m.group(2)] = m.group(1)
                    if n <= since:
                        continue
                    if name in ("Write", "Edit", "MultiEdit"):
                        written |= bool(SKILL_FILE.search(path))
                    elif name == "Bash":
                        if FIX_COMMIT.search(cmd):
                            fixes += 1
                        written |= bool(SKILL_BASH_WRITE.search(cmd))
    # Only a user correction or a fix commit counts (nudges that fired on ordinary tool
    # errors broke flow). Errors are normal work, not lessons (`errors` is still counted, unused).
    signals = []
    if corrections:
        signals.append(f"{corrections} user correction(s)")
    if fixes:
        signals.append("fix commit")
    return n, written, signals, loaded


def _codex(rec, n, since, corrections, fixes, written, loaded):
    """Codex rollout record {type: response_item, payload}. Returns updated (n, corrections, fixes, written)."""
    pl = rec.get("payload") or {}
    if pl.get("type") == "message" and pl.get("role") == "user":
        said = " ".join(b.get("text", "") for b in pl.get("content") or [] if isinstance(b, dict) and b.get("type") == "input_text").strip()
        if (n >= since and said and not said.startswith(("<", "# AGENTS.md")) and "[skill-capture]" not in said
                and CORRECTION.search(said[:400])):
            corrections += 1
    elif pl.get("type") in ("function_call", "custom_tool_call"):
        n += 1
        name = pl.get("name")
        if name == "exec_command":
            try:
                cmd = str(json.loads(pl.get("arguments") or "{}").get("cmd", ""))
            except (ValueError, AttributeError):
                cmd = ""
            for m in SKILL_MD.finditer(cmd):
                loaded[m.group(2)] = m.group(1)
            if n > since:
                fixes += bool(FIX_COMMIT.search(cmd))
                written |= bool(SKILL_BASH_WRITE.search(cmd))
        elif name == "apply_patch" and n > since:
            written |= any(SKILL_FILE.search(f) for f in PATCH_FILE.findall(str(pl.get("input") or "")))
    return n, corrections, fixes, written


def skill_path(name: str, known: str, cwd: Path) -> str:
    if known:
        return known
    for base in (cwd / ".claude/skills", Path.home() / ".claude/skills"):
        if (base / name / "SKILL.md").is_file():
            return str(base / name / "SKILL.md")
    return "(plugin skill: read-only, patch a local skill instead)"


def decide(payload: dict):
    """Return the note for the user, or None (no note, the stop is never blocked)."""
    if os.environ.get("CLAUDE_SKILL_CAPTURE") == "0" or payload.get("stop_hook_active"):
        return None
    sid = payload.get("session_id") or ""
    transcript = Path(payload.get("transcript_path") or "")
    if not sid or not transcript.is_file():
        return None
    marker = STATE_DIR / sid
    if marker.exists():
        return None  # said once; never again this session
    n, written, signals, loaded = scan(transcript)
    if n < MIN_TOOL_CALLS or written or not signals:
        return None
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    marker.write_text(str(n))
    cwd = Path(payload.get("cwd") or os.getcwd())
    loaded_txt = (" Skills loaded: " + ", ".join(loaded) + ".") if loaded else ""
    return SKILL_PASS.format(n=n, sig=", ".join(signals), doc=DOC, loaded=loaded_txt)


def post_tool(payload: dict):
    """PostToolUse(Bash): one mid-flight line per session, right after a fix commit. No session id -> silent."""
    sid = payload.get("session_id") or ""
    if os.environ.get("CLAUDE_SKILL_CAPTURE") == "0" or not sid:
        return None
    cmd = str((payload.get("tool_input") or {}).get("command", ""))
    if not FIX_COMMIT.search(cmd):
        return None
    marker = STATE_DIR / f"{sid}.post"
    if marker.exists():
        return None
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    marker.write_text("1")
    return MID_FLIGHT


def main():
    try:
        payload = json.load(sys.stdin)
        if sys.argv[1:] == ["post"]:
            note = post_tool(payload)
            if note:
                print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": note}}))
            return
        reason = decide(payload)
    except Exception:
        return
    if reason:
        print(json.dumps({"systemMessage": reason}))


if __name__ == "__main__":
    main()
