# Delegation: who does what, at which effort

Read this before starting any subagent, `claude -p`, `codex exec` or `agy -p` run. Vendor syntax (how an effort level is set)
is in `rules/effort/claude-code.md`, `rules/effort/codex.md` and `rules/effort/agy.md`; read the file of the tool you dispatch to.

## Model split (don't ask each time)

| Work | Who |
|---|---|
| Plan, pick architecture, write the brief, review every diff, re-run test/build, check the UI in a browser | main session (Opus/Fable) |
| Design on the ai-sdlc Requirement path | 2 subagents in parallel (Dev view + QA view), see `rules/ai-sdlc-workflow.md` |
| Multi-file feature or bug fix | 1 Sonnet subagent in its own worktree; more only for disjoint files with an explicit scope each |
| Design delegated to ChatGPT | `sol` writes the design; main reviews it before any code |
| Implementation of a ChatGPT design | `terra`; keeps working until every acceptance check passes or it reports one concrete blocker; main reviews the diff |
| Search, lookup, run build/test, summaries, data dumps, ≤9-item batches | Haiku subagents, in parallel when independent |

On Codex the tiers are `sol` = Opus/Fable, `terra` = Sonnet, `luna` = Haiku. Haiku writes no code (see Bake-off).

## Cheap-model delegation

Search with Haiku, check with Sonnet, escalate to the `advisor`.

| Work | 1. Do it | 2. Check it |
|---|---|---|
| Search, lookup, research, file/log sweeps | Haiku returns facts + paths, no dumps | Sonnet reads the cited files itself before building on it |
| Code lookup (graphify tools or grep) | Haiku returns file paths + edges | Sonnet reads in full every file it will edit or judge |
| Run an approved build / test / deploy, verify a page | Haiku reports pass/fail + output excerpt | Sonnet re-checks the excerpt against the brief |
| Write or change code, debug, plan, review a diff | Sonnet (main or a subagent) | main reviews every diff |

A Haiku result is input, not a conclusion. The advisor (Fable/Opus only, never Sonnet/Haiku) gets a curated brief: decision,
options, constraints, evidence; it sees none of the conversation. At most two advisor calls per task, then tell the user.

- Do it yourself when the job is one short command, one lookup, or a file main must read anyway: a helper re-reads cold.
- Data over ~300 lines or 40KB (ingest, scrape, dump) goes to a Haiku subagent or a local script that prints a short summary.
- The subagent sees none of this conversation: pass the facts it needs. `hooks/delegation-nudge.py` reminds after 8 lookups in a row.
- A background CLI agent gets `</dev/null` (`docs/codex.md`); check within a few minutes that it works.

## Effort ladder

Five levels, shared by every vendor: `low` < `medium` < `high` < `xhigh` < `max`.

- **Announce once per plan.** Before the first run of a plan, tell the user the model, the effort and the number of runs, and
  wait for a yes. After that the runs in that plan go without asking again. Ask again only to add runs or raise effort
  outside the plan. Small lookups the main session does itself need no announcement.
- **Start at `low`**, unless the ticket's `Effort:` line says otherwise.
- **Escalate one step at a time:** 3 failing checks in a row raise one step, `low` → `medium` → `high`. Still failing at
  `high`: stop and tell the user. No vendor switching.
- `xhigh` and `max` run only when a ticket says so or the ai-sdlc review stage requires `xhigh`.
- A passing check returns the task to its starting level.

## Bake-off: a tier change is measured, not guessed

Before a model or default effort changes for a work type: pick 3-5 past tickets with known outcomes from `$AODD_PLANS`, run each
candidate on them, record pass rate, rework rounds, tokens and cost. Choose the higher pass rate when costs are within 20%
(a proposal, needs CEO confirmation); on equal pass rates choose the cheaper. Until a bake-off exists, keep the table default.

A Haiku code row needs a bake-off result and CEO approval. Any Haiku code trial gets an explicit brief (files it may touch,
acceptance checks, "stop and report one blocker") and main reviews every diff. A project's own workflow may refine this split.
