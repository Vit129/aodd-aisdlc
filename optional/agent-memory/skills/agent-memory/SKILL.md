---
name: agent-memory
description: >
  This skill should be used when the user asks to "bootstrap agent memory",
  "setup memory", "สร้าง agent memory", "reset memory", "memory template",
  "initialize memory files", "create memory structure",
  or needs guidance on the agent memory file structure, session flow,
  knowledge capture, or subagent delegation patterns.
  Non-coding tasks (research, analysis, writing) use this memory system alongside coding tasks.
version: 4.0.1
---

# Agent Memory

Set up and use a small, file-based memory for a project. It is agent-driven during a live session; no hook automates any of it
(the only hooks involved are the optional `skill-capture-nudge` Stop hook and your own).

## Memory structure

The memory directory is `$AODD_PLANS`'s parent by default: `$AODD_HOME/` (see `hooks/_aodd_paths.py`; `python3 hooks/_aodd_paths.py plans` prints the plans path for the current project). Per project:

```text
<memory dir>/
├── INDEX.md      ← catalog of knowledge/ and plans/
├── plans/        ← per-feature ai-sdlc-task-progress.md, handoff.md
└── knowledge/    ← flat topic files named by domain (no subdirectories)
```

Files are UPPERCASE for the fixed ones (`INDEX.md`), lowercase topic names for `knowledge/`.

## Bootstrap

If the memory directory is missing, create it from `references/templates/` (idempotent: only add what is missing, never overwrite):

```bash
M="$(dirname "$(python3 hooks/_aodd_paths.py plans)")"   # or your own location
mkdir -p "$M/plans" "$M/knowledge"; [ -f "$M/INDEX.md" ] || cp references/templates/INDEX.md "$M/INDEX.md"
```

Never skip silently when it is missing: create it, then continue.

## When to load each reference

| User says | Load |
|-----------|------|
| "bootstrap memory", "setup memory", "initialize", "reset" | Bootstrap above, then `references/templates/` |
| "session flow", "how does memory work" | `references/session-flow.md` |
| "subagent", "memory curator", "knowledge curation", "delegate memory" | `references/subagent-patterns.md` |
| "review rubric", "self-review", "what to save", "grading criteria" | `references/self-review-rubric.md` |

## Knowledge capture

- **Skills** hold every reusable procedure, pitfall and correction. Procedure: `docs/skill-learning.md` (the Stop hook `skill-capture-nudge.py` asks for it).
- `knowledge/` holds reference facts that are not a procedure (a domain note, a decision record): flat topic files, no taxonomy.
- `INDEX.md` lists every `knowledge/` and `plans/` file. Do not maintain it by hand: run `python3 scripts/memory_index.py <memory dir>` (installed next to the other scripts) after adding, moving or finishing files; it rebuilds only its marked block, so hand-written notes stay.

### Promotion flow

1. A problem is resolved, the user corrects an approach, or a loaded skill was wrong.
2. Verify the fix (test/build/command passed, or the user confirmed).
3. Patch the first skill that fits: a skill loaded this session > an existing umbrella skill > a `references/<topic>.md` under it > a new skill.
4. Tell the user which skill changed.

## Rules

- Crystallize: 3+ files in the same domain sharing a keyword, consider one `knowledge/{domain}-pattern.md`.
- Never store secrets, credentials, or PII in any memory file or skill.
- Before marking a feature Done: the `ai-sdlc-task-progress.md` checkboxes are updated and reusable lessons are patched into their skill.
- Session handoff to another session: save to `$AODD_PLANS/<feature>/handoff.md`.
- Cross-reference with `[[relative/path/without/extension]]` only for a real relation between knowledge or plan files.
- Plan or progress status can be stale: before reporting a plan as in-progress or done, confirm with `git log main --grep=<feature>`.
- Never auto-delete or auto-archive without at least logging what was removed.

## Session search

Find context from earlier work without re-reading everything: first the skill that governs the task (its pitfalls), then `knowledge/` (grep it), then `plans/`.

| Situation | Search where |
|-----------|-------------|
| New task in a familiar domain | the governing skill + `knowledge/` |
| Bug looks familiar | `grep -ri "<symptom>" <memory dir>/knowledge` |
| A skill keeps failing | patch the skill (wrong rule: rewrite or delete it, do not append a contradicting one) |

## Context compression

When a session passes ~50 turns without resolution: summarize, do not truncate (keep the "why"), never delete anything not yet promoted to `knowledge/` or a skill, and archive before deleting.

## Verification

- [ ] No secrets/credentials stored in any memory file
- [ ] `memory_index.py` ran after adding or finishing knowledge/plans files

## Self-update

When the memory layout changes (a new file role, a new hook), edit this file and bump `version`.
