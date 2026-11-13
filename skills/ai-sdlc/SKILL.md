---
name: ai-sdlc
description: >
  Change behaviour with tests: "build a feature" / "เพิ่มฟีเจอร์" in new or existing code; "refactor across files" needing QA coverage. Vague feature requests and idea questioning use Phase 1 interview; continue into an artifact refined until ready for coding. Whole jobs across disciplines: chief-of-staff.
version: 1.0.1
---

# ai-sdlc

Read `rules/ai-sdlc-workflow.md` (installed under your Claude home, `~/.claude/rules/`) now and follow it phase by phase for this feature: load each phase file from the Phase map below only when you reach that phase. Pull the
`references/*.md` files next to this SKILL.md only when the phase you are in points to them.

- Argument = feature slug. Create `$AODD_PLANS/<slug>/ai-sdlc-task-progress.md` yourself
  (`AODD_PLANS` defaults to `~/.aodd/plans`; `python3 hooks/_aodd_paths.py plans` prints the resolved dir).
- The 3 approval gates are real stops even in auto mode — the user opted in by invoking this.
- `hooks/done-gate.py` blocks stopping while that progress file still has `- [ ]` boxes,
  so keep checkboxes current as you go, not at the end.
- Runs as `chief-of-staff` full: Phase 1 output is the brief (`$AODD_PLANS/<slug>/brief.md`),
  each phase dispatches to its team, and the run ends with the report in `rules/ai-sdlc-workflow.md` § Boss mode. Risky work: propose the audit (`docs/audit.md`).
- Which skill for which task: `references/skill-routing.md`.
- Resume = read the progress file and continue at its first `- [ ]`.

## Phase map: load only the phase you are on

| Phase | File |
|---|---|
| 1 Interview | `skills/ai-sdlc/phases/phase1-interview.md` |
| 2 Architect (Requirement path; any path that adds files) | `skills/ai-sdlc/phases/phase2-architect.md` |
| 2 Existing Asset Scan | `skills/ai-sdlc/phases/phase2-existing-asset-scan.md` |
| 2 Reuse table and Nth-occurrence rule | `skills/ai-sdlc/phases/phase2-reuse-table.md` |
| 2 Reuse modification retest | `skills/ai-sdlc/phases/phase2-reuse-retest.md` |
| 3 QA-Design | `skills/ai-sdlc/phases/phase3-qa-design.md` |
| 4 Dev | `skills/ai-sdlc/phases/phase4-dev.md` |
| 5 QA-Verify | `skills/ai-sdlc/phases/phase5-qa-verify.md` |

## Read before each phase (memory dir from the `agent-memory` skill; open only matching sections)

| Before | Read first |
|---|---|
| Any phase / "continue" | this feature's progress file → resume at its first `- [ ]` (session start lists unfinished ones) |
| 1 Interview | `INDEX.md` → `knowledge/` notes for this domain; earlier plans of the same feature |
| 2 Architect | `PRODUCT.md` / `ARCHITECTURE.md`, `knowledge/` decision records, the governing skills' pitfalls |
| 3 QA design | `knowledge/` notes on known bugs in this area (each one gets a regression test) |
| 4 Dev / 5 Verify | the governing skills' pitfalls, `knowledge/` notes on known bugs |
