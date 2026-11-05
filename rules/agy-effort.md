# agy effort mapping

Scope: only for setups that use Antigravity (`agy`). The shared ladder, bake-off and escalation rules are in `rules/aodd.md` § Effort ladder and tier choice.

## Setting effort

- **Command:** `agy -p --model <m> --effort <low|medium|high|xhigh|max> --mode accept-edits`, run in its own worktree.
- **Models:** check the list with `agy models` before use. Names change between releases.

## Row

| Work | Who | Start effort | Rules |
|---|---|---|---|
| Implementation handed to Antigravity (`agy`) | agy, in its own worktree | `medium` | commits, never pushes; main reviews the diff before Done |

Escalation follows the shared ladder: 3 failing checks raise one level, capped at `high`. Then switch vendor family, then the advisor rule. `xhigh` and `max` only when a ticket says so.
