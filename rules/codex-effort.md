# Codex effort mapping

Scope: only for setups that use Codex. The shared ladder, bake-off and escalation rules are in `rules/aodd.md` § Effort ladder and tier choice.

## Setting effort

- **Config file:** `model_reasoning_effort = "<level>"` in `~/.codex/config.toml`. The key name is confirmed by a working user config.
- **Per run:** `codex exec -m <m> -c model_reasoning_effort=<level>`.
- **Stdin:** a background `codex exec` run needs `</dev/null` so it cannot hang waiting on stdin (see `docs/codex.md`).

## Row

| Work | Who | Start effort | Rules |
|---|---|---|---|
| Second opinion, rescue, or an independent check from another family | Codex (`codex:rescue` or `codex exec`) | `medium` | returns a diff or findings; main reviews before anything is reported |

Escalation follows the shared ladder: 3 failing checks raise one level, capped at `high`. Then switch vendor family, then the advisor rule. `xhigh` and `max` only when a ticket says so.
