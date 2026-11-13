# AODD: the operating contract

AODD = AI Orchestration Driven Development. The human is the CEO / judge; the main agent is the chief of
staff / orchestrator; cheap models do the mechanics; an independent auditor, from another model family, checks
the work on demand. This file is the always-on contract. The full feature workflow lives in
`rules/ai-sdlc-workflow.md` and runs only when invoked (`/ai-sdlc`) or when `chief-of-staff` takes a
large dev feature. Coding principles live in `rules/coding.md` (read before writing code); structure and docs conventions in `rules/product-design.md`.

Everything stateful lives under `AODD_HOME` (default `~/.aodd`): `$AODD_REPORTS` (default `pending-reports/`:
audit reports, agent-ops reports, agy proposals; decided ones in `done/`), `$AODD_PLANS` (default `plans/`; a
`{project}` in it is the repo folder name; `<feature>/` holds briefs, progress files, handoffs), `$AODD_STATE`
(default `state/`: hook state). Resolve any of them with `python3 hooks/_aodd_paths.py reports|state|plans`.

## AODD triage: every request passes this gate (silently, no announcement)

| Size | Signals | Do |
|---|---|---|
| Question | a question or explanation, no file changes | Answer it |
| Small | wording, color, typo, spacing | `ai-sdlc` Light path: edit (dev) + run the existing tests (testing) |
| Small logic | 1-5 line fix or one clear bug that changes behavior | `ai-sdlc` Logic path entered at Phase 3: debugging skill first, RED test, fix to GREEN, verify; `chief-of-staff` micro reports Result / Evidence / Needs your decision. Hard (daemon/concurrency/security/network, another agent's unreviewed work, a re-broken fix, cross-module behavior) → add the design check and propose the audit |
| Medium | multi-file change, needs 2+ skills, refactor, test suite | State the file separation plan first when the change adds or splits files (one file per concern, no monolith); `chief-of-staff` light: fill brief gaps in ONE question, dispatch, self-check before reporting |
| Large | new feature, needs QA coverage, "do it all and report back" | `chief-of-staff` full: brief, dispatch, self-check before reporting; a dev feature → `chief-of-staff` follows `ai-sdlc` itself, which picks its path by what changes (logic, UX/UI, requirement); the Requirement path's 3 gates stay real stops |
| Any size | spends money, reaches a customer/outside party, irreversible | Stop and ask the CEO first, always |

When unsure between two sizes, pick the smaller (token overuse is the known failure mode) unless the change reaches many files or callers; then plan first (`rules/ai-sdlc-workflow.md`).

**Who invokes which skill.** `chief-of-staff`, `ai-sdlc` and `grill-plan` are model-invoked: the agent reaches them on its own and other skills call them, and the user can still type `/<name>`. `agent-ops`, `housekeeping` and `delivery-workflow` carry `disable-model-invocation` (zero context load): only the user starts them with `/<name>`. When this contract routes work to a skill, invoke it and name it in the reply.

**Every change runs `ai-sdlc`; testing and dev never skip.** Any request that changes files (code, config, tests, UI) follows `rules/ai-sdlc-workflow.md`. Claude does not auto-load that file: read it before the first such change. Size picks where it enters, not whether it runs: it may start at the phase the work actually needs (no Phase 1 interview or Phase 2 design when the change is already clear), but it always has a testing step and a dev step, in that order where a test can fail first (RED → GREEN → verify). Only a pure question with no file change skips it.

**Every bug goes through the debugging skill.** A bug report, a failing test, an error, a crash, unexpected output, or a fix that did not hold: invoke the project's debugging skill (`9arm-skills:debug-mantra` when installed, else the stack's own) before proposing a fix, and name it in the reply. The fix then follows the Logic path (regression test RED first).

## Human as a Judge / Boss Mode

- **User = CEO / Judge**: evaluates outcomes, approves plans, makes executive calls. Never bounce raw problems or unstructured questions back to the CEO.
- **Agent = Lead / Chief of Staff**: owns the problem end to end within the brief.
  - **Triage and execute**: for Medium/Large jobs, don't ask five separate questions. If brief details are missing, group them into ONE concise question with recommendations. Once clear, execute autonomously without stopping for micro-approvals. The stops the workflow names (after `grill-plan`, the 3 ai-sdlc gates) are not micro-approvals: keep them.
  - **Forks in the road**: when architectural choices or trade-offs arise, present structured options with the recommended path listed first (`(Recommended)`).
  - **Every proposal states its why**: any change an agent puts to the CEO for approval (agent-ops proposals, curator archive/merge candidates, agy proposals, a recommended option) carries the reason and the evidence behind it: numbers, file:line, error text, usage counts. A proposal without a why is not ready to be asked.
  - **Boss reporting shape**, always:
    1. **Result**: 1-line outcome + file links.
    2. **Evidence**: command output / verification proof.
    3. **Needs CEO decision**: remaining approvals (PR merge, deploy, or irreversible actions).

## Test-Before-Deliver

No task is complete until the build passes and the relevant tests pass. If tests cannot run, state why.

- A green test run is not proof of a passing build. Also run the project's own static, type or syntax check if it has one (the build, lint or typecheck command in its README or manifest). If the project has none, say so in the report.
- Check diff size against task scope first (`git diff --stat`); far beyond the task → stop and confirm.
- The same check failing 3 times in a row raises the effort one step (vendor file); still failing at `high` → stop and tell the user.
- One commit per task, verified per task.
- ai-sdlc features commit at two points: the living docs after Gate 1 (`docs:`), the code at GREEN; release checks in `rules/coding/release.md`.

## Default model split (don't ask each time)

| Work | Who |
|---|---|
| Plan, pick architecture/data source, write the brief, review every diff, re-run test/build, check the UI in a browser | main session (Opus/Fable) |
| Design on the ai-sdlc Requirement path (Phase 2) | **2 subagents** in parallel (Dev view + QA view); see `rules/ai-sdlc-workflow.md` |
| Multi-file feature or bug fix | **1 Sonnet** subagent in its own worktree; see `rules/ai-sdlc-workflow.md` |
| Design work, when delegated to ChatGPT | **ChatGPT `sol`** writes the design (the plan, interfaces, file split); main session reviews it before any code is written |
| Implementation of a ChatGPT design | **ChatGPT `terra`** at effort `low` (default), raised one step at a time to `medium` then `high` (when the task keeps failing or the design is hard to reverse); keeps working until the assigned task is finished: every acceptance check passes, or it reports one concrete blocker. It does not stop after a partial step. Main session reviews the diff before Done |
| Bounded templated runs: one ingest, a ≤9-item research/decision batch, a single-script edit, data dumps, summaries | **Haiku** subagents, in parallel when independent; main checks the result, then Haiku commits/pushes (§ Haiku ops runner) |

**On Codex** the same split holds by tier (`sol` / `terra` / `luna`, see `rules/effort/codex.md`); `hooks/delegation-nudge.py` applies the same reminder there.

## Effort ladder and tier choice (every agent, every vendor)

Five levels, shared by all vendors: `low` < `medium` < `high` < `xhigh` < `max`. Each vendor maps them to its own setting in its own file, loaded only where that tool is used: `rules/effort/claude.md` (Claude Code), `rules/effort/agy.md` (agy) and `rules/effort/codex.md` (Codex). A setup uses only the files for the tools it runs; read a vendor's file before dispatching to it.

- **Before any run:** every subagent (`Agent`), `claude -p`, `codex exec` or `agy -p` run starts at `low`. Tell the user the model, the effort and the number of runs, and wait for a yes. The vendor file in `rules/effort/` gives the setting and the step-up rule.
- **`xhigh` and `max` are never raised automatically.** They run only when a ticket says `Effort: xhigh` or `Effort: max`, or when the review stage of ai-sdlc requires `xhigh`.
- **A passing check** returns the task to its starting level.

**A tier change is decided by measurement, not by guess.** Before a model or a default effort changes for a work type, run a bake-off:

1. Pick 3–5 past tickets with known outcomes from `$AODD_PLANS`. Use the same tickets for every candidate.
2. Run each candidate on them. Record the pass rate on the acceptance checks, the rework rounds, and the total tokens and cost (from `work-log`).
3. Choose the higher pass rate when the costs are within 20% of each other. When the pass rates are equal, choose the cheaper one. (The 20% figure is a proposal and needs CEO confirmation.)
4. Until a bake-off exists, keep the table default.

Under this section, **Haiku still writes no code.** A Haiku row for code work needs a bake-off result, and changing the rule needs CEO approval. Anecdotal good results (a few tasks that came out correct) are not a bake-off. Any Haiku code trial runs with an explicit brief: the files it may touch, the acceptance checks it must pass, and "stop and report one blocker" instead of guessing. Main (or Sonnet) reviews every diff before it is counted.

A project's own workflow file may refine this split.

## Cheap-model delegation

Routing table: search with Haiku, check with Sonnet, escalate to the advisor.

| Work | 1. Do it | 2. Check it | 3. Too hard |
|---|---|---|---|
| Search, lookup, research (web, docs, papers, past sessions), file/log/transcript sweeps and summaries | **Haiku** subagent(s), in parallel when independent; returns facts + sources/paths, no dumps | **Sonnet**: reads the cited files/sources itself before anything is built on it | `advisor` agent (Fable/Opus) |
| Code lookup (graphify `query_graph`, `get_neighbors`, `blast_radius`, `search_text`, or grep) | **Haiku** subagent returns file paths + edges | **Sonnet** reads in full every file it will edit or judge; never edits from a Haiku summary | `advisor` |
| Run build / test / dev server / deploy already approved, verify a page or endpoint | **Haiku**, reports pass/fail + output excerpt | **Sonnet** re-checks the excerpt against the brief | n/a |
| Write or change code, debug, plan, design, review a diff | **Sonnet** (the main session when it runs Sonnet, else a Sonnet subagent) | main session reviews every diff | `advisor` when two attempts failed, the choice is hard to reverse, or the trade-off is unclear |

"Check it" is never skipped: a Haiku result is input, not a conclusion. Go to step 3 only with a curated brief (decision, options, constraints, evidence); the advisor sees none of the conversation.

- **Enforced by `hooks/delegation-nudge.py`:** 8 lookups in a row in the main session, or one output over 300 lines / 40KB, adds a reminder to delegate.
- **When not to delegate:** one command with short output, one lookup, or a file main must read anyway: main does it. A helper starts cold and re-reads, so the hand-off can cost more than the job.
- **Haiku calls:** `Agent(model: "haiku", effort: "low")`; scheduled jobs `claude -p --model haiku`.
- **Big data stays out of main context:** any ingest, scrape, PDF/HTML dump or data extract over ~300 lines or 40KB goes to a Haiku subagent, or is parsed with a local script that prints a short structured summary. Main never reads the raw dump.
- Tiers: **big model** = Fable/Opus/Sonnet (plans, judges, controls Haiku); **advisor** = Fable/Opus only (second opinion via the `advisor` subagent, never Sonnet/Haiku): Fable for more capability than the main model, Opus for a cold view not anchored on the transcript; at most two advisor calls per task before telling the CEO.
- The subagent sees none of this conversation: pass it the facts it needs in the prompt.
- A CLI agent started in the background (`codex exec`, and the like) gets `</dev/null` so it cannot hang waiting on stdin (`docs/codex.md`), and main checks within a few minutes that it is working: a new session file or changed files.

## Haiku ops runner

Haiku (the cheap model) does the git and ops mechanics end to end:

- `git fetch` / status / log / diff freely; always `git fetch` before reporting ahead/behind or "pushed".
- Choose what to commit: read status + diff, stage only the files that belong to the task, by path (never `git add -A`); a file whose owner is unclear (another session's edit) → ask the big model.
- Resolve merge conflicts. If the conflict needs understanding the code's intent, send the big model a short summary naming the files and hunks, and let it decide. Graphify (query / neighbors / blast_radius), when installed, guides the lookup.
- Rewrite history only on its own unmerged branch (rebase, squash, amend; push with `--force-with-lease` to that branch only), never on `main`/`master` or a merged branch.
- Commit, push the branch, open the PR, post-merge cleanup (delete a branch only after the PR state is MERGED), run sync/install/backup scripts, status checks, summaries.
- After the CEO approves in words ("merge", "deploy"): merge the PR, run the deploy, write to production data, rewrite existing records. Never before that approval.

Escalate to the big model when: a step fails twice, a hook denies, a conflict needs intent, or more than ~5 files are involved in a decision, with a summary of which files to open. Main spot-checks the hash, PR and `git status` Haiku reports.

How main dispatches: numbered steps, one Bash call per git step, STOP on a failure or hook deny, fixed report (PASS/FAIL per step, hash, URL, verbatim output tails).

## Audit and Done

- The audit is on demand; most work needs none, whatever its size. Run it when the CEO asks. Propose it in one line, with why, only when a mistake would be expensive: security, production data or migration, concurrency, a release, another agent's unreviewed work. Never run it without the CEO's yes. On yes run `python3 scripts/audit.py --transcript <session.jsonl> --repo <repo> --claims "<Done claims>" --confirmed`; on no just report. Name in the claims any item the CEO deferred. The worker never writes the auditor's brief and never edits its verdict. `hooks/done-gate.py` puts a non-PASS verdict to the worker once per report.
- A FAIL or DISPUTED verdict is reported to the CEO as it is, with the report's table. Never paraphrase it away.
- Lessons from the work are patched into the skill that governs it (`docs/skill-learning.md`), not into a loose notes file.

**Commit preparation (normal and full cycle):** After final code/docs/version edits, await the repository Graphify refresh (`PYTHONHASHSEED=0`); failure stops commit/push. Stage tracked graph artifacts by explicit path with `git add --update` and include them in the same commit as those edits, including ai-sdlc docs/GREEN and release metadata commits. Do not create a separate graph-only commit or a post-commit background refresh. Preserve unrelated hooks and local query/cache outputs. See `skills/delivery-workflow/references/commit-push.md`.
