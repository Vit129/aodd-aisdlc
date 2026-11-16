# Phase 1 — Interview

> Load when clarification or idea questioning is needed. Parent: `rules/ai-sdlc-workflow.md`.

## Interview

Use the request and visible context to pick the path (§ Paths in the parent workflow).
If the goal, scope and acceptance criteria are complete, skip questions and take that path.
Otherwise identify the weakest assumptions and unresolved choices. Follow each answer to
what it leaves open, challenge contradictions, and finish when every branch has a decision,
or the user says to stop. Having enough to start is not enough to end the interview.

1. Order depends on the repo. **Extending existing code** (including a new idea in a repo that
   already has code): skim the structure and read the relevant code and docs first, then
   interview from what they show. **New work** (a new repo or module with no existing code):
   interview first. Never ask a question the code or docs can answer; use the codebase's terms
   and note any ADR-worthy decision. For version-sensitive framework/API facts, verify primary
   docs (delegation mechanics: `rules/ai-sdlc/delegation.md`).
2. Ask **one at a time** (`AskUserQuestion` where available), recommend an answer with its
   reason, and resolve any contradiction with earlier answers or the code. If the kind of
   change is unclear, settle that first.
3. Draft no design and touch no product code during questioning. Keep decisions in the plan.

## Build the artifact until ready for coding

After questioning, create the agreed requirement and implementation plan as an HTML file
(`plan.html`; rendering and storage follow the parent workflow § Every path).
Continue refining that artifact through the design and QA planning phases required by the
chosen path until it is ready for coding. Do not ask for an extra "continue" between
interview and artifact preparation.

Who does what (tiers from `rules/ai-sdlc/delegation.md`): the big model asks the questions and judges
readiness; the middle model writes the agreed plan text (or the big model, when the plan is very small);
the small model (Haiku, `luna` on Codex) only turns the agreed text into `plan.html` and never adds,
drops or reinterprets content. The big model checks the rendered file against the agreed text.

Once the artifact is fully agreed, write `brief.md` next to the progress file (goal, scope in / out,
acceptance criteria, decisions with reasons) for agents and handoff. For new work, first check the
project structure standard and `rules/coding.md` for which parts apply, and record them in `brief.md`.
Look at the user's other projects for reuse only when the user asks; otherwise design fresh.
Living docs stay where the parent workflow puts them (after Gate 1).

Keep one `plan.html` and update it as those phases progress. Show its current state and pending
approvals: **Draft** after interview, **Design approved** after Gate 1, **Scenarios approved**
after Gate 2, and **Ready for coding** after Gate 3 and the readiness checks below. Before Gate 1,
verification ideas and test seams are provisional; Phase 3 settles them after design approval.
Do not complete Phase 3 early just to finish the HTML, or require a final HTML before Gate 1.
On paths without gates, move from Draft to Ready for coding once the applicable readiness checks hold.

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
