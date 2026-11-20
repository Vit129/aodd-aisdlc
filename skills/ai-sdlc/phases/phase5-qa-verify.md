# Phase 5 — QA-Verify (confirm GREEN)

> Load when you start Phase 5. Parent: `rules/ai-sdlc-workflow.md`.


Verify the full scenario suite from Phase 3 against the Phase 4 implementation, including
recorded manual results for scenarios approved without automation. Reuse existing PASS results
when they cover the delivered source and relevant inputs; run missing or invalidated checks only
(parent workflow § Verification evidence). Every automated
test still carries its `[TS-XXXX]`/`[TC-XXXX]` ID and obeys the core facts in `rules/ai-sdlc-workflow.md`. This phase
is verification only — no new scenarios get invented here; a genuinely missing case
found during verification goes back to Phase 3, it doesn't get patched in place.

Pre-merge gate: once all tests confirm GREEN, run `scrutinize` (9arm) on the full diff, checking two axes:
- **Standards Axis**: conforms to the project's coding standards
- **Spec Axis**: faithfully implements the originating spec produced in Phase 1

**UI and flow evidence:** a change that touches a UI or a user flow attaches a screenshot or video of the affected screens (for example `playwright-cli` video or screenshot) to the verification record or PR, not text alone.

**Traceability table** (before sign-off, in the progress file): one row per Phase 1 requirement and Phase 2 NFR → the test(s) that cover it → result. A requirement with no test is a gap: add the test or record why not. The auditor checks against this table.

**Release or deploy after this feature:** satisfy the release gate in `rules/coding/release.md`
(security/pen test, performance, audit, version + changelog), reusing valid results without a separate Test-Before-Deliver run.

**Final step:** no manual index refresh; a configured search index updates on its own and is never committed (`rules/ai-sdlc/git-ops.md`).

**Update `ai-sdlc-task-progress.md` now** — mark the final checkbox, feature Done (§
Incremental Update Rule, `skills/ai-sdlc/references/ai-sdlc-progress-spec.md`; this IS the Done-gate (`rules/ai-sdlc-workflow.md`) — don't call it Done anywhere
else first).
