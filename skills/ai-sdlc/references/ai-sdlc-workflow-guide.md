# AI-SDLC Workflow & Execution Guide

Operational guide for executing the 5-phase Shift-Left software lifecycle using `ai-sdlc` as the spine, optionally powered by the companion plugins `mattpocock-skills` and `9arm-skills` (see the README) and your project's QA automation. Without them, do each step directly.

---

## 5-Phase Lifecycle Overview

| Phase | Purpose | Tool / Slash Command | Primary Artifact |
|---|---|---|---|
| **Phase 0: Scope & Discovery** | Map unknowns, spikes, multi-session work | `/wayfinder`, `/research`, `/prototype` | Decision tickets, exploratory spike |
| **Phase 1: Interview** | Uncover assumptions, clarify scope | `/grilling`, `/grill-me`, `/grill-with-docs` → `/to-spec` | Feature Spec (`docs/specs/` or prompt output) |
| **Phase 2: Architect** | Domain language, interface/seam design & ticket slicing | `/domain-modeling`, `/codebase-design`, `/to-tickets` | `CONTEXT.md`, `$AODD_PLANS/[FEATURE]/[FEATURE]-architecture.md`, `$AODD_PLANS/[FEATURE]/ai-sdlc-task-progress.md` |
| **Phase 3: QA-Design** | Shift-Left test scenarios & skeletons | scenario tool + your test framework (Playwright, Robot Framework, ...) | `[TS-XXXX]` test files in **RED (failing)** state |
| **Phase 4: Dev** | Implement tickets until tests pass | `/tdd`, `/implement`, `/improve-codebase-architecture` | Application code driving tests to **GREEN** |
| **Phase 5: QA-Verify** | Verify suite & run parallel pre-merge audit | Full test suite run + `/code-review`, `/handoff` | Code Review Report (Standards + Spec) |

---

## Step-by-Step Execution Guide

### Step 0: Scope & Discovery (Pre-SDLC)
1. If the task is too broad or spans multiple sessions:
   - Run `/wayfinder` to chart a decision map with blocking edges and identify the next unblocked ticket.
2. If exploring unfamiliar libraries or codebase areas:
   - Run `/research` to gather primary-source evidence before proposing architecture.
3. If technical viability is unproven:
   - Run `/prototype` to build a throwaway spike to validate feasibility before writing formal specs.

### Step 1: Clarify & Spec (Phase 1)
1. When receiving a new feature request:
   - If greenfield/fuzzy: Run `/grilling` (or `/grill-me`) to stress-test requirements and uncover hidden assumptions.
   - If extending existing code or using complex frameworks: Run `/grill-with-docs` to challenge assumptions against official documentation.
2. Once aligned, crystallize scope into an explicit, verifiable spec via `/to-spec` (or `/to-questionnaire`).

### Step 2: Architect & Slice Tickets (Phase 2)
1. Standardize ubiquitous domain terms in `CONTEXT.md` using `/domain-modeling`.
2. Determine module depth, public seams, and adapters using `/codebase-design`.
3. Create/record the architecture plan directly in `$AODD_PLANS/[FEATURE]/[FEATURE]-architecture.md` (co-located with `ai-sdlc-task-progress.md`).
4. Determine QA testability requirements (`data-testid`, DB fixtures, mock boundaries) per `references/dev-qa-handoff.md`.
5. Break the spec into vertical slices via `/to-tickets` and initialize `$AODD_PLANS/[FEATURE]/ai-sdlc-task-progress.md`.

### Step 3: Design Test Skeletons in RED (Phase 3)
1. Generate `[TS-XXXX]` scenarios (your scenario tool, or by hand).
2. Stub automated test skeletons at confirmed seams:
   - Use the framework the project already has; greenfield defaults: Playwright for web/API, Robot Framework for mobile.
3. Execute tests once: confirm they **FAIL (RED)** strictly for the expected reasons.

### Step 4: Implement to GREEN (Phase 4)
1. Pick the stack-specific coding skill if you have one (frontend, backend, platform-specific).
2. Run `/tdd` (Red → Green → Refactor vertical tracer bullets at agreed seams) or `/implement` to implement ticket-by-ticket.
3. For architectural cleanup, invoke `/improve-codebase-architecture` to deepen modules and simplify seams.
4. For difficult design/typing decisions, consult the `advisor` agent or generate a `/wizard` (mattpocock-skills).
5. Stop when all Phase 3 tests pass (**GREEN**).

### Step 5: Verify & Pre-Merge Gate (Phase 5)
1. Run the entire test suite to confirm zero regressions.
2. Invoke `/code-review` to launch parallel sub-agents:
   - **Standards Sub-agent**: Validates against the project's coding standards and baseline code smells.
   - **Spec Sub-agent**: Verifies complete coverage against the Phase 1 spec.
3. Optionally run `/scrutinize` for an outsider-perspective sanity check.
4. If handing off to another agent or session, produce a structured summary via `/handoff` — save it to `$AODD_PLANS/[FEATURE]/handoff.md`; `ai-sdlc-task-progress.md` is a checkbox list, don't drop the narrative into that.

---

## Bugs, Incidents & Git Operations

- **Bug Investigation:** Route through `9arm-skills:debug-mantra` (Reproduce → Trace → Falsify → Cross-reference) and `/diagnosing-bugs` or `/triage`.
- **Post-Mortem:** Conduct root cause analysis and document prevention via `/post-mortem`.
- **Merge Conflicts:** Safely resolve git conflicts without loss of intent via `/resolving-merge-conflicts`.
- **Stakeholder Communication:** Translate technical changes into leadership updates via `/management-talk`.

---

## Collapse Rules (When to Skip Phases)

- **Large Feature (Default):** Full 5-phase lifecycle.
- **Medium Task (Small feature/subsystem addition):** Collapse Phase 1 & 2 into a 1-paragraph summary → Phase 3 (quick RED test) → Phase 4 (GREEN) → Phase 5 (`/code-review`).
- **Small Fix (Typo, bug fix, 1-5 lines):** Skip Phase 1-3 → Implement directly → Verify existing tests pass → Done.
