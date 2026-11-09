# Commit and Push

Use when the user asks for commit + push, or when it is a stage of a full cycle. These mutate the repo. Inspect first, and respect ownership of changes you did not make.

## Graphify first

Graphify is required setup (see SKILL.md). Refresh it after the code or docs change and before the commit, using the repo's documented command, otherwise `graphify update .`. If the refresh fails, stop and report. If the repo has no Graphify setup, report it as a setup gap and stop before the commit. Do not create the graph as a side effect of this stage.

Wait for the refresh to finish successfully after the final code/docs/version edits. Set `PYTHONHASHSEED=0`. Stage existing tracked graph artifacts using `git add --update -- <explicit tracked paths>` and include them in the **same commit** as the product/docs/version files. Leave new query/cache/snapshot outputs local; never bulk-add `graphify-out/`.

Use the repo's shared preparation helper, including its curated renderer if present. For repositories using the standard `graphify update .`, the installed `scripts/graphify_commit.py -m "<message>"` refreshes, stages tracked graph paths, then commits the already prepared index. Review and stage only owned product paths first. A failure stops before commit and push.

Set `GRAPHIFY_SKIP_HOOK=1` only on the prepared commit when the repo's Graphify post-commit hook supports it; keep every unrelated Git hook active. Do not run a second background refresh after committing. Coordinate any branch-switch refresh before preparing the next commit; never discard dirty graph output to make a delivery flow proceed.

## Before committing

1. Check the branch, `git status`, the staged diff, and the unstaged diff. Record anything already staged and leave it alone.
2. Confirm the change is ready. Run the checks the repo requires. Do not claim unrun checks passed.
3. Review every path. If ownership is unclear, leave that path out and say so.
4. Stage explicit paths only. Never `git add -A` or `git add .`. Prove the commit contains exactly those paths (for example inspect `git diff --cached --name-only`; if using `git commit --only`, include the tracked graph paths too). If that cannot be proven without touching pre-existing staged work, stop.
5. Use the repo's commit convention and make one scoped commit. Verify the hash and the clean worktree afterward.

## Before pushing

1. Push only the requested branch. A normal push does not authorize `--force`, `--force-with-lease`, a history rewrite, or deleting a remote branch.
2. If the push is non-fast-forward or the branch diverged, stop and report. Do not rebase, merge, or force-push silently.
3. Verify the push on the remote and report the branch and hash.

A commit + push request does not authorize a PR, a merge, a tag, a hosted release, or a deploy. Report those as NOT RUN. If a repo helper does several of these at once, use narrower commands or stop and explain the mismatch.
