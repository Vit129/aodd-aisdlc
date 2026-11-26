# agy effort mapping

Scope: only for Antigravity (`agy`). Ladder rules: `rules/ai-sdlc/delegation.md` § Effort ladder.

Before writing any prompt or dispatching to `agy` or a Gemini model, read `rules/gemini-prompting.md` in full.

## Setting effort

- **Command:** `agy -p --model <m> --effort <low|medium|high|xhigh|max> --mode accept-edits`, run in its own worktree.
- **Models:** check the list with `agy models` before use. Names change between releases.

## Tier mapping (customizable)

Fill in from `agy models` when agy takes a tier in `rules/ai-sdlc/delegation.md`. Empty means agy is not used for that tier.

| Tier | Model |
|---|---|
| big | |
| middle | |
| small | |

## Start effort

| Work | Who | Start effort | Rules |
|---|---|---|---|
| Implementation handed to Antigravity (`agy`) | agy, in its own worktree | `low` | commits, never pushes; main reviews the diff before Done |
