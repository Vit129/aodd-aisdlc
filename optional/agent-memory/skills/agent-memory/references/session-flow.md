# Session Flow

Entirely agent-driven during a live session; no hook runs it.

```text
Session Start
  → If the task looks familiar, grep knowledge/ and read the governing skill
  → Proceed with the user's request

Mid-Session Work
  → Problem resolved → patch the governing skill (Promotion flow in SKILL.md)

Skill Evolve
  → A task reveals a skill is missing a good pattern or has a wrong rule:
    patch the skill directly (verified, versioned), see docs/skill-learning.md

Knowledge Curation (when warranted, not every session)
  → 3+ knowledge files, same domain + keyword → consider crystallizing into {domain}-pattern.md
  → unused / oversized / overlapping skills → review them with the agent-ops skill
```

## Meaningful changes (worth updating memory for)

- A new decision (knowledge/ or the governing skill)
- A resolved problem (patch the governing skill)

Skip when the session was only Q&A, comparison, research, exploration without decisions, or reading files without changes.
