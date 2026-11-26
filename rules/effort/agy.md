# agy effort mapping

Scope: only for Antigravity (`agy`). Ladder rules: `rules/ai-sdlc/delegation.md` § Effort ladder.

Before writing any prompt or dispatching to `agy` or a Gemini model, read `rules/gemini-prompting.md` in full.

## Setting effort

- **Command:** `agy -p --model <m> --effort <low|medium|high|xhigh|max> --mode accept-edits`, run in its own worktree.
- **Models:** check the list with `agy models` before use. Names change between releases.

## Tier mapping (customizable)

Which Gemini 4 model fills each `rules/ai-sdlc/delegation.md` tier by default; change the rows to suit. Exact ids (`gemini-4-<family>-<effort>`) come from `agy models`.

| Tier | Model |
|---|---|
| big | Gemini 4 Carbon or Neon (`gemini-4-carbon-*`, `gemini-4-neon-*`) |
| middle | Gemini 4 Neon (`gemini-4-neon-*`) |
| small | Gemini 4 Hydrogen (`gemini-4-hydrogen-*`) |

## Start effort

| Work | Who | Start effort | Rules |
|---|---|---|---|
| Implementation handed to Antigravity (`agy`) | agy, in its own worktree | `low` | commits, never pushes; main reviews the diff before Done |
