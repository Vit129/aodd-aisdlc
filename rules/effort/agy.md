# agy effort mapping

Scope: only for Antigravity (`agy`). Ladder rules: `rules/ai-sdlc/delegation.md` § Effort ladder.

Before writing any prompt or dispatching to `agy` or a Gemini model, read `rules/gemini-prompting.md` in full.

## Setting effort

- **Command:** `agy -p --model <m> --effort <low|medium|high|xhigh|max> --mode accept-edits`, run in its own worktree.
- **Models:** check the list with `agy models` before use. Names change between releases.

## Tier mapping (customizable)

Default Gemini 4 models for the tiers in `rules/ai-sdlc/delegation.md`. Edit this table to use other models; check the exact ids (`gemini-4-<family>-<effort>`) with `agy models`.

| Tier | Model |
|---|---|
| big | Gemini 4 Carbon or Neon (`gemini-4-carbon-*`, `gemini-4-neon-*`) |
| middle | Gemini 4 Neon (`gemini-4-neon-*`) |
| small | Gemini 4 Hydrogen (`gemini-4-hydrogen-*`) |

## Start effort

| Work | Who | Start effort | Rules |
|---|---|---|---|
| Implementation handed to Antigravity (`agy`) | agy, in its own worktree | `low` | commits, never pushes; main reviews the diff before Done |
