# Phase 1 — Interview

> Load when clarification or idea questioning is needed. Parent: `rules/ai-sdlc-workflow.md`.

## Interview

Use the request and visible context to pick the path (§ Paths in the parent workflow).
If the goal, scope and acceptance criteria are complete, skip questions and take that path.
Otherwise identify the weakest assumptions and unresolved choices. Follow each answer to
what it leaves open, challenge contradictions, and finish when every branch has a decision,
or the user says to stop. Having enough to start is not enough to end the interview.

1. Read relevant code and docs first. Never ask a question those sources can answer; use the
   codebase's terms and note any ADR-worthy decision. For version-sensitive framework/API
   facts, verify primary docs (delegation mechanics: `rules/ai-sdlc/delegation.md`).
2. Ask **one at a time** (`AskUserQuestion` where available), recommend an answer with its
   reason, and resolve any contradiction with earlier answers or the code. If the kind of
   change is unclear, settle that first.
3. Draft no design and touch no product code during questioning. Keep decisions in the plan.

## Build the artifact until ready for coding

Capture the goal, scope in / out, acceptance criteria and decisions with reasons in `brief.md`
next to the progress file. This is input to the artifact, not the endpoint of the work.
After questioning, create the agreed requirement and implementation plan as an HTML file
(`plan.html`; rendering and storage follow the parent workflow § Every path).
Continue refining that artifact through the design and QA planning phases required by the
chosen path until it is ready for coding. Do not stop at a brief or ask for an extra
"continue" between interview and artifact preparation.

The artifact is ready when the scope and acceptance criteria are settled, implementation
steps and affected files are clear, verification cases and test seams are defined, and
no decision blocking coding remains open. Apply the parent workflow's approval gates at
their named points; proceed to coding only after the applicable approvals. If the user
explicitly asks for questions only or asks to stop, respect that narrower scope.

On the Requirement path, enter plan mode before Phase 2 design (`EnterPlanMode` in Claude
Code; elsewhere a plan file in `$AODD_PLANS/[FEATURE]/` for approval), even when questions were skipped.
Handoff mechanics: `skills/ai-sdlc/references/dev-qa-handoff.md`. Record decisions and artifact
links in the existing task progress file when required
(`skills/ai-sdlc/references/ai-sdlc-progress-spec.md`); single-sitting work skips it.
