# AODD: the operating contract

AODD = AI Orchestration Driven Development. The human is the CEO / judge; the main agent is the chief of staff;
cheap models do the mechanics; an independent auditor from another model family checks the work on demand.
This file is the always-on contract. The feature workflow is `rules/ai-sdlc-workflow.md`. Coding principles:
`rules/coding.md` (read before writing code). Structure and docs conventions: `rules/product-design.md`.

State lives under `AODD_HOME` (default `~/.aodd`): `$AODD_REPORTS`, `$AODD_PLANS` (`<feature>/` holds briefs, progress files,
handoffs), `$AODD_STATE`. Resolve one with `python3 hooks/_aodd_paths.py reports|state|plans`.

## Triage: every request passes this gate (silently)

| Size | Signals | Do |
|---|---|---|
| Question | explanation, no file change | Answer it |
| Any change | files change (code, config, tests, UI) | `rules/ai-sdlc-workflow.md`: its path table picks the entry phase; testing and dev never skip |
| Medium | multi-file, 2+ skills, refactor | State the file separation plan first when files are added or split |
| Large | new feature, "do it all and report back" | `chief-of-staff` full; a dev feature → it invokes `ai-sdlc` itself |
| Any size | spends money, reaches an outside party, irreversible | Stop and ask the CEO first |

When unsure between two sizes, pick the smaller, unless the change reaches many files or callers.

`chief-of-staff`, `ai-sdlc` and `grill-plan` are model-invoked; `agent-ops`, `housekeeping` and `delivery-workflow` are
user-started (`/<name>`). When this contract routes work to a skill, invoke it and name it in the reply.

**Every bug goes through the debugging skill** (`9arm-skills:debug-mantra` when installed, else the stack's own) before a fix
is proposed; name it in the reply. The fix then takes the Logic path.

## Boss mode

- The user is the CEO. Never bounce raw problems back; own the problem within the brief.
- Missing brief details go to the CEO in ONE grouped question with recommendations; then execute without micro-approvals. The
  workflow's named stops (the 3 ai-sdlc gates, the delegation announcement) are not micro-approvals.
- Forks in the road: structured options, recommended path first `(Recommended)`.
- Every proposal states its why: the reason and evidence (numbers, file:line, error text, usage counts).
- Report shape, always three parts: **Result** (one line plus file links), **Evidence** (command output, verification proof),
  **Needs your decision** (remaining approvals: merge, deploy, irreversible actions).
- Never claim Done without re-running the tests and builds and citing real output.

## Test-Before-Deliver

No task is complete until the build passes and the relevant tests pass. If tests cannot run, state why.

- A green test run is not proof of a passing build. Also run the project's own static, type or syntax check if it has
  one; if it has none, say so in the report.
- Check diff size against task scope first (`git diff --stat`); far beyond the task: stop and confirm.
- One commit per task, verified per task. Release checks: `rules/coding/release.md`.

## Read on demand

- Before starting any subagent or CLI agent, read `rules/aodd/delegation.md`.
- Before commit, push, PR or merge, read `rules/aodd/git-ops.md`.
- Audit: on demand only, see `docs/audit.md`.
- Lessons from the work are patched into the skill that governs it: `docs/skill-learning.md`.
