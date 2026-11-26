# Delegation: who does what, at which effort

Read this before starting any subagent, `claude -p`, `codex exec` or `agy -p` run. Vendor syntax (how an effort level is set)
is in `rules/effort/claude-code.md`, `rules/effort/codex.md` and `rules/effort/agy.md`; read the file of the tool you dispatch to.

## Tiers (customizable)

This file names roles, not models: `big` (plans, reviews, advisor), `middle` (writes briefs, very easy changes), `small` (executes briefs, searches, runs commands). Which model fills each tier is set per tool in `rules/effort/<tool>.md` § Tier mapping. Change that table, not this file, to use other models or vendors; a personal override (one tier, one kind of work) goes in your own workspace rules.

## Model split: plan big, brief middle, execute small (mandatory)

Every delegated task runs this pipeline. No exceptions, no asking each time.

| Step | Who | Does |
|---|---|---|
| 1. Plan | big tier (main session) | always plans first: goal, approach, architecture, files in scope, acceptance checks |
| 2. Brief | middle tier | turns the plan into a step-by-step execution brief: exact files, edits, commands, checks, "stop and report one blocker" |
| 3. Execute | small tier | carries out the brief, code included; reports the diff and check output |
| Very easy task | middle tier | skips the brief and does it itself (one small, obvious change) |
| Search, lookup, research, summaries, and every command run: build, test, lint, install, git/ops, release, deploy, migrations, health checks | small tier | always; reports pass/fail + output excerpt; in parallel when independent, ≤9 items per batch; publish/irreversible steps still need the CEO's approval first |
| Review | big tier | reviews every diff and every piece of verification evidence before anything is reported |

- **Announce before every piece of work.** Before any step starts, tell the user which model does what (model, effort, number of runs). Nothing runs before that line is shown.
- Requirement-path design still uses 2 subagents in parallel (Dev view + QA view, `rules/ai-sdlc-workflow.md`); their merged
  plan is step 1, then steps 2-3 apply.
- Multi-file executions: one executor per disjoint file set, each with its own explicit scope, in its own worktree.
- Tier names per tool: `rules/effort/<tool>.md` § Tier mapping; same pipeline everywhere.
- If the CEO explicitly names Luna as the implementer, honor that assignment for the
  requested implementation work (code, tests, rules, docs, configuration or other artifacts).
  The task still passes AODD triage, gets a bounded brief and acceptance checks, and the main
  session reviews the diff and verification evidence. This assignment does not authorize
  unrelated work or publish/irreversible actions.

## Cheap-model delegation

Search with the small tier, check with the middle tier, escalate to the `advisor` (big tier).

| Work | 1. Do it | 2. Check it |
|---|---|---|
| Search, lookup, research, file/log sweeps | small tier returns facts + paths, no dumps | middle tier reads the cited files itself before building on it |
| Code lookup (`project_search` or rg) | small tier returns file paths + edges | middle tier reads in full every file it will edit or judge |
| Run an approved build / test / deploy, verify a page | small tier reports pass/fail + output excerpt | middle tier re-checks the excerpt against the brief |
| Write or change code | small tier, from the middle tier's brief (middle itself when very easy) | main reviews every diff |
| Debug, plan, review a diff | main session | main |

A small-tier result is input, not a conclusion. The advisor (big tier only, never middle/small) gets a curated brief: decision,
options, constraints, evidence; it sees none of the conversation. At most two advisor calls per task, then tell the user.

- Do it yourself when the job is one short command, one lookup, or a file main must read anyway: a helper re-reads cold.
- Data over ~300 lines or 40KB (ingest, scrape, dump) goes to a small-tier subagent or a local script that prints a short summary.
- The subagent sees none of this conversation: pass the facts it needs. `hooks/delegation-nudge.py` reminds after 8 lookups in a row.
- A background CLI agent gets `</dev/null` (`docs/codex.md`); check within a few minutes that it works.

## Effort ladder

Five levels, shared by every vendor: `low` < `medium` < `high` < `xhigh` < `max`.

- **Announce, then run.** Before each run, the user is told the model, the effort and the number of runs (see Model split). Wait for a yes on the first run of a plan; later runs in the same plan are announced but need no new yes. Ask again to add runs or raise effort outside the plan.
- **Start at `low`**, unless the ticket's `Effort:` line says otherwise.
- **Escalate one step at a time:** 3 consecutive unsuccessful attempts to solve the same diagnosed problem raise one step,
  `low` → `medium` → `high`. Count only attempts where the agent could change the outcome through its reasoning or implementation.
  Expected RED tests, unavailable dependencies/services, environment failures and missing permissions do not count; resolve or
  report those blockers instead. Still failing at `high`: stop and tell the user. No vendor switching.
- `xhigh` and `max` run only when a ticket says so or the ai-sdlc review stage requires `xhigh`.
- A passing check returns the task to its starting level.

## Model escalation (proposal, not active)

Status: proposal. It stays inactive until the CEO confirms the thresholds and the per-ticket budget below, and a bake-off
(see Bake-off) supports it. Until then the Model split table and the effort ladder above apply unchanged.

The model does not judge its own difficulty. Escalation runs on external signals only: check results, diff scope, review
verdicts and token use. Each ticket starts at its Model split tier and effort `low`.

Tier order: small → middle → big (advisor only). Escalate one tier when, on the same diagnosed problem:

1. A required check still fails after 3 consecutive attempts at `high` effort on the current tier.
2. The diff touches a file outside the brief's scope, or the main review rejects the diff twice.
3. The ticket's token budget is more than 50% spent with no passing check.

Rules for escalation:

- Expected RED tests, unavailable services, environment failures and missing permissions never trigger escalation (same as the effort ladder).
- The middle tier fixes from the failing check output; it does not re-plan. Re-planning stays with the big tier.
- The big tier is reached through the advisor, at most two calls per task (Cheap-model delegation). If it still fails, stop and report to the user.
- Each ticket records its tier path, effort per attempt, attempt count, pass or fail and total tokens, so the bake-off can measure the rule.
- Ticket token budget: `[CEO to set]`. A ticket that reaches its budget stops and reports, whatever its tier.

## Bake-off: a tier change is measured, not guessed

Before a model or default effort changes for a work type: pick 3-5 past tickets with known outcomes from `$AODD_PLANS`, run each
candidate on them, record pass rate, rework rounds, tokens and cost. Choose the higher pass rate when costs are within 20%
(a proposal, needs CEO confirmation); on equal pass rates choose the cheaper. Until a bake-off exists, keep the table default.

The small tier executing code is the default (Model split). Its brief always names the files it may touch, the acceptance checks and
"stop and report one blocker"; main reviews every diff. A project's own workflow may refine this split.
