# Git ops: the Haiku ops runner and commit preparation

Read this before commit, push, PR or merge. Haiku (the cheap model) does the git and ops mechanics end to end.

## Haiku ops runner

- `git fetch` / status / log / diff freely; always `git fetch` before reporting ahead/behind or "pushed".
- Choose what to commit: read status + diff, stage only the files that belong to the task, by path (never `git add -A`); a file
  whose owner is unclear (another session's edit) goes to the big model.
- Resolve merge conflicts. If a conflict needs the code's intent, send the big model a short summary naming the files and
  hunks, and let it decide. Graphify (query / neighbors / blast_radius), when installed, guides the lookup.
- Rewrite history only on its own unmerged branch (rebase, squash, amend; push with `--force-with-lease` to that branch only),
  never on `main`/`master` or a merged branch.
- Commit, push the branch, open the PR, post-merge cleanup (delete a branch only after the PR state is MERGED), run
  sync/install/backup scripts, status checks, summaries.
- After the CEO approves in words ("merge", "deploy"): merge the PR, run the deploy, write to production data, rewrite existing
  records. Never before that approval.

Escalate to the big model when a step fails twice, a hook denies, a conflict needs intent, or more than ~5 files are involved in
a decision, with a summary of which files to open. Main spot-checks the hash, PR and `git status` Haiku reports.

Dispatch: numbered steps, one Bash call per git step, STOP on a failure or hook deny, fixed report (PASS/FAIL per step, hash,
URL, verbatim output tails).

## Commit preparation

- The graph refresh is the last step of `rules/ai-sdlc-workflow.md`; do not refresh again here. A repo without graphify skips it.
- Stage the tracked graph artifacts by explicit path with `git add --update -- <paths>` in the same commit as the edits they
  describe. Never a separate graph-only commit. Set `PYTHONHASHSEED=0` when a helper script refreshes the graph.
- `python3 scripts/graphify_commit.py -m "<message>"` refreshes, stages tracked graph paths and commits the prepared index for
  standard graphify repos; the release runner uses it too.
