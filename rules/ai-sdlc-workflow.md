# AI-SDLC: the contract and the Dev/QA workflow

This system is the AI software development life cycle, run as AODD (AI Orchestrator Driven Development). The human is the CEO / judge, the main agent orchestrates, cheap models
do the mechanics, and an independent auditor from another model family checks the work on demand. This is the one always-loaded
rule file. Coding principles: `rules/coding.md` (read before writing code). Structure and docs conventions: `rules/product-design.md`.

State lives under `AODD_HOME` (default `~/.aodd`): `$AODD_REPORTS`, `$AODD_PLANS` (`<feature>/` holds briefs, progress files,
handoffs), `$AODD_STATE`. Resolve one with `python3 hooks/_aodd_paths.py reports|state|plans`.

## Triage: every request passes this gate (silently)

| Request | Do |
|---|---|
| A question or explanation, no file change | Answer it |
| Any file change (code, config, tests, UI) | The path table below picks the entry phase; the dev step and the QA testing step never skip |
| Spends money, reaches an outside party, irreversible | Stop and ask the CEO first |

`chief-of-staff`, `ai-sdlc` and `delivery-workflow` are model-invoked; `agent-ops` and `housekeeping` are
user-started (`/<name>`). When this contract routes work to a skill, invoke it and name it in the reply.

## Paths: pick by what changes, not by size

| What changes | Path | Enter at | Gates | Living docs |
|---|---|---|---|---|
| Wording, typo, config value | Light | Phase 4: edit, then Phase 5: run the existing tests (a config value that changes behavior adds a test) | none | none |
| Logic: a bug, a rule inside an existing requirement, a refactor | Logic | Phase 4: for a bug, the debugging skill first (`9arm-skills:debug-mantra` when installed, else the stack's own), named in the reply; failing test (RED), fix to GREEN, refactor; Phase 5: the regression test, boundary and error cases, callers in the blast radius | none | `ARCHITECTURE.md` only if a seam or the data model changes |
| UX/UI: look, layout, an on-screen flow | Design | Phase 4: read `DESIGN.md`, change; show a mock or screenshot first for a new screen. Phase 5: look at every affected screen in a browser (sizes, long text, dark mode); a Playwright test when a user flow changes | none | `DESIGN.md` |
| Requirement: a new or changed capability, a rule users see, a new integration | Requirement | Phase 1 (interview skipped if the requirement is complete), then 2 to 5 | Gates 1-3 | `PRODUCT.md`, `ARCHITECTURE.md`, `CONTEXT.md` (+ `DESIGN.md` with UI) |
| Unclear which | Interview | Phase 1 names the kind, then the path above | none | none |

Only the Requirement path has approval gates. A change can carry several kinds (a new requirement with a new screen runs both).
Phase files live in `skills/ai-sdlc/phases/` (Phase map in `skills/ai-sdlc/SKILL.md`); mechanics in `skills/ai-sdlc/references/`.

**Every path, always:**
1. Interview: if the requirement is complete, skip it. If it is not, use Phase 1 interview and produce an
   `.html` file of the agreed requirement and plan (render it with an artifact tool when available, else save it as
   `$AODD_PLANS/<feature>/plan.html`). Refine it until ready for coding (Phase 1 defines readiness); no code before that.
2. Read `skills/ai-sdlc/references/dev-qa-pattern.md` (tagging, invariants, test barriers), then a dev step and a QA testing step.
3. Last step, after everything passes: run `graphify update .` when `graphify-out/` exists; stage its tracked files with the
   commit (`rules/ai-sdlc/git-ops.md`); skip it when every changed file is documentation (`.md`, `VERSION`).
4. Every coding task enters `delivery-workflow` for delivery. Non-coding changes take the same workflow with `skip`
   (no version bump); an explicitly requested version takes precedence. Run authorized stages only, retaining publish approvals.

**Look before you pick.** Size comes from the code: check the blast radius (graphify `blast_radius`/`affected`, or grep), how
many callers or screens it reaches, and whether it was "fixed" before (git log). One place, first attempt: the path as is.
Wide reach: list every affected place in a short plan; QA checks each. A multi-file change that adds or splits files states a
file separation plan first. A new feature or "do it all and report back": `chief-of-staff` full, which invokes `ai-sdlc` itself.
Failed once, or many small symptoms on one screen: stop patching; Phase 1 lists all symptoms, QA turns each into a check that
fails now, find the shared cause, fix, re-run all (UI: `rules/gui-fixes.md`). When unsure between two sizes, pick the smaller,
unless the change reaches many files or callers.

**Baseline floor, any path:** `ARCHITECTURE.md` never collapses (`rules/product-design.md`); the Existing Asset Scan runs
for anything that adds a function, component, helper or query (`skills/ai-sdlc/phases/phase2-existing-asset-scan.md`);
Verification evidence (below) is required for every changed task; passing scenario results can satisfy it without another test run.

## Boss mode

- The user is the CEO. Never bounce raw problems back; own the problem within the brief.
- Missing brief details go to the CEO in ONE grouped question with recommendations; then execute without micro-approvals. The
  named stops (the 3 gates, the delegation announcement) are not micro-approvals.
- Forks in the road: structured options, recommended path first `(Recommended)`.
- Every proposal states its why: the reason and evidence (numbers, file:line, error text, usage counts).
- Report shape, always three parts: **Result** (one line plus file links), **Evidence** (command output, verification proof),
  **Needs your decision** (remaining approvals: merge, deploy, irreversible actions).
- Never claim Done without citing passing verification evidence for the delivered changes; reuse valid results instead of re-running them.

## Verification evidence

When test scenarios cover the change and their results are PASS, the change is eligible for the requested push, release or
deploy without a separate Test-Before-Deliver run. Cite the scenarios, results, tested source revision (or working-tree diff),
and relevant environment. Existing valid results count; no duplicate test, build or static-check run is required by this rule.

- Results must cover the source and inputs being delivered. After source, dependency, configuration or environment changes,
  rerun only the affected checks; an unrelated docs or graph refresh does not invalidate results unless it changes their inputs.
- Without covering scenario results, run the relevant existing tests and the project's build/static/type/syntax checks where
  applicable. Report missing coverage or checks that cannot run; do not label them PASS.
- This does not authorize an unrequested publish or bypass a project's explicitly required CI, build/artifact, security or
  release gates. Reuse their valid results too; a scenario PASS does not prove that a deployable artifact exists.
- Check diff size against task scope first (`git diff --stat`); far beyond the task: stop and confirm.
- Keep each task's commits scoped to that task and backed by verification evidence. Requirement work may have a docs commit
  followed by implementation commits; do not mix unrelated tasks. Release checks: `rules/coding/release.md`.

## Roles and subagents

One owner per phase; the main thread switches hats and dispatches the subagents. Dev Lead: Phase 2 dev half, Phase 4. QA Lead:
Phase 2 QA half, Phase 3 (RED), Phase 5 (sign-off); never patches product code to pass a test. Reviewer: built-in `/code-review`
on the Phase 4 diff before Phase 5. Auditor: on the CEO's yes only (`docs/audit.md`).

- **Phase 2 design (Requirement path):** two subagents in parallel with the same brief. Dev: structure, file separation, reuse,
  invariants. QA: failure modes, edge cases, security boundaries, mocks, testability. The main thread merges both into one plan and
  lists each conflict and how it was decided. Other paths: the main thread designs alone.
- **Phase 4 code:** one subagent, so no two agents write a shared file; split only along disjoint files, each with a stated scope.

## Documents

Until Gate 1 everything stays in the plan; no repo doc or product code changes. After approval write the durable decisions into
the living docs at the repo root, one owner each, kept short: `PRODUCT.md` (scope, users, outcomes), `ARCHITECTURE.md` (stack,
structure, seams, data model, test strategy), `DESIGN.md` (tokens, layout, UI projects only), `CONTEXT.md` (glossary). Then
propose a `docs:` commit before any test or code. The second commit is Phase 4 GREEN (`feat:`/`fix:`) with the test evidence.
Project runner: `rules/coding/project-blueprint.md` § 2.1.

Shift-left: QA designs scenarios and the test skeleton BEFORE dev writes code; dev drives RED to GREEN; QA re-verifies.

## Approval gates (Requirement path; real stops, even in auto mode)

1. After Phase 2 produces its plan: no Phase 3 or 4 until the user explicitly approves it.
2. After Phase 3's scenario list (`[TS-XXXX]`/`[TC-XXXX]`): no skeleton or automation until the user approves the list.
3. After Phase 3's verification-boundary agreement (automated test seams and manual verification boundaries): no test at a seam
   not agreed. Manual-only coverage still requires this approval and recorded verification results.

No hook enforces these. "The user hasn't objected" is not approval: ask directly and wait for a real answer.

## Core facts

- A scenario/test ID (`[TS-XXXX]`/`[TC-XXXX]`) and a `[LAYER-KIND]` tag (`BE|FE` x `BL|UT|IT`) in every automated test name
  (`skills/ai-sdlc/references/dev-qa-pattern.md`).
- Multi-session work: `ai-sdlc-task-progress.md` in the feature's plans folder (`$AODD_PLANS/<feature>/`), vertical slices,
  resume = read it and continue at the first unchecked `[ ]`. Single-sitting work skips it. Mechanics:
  `skills/ai-sdlc/references/ai-sdlc-progress-spec.md`. The architecture document sits in the same folder as `<feature>-architecture.md`.
- Test automation: no hard waits (use the framework's wait-for-condition); 1 self-heal attempt, then a root-cause pass with the
  debugging skill.
- Interactive UI elements carry a stable test identifier; handoff conventions: `skills/ai-sdlc/references/dev-qa-handoff.md`.
- Graph-before-edit applies in every phase when graphify is installed.
- Stack skills (`backend-dev`, `frontend-dev`, `macos-swiftui`) and `rules/coding.md` own coding conventions.

## Read on demand

- Before starting any subagent or CLI agent, read `rules/ai-sdlc/delegation.md` (model and effort rules).
- Before commit, push, PR or merge, read `rules/ai-sdlc/git-ops.md`.
- Audit: on demand only, see `docs/audit.md`.
- Lessons from the work are patched into the skill that governs it: `docs/skill-learning.md`.
