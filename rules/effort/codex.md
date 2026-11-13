# Codex effort mapping

Scope: only for Codex. Ladder rules: `rules/aodd/delegation.md` § Effort ladder.

## Setting effort

- **Config file:** `model_reasoning_effort = "<level>"` in `~/.codex/config.toml`. The key name is confirmed by a working user config.
- **Per run:** `codex exec -m <m> -c model_reasoning_effort=<level>`.
- **Stdin:** a background `codex exec` run needs `</dev/null` so it cannot hang waiting on stdin (see `docs/codex.md`).

## Start effort

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
