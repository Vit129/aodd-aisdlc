# Phase 5 — QA-Verify (confirm GREEN)

> Load when you start Phase 5. Parent: `rules/ai-sdlc-workflow.md`.


Run the full scenario suite from Phase 3 against the Phase 4 implementation. Every
test still carries its `[TS-XXXX]`/`[TC-XXXX]` ID and obeys the core facts in `rules/ai-sdlc-workflow.md` (no
hard waits, 1 heal attempt max before routing to `9arm-skills:debug-mantra`). This phase
is verification only — no new scenarios get invented here; a genuinely missing case
found during verification goes back to Phase 3, it doesn't get patched in place.

Pre-merge gate: once all tests confirm GREEN, run `/code-review` (or any review skill you have) on the full diff, checking two axes:
- **Standards Axis**: conforms to the project's coding standards
- **Spec Axis**: faithfully implements the originating spec produced in Phase 1

**Pre-Deploy & Delivery Gate (Mandatory before Release/Deploy):**
Before any code is merged to main, released, or deployed:
1. **Security Scan:** Run security verification (via the `security` skill): secret leak scan, SAST, dependency vulnerability checks, and verify authorization/trust boundaries.
2. **Performance & Regression Check:** Run performance benchmarks (e.g. bundle size check, endpoint latency, load test, or memory/CWV regression check if flagged in Phase 2 or core paths) — ensure no performance regressions before production.
3. **Cross-Family Audit:** Run `scripts/audit.py` with the session transcript, target repo, and Done claims. The verdict must be PASS (or explicitly approved by CEO if DISPUTED) — `hooks/done-gate.py` strictly blocks Done without this.
4. **Version Bump & git-cliff Changelog:**
   - Bump version (`VERSION`, `package.json`, `version.json`, or `Info.plist` via semantic bump `major|minor|patch` per `rules/coding/release.md`).
   - Run `git-cliff --tag vX.Y.Z --output CHANGELOG.md` (using project `cliff.toml`) to update release notes automatically.
   - Propose release commit & tag (`chore(release): vX.Y.Z`) before triggering deployment.

**Knowledge graph sync:** If `graphify-out/` exists in the repository, run `graphify update .` before closing the task (AST-only, keeps the graph fresh for subsequent queries/tools).

**Update `ai-sdlc-task-progress.md` now** — mark the final checkbox, feature Done (§
Incremental Update Rule, `skills/ai-sdlc/references/ai-sdlc-progress-spec.md`; this IS the Done-gate (`rules/aodd.md`) — don't call it Done anywhere
else first).
