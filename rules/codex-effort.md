# Codex effort mapping

Scope: only for setups that use Codex. The shared ladder, bake-off and escalation rules are in `rules/aodd.md` § Effort ladder and tier choice.

## Setting effort

- **Config file:** `model_reasoning_effort = "<level>"` in `~/.codex/config.toml`. The key name is confirmed by a working user config.
- **Per run:** `codex exec -m <m> -c model_reasoning_effort=<level>`.
- **Stdin:** a background `codex exec` run needs `</dev/null` so it cannot hang waiting on stdin (see `docs/codex.md`).

## Row

| Work | Who | Start effort | Rules |
|---|---|---|---|
| Second opinion, rescue, or an independent check from another family | Codex (`codex:rescue` or `codex exec`) | `low` | returns a diff or findings; main reviews before anything is reported |

## Tiers (same roles as Claude)

| Codex | Claude row | Does |
|---|---|---|
| `sol` | Opus/Fable | main session: plan, design, review every diff |
| `terra` | Sonnet | writes and changes code, in its own worktree |
| `luna` | Haiku | search, lookup, run build/test, summaries; writes no code |

Delegate with `spawn_agent` (model per the table, effort per the ladder).

## Start, announce, escalate

- **Start:** every `codex exec` / `codex:rescue` / `spawn_agent` run starts at `low`, unless the ticket's `Effort:` line says otherwise.
- **Announce before the run:** tell the user the model, the effort and how many runs, and wait for their yes. Usage limits are the user's to spend.
- **Escalate one step at a time:** `low` → `medium` → `high`. 3 failing checks in a row raise one step; never skip a step; capped at `high`. `xhigh` and `max` only when a ticket says so.
