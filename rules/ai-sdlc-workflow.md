# AI-SDLC — Dev/QA Workflow Spine

## Contents

- [Approval Gates (mandatory when the full shape is running)](#approval-gates-mandatory-when-the-full-shape-is-running)
- [Core facts (non-negotiable, not model-inferable — everything else is judgment)](#core-facts-non-negotiable-not-model-inferable--everything-else-is-judgment)
- [Phase 1 — Interview](#phase-1--interview)
- [Phase 2 — Architect (Dev + QA combined)](#phase-2--architect-dev--qa-combined)
- [Phase 3 — QA-Design (scenario + skeleton, RED)](#phase-3--qa-design-scenario--skeleton-red)
- [Phase 4 — Dev (implement to GREEN)](#phase-4--dev-implement-to-green)
- [Phase 5 — QA-Verify (confirm GREEN)](#phase-5--qa-verify-confirm-green)
- [Status](#status)

Lean AI-SDLC spine — interview → architect (dev+qa) → qa-design (scenario+skeleton,
RED) → dev (implement to GREEN) → qa-verify (confirm GREEN). Mandatory shape for work
that genuinely needs QA coverage; depth per phase, and which phases even apply, is
model judgment. This page carries the workflow shape; mechanics too dense to inline
live in `skills/ai-sdlc/references/` — `ai-sdlc-progress-spec.md` (task
tracking), `dev-qa-handoff.md` (dev↔QA handoff), `ai-sdlc-workflow-guide.md`
(execution guide), `qa-automation-loop.md` (self-heal/reporting).

**Roles (AODD JD — one owner per phase; the main thread switches hats, they are not subagents):**

| Role | Owns | Out of scope | KPI |
|---|---|---|---|
| Dev Lead | Phase 2 dev half (design, Existing Asset Scan), Phase 4; dispatches stack-specific skills if you have them, mechanical pieces to Haiku | Writing scenarios; declaring QA pass | Phase 5 failures sent back to Phase 4 |
| QA Lead | Phase 2 QA half, Phase 3 (RED), Phase 5 (GREEN sign-off); dispatches your scenario, test-framework and performance skills if you have them | Patching product code to make a test pass | Defects found after Phase 5 sign-off |
| Reviewer | Built-in `/code-review` on the Phase 4 diff before Phase 5 | — | — |
| Auditor | `scripts/audit.py` after Phase 5 (cross-family, writes its own report): re-checks evidence vs. the brief, reports to the CEO | Fixing | Defects after audit PASS |

Each role follows the same SOP: read brief + progress file → ask once, everything at once → do →
check vs. Definition of Done → hand back to the next owner via the progress/handoff file → leave the record (checkbox).

**Shift-left:** QA scenario/test-skeleton design happens BEFORE dev writes
implementation code — dev implements against a known RED state and drives it to
GREEN, QA re-verifies GREEN at the end. TDD applied at the feature level, not just
the unit level.

**Task Sizing & Phase 2 Architect Enforcement (Small vs. Medium vs. Large):**
- **Small tasks (1-5 line fix, typo, single clear bug, direct question)**: Ceremony collapses skips straight to Architect (one sentence) → Dev → done — no `[TS-XXXX]` scenario, no tracked `ai-sdlc-task-progress.md`, no automation skeleton, none of the 3 approval gates.
- **Medium tasks (multi-file change, new component/helper, refactoring a module, state/API changes, QA test suites)**:
  - **Phase 2 Architect is mandatory:** state the file separation plan before touching code or tests (split by responsibility, e.g. UI, flow, pure logic, integration, config, types, data; one file per concern, no monolith). QA ceremony (TS-XXXX / gates) can stay light.
- **Large tasks (new full feature, cross-service flow)**: Full `/ai-sdlc` shape with all 5 phases and 3 approval gates.

**Four independent baseline rules — a floor, not a free pass (single authoritative version — other files point back to this list):**
1. **Ceremony collapses ONLY for Small tasks.** Medium and Large tasks require architectural separation before coding.
2. **ARCHITECTURE.md never collapses.** Every project gets one regardless of task
   size. This is a standing
   per-project artifact, not a per-task ceremony step, so it isn't something a small
   task "skips": if the project doesn't have one yet, this is where it gets created
   (one bullet is enough), collapsed task or not.
3. **The Existing Asset Scan never collapses** for any task that adds a new
   function/component/helper/query. § Existing Asset Scan (Phase 2) and its
   Reuse-Table/Nth-Occurrence rule run regardless of task size — exempt only when
   there's genuinely nothing to scan (a single-line edit to an existing line).
4. **Verification never collapses.** `rules/aodd.md`'s Test-Before-Deliver (build
   passes + relevant tests pass) is a baseline outside this file's
   phase shape — every task runs it regardless of what collapsed.

## Approval Gates (mandatory when the full shape is running)

Three checkpoints carry a real hard stop — everything else stays Auto Mode default
(don't stop to ask). These three have a uniquely expensive undo: get one wrong and
everything built on top of it gets thrown away.

1. **After Phase 2 (Architect) produces its design/implementation plan** — do not start
   Phase 3 or Phase 4 until the user has explicitly approved it. A wrong architecture
   discovered after Dev has built against it means redoing the build, not just the doc.
2. **After Phase 3's scenario list is written** (the `[TS-XXXX]`/`[TC-XXXX]`
   output of your scenario skill or tool) — do not move on to skeleton/automation until the
   user has explicitly approved the scenario list. A wrong scenario found after
   automation is built against it means rewriting the automation, not just the list.
3. **After Phase 3's seam/automation-architecture agreement** (which public seam —
   API endpoint, function, UI element — each scenario tests at, and how the automation
   is structured) — write no test at a seam not explicitly agreed to. A real HITL gate,
   not a formality.

No mechanical hook enforces these — treat "the user hasn't objected" as different from
"the user approved"; ask directly and wait for a real answer before crossing the gate.

## Core facts (non-negotiable, not model-inferable — everything else is judgment)

- QA scenario/test ID (`[TS-XXXX]`/`[TC-XXXX]`) in every automated test name — the only
  link between a scenario, its automation, and any tracker. Without it, nothing traces.
- Scenario/test titles also carry a `[LAYER-KIND]` tag (`BE|FE` × `BL|UT|IT`, e.g. `[BE-BL]`) — layer/kind
  definitions and Dev + QA rules → `skills/ai-sdlc/references/dev-qa-pattern.md`.
- Multi-step/multi-session work: track in `$AODD_HOME/plans/[FEATURE]/ai-sdlc-task-progress.md`
  (legacy `dev-task-progress.md`/`qa-task-progress.md` supported), vertical slices not phases, resume at first unchecked `[ ]`.
  Skip entirely for single-sitting work. Full mechanics (tags, sensitive-data/mock rules,
  rollback, resume protocol) → `skills/ai-sdlc/references/ai-sdlc-progress-spec.md`.
- Project/Feature Architecture Planning: the architecture document always goes in `$AODD_HOME/plans/[FEATURE]/[FEATURE]-architecture.md` (or `[FEATURE]-architecture/`), next to `ai-sdlc-task-progress.md` and the feature's other artifacts, never scattered.
- Test automation: zero hard waits — whatever fixed-delay primitive the framework in
  use offers is forbidden, use its wait-for-condition primitive instead. 1 self-heal attempt max then
  route to a root-cause debugging pass (`9arm-skills:debug-mantra` if installed) — both are anti-flakiness facts, not
  code-quality opinions a model would guess.
- Interactive UI elements carry a stable test identifier (`data-testid` etc., naming
  convention fixed once per project) — a
  contract QA automation depends on existing, not something to rediscover per task. Full
  dev→QA handoff conventions (testid map, test-env requirements, schema consistency,
  DB strategy) → `skills/ai-sdlc/references/dev-qa-handoff.md`.
- Graph-before-edit (if graphify is installed) and surgical changes (no drive-by refactors) apply in every phase.
- **Skill visibility + Self-Update, every phase:** name every skill invoked in the response text — never call one silently. Every
  skill learns the same way: when a phase hit a correction, a gotcha, or a
  wrong/missing step in the invoked skill, and the fix was verified, patch that skill's
  `SKILL.md` (or its `references/`) in place and bump `version`/`last_improved` — see its
  `## Self-Update` section and `docs/skill-learning.md`.
  A phase's attention being on the workflow doesn't excuse skipping whichever loop the
  invoked skill actually uses. Log which skill(s) ran in each phase into
  `ai-sdlc-task-progress.md` per
  `skills/ai-sdlc/references/ai-sdlc-progress-spec.md`'s Skill Invocation Log.

## Phase 1 — Interview

`mattpocock-skills:grilling` and `mattpocock-skills:research` can be called directly via the
Skill tool. `to-spec`, `to-questionnaire`, and `grill-with-docs` are configured
`disable-model-invocation` in this plugin — only the user can run
`/to-spec`/`/grill-with-docs` themselves; calling them via the Skill tool fails outright.
Route by situation:
- No codebase, vague/underspecified idea → `mattpocock-skills:grilling` to stress-test the
  idea via the Skill tool, then write the resulting spec directly as a short markdown doc
  (what `/to-spec` would have produced) — or tell the user they can run `/to-spec` themselves
  for its structured questionnaire flow.
- Has codebase, align language, stress-test plan against code, record ADRs/glossary as it
  goes → do this directly: read the actual code the plan touches, note where the plan's
  language drifts from what the code already calls things, record any real ADR-worthy
  decision inline. Tell the user they can run `/grill-with-docs` themselves for its fuller,
  doc-grounded version of this.
- High-stakes decision, non-trivial logic, before commit/deploy → `mattpocock-skills:grilling` (adversarial stress-test)
- Framework/library specific implementation, API version matters → `mattpocock-skills:research`

Step 0 still applies first, silently: if scope is already unambiguous from the request + visible context (typo fix, single clear bug, direct question, explain/summarize/search/diagnose), state the 1-line scope read and skip straight to the fitting phase/action — don't invoke any of the above.

**When the full shape is running, Phase 1 is not skippable and hands off to plan mode.**
Step 0's skip is for collapsed tasks only. For full-shape work, close Phase 1 by stating
the resolved scope (spec summary + any assumptions still open) in the response, then —
Claude Code only — call `EnterPlanMode` *before* writing any Phase 2 design, so Phase 2
drafts inside plan mode and Gate 1 is the native `ExitPlanMode` approval (mechanics:
`skills/ai-sdlc/references/dev-qa-handoff.md`). Never go interview → architect
file directly without passing through plan mode.

**Update `ai-sdlc-task-progress.md` now** — initialize it if this is the first phase touching
this feature, record the spec/decisions this phase produced (§ Incremental Update Rule,
`skills/ai-sdlc/references/ai-sdlc-progress-spec.md`).

## Phase 2 — Architect (Dev + QA combined)

Entry check (full shape): Phase 1 closed with a stated scope, and — Claude Code — plan
mode is active (§ Phase 1 end). If either is missing, go back and do it first.

No template. Write however much design the task needs — a sentence for a small fix,
more for something with a real trade-off — then stop. Read `PRODUCT.md`/`ARCHITECTURE.md`
first if the project has them; every project gets an `ARCHITECTURE.md` regardless of
size — write/update it with the stack/data-model decision now, a one-bullet entry for a
trivial task, a full living-doc entry for a real one. For a new feature or project, write the architecture/design document directly at
`$AODD_HOME/plans/[FEATURE]/[FEATURE]-architecture.md` (or `[FEATURE]-architecture/`), always in the same folder as
`ai-sdlc-task-progress.md`. Combined with the old
pipeline's separate Dev/QA architecture split: decide here, in the same pass, **what
needs QA coverage and why** — not the scenarios themselves (that's Phase 3), just
which behaviors are worth a test at all. A design done in isolation from QA concerns
is how the old pipeline ended up with dev and QA designs that quietly diverged. The
concrete handoff conventions that make this work (data-testid map, test-environment
requirements, schema consistency) → `skills/ai-sdlc/references/dev-qa-handoff.md`.

### Existing Asset Scan (Dev + QA) — before designing any new module/component/service/test helper

Applies to Dev code and QA automation alike, in whatever language or test framework the
project already uses:

1. Check both the module-scoped and top-level/cross-module shared locations first,
   following whatever convention the project already has — naming varies (`shared/`,
   `util/`, `common/`, `base/`, a per-package root file like `paths.py`/`config.py`, or a
   dedicated package in a multi-package repo). Look for what's actually reused, not for a
   specific folder name to match.
2. If `graphify-out/` exists, query it (`mcp__graphify__query_graph`) for a similar symbol/concept; otherwise `grep -r` other feature/module folders by
   keyword (translate non-English intent to English terms first).
3. Classify: does exactly what's needed → **reuse** (use as-is); close but missing a
   method/parameter → **extend** (keep the existing signature backward-compatible — see
   Reuse Modification Retest below); nothing matches → **create**.
4. **Smart-Copy Rule:** never copy a whole file — copy only the function/method needed
   plus its direct dependencies.
5. **Known-bug check:** for a `reuse`/`extend` candidate, check the project's notes and the Pitfalls sections of loaded skills for gotchas already recorded against that component before building on it.

### Reuse-Table Artifact & the Nth-Occurrence Centralization Rule — Backend, Frontend, DB, QA alike

**MANDATORY, always — this does not collapse for small tasks and is not the model's call
to skip.** See § Collapse for small tasks above: a trivial one-line edit with nothing to
scan is exempt because there's genuinely nothing to check, not because this rule is
optional. The instant a task adds any new function/component/query/helper, run the scan
and produce the table below before writing that code — on a "small" task exactly as much
as a large one.

**Mandatory when Phase 2 touches more than one file:** produce a markdown table as part of
the feature's `[FEATURE]-architecture.md`, columns exactly:

```markdown
| Concern | File | Symbol/Function | Verdict | Rationale |
|---|---|---|---|---|
```

`Verdict` is one of four values:

- **Reuse-as-is** — an existing symbol already does exactly what's needed, called
  unmodified. Cite `file:line`.
- **Extend** — one existing symbol/file is close, gets a backward-compatible parameter/
  behavior added in place (feeds § Reuse Modification Retest below). Still ONE file being
  touched, not a new one.
- **Create-centralized** — see the Nth-Occurrence Rule immediately below. A **new** shared
  file/symbol is created, but *because* the scan found the same logic already duplicated
  independently ≥2 times, and the existing duplicates get refactored to call the new
  centralized one instead of the task adding a 3rd/4th independent copy.
- **Create-new** — genuinely nothing to reuse/extend/centralize; a new file/symbol with no
  precedent. This is the only verdict that adds code without also removing or redirecting
  any existing duplication.

**The Nth-Occurrence Rule** (what turns a `create` into a `create-centralized`): during
step 2 of the Existing Asset Scan (graphify query / grep for a similar symbol), if the
*same* non-trivial logic pattern — not merely a similar-sounding name — turns up already
implemented **independently in 2 or more places** that don't already share a common
call site, the correct move for this task (which would otherwise be the 3rd copy) is:

1. Extract the shared logic into one new file/symbol in the project's existing shared
   location (per step 1 of the Existing Asset Scan — reuse the shared-folder convention
   already established, don't invent a new one).
2. Refactor the existing N duplicates to call the new centralized symbol, deleting their
   private copies. This is itself an `extend` on each of those N files — run § Reuse
   Modification Retest on each before considering the centralization done, since each
   duplicate has its own existing callers/tests that must stay green.
3. The task's own new caller reuses the centralized symbol — it contributes **zero** new
   duplicate logic.

**A 3rd independent copy of the same logic is itself the signal to centralize — don't
wait for a 4th.** Two independent copies can still be coincidence; three is a pattern
the codebase is asking to have named once.

**Applies identically across Backend, Frontend, DB, and QA** — this is not a Dev-only or
QA-only rule: a validation rule, form hook, seed helper, or login helper reimplemented
per-file instead of centralized in the project's existing shared location is the same
pattern in every domain.

**This table is Gate 1's actual review artifact, not a nice-to-have** — the user approving
Phase 2's design is approving this table specifically, not just the prose.

### Reuse Modification Retest — decided here, executed in Phase 4 (not now)

Extending a shared module/component can break every other caller/spec that already
depends on it. This rule is defined here, next to the classification that triggers it,
but **it cannot run in Phase 2** — no code has changed yet. If Existing Asset Scan above
classified something `extend`, carry that flag into Phase 4 and execute there, right
after this task's own change passes:

1. Find dependents: use graphify (`mcp__graphify__get_neighbors`/`blast_radius` on the
   changed symbol) as the default — it tracks real call/reference edges from a real AST,
   more reliable than grep across every language (import-only languages like Swift/Go/Rust,
   and Robot Framework's keyword calls, aren't visible via grep at all). Install the
   project's graphify extractor if missing before falling back to grep.

   **Grep fallback** (only when graphify isn't set up): target the actually-invoked token,
   not the file/class name, scoped to real source+test dirs (never the bare repo root).
   Include any receiver/namespace prefix (`cy.mount`, not bare `mount`) to avoid collisions
   with common words. Start case-sensitive; only add `-i` if the language allows casing to
   legitimately differ, or the DSL is case-insensitive at runtime (e.g. Robot Framework).
2. Re-run the **existing** unit/integration tests (Dev) or specs (QA) covering those
   dependents — not the whole suite unless the change is genuinely cross-cutting.
3. **1 fix attempt on a broken dependent, then rollback if it's still failing** — revert
   the shared component to its pre-extend state and put the new logic in a dedicated
   local helper instead. Don't debug a reuse decision into a redesign of someone else's
   already-green code.
4. **Exception — QA/E2E specs only, never Dev unit tests:** an E2E-level spec that runs
   through a real login/session setup every execution doesn't need a targeted retest for
   that setup logic — it already re-verifies it every run. A Dev unit test that **mocks**
   auth gets NO exception — it never exercises the real path, so retest it normally.

**Approval Gate 1 applies here** — see § Approval Gates above: don't start Phase 3/4
until the user has approved this phase's design/implementation plan (skip only if the
task collapsed per § Collapse for small tasks).

Deep DDD work (bounded contexts, aggregates/events, sync-vs-async integration tradeoffs)
is model judgment applied directly here — there's no separate skill for it. Domain-term
discipline specifically (writing/updating `CONTEXT.md` via `mattpocock-skills:domain-modeling`) →
`skills/ai-sdlc/references/dev-qa-handoff.md`'s Domain Language note.

Task breakdown: `to-tickets` and `wayfinder` are also `disable-model-invocation` — for
multi-step tasks, slice the design and spec into vertical slices directly and write them
straight into `$AODD_HOME/plans/[FEATURE]/ai-sdlc-task-progress.md` (checkbox per slice; see
`skills/ai-sdlc/references/ai-sdlc-progress-spec.md`) instead of `to-tickets`' own
`.scratch/<slug>/issues/` output, which nothing here reads anyway. For a multi-session epic
genuinely too big to chart this way, tell the user they can run `/wayfinder` themselves for
its dedicated decision-map flow.

If the feature touches auth, permissions, or sensitive data → flag it for a security review
here (the `security` skill if you have one), in this same pass (its own coverage decision, same reasoning as "what needs QA
coverage"), not discovered later during implementation. If it's a core/load-sensitive
API → flag it for performance testing too, to run after Phase 5 confirms GREEN.

**Update `ai-sdlc-task-progress.md` now** — mark the design/implementation plan approved,
record approver/scope/timestamp for Approval Gate 1, and log the vertical-slice task
breakdown if multi-step (§ Incremental Update Rule, `skills/ai-sdlc/references/ai-sdlc-progress-spec.md`).

## Phase 3 — QA-Design (scenario + skeleton, RED)

Only when Phase 2 flagged real QA coverage needed — skip entirely otherwise.

Scenario: use your scenario skill or tool, or write it by hand — it produces the
`[TS-XXXX]`/`[TC-XXXX]`-tagged scenario list Phase 4 implements
against. If Phase 2 flagged a security concern, fold the security QA scenarios into this same scenario list rather than a separate pass.

**Approval Gate 2 applies here** — see § Approval Gates above: don't move on to skeleton
work until the user has approved the scenario list.

**Update `ai-sdlc-task-progress.md` now** — mark the scenario list approved, record
approver/scope/timestamp for Approval Gate 2 (§ Incremental Update Rule).

Test skeleton: before stubbing any test, state the public seam(s) each scenario will
test at (the boundary — an API endpoint, a public function, a UI element — not the
internal steps behind it) and get the user's confirmation; write no test at a seam not
agreed to (**Approval Gate 3**). Then stub the automated test(s) from that scenario list, before
Dev implements — failing/RED is expected and correct at this point.

**Framework pick — check what the project already uses first, never assume:**
1. Repo already has a test framework installed/configured → use that one, matching
   its existing conventions.
2. Nothing installed yet (genuinely greenfield) → a sensible default:
   Web UI/API → Playwright; Mobile → Robot Framework. Say this is a
   default, not the only valid choice, and ask if the user wants something else
   before scaffolding it.
3. Still ambiguous → check repo signals (dependency manifests, build config, existing
   test folders) before asking the user.
- Every framework shares the same self-heal/reporting discipline (1-attempt heal,
  Impact Analysis tiers, Reflexion Log, Test Results format) →
  `skills/ai-sdlc/references/qa-automation-loop.md` — framework-agnostic,
  applies whichever framework was picked above.

**Update `ai-sdlc-task-progress.md` now** — mark Approval Gate 3's seam agreement recorded,
mark each skeleton file `[ ]` (RED, not yet green) as it's stubbed (§ Incremental Update Rule).

## Phase 4 — Dev (implement to GREEN)

**If Phase 2's Existing Asset Scan classified anything `extend`, this is where § Reuse
Modification Retest actually executes** — right after this task's own change passes, before
moving on. It was only decided in Phase 2; it runs here, not there.

Implement against the Phase 3 skeleton(s) until they pass. Call `mattpocock-skills:tdd`
via the Skill tool for its red→green/seam/anti-pattern methodology, then write the code
directly (`implement` is `disable-model-invocation` — see § Status). If code structure
gets cluttered, call `mattpocock-skills:codebase-design` for deep-module/seam vocabulary
and refactor directly against it (`improve-codebase-architecture` is likewise blocked).

Before writing code, pick the matching stack-specific coding-standards skill based on project stack
(if you have one) and apply
its conventions — this phase owns the workflow shape (skeleton → GREEN), the platform
skill only supplies stack-specific syntax/pattern, it does not replace this phase.

If Phase 2 flagged auth/permissions/sensitive-data/security concerns, this phase is where
that flag actually gets acted on: apply secure-coding practice
(input validation at trust boundaries, parameterized queries, secret isolation) while
implementing — don't let the Phase 2 flag sit unaddressed until a QA scenario happens to
catch it later.

**Two test tiers, paired not duplicate:** Phase 3's skeleton is QA's feature/E2E-level
scenario (the acceptance criteria). Phase 4 additionally owns unit-level tests for the
internal logic it writes — derived FROM the same business rules/edge cases QA already
spelled out in Phase 3's scenarios (boundary values, validation rules, error paths), not
invented separately — per the rule that non-trivial logic leaves one
runnable check behind and `mattpocock-skills:tdd`'s red→green→refactor applied at the unit
level. Phase 5 verifies the QA scenario suite; it doesn't re-verify Phase 4's own unit
tests — those stay green as part of Phase 4's own Done-gate (`rules/aodd.md`
Test-Before-Deliver).

**Update `ai-sdlc-task-progress.md` now** — mark each skeleton `[x]` as it actually goes
GREEN, not batched at the end (§ Incremental Update Rule).

## Phase 5 — QA-Verify (confirm GREEN)

Run the full scenario suite from Phase 3 against the Phase 4 implementation. Every
test still carries its `[TS-XXXX]`/`[TC-XXXX]` ID and obeys the core facts above (no
hard waits, 1 heal attempt max before routing to `9arm-skills:debug-mantra`). This phase
is verification only — no new scenarios get invented here; a genuinely missing case
found during verification goes back to Phase 3, it doesn't get patched in place.

Pre-merge gate: once all tests confirm GREEN, invoke `mattpocock-skills:code-review` (or `/code-review`) to run parallel sub-agents evaluating two distinct axes:
- **Standards Axis**: conforms to the project's coding standards
- **Spec Axis**: faithfully implements the originating spec produced in Phase 1

**Knowledge graph sync:** If `graphify-out/` exists in the repository, run `graphify update .` before closing the task (AST-only, keeps the graph fresh for subsequent queries/tools).

**Update `ai-sdlc-task-progress.md` now** — mark the final checkbox, feature Done (§
Incremental Update Rule; this IS the Done-gate (`rules/aodd.md`) — don't call it Done anywhere
else first).

## Status

Default route for new/unclear-scope Dev/QA feature work. Stack-specific coding skills, if you have them, still own coding conventions.

**`mattpocock-skills` invocation split** — some sub-skills are `disable-model-invocation`
and cannot be called via the Skill tool mid-task, only run by the user as a
`/slash-command`: `to-spec`, `to-questionnaire`, `grill-with-docs`, `to-tickets`,
`wayfinder`, `implement`, `implement-spec`, `improve-codebase-architecture`, `ask-matt`,
`handoff`, `triage`, `setup-matt-pocock-skills`. Every phase above accounts for this —
where the referenced sub-skill is blocked, the phase does the work directly instead and
points the user at the `/slash-command` as an optional fuller alternative. Directly
invocable: `grilling`, `research`, `domain-modeling`, `codebase-design`, `tdd`,
`code-review`, `diagnosing-bugs`, `resolving-merge-conflicts`, `prototype`, `wizard`.
