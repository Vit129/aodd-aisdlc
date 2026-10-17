# Skill Routing Table

Read when running `/ai-sdlc` or when unsure which skill fits. Everything outside this repo
(the `mattpocock-skills`, `9arm-skills`, `agy`/`codex` plugins) is optional: install the companion plugins listed in the README for the full set, otherwise
do the step directly.

| Task signal | Route to |
|---|---|
| New feature / non-trivial refactor / bug fix, unclear scope | `ai-sdlc` skill (`/ai-sdlc`): the full phase spine with its 3 approval gates |
| Epic too big for one session / complex unknowns | Chart the decision map directly as a written doc |
| Codebase / ecosystem investigation | `mattpocock-skills:research` (companion) |
| Exploratory spike / feasibility check | `mattpocock-skills:prototype` (companion) |
| Deep interview / stress-test an idea or plan | `mattpocock-skills:grilling` (companion) |
| Structured spec needed | Write it directly as a short markdown doc |
| Domain language / `CONTEXT.md` | `mattpocock-skills:domain-modeling` (companion) |
| Interface & seam design (deep modules, adapters) | `mattpocock-skills:codebase-design` (companion) |
| Project / feature architecture plan | Write `$AODD_PLANS/[feature]/[feature]-architecture.md`, next to `ai-sdlc-task-progress.md` |
| Ticket slicing | Write vertical slices directly into `$AODD_PLANS/[feature]/ai-sdlc-task-progress.md` |
| QA test skeletons (RED, shift-left) | `test-scenario` (scenario design), then `playwright-testing` (web/API) or `robotframework-testing` (mobile); name testids per `rules/data-testid-mapping.md` |
| Stack coding conventions | `backend-dev`, `frontend-dev` (with `uxui-designer` when there are no design tokens), `macos-swiftui`; always `rules/coding.md` |
| Project folder structure / scaffolding | `project-blueprint` skill and `rules/coding/project-blueprint.md`; `ARCHITECTURE.md`/`PRODUCT.md`/`DESIGN.md` per `rules/product-design.md` |
| Load / performance test | `performance-testing` |
| UI layout bug | `rules/gui-fixes.md` |
| Delete / overwrite / bulk cleanup; branch deletion, PR pushes | `destructive-ops-verify`; `git-safety` |
| TDD implementation | `mattpocock-skills:tdd` for methodology, then write the code directly |
| Security concern (auth, permissions, user input, secrets) | `security` skill: secure-coding half in Phase 4, QA half in Phase 3 |
| Hard technical decision, no clear answer | The `advisor` agent with a curated brief (decision, options, constraints) |
| Bounded subtask: search files, read/summarize logs, classify, extract facts, run build/test/lint, git/ops mechanics | `Agent(model: "haiku")`, several in parallel; the big model plans and judges. See `rules/aodd.md` |
| Read/map code ("where is X", "who calls Y") | graphify (companion) first, then a Haiku subagent for broad sweeps; the big model reads every file it will edit itself |
| Pre-merge review (standards + spec) | `mattpocock-skills:code-review` (companion) or any review skill; feed it the project's coding standards explicitly |
| Session handoff to another agent/session | Write `$AODD_PLANS/[FEATURE]/handoff.md` (sibling of, not the same file as, `ai-sdlc-task-progress.md`) |
| Bug investigation | `9arm-skills:debug-mantra` (companion) or `mattpocock-skills:diagnosing-bugs` |
| Post-incident RCA | `9arm-skills:post-mortem` (companion) |
| Independent audit of a "Done" claim | `python3 scripts/audit.py` (never a worker-briefed subagent) |
| Cross-provider second opinion or stuck investigation | The `agy` / `codex` Claude Code plugins if installed; brief with a curated summary, not the raw transcript |
