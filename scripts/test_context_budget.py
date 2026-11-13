#!/usr/bin/env python3
"""Always-loaded text has a size budget: the one always-loaded rule file (also Codex's inline), descriptions the model
reads every session, and long prompt strings in hooks."""
import re, sys
from rulescan import root, hook_files, hook_strings

RULE_MAX_LINES, RULE_MAX_CHARS = 140, 16000
CODEX_INLINE_MAX_LINES = 140
DESCRIPTION_MAX = 400
HOOK_STRING_LONG, HOOK_STRING_MAX = 200, 600

bad = []
wf = (root / "rules/ai-sdlc-workflow.md").read_text(encoding="utf-8")
if len(wf.splitlines()) > RULE_MAX_LINES:
    bad.append(f"rules/ai-sdlc-workflow.md: {len(wf.splitlines())} lines > {RULE_MAX_LINES}")
if len(wf) > RULE_MAX_CHARS:
    bad.append(f"rules/ai-sdlc-workflow.md: {len(wf)} chars > {RULE_MAX_CHARS}")
tot = len(wf.splitlines())   # Codex and Antigravity inline only this file
if tot > CODEX_INLINE_MAX_LINES:
    bad.append(f"Codex inline total (rules/ai-sdlc-workflow.md): {tot} lines > {CODEX_INLINE_MAX_LINES}")


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    return m.group(1) if m else ""


def description(fm):
    m = re.search(r"^description:[ \t]*(.*?)(?=^\w[\w-]*:|\Z)", fm, re.S | re.M)
    if not m:
        return None
    d = m.group(1).strip()
    if d[:1] in ">|":
        d = d[1:].lstrip("-+ ")
    return " ".join(d.split()).strip("\"'")


for f in sorted([*root.glob("skills/*/SKILL.md"), *root.glob("agents/*.md"), *root.glob("optional/*/skills/*/SKILL.md")]):
    rel = f.relative_to(root).as_posix()
    fm = frontmatter(f.read_text(encoding="utf-8"))
    if f.name == "SKILL.md" and re.search(r"^disable-model-invocation:\s*true", fm, re.M):
        continue
    d = description(fm)
    if d is not None and len(d) > DESCRIPTION_MAX:
        bad.append(f"{rel}:1: description {len(d)} chars > {DESCRIPTION_MAX}")
for f in hook_files():
    rel = f.relative_to(root).as_posix()
    for ln, s in hook_strings(f, docstrings=False):
        if HOOK_STRING_LONG < len(s) > HOOK_STRING_MAX:
            bad.append(f"{rel}:{ln}: string constant {len(s)} chars > {HOOK_STRING_MAX}")
if bad:
    sys.exit(f"{len(bad)} context budget offense(s):\n" + "\n".join(bad))
print("ok - context budgets hold")
