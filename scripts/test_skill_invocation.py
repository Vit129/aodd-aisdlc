#!/usr/bin/env python3
"""Step-by-step workflow skills are user-invoked: the model would pick them by matching words in the
description, which misses most real requests, and every model-invoked description costs context on
every turn. The rules route work to them by name instead."""
import pathlib, re, sys

root = pathlib.Path(__file__).resolve().parent.parent
USER_INVOKED = {"ai-sdlc", "chief-of-staff", "agent-ops", "housekeeping", "delivery-workflow",
                "test-scenario", "robotframework-testing", "performance-testing"}


def frontmatter(path):
    m = re.match(r"---\n(.*?)\n---", path.read_text(encoding="utf-8"), re.S)
    return m.group(1) if m else ""


bad = [n for n in sorted(USER_INVOKED)
       if not re.search(r"^disable-model-invocation:\s*true\s*$", frontmatter(root / "skills" / n / "SKILL.md"), re.M)]
if bad:
    sys.exit("workflow skills not marked disable-model-invocation: " + ", ".join(bad))

# A rule that routes to a user-invoked skill must tell the model to open the file, not to call the Skill tool.
for f in [root / "rules/aodd.md", root / "skills/chief-of-staff/SKILL.md"]:
    if re.search(r"invoke the `ai-sdlc` skill yourself|\(Skill tool", f.read_text(encoding="utf-8")):
        sys.exit(f"{f.relative_to(root)} still tells the model to call a user-invoked skill through the Skill tool")
print("ok - workflow skills are user-invoked")
