#!/usr/bin/env python3
"""PreToolUse hook: scan Write/Edit content going into memory files (agent-memory/,
memory/, knowledge/, projects/*/memory/) for leaked secrets and prompt-injection markers
before it lands. Memory files get auto-injected into every future session's context and pushed
to a git remote, so a credential written there is a standing leak. Fail-open on any error.

  DENY   a real token shape (_aodd_secrets.SECRET_PATTERNS: AWS/GitHub/OpenAI/Anthropic/Slack/
         Google/Stripe/npm key prefixes, PEM private key blocks, JWTs). The message names the
         pattern, never the value, so the agent rewrites the entry without the credential.
  ADVICE invisible unicode (zero-width space/joiners, bidi controls: normal in Thai text and
         emoji) and injection-like phrases ("ignore all previous instructions"): the write goes
         through, one line of additionalContext asks the agent to check it, once per session
         (silent without a session id).

ponytail: regex/codepoint heuristic scan, not semantic. It does not catch a novel obfuscation or an
arbitrary high-entropy string. Upgrade path: route flagged-but-uncertain content through an LLM
classifier.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _d in (HERE, HERE.parents[2] / "hooks"):  # installed: next to this file; in the repo: core hooks/
    sys.path.append(str(_d))
from _aodd_secrets import SECRET_PATTERNS  # noqa: E402
import _aodd_paths  # noqa: E402

MEMORY_PATH_MARKERS = ("/agent-memory/", "/memory/", "/knowledge/")

INVISIBLE_CODEPOINTS = {
    "​", "‌", "‍", "﻿",  # zero-width space/joiners/BOM
    "‪", "‫", "‬", "‭", "‮",  # bidi overrides
    "⁦", "⁧", "⁨", "⁩",  # bidi isolates
}

INJECTION_PATTERNS = [
    re.compile(r"ignore (all )?(previous|prior|above) instructions", re.I),
    re.compile(r"disregard (all )?(previous|prior|above)", re.I),
    re.compile(r"you are now (in )?(developer|debug|admin|jailbreak)", re.I),
    re.compile(r"reveal (your|the) (system prompt|instructions)", re.I),
    re.compile(r"do not tell (the )?user", re.I),
    re.compile(r"<\s*system\s*>", re.I),
    # Credential/SSH-key exfiltration — match the *exfiltrate* shape (an
    # instruction to send a secret somewhere), not bare secret vocabulary.
    # Memory notes discuss .env/API keys/credentials
    # constantly as ordinary content; a word-presence pattern would deny
    # legitimate writes. See the false-positive self-test below.
    re.compile(
        r"(send|post|upload|exfiltrate|email)\s+(your|my|the)?\s*"
        r"(ssh key|private key|id_rsa|api[_ ]?key|access token|credentials?|password)s?\s+to\s+\S",
        re.I,
    ),
    re.compile(
        r"\bcat\b.{0,30}(id_rsa|\.ssh/|\.aws/credentials|\.env\b).{0,40}\|\s*(curl|nc|wget|ssh)\b",
        re.I,
    ),
]

def is_memory_path(path: str) -> bool:
    return any(marker in path for marker in MEMORY_PATH_MARKERS) and path.endswith(".md")


def secret(text: str) -> str | None:
    """Reason for the one deny: a real token shape. The value is never named."""
    for name, pattern in SECRET_PATTERNS:
        if pattern.search(text):
            return f"looks like a real {name} — value withheld from this message"
    return None


def advice(text: str) -> str | None:
    """Advice only: invisible codepoints or an injection-like phrase."""
    found_invisible = sorted({f"U+{ord(c):04X}" for c in text if c in INVISIBLE_CODEPOINTS})
    if found_invisible:
        return f"invisible unicode codepoint(s) found: {', '.join(found_invisible)}"
    for pattern in INJECTION_PATTERNS:
        m = pattern.search(text)
        if m:
            return f"injection-like phrase matched: \"{m.group(0)}\""
    return None


def first_time(sid: str, text: str) -> bool:
    """True once per (session, text); same advice again in a session -> False."""
    d = _aodd_paths.state() / "memory-write-scan"
    f = d / re.sub(r"[^\w.-]", "_", sid)
    digest = hashlib.sha1(text.encode()).hexdigest()
    seen = f.read_text().split() if f.is_file() else []
    if digest in seen:
        return False
    d.mkdir(parents=True, exist_ok=True)
    f.write_text("\n".join(seen + [digest]))
    return True


def main() -> None:
    data = json.load(sys.stdin)
    if data.get("tool_name") not in ("Edit", "Write"):
        return

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    if not is_memory_path(file_path):
        return

    content = tool_input.get("content") or tool_input.get("new_string") or ""
    if not content:
        return

    name = Path(file_path).name
    reason = secret(content)
    if reason:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    f"memory-write-scan: blocked write to {name} — {reason}. "
                    "Memory files auto-load into every future session and are pushed to a git remote; "
                    "rewrite the entry without the credential."
                ),
            }
        }))
        return
    note = advice(content)
    sid = data.get("session_id")
    if note and sid and first_time(str(sid), note):
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": (
                    f"memory-write-scan (advice, not a block): {name}: {note}. Memory files auto-load into "
                    "every future session; check the content is what you mean to store."
                ),
            }
        }))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
