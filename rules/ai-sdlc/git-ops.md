# Git ops: the Haiku ops runner and commit preparation

Read this before commit, push, PR or merge. Haiku (the cheap model) does the git and ops mechanics end to end.

## Haiku ops runner

- `git fetch` / status / log / diff freely; always `git fetch` before reporting ahead/behind or "pushed".
- Choose what to commit: read status + diff, stage only the files that belong to the task, by path (never `git add -A`); a file
  whose owner is unclear (another session's edit) goes to the big model.
- Resolve merge conflicts. If a conflict needs the code's intent, send the big model a short summary naming the files and
  hunks, and let it decide. `project_search` (or rg + Read) guides the lookup.
- Rewrite history only on its own unmerged branch (rebase, squash, amend; push with `--force-with-lease` to that branch only),
  never on `main`/`master` or a merged branch.
- Commit, push the branch, open the PR, post-merge cleanup (delete a branch only after the PR state is MERGED), run
  sync/install/backup scripts, status checks, summaries.
- After the CEO approves in words ("merge", "deploy"): merge the PR, run the deploy, write to production data, rewrite existing
  records. Never before that approval.
- Every report to the CEO lists each open PR by number and link (`#N https://...`) until its state is MERGED, not only the
  report that opened it.

Escalate to the big model when a step fails twice, a hook denies, a conflict needs intent, or more than ~5 files are involved in
a decision, with a summary of which files to open. Main spot-checks the hash, PR and `git status` Haiku reports.

Dispatch: numbered steps, one Bash call per git step, STOP on a failure or hook deny, fixed report (PASS/FAIL per step, hash,
URL, verbatim output tails).

## Commit preparation

- Code-search index output (any backend) is generated, never tracked in git: list its folder in the repo's `.gitignore` and
  never stage it. The index refreshes on its own (the backend's watcher, or the search guard's opt-in Stop step); there is no refresh step in the commit flow.
