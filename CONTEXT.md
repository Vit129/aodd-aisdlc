# Context

Terms used across this repo, as defined by `rules/ai-sdlc-workflow.md`.

- **AODD (AI Orchestrator Driven Development):** the operating contract in `rules/ai-sdlc-workflow.md`: a human decides, the main agent orchestrates, and an independent auditor checks Done claims on request.
- **CEO / judge:** the human who approves plans, makes executive calls and decides on merges, deploys and irreversible actions.
- **Chief of staff:** the main agent (or the `chief-of-staff` skill) that owns a brief end to end and reports one result.
- **Triage:** the three-row gate at the top of `rules/ai-sdlc-workflow.md`: a question, a file change (which picks a path), or an action that needs the CEO first.
- **Auditor:** the independent `auditor` agent that re-checks the evidence for a Done claim. Only Medium+ work is audited. Its FAIL or DISPUTED verdict is reported as it is.
- **Advisor:** the second-opinion agent (Fable or Opus) for a hard or irreversible decision.
- **ai-sdlc:** the Dev/QA feature workflow every change runs through; only its requirement path has the approval gates. A gate is passed only on an explicit answer, never on silent consent.
- **Done gate:** the `done-gate` hook, which blocks a Done claim while the task progress file has unchecked boxes, and relays a non-PASS audit verdict.
- **Test-Before-Deliver:** no task is complete until the build and the relevant tests have run; a green test run alone is not proof of a passing build.
- **Git ops runner:** the cheap-model routine for git and ops mechanics (status, staging by path, commit, push, PR); the main session decides what to commit (`rules/ai-sdlc/git-ops.md`).
- **Skill learning:** the procedure that turns a correction or a fix into a patch on the governing skill (`docs/agents/skill-learning.md`).
- **Installed copy:** the files `install.sh` copies into an agent home. Never edit the installed copy; change the source here.
