#!/usr/bin/env python3
"""Each skill is either model-invoked (the agent and other skills can reach it, and the user can still
type /<name>) or user-invoked (zero context load, only the user starts it). This pins which is which."""
import pathlib, re, sys

root = pathlib.Path(__file__).resolve().parent.parent
# Only the user starts these; nothing else needs to reach them.
USER_INVOKED = {"agent-ops", "housekeeping", "delivery-workflow",
                "test-scenario", "robotframework-testing", "performance-testing"}
# The agent and other skills must reach these (triage routes to them; chief-of-staff calls ai-sdlc,
# Phase 1 handles questioning directly). A user-invoked skill cannot be called by another skill.
MODEL_INVOKED = {"ai-sdlc", "chief-of-staff"}


def frontmatter(path):
    m = re.match(r"---\n(.*?)\n---", path.read_text(encoding="utf-8"), re.S)
    return m.group(1) if m else ""


bad = [n for n in sorted(USER_INVOKED)
       if not re.search(r"^disable-model-invocation:\s*true\s*$", frontmatter(root / "skills" / n / "SKILL.md"), re.M)]
if bad:
    sys.exit("user-only skills not marked disable-model-invocation: " + ", ".join(bad))

bad = [n for n in sorted(MODEL_INVOKED) if "disable-model-invocation" in frontmatter(root / "skills" / n / "SKILL.md")]
if bad:
    sys.exit("skills other skills must reach are marked user-invoked: " + ", ".join(bad))
# One interview leads to an HTML artifact ready for coding.
interview = (root / "skills/ai-sdlc/phases/phase1-interview.md").read_text(encoding="utf-8")
for instruction in ("weakest assumptions", "one at a time",
                    "every branch has a decision", "brief.md", "plan.html", "ready for coding",
                    "even when questions were skipped"):
    assert instruction in interview, f"interview lost questioning behavior: {instruction}"
assert "brief in the reply and **stop**" not in interview
assert "**Short:**" not in interview and "**Full:**" not in interview
print("ok - skill invocation split")
