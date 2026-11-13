# AI-SDLC Progress Spec — Task Breakdown & Progress Tracking

## Contents

- [Artifact locations](#artifact-locations)
- [Task granularity — vertical slices, not horizontal phases](#task-granularity--vertical-slices-not-horizontal-phases)
- [Task tags (dashboard view, not phases)](#task-tags-dashboard-view-not-phases)
- [Sensitive data classification (QA, before writing fixture data)](#sensitive-data-classification-qa-before-writing-fixture-data)
- [Mock strategy (QA, before writing mock/interceptor tasks)](#mock-strategy-qa-before-writing-mockinterceptor-tasks)
- [Progress file — required sections](#progress-file--required-sections)
- [File behavior](#file-behavior)
- [Resume protocol](#resume-protocol)
- [Incremental update rule](#incremental-update-rule)
- [Rollback protocol](#rollback-protocol)
- [When all tasks complete](#when-all-tasks-complete)
- [Lessons learnt](#lessons-learnt)

Mechanics behind ai-sdlc's core fact "track multi-step work in `ai-sdlc-task-progress.md`
(or legacy `dev-task-progress.md`/`qa-task-progress.md`), vertical slices not phases."
When breaking work into tickets, format the tasks directly into the vertical-slice checkbox structure documented
below. Load this file when actually breaking a design into tasks.

## Artifact locations

- **AI-SDLC Feature Tracking** — everything under `$AODD_PLANS/[FEATURE]/` (default `~/.aodd/plans/[FEATURE]/`):
  - `ai-sdlc-task-progress.md` (this IS the unified implementation & verification plan — no separate Dev vs QA tracking files; legacy `dev-task-progress.md`/`qa-task-progress.md` remain supported).
  - Design & Architecture: `[FEATURE]-architecture.md` (or `[FEATURE]-architecture/`, legacy `design.md`), test script skeletons under `test-scripts/`.
  - Handoff notes: `handoff.md`.
- **QA Test Suite Artifacts** — under the project's `tests/` tree, never under `$AODD_HOME`: scenarios under
  `tests/test-scenario/[system]/[feature]/`, automation under `tests/{api,web,mobile}-testing/.../[system]/[feature]/`,
  shared fixtures under `tests/shared-fixtures/[system]/[feature]/` when platforms combine.

## Task granularity — vertical slices, not horizontal phases

- Each task cuts through every layer it touches (schema, API, UI, tests) for one demoable
  piece of behavior — not "all the schema work" then "all the API work" as separate tasks.
  A task that can't be demoed end-to-end on its own is too horizontal.
- Genuine blocking dependency is stated explicitly on the blocked task
  (`- [ ] Task 4 — blocked by Task 2`). Unblocked tasks can run in any order, including in
  parallel by different sessions/agents.
- Large blast-radius refactors (schema migrations, renames touching many callers) use
  expand-contract as their own slice: add the new form → migrate call sites in batches →
  remove the old form. Don't collapse this into one giant task.
- Tasks should be completable in 1-2 hours.
- A ticket may carry three optional lines under its heading: `Agent: claude | agy | codex`, `Model: <name>`, and `Effort: low | medium | high | xhigh | max`. A missing line takes the default in `rules/ai-sdlc/delegation.md` § Effort ladder. Set `xhigh` or `max` here only on purpose, never by the agent.

## Task tags (labels, not phases)

Tag each task with the track(s) it touches, in brackets after the checkbox. Tags never license planning
"all Backend tasks" as a phase before touching Frontend; the task list stays vertical slices.

**Dev** — use only tags that apply to the project type:

| Tag | Traditional (REST+SQL) | Serverless | Spreadsheet-backed | Frontend-only |
|---|---|---|---|---|
| `[Infra]` | DB migrations, broker config | NoSQL collections, function config | Spreadsheet tab structure | LocalStorage schema |
| `[Backend]` | DTOs, Repository, Service, Controller | NoSQL collections, triggers | GAS doGet/doPost | N/A (skip) |
| `[Frontend]` | Components, Pages, State, API integration | Same | Same + LocalStorage sync | Components, Pages, State |

Most real tasks carry `[Backend][Frontend]` together (or `[Infra]` too) because they're
vertical slices, e.g. "Order confirmation flow" touches the endpoint AND the screen in one
task. A schema migration that has to land before any slice can start is its own
`[Infra]`-only task, explicitly marked `blocked by` on later tasks.

**QA** — tag by platform:

| Tag | Playwright (API) | Playwright (Web UI) | Robot Framework (Mobile) |
|---|---|---|---|
| `[Infra]` | DB config, .env, fixtures | Same + storageState | Appium config, .env, YAML fixtures |
| `[Shared]` | AuthService, API helpers, DB service | Same + storageState login | Python DB helpers, API helpers |
| `[PageObject]` | N/A (use helpers) | NavigationPage, FeaturePage | FeaturePage.robot |
| `[Script]` | feature.spec.ts (per scenario) | Same | feature.robot (per scenario) |
| `[Pipeline]` | package.json scripts, pipeline YAML | Same | robot commands, pipeline YAML |

A `[Script]` task that calls a Page Object states `blocked by` that Page Object's task —
never implied by "Page Objects come before scripts" as a blanket phase rule.

## Sensitive data classification (QA, before writing fixture data)

| Classification | Location | Examples |
|---|---|---|
| Sensitive → `.env` | `process.env.X` | credentials, tokens, passwords, login emails, API keys |
| Encrypted → fixture (plain text) | hardcoded plain text | PDPA fields, health data, PII — DbService encrypts/decrypts |
| Non-sensitive → fixture file | hardcoded in `.ts`/`.yaml` | companyCode, customerCode, invoiceNumber |

`process.env.X` in a fixture is allowed ONLY for sensitive fields — business data must be
hardcoded in the fixture file, never read from `.env`.

Encrypted fields (PDPA, health data, PCI-DSS) — fixture holds plain text (DbService
encrypts/decrypts on insert/verify), except PCI-DSS fields which must be masked
(`****1234`) in the fixture, never plain text.

## Mock strategy (QA, before writing mock/interceptor tasks)

| Dependency | Mock type | Success | Edge case |
|---|---|---|---|
| External API | `page.route()` interceptor | fixture JSON | slow (>5s) → cached + warning |
| External API (5+ endpoints) | HAR replay (`routeFromHAR`) | recorded responses | service down → auto-fallback |
| Third-party service | mock service class | stub data | unavailable → fallback to fixture |
| DB (brownfield) | real DB + `TEST_` prefix | real data | conflict → skip with warning |

HAR vs `page.route()`: HAR when there are 5+ endpoints, backend isn't ready, or CI needs to
run offline; `page.route()` when a specific error response or dynamic per-test-case
response is needed.

Auth/security mocks: real encryption library in test env when validating encrypt/decrypt
itself; mock response when testing business logic, not the security layer. Never mock an
auth token — always get a real one from the login flow. Never hardcode an API key — always
`process.env`.

## Progress file — required sections

```markdown
# AI-SDLC Task Progress — {Feature Name}
Last updated: {YYYY-MM-DD HH:mm}
Status: In Progress | Completed

## Context
- System: {SYSTEM_KEBAB}
- Feature: {SYSTEM_FEATURE_KEBAB}

## SDLC Workflow Gates (not domain/business approvals — those belong in the feature's own data model)
- [ ] Gate 1 (Architect design) — approver: {name}, scope: {what was approved}, {YYYY-MM-DD HH:mm}
- [ ] Gate 2 (Scenario list) — approver: {name}, scope: {what was approved}, {YYYY-MM-DD HH:mm}
- [ ] Gate 3 (Seam agreement) — approver: {name}, scope: {seams agreed}, {YYYY-MM-DD HH:mm}

## Artifacts
- Architecture / Design: $AODD_PLANS/[FEATURE]/[FEATURE]-architecture.md

## Tasks
- [ ] [Infra] Storage setup — migration/schema/env config
- [ ] [QA-Skeleton] [TS-0001] Stub test scenario skeleton (RED)
- [ ] [Backend][Frontend] {vertical slice} — implement against [TS-0001]
  - [ ] ✅ Run test scripts (verify GREEN)

## Integration & Review
- [ ] End-to-end wiring across all slices
- [ ] ✅ Run all test scripts / full test scenario suite (verify GREEN)
- [ ] Pre-merge code review (Standards + Spec)
```

Combined tags can be used across Dev and QA (`[Infra]`, `[Backend]`, `[Frontend]`, `[QA-Skeleton]`, `[QA-Verify]`, `[Performance]`, `[Shared]`, `[PageObject]`, `[Pipeline]`). A Performance Testing task can be added optionally after all core tasks pass.

## File behavior

- 1 feature = 1 progress file; reuse it in place (`[x]` in place, not a new file per session).
- Rerunning the same feature from scratch → archive the existing file as `{name}.v{N}.md`.

## Resume protocol

Resume ("ทำต่อ" / "continue") = read the feature's progress file and continue.

1. Read the progress file; verify every path in `## Artifacts` still exists. If one is missing, warn before resuming.
2. If `handoff.md` exists next to it, read it before anything else.
3. Find the first `[ ]` task and resume there.

**Writing `handoff.md`** (when stopping mid-feature, the user asks for a handoff, or context is about to run out): overwrite `$AODD_PLANS/[FEATURE]/handoff.md` with
- **State:** phase, current task, branch/worktree, last green command
- **Tried:** what was attempted and why it failed (error text), so it is not retried
- **Next:** the exact next step
- **Open:** decisions waiting on the user, files to open first
Keep it under 30 lines; delete it once the feature is Done.

## Incremental update rule

After every completed task, mark its `[x]` and update the `Last updated` line, in real time, never batched at the end. Stale
progress files make a resumed session redo finished work.

## Rollback protocol

| Situation | Action |
|---|---|
| Task fails (test doesn't pass) | Mark ❌, note root cause, fix before proceeding |
| Dependent task breaks because task A broke | Re-sequence: fix A first, re-run B |
| Architecture assumption was wrong | Escalate to re-design, then re-plan affected tasks |
| Multiple tasks break at once | Stop, assess scope, re-break-down |

Never mark a task ✅ while its test is still failing — completion means GREEN.

## When all tasks complete

Run the full suite one final time and record pass/fail. **Dev only** — run
code review (via `/code-review` or any review skill you have)
against the full diff before committing; don't commit with Critical/Important
findings unresolved.

## Lessons learnt

Before creating tasks, check the project's own notes and the loaded skills' Pitfalls
sections for known gotchas on the components you will touch. Lessons learned in this
feature go into the governing skill (`docs/skill-learning.md`), not a loose notes file.
