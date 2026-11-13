# Claude Code effort syntax

Scope: Claude Code only. Ladder rules: `rules/ai-sdlc/delegation.md` § Effort ladder. This file only says how levels are set on Claude.

## Setting effort

- **Subagent call:** `Agent(model: "<haiku|sonnet|opus>", effort: "<low|medium|high|xhigh|max>")`. Set both on every call, so the
  subagent does not inherit the session's setting.
- **Main session:** the session's own effort and model, picked by the user. The ladder does not change it.

## Start effort

| Work | Model | Start effort |
|---|---|---|
| Code change, multi-file fix | Sonnet subagent in its own worktree | `low` |
| Plan, design, architecture | main session (Opus/Fable) | `high` |
| Mechanical run, search, summary, data dump | Haiku subagent | `low` |
| Review of a diff | main session | `high`; `xhigh` only when the ticket says so |
