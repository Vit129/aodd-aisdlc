# Agent Memory Subagent Patterns

Use `agent-memory` as a utility-style subagent, not as the main reasoning agent.

## Why This Skill Fits Subagents

- The work is bounded and operational.
- The outputs are file-oriented and easy to verify.
- The task often appears as side work after the main task is done.
- The main agent should avoid spending context on housekeeping.

## When to Delegate vs Inline

| Condition | Action |
|-----------|--------|
| 5+ unprocessed lessons | Delegate to subagent |
| 3+ knowledge files same domain | Delegate to subagent |
| Simple append or single-file update | Do inline |
| Short session with no durable learnings | Skip entirely |

## Recommended Utility Subagents

### 1. `memory-curator`

Use when:
- A task or session just completed
- A useful lesson should be patched into the governing skill

Responsibilities:
- Read the session's notes and the skills used
- Propose the minimal updates needed
- Identify candidate lessons and the skill each one belongs in

Expected output:
- Short summary of changes
- Files to update
- Any follow-up questions only if strictly necessary

### 2. `memory-bootstrapper`

Use when:
- Starting a new project
- Resetting the memory structure
- Recreating missing memory files

Responsibilities:
- Create the base `agent-memory/` structure
- Ensure required files exist: `INDEX.md`
- Apply the standard templates from `references/templates/`
- Create `knowledge/`, `plans/` subdirectories

Expected output:
- Created file list
- Missing optional folders, if any

### 3. `knowledge-promoter`

Use when:
- A fix or pattern has been reused several times (3+)
- Multiple related lessons should be grouped into `knowledge/`
- 3+ promoted files share same domain (crystallization candidate)

Responsibilities:
- Create `knowledge/{topic}.md` with full detail for a repeated fact
- Detect domain clusters for crystallization
- Create `knowledge/{domain}-pattern.md` when 3+ files share domain + keyword
- Archive knowledge files unused for 30+ days (log what moved)

Expected output:
- Promotion candidates + actions taken
- Crystallization candidates + actions taken
- Archive candidates + actions taken

### 4. `skill-evolution-checker`

Use when:
- A skill was used successfully and the pattern might be missing from the skill file
- A proposal file is waiting for review

Responsibilities:
- Compare the approach used in this session with the skill file content
- If a novel, reusable, evidence-backed pattern is missing → propose the skill patch
- If the same gap shows up in 2+ sessions → recommend applying the patch

Expected output:
- Proposals created or recommended for auto-apply
- Rationale for each

## Invocation Pattern

Recommended flow:

1. Main agent finishes the primary task
2. Main agent spawns a utility subagent with a narrow scope
3. Subagent reads only memory files
4. Subagent returns a compact update plan or applies the scoped edits
5. Main agent verifies and resumes the primary thread

## Scope Rules

- Read scope: `agent-memory/**`
- Write scope: only the files requested or clearly implied by the task
- Never touch source code or unrelated project files
- Never store secrets, credentials, or PII

## Cost Guidance

Good value:
- End-of-session cleanup with 5+ unprocessed lessons
- Knowledge promotion/crystallization with 3+ files

Poor value:
- Short sessions with no durable learnings
- Running after every minor turn
- Using a subagent when a single append is enough

## Suggested Prompt Skeleton

```text
You are a utility subagent for the agent-memory system.

Task:
- Curate/update the memory files for this completed task/session.

Read first:
- the skill(s) used this session  ← patch targets for lessons

Constraints:
- Stay within agent-memory files and the skills used this session.
- Keep edits minimal and structured.
- Lessons go into skills, not into free-standing logs.
- Do not invent lessons that are not supported by this session.

Return:
- What changed
- Why it changed
- Any promotion/crystallization candidates
```
