# Context

Terms used across this repo, as defined by `rules/aodd.md` and `rules/ai-sdlc-workflow.md`.

- **AODD (AI Orchestration Driven Development):** the operating contract. The human is the CEO and judge; the main agent is the chief of staff; cheap models do the mechanics; an independent auditor from another model family checks every claim of Done.
- **CEO / judge:** the human who approves plans, makes executive calls and decides on merges, deploys and irreversible actions.
- **Chief of staff:** the main agent (or the `chief-of-staff` skill) that owns a brief end to end and reports one result.
- **Triage size:** Small (just do it), Small logic (one-line fix with a micro Done), Medium (multi-file, audited), Large (new feature, audited, may invoke ai-sdlc). Unsure: pick the smaller size.
- **Auditor:** the independent `auditor` agent that re-checks the evidence for a Done claim. Only Medium+ work is audited. Its FAIL or DISPUTED verdict is reported as it is.
- **Advisor:** the second-opinion agent (Fable or Opus) for a hard or irreversible decision.
- **ai-sdlc:** the full Dev/QA feature workflow with three approval gates. A gate is passed only on an explicit answer, never on silent consent.
- **Done gate:** the `done-gate` hook, which blocks a Done claim while the task progress file has unchecked boxes, and puts the audit question to the user once when none ran.
- **Test-Before-Deliver:** no task is complete until the build and the relevant tests have run; a green test run alone is not proof of a passing build.
- **Haiku ops runner:** the cheap-model routine for git and ops mechanics (status, staging by path, commit, push, PR); the main session decides what to commit.
- **Skill learning:** the procedure that turns a correction or a fix into a patch on the governing skill (`docs/agents/skill-learning.md`).
- **Installed copy:** the files `install.sh` copies into an agent home. Never edit the installed copy; change the source here.
