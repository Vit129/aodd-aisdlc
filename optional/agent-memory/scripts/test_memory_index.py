#!/usr/bin/env python3
"""Self-test for memory_index.py: python3 optional/agent-memory/scripts/test_memory_index.py"""
import importlib.util
import tempfile
from pathlib import Path

spec = importlib.util.spec_from_file_location("mi", Path(__file__).with_name("memory_index.py"))
mi = importlib.util.module_from_spec(spec); spec.loader.exec_module(mi)
with tempfile.TemporaryDirectory() as t:
    m = Path(t)
    (m / "knowledge").mkdir(); (m / "knowledge/auth.md").write_text("# Auth modes\nSSO vs form\n")
    p = m / "plans/login"; p.mkdir(parents=True)
    (p / "ai-sdlc-task-progress.md").write_text("- [x] design\n- [ ] write tests\n")
    d = m / "plans/old"; d.mkdir(); (d / "ai-sdlc-task-progress.md").write_text("- [x] a\n")
    (m / "INDEX.md").write_text("# Agent Memory Index\nhand-written note\n")
    mi.rebuild(m)
    s = (m / "INDEX.md").read_text()
    assert "hand-written note" in s                                   # text outside the markers is kept
    assert "knowledge/auth.md" in s and "Auth modes" in s             # knowledge row with its title
    assert "plans/login" in s and "open" in s and "write tests" in s  # live plan, first open box
    assert "plans/old" in s and "done" in s
    mi.rebuild(m)
    assert (m / "INDEX.md").read_text().count(mi.START) == 1           # idempotent: block replaced, not appended
    (m / "knowledge/auth.md").unlink(); mi.rebuild(m)
    assert "auth.md" not in (m / "INDEX.md").read_text()               # removed file -> row gone
print("ok - memory_index self-test passed")
