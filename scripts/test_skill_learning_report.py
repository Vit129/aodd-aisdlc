#!/usr/bin/env python3
"""Self-test for skill_learning_report.capture_outcome: python3 scripts/test_skill_learning_report.py"""
import importlib.util
import json
import tempfile
from pathlib import Path

spec = importlib.util.spec_from_file_location("rep", Path(__file__).with_name("skill_learning_report.py"))
rep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rep)

NUDGE = {"type": "user", "message": {"content": "Stop hook feedback: [skill-capture] run the pass"}}


def tool(name, **inp):
    return {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": name, "input": inp}]}}


def say(text):
    return {"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}}


def outcome(*recs):
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
        f.write("\n".join(json.dumps(r) for r in recs))
    return rep.capture_outcome(Path(f.name))


assert outcome(NUDGE, tool("Write", file_path="/srv/u/.claude/skills/foo/SKILL.md")) == "skill"
assert outcome(NUDGE, say("skill-capture: nothing reusable: x / y")) == "declined"
assert outcome(NUDGE, say("ok")) == "unanswered"
assert outcome(tool("Write", file_path="/x/skills/foo/SKILL.md"), NUDGE) == "unanswered"  # writes before the nudge don't count
assert outcome(say("hi")) == "no-nudge-in-transcript"
assert outcome(NUDGE, tool("Edit", file_path="/srv/p/.claude/skills/foo/references/x.md")) == "skill"
assert outcome(NUDGE, say("skill-capture: nothing: 2 tool errors / one-off typo")) == "declined"

# curator: states, lint, overlap, archive (never delete)
from datetime import date
root = Path(tempfile.mkdtemp())
def mk(name, head, body="x"):
    (root / name).mkdir(parents=True, exist_ok=True)
    (root / name / "SKILL.md").write_text(f"---\n{head}\n---\n{body}")
mk("old-auto", "name: a\ndescription: alpha beta gamma delta\nversion: 0.1.0\norigin: auto-captured\ncreated: 2026-08-01")
mk("young-auto", "name: b\ndescription: unrelated words here only\nversion: 0.1.0\norigin: auto-captured\ncreated: 2026-10-01")
mk("old-human", "name: c\ndescription: alpha beta gamma delta\ncreated: 2026-08-01", body="see references/gone.md")
mk("pinned-auto", "name: d\ndescription: zzzz\nversion: 1.0.0\norigin: auto-captured\npinned: true\ncreated: 2026-01-01")
rep.skill_files = lambda: sorted(root.glob("*/SKILL.md"))
rows, overlap = rep.curate([(date(2026, 10, 14), "used-elsewhere")], today=date(2026, 10, 15))
st = {r["skill"]: r for r in rows}
assert st["old-auto"]["state"] == "archive" and st["young-auto"]["state"] == "new"
assert "auto-captured, no use for" in st["old-auto"]["why"] and "flagged only" in st["old-human"]["why"]   # every candidate carries its reason
assert st["old-human"]["state"] == "stale" and st["pinned-auto"]["state"] == "pinned"     # only auto-captured get archived
assert "no version in frontmatter" in st["old-human"]["lint"] and any("dead refs" in l for l in st["old-human"]["lint"])
assert ("old-auto", "old-human") in overlap
mk("reborn-auto", "name: e\ndescription: qqqq\nversion: 0.1.0\norigin: auto-captured\ncreated: 2026-10-10")
r2, _ = rep.curate([(date(2026, 8, 1), "reborn-auto")], today=date(2026, 10, 15))   # old use of a same-named skill
assert {r["skill"]: r for r in r2}["reborn-auto"]["state"] == "new"
(root / "reborn-auto/SKILL.md").unlink(); (root / "reborn-auto").rmdir()
moved = rep.archive(rows)
assert moved == [str(root / ".archive" / "old-auto")] and (root / ".archive/old-auto/SKILL.md").is_file() and not (root / "old-auto").exists()
led = root / "led.json"
assert (date(2026, 9, 1), "x") in rep.with_ledger([(date(2026, 9, 1), "x")], led)
assert (date(2026, 9, 1), "x") in rep.with_ledger([], led)                          # survives transcript cleanup
m = [next(g for g in mm.groups() if g) for mm in rep.CALL.finditer('"file_path": "/srv/u/.claude/skills/foo/SKILL.md" <command-name>/bar:baz</command-name>')]
assert m == ["foo", "bar:baz"]
print("ok - skill_learning_report self-test passed")
