# Self-Review Rubric

Rubric-based evaluation for deciding what's worth saving to memory — not free-form judgment.
Apply this yourself during or at the end of a task; nothing runs it automatically.

## When to Apply This

- After a task resolves a real problem
- At session end, if anything worth capturing happened

## What to Review

| Item | Source | Decision |
|------|--------|----------|
| Problem resolution | Current session context | → Patch the governing skill if the Save Rubric below scores it |
| Skill performance | Tool outputs + results | → Patch the skill (wrong rule → rewrite it) |
| Knowledge gap | Missing pattern that would have helped | → Add it to the governing skill |

## Save Rubric (before patching a skill)

Score the resolved problem on 3 criteria (yes/no):

| # | Criterion | Question |
|---|-----------|----------|
| 1 | **Novel** | Is this a new pattern not already in the skill, or knowledge? |
| 2 | **Recurrent** | Could this problem happen again (not a one-off typo)? |
| 3 | **Non-trivial** | Did it take >1 attempt to solve, or would it waste >5 min next time? |

**2/3 or better → patch the skill (`docs/skill-learning.md`). Otherwise → don't bother.**

## Skill Flag Rubric

After a task that used a skill, evaluate it:

| Signal | Action |
|--------|--------|
| Output has errors requiring rework | Patch the skill step that caused it (pitfall + how to check) |
| Output is correct | No action (usage is counted by `skill_learning_report.py`) |

## Skill Improvement Rubric

After a task, evaluate if a skill could be improved:

| Signal | Score | Action |
|--------|-------|--------|
| Skill was loaded but missing a pattern that would have helped | High | Patch the skill now |
| Skill has outdated info that caused confusion | High | Rewrite that rule in place now |
| Skill worked perfectly | — | No action |
| Minor style preference | Low | Skip — not worth a proposal |

**Proposal threshold:** Only propose if the improvement would save 5+ minutes on next occurrence.

## Constraints

- **Max 1 proposal per skill per session:** prevents spam
- **Evidence required:** every proposal must cite the specific moment/output that triggered it

## Anti-Patterns

- ❌ Free-form "should I save this?" — use the rubric
- ❌ Saving every minor observation — gate with the 2/3 criteria
- ❌ Proposing skill changes without evidence — cite the failure
- ❌ Flagging skills for style preferences — only flag for functional failures
