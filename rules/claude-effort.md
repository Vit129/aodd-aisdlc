# Claude effort mapping

Scope: Claude Code only. The shared ladder, bake-off and escalation rules are in `rules/aodd.md` § Effort ladder and tier choice. This file only says how those levels are set on Claude.

## Setting effort

- **Subagent call:** `Agent(model: "<haiku|sonnet|opus>", effort: "<low|medium|high|xhigh|max>")`. Set both on every call, so the subagent does not inherit whatever the session happens to use.
- **Main session:** the session's own effort and model, picked by the user. The ladder does not change it on its own.

## Defaults for Claude work

| Work | Model | Start effort |
|---|---|---|
| Code change, multi-file fix | Sonnet subagent in its own worktree | `medium` |
| Plan, design, architecture | main session (Opus/Fable) | `high` |
| Mechanical run, search, summary, data dump | Haiku subagent | `medium`; `high` when the result feeds a decision |
| Review of a diff | main session | `high`; `xhigh` only when the ticket says so |

## Limits

- **Haiku writes no code** under this file. A Haiku code row needs a bake-off result from `rules/aodd.md` first.
- `xhigh` and `max` are set only by a ticket's `Effort:` line or by the ai-sdlc review stage, never by the escalation ladder.
