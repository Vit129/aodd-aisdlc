# Phase 1 — Interview

> Load when you start Phase 1. Parent: `rules/ai-sdlc-workflow.md`.


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

The scope check comes first, silently: if scope is already unambiguous from the request + visible context (typo fix, single clear bug, direct question, explain/summarize/search/diagnose), state the 1-line scope read and skip straight to the fitting phase/action — don't invoke any of the above.

**When the full shape is running, Phase 1 is not skippable and hands off to plan mode.**
The scope-check skip is for collapsed tasks only. For full-shape work, close Phase 1 by stating
the resolved scope (spec summary + any assumptions still open) in the response, then —
Claude Code only — call `EnterPlanMode` *before* writing any Phase 2 design, so Phase 2
drafts inside plan mode and Gate 1 is the native `ExitPlanMode` approval (mechanics:
`skills/ai-sdlc/references/dev-qa-handoff.md`). Never go interview → architect
file directly without passing through plan mode.

**Update `ai-sdlc-task-progress.md` now** — initialize it if this is the first phase touching
this feature, record the spec/decisions this phase produced (§ Incremental Update Rule,
`skills/ai-sdlc/references/ai-sdlc-progress-spec.md`).
