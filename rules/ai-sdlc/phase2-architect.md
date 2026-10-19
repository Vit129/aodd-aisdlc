# Phase 2 — Architect (Dev + QA combined)

> Load when you start Phase 2 (full or Medium shape). Parent: `rules/ai-sdlc-workflow.md`.


Entry check (full shape): Phase 1 closed with a stated scope, and — Claude Code — plan
mode is active (§ Phase 1 end). If either is missing, go back and do it first.

No template. Write however much design the task needs — a sentence for a small fix,
more for something with a real trade-off — then stop. Read `PRODUCT.md`/`ARCHITECTURE.md`
first if the project has them; every project gets an `ARCHITECTURE.md` regardless of
size — write/update it with the stack/data-model decision now, a one-bullet entry for a
trivial task, a full living-doc entry for a real one. For a new feature or project, write the architecture/design document directly at
`$AODD_PLANS/[FEATURE]/[FEATURE]-architecture.md` (or `[FEATURE]-architecture/`), always in the same folder as
`ai-sdlc-task-progress.md`. Combined with the old
pipeline's separate Dev/QA architecture split: decide here, in the same pass, **what
needs QA coverage and why** — not the scenarios themselves (that's Phase 3), just
which behaviors are worth a test at all. A design done in isolation from QA concerns
is how the old pipeline ended up with dev and QA designs that quietly diverged. The
concrete handoff conventions that make this work (data-testid map, test-environment
requirements, schema consistency) → `skills/ai-sdlc/references/dev-qa-handoff.md`.
