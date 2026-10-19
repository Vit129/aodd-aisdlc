# Phase 2 — Reuse Modification Retest

> Load when a design modifies an existing shared component (decided in Phase 2, executed in Phase 4). Parent: `rules/ai-sdlc-workflow.md`.


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
straight into `$AODD_PLANS/[FEATURE]/ai-sdlc-task-progress.md` (checkbox per slice; see
`skills/ai-sdlc/references/ai-sdlc-progress-spec.md`) instead of `to-tickets`' own
`.scratch/<slug>/issues/` output, which nothing here reads anyway. For a multi-session epic
genuinely too big to chart this way, tell the user they can run `/wayfinder` themselves for
its dedicated decision-map flow.

If the feature touches auth, permissions, or sensitive data → flag it for a security review
here (the `security` skill), in this same pass (its own coverage decision, same reasoning as "what needs QA
coverage"), not discovered later during implementation. If it's a core/load-sensitive
API → flag it for performance testing too, to run after Phase 5 confirms GREEN.

**Update `ai-sdlc-task-progress.md` now** — mark the design/implementation plan approved,
record approver/scope/timestamp for Approval Gate 1, and log the vertical-slice task
breakdown if multi-step (§ Incremental Update Rule, `skills/ai-sdlc/references/ai-sdlc-progress-spec.md`).
