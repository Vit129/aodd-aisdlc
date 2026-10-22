# Phase 2 — Architect (Dev + QA combined)

> Load when you start Phase 2 (full or Medium shape). Parent: `rules/ai-sdlc-workflow.md`.


Entry check (full shape): Phase 1 closed with a stated scope, and — Claude Code — plan
mode is active (end of `skills/ai-sdlc/phases/phase1-interview.md`). If either is missing, go back and do it first.

No template. Write however much design the task needs — a sentence for a small fix,
more for something with a real trade-off — then stop. Read `PRODUCT.md`/`ARCHITECTURE.md`
first if the project has them.

**Subagent Co-Design (Medium/Large tasks):**
Dispatch two subagents to evaluate the design from counterbalancing perspectives:
- **Dev Subagent:** Proposes file separation, component structure, tech stack choices, API/data interfaces, and executes the Existing Asset Scan (`phase2-existing-asset-scan.md`) & Reuse Table (`phase2-reuse-table.md`).
- **QA Subagent:** Stress-tests the design for failure modes, edge cases, boundary values, security/auth concerns, testability, and external mock requirements (`dev-qa-handoff.md`).

The main thread synthesizes both perspectives into the **Single Plan Artifact** (`/plan` or `[FEATURE]-plan.md`, also stored at `$AODD_PLANS/[FEATURE]/[FEATURE]-architecture.md`). Combined with the old
pipeline's separate Dev/QA architecture split: decide here, in the same pass, **what
needs QA coverage and why** — not the scenarios themselves (that's Phase 3), just
which behaviors are worth a test at all. A design done in isolation from QA concerns
is how the old pipeline ended up with dev and QA designs that quietly diverged. The
concrete handoff conventions that make this work (data-testid map, test-environment
requirements, schema consistency) → `skills/ai-sdlc/references/dev-qa-handoff.md`.

## Closing Phase 2 (always, whichever Phase 2 files you loaded)

**Approval Gate 1 applies here when the full shape is running** — see § Approval Gates in `rules/ai-sdlc-workflow.md`: don't start Phase 3/4
until the user has approved this phase's design/implementation plan. A Medium task states its file separation plan and keeps the gates light (Task Sizing in the same file); a Small task that collapsed per baseline rule 1 skips the gate.

**Post-Approval Living Docs Sync & Commit Proposal (Once Gate 1 is Approved):**
Immediately sync approved durable decisions from the Plan Artifact into the project's living documentation:
- **`PRODUCT.md`**: Record the feature scope, target outcome, and boundaries so future sessions understand what the system does.
- **`DESIGN.md`**: Record UI/UX tokens, typography, layout, and component guidelines (if frontend/UI work).
- **`ARCHITECTURE.md` + Tech Stack**: Record architectural choices, library selections, data models, and seams (`hooks/coding-rules-gate.py` enforces reading this before writing code).
- **`CONTEXT.md`**: Update domain glossary / ubiquitous language dictionary to ensure consistent naming.
- **Propose commit to user:** Prompt the user to commit these living docs (e.g. `docs: update specifications for [feature]`) before proceeding to test design or implementation code. This locks the specification into git history.

Deep DDD work (bounded contexts, aggregates/events, sync-vs-async integration tradeoffs)
is model judgment applied directly here — there's no separate skill for it. Domain-term
discipline specifically (writing/updating `CONTEXT.md`) →
`skills/ai-sdlc/references/dev-qa-handoff.md`'s Domain Language note.

Task breakdown: for multi-step tasks, slice the design and spec into vertical slices and
write them straight into `$AODD_PLANS/[FEATURE]/ai-sdlc-task-progress.md` (checkbox per
slice; see `skills/ai-sdlc/references/ai-sdlc-progress-spec.md`). For a multi-session epic
too big for that, write a decision map first (open decisions, what blocks what).

If the feature touches auth, permissions, or sensitive data → flag it for a security review
here (the `security` skill), in this same pass (its own coverage decision, same reasoning as "what needs QA
coverage"), not discovered later during implementation. If it's a core/load-sensitive
API → flag it for performance testing too, to run after Phase 5 confirms GREEN.

**Update `ai-sdlc-task-progress.md` now** — mark the design/implementation plan approved,
record approver/scope/timestamp for Approval Gate 1, and log the vertical-slice task
breakdown if multi-step (§ Incremental Update Rule, `skills/ai-sdlc/references/ai-sdlc-progress-spec.md`).
