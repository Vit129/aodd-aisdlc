#!/usr/bin/env python3
"""Each rule topic has one home file. A signature phrase of a topic may appear only in its home;
everywhere else must point to it. Offenses print as file:line so they work as a to-do list."""
import re, sys
from rulescan import text_units

# topic -> (home files, [signature regexes])
SINGLE_HOME = {
    "delegation + effort ladder": (["rules/ai-sdlc/delegation.md"], [
        r"starts at .low.", r"3 failing checks", r"low\s*(?:->|→|to)\s*medium\s*(?:->|→|to)\s*high",
        r"announce[sd]? (?:the )?(?:effort|level)[^.\n]*once"]),
    "git ops / commit prep / graph refresh": (["rules/ai-sdlc/git-ops.md"], [
        r"PYTHONHASHSEED", r"Haiku ops runner", r"never `git add -A`", r"graph-only commit"]),
    "audit command and procedure": (["docs/audit.md"], [r"audit\.py --transcript"]),
    "skill-learning procedure": (["docs/skill-learning.md"], [
        r"Self-Update \(after every use\)", r"auto-captured`? skill"]),
    "ai-sdlc paths, phases, gates": (["rules/ai-sdlc-workflow.md"], [
        r"entered at Phase", r"Logic path entered", r"Requirement path's 3 gates"]),
    "Boss report shape": (["rules/ai-sdlc-workflow.md"], [r"Result\W+Evidence\W+Needs (?:your |CEO )?decision"]),
    "debugging-skill rule": (["rules/ai-sdlc-workflow.md"], [r"Every bug goes through the debugging skill", r"debugging skill first"]),
    "size rule": (["rules/ai-sdlc-workflow.md"], [r"pick the smaller"]),
    "skill routing table": (["skills/ai-sdlc/references/skill-routing.md"], [r"Skill-by-situation routing"]),
    "artifact/plan file locations": (["skills/ai-sdlc/references/ai-sdlc-progress-spec.md"], [
        r"agent-memory/plans/\[?<?(?:FEATURE|feature)"]),
}
# a signature in a per-vendor effort file is fine only for the vendor syntax, so no vendor exemption is listed

units = text_units()
offenses = {}
for topic, (homes, sigs) in SINGLE_HOME.items():
    pat = re.compile("|".join(sigs), re.I)
    for rel, ln, line in units:
        if rel not in homes and (m := pat.search(line)):
            offenses.setdefault(topic, []).append(f"{rel}:{ln}: {m.group(0)!r} (home: {homes[0]})")
if offenses:
    n = sum(map(len, offenses.values()))
    sys.exit(f"{n} signature(s) outside their single home:\n" + "\n".join(
        f"[{t}] ({len(v)})\n  " + "\n  ".join(v) for t, v in offenses.items()))
print("ok - every rule topic appears only in its single home")
