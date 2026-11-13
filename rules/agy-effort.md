# agy effort mapping

Scope: only for setups that use Antigravity (`agy`). The shared ladder, bake-off and escalation rules are in `rules/aodd.md` § Effort ladder and tier choice.

## Setting effort

- **Command:** `agy -p --model <m> --effort <low|medium|high|xhigh|max> --mode accept-edits`, run in its own worktree.
- **Models:** check the list with `agy models` before use. Names change between releases.

## Row

| Work | Who | Start effort | Rules |
|---|---|---|---|
| Implementation handed to Antigravity (`agy`) | agy, in its own worktree | `low` | commits, never pushes; main reviews the diff before Done |

## Start, announce, escalate

- **Start:** every `agy -p` run starts at `low`, unless the ticket's `Effort:` line says otherwise.
- **Announce before the run:** tell the user the model, the effort and how many runs, and wait for their yes. Usage limits are the user's to spend.
- **Escalate one step at a time:** `low` → `medium` → `high`. 3 failing checks in a row raise one step; never skip a step; capped at `high`. Then switch vendor family, then the advisor rule. `xhigh` and `max` only when a ticket says so.
