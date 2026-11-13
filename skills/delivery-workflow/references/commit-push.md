# Commit and Push

Use when the user asks for commit + push, or when it is a stage of a full cycle. These mutate the repo. Inspect first, and respect ownership of changes you did not make.

## Before committing

1. Check the branch, `git status`, the staged diff, and the unstaged diff. Record anything already staged and leave it alone.
2. Confirm the change is ready. Run the checks the repo requires. Do not claim unrun checks passed.
3. Review every path. If ownership is unclear, leave that path out and say so.
4. Stage explicit paths only (`rules/aodd/git-ops.md`). Prove the commit contains exactly those paths (for example inspect `git diff --cached --name-only`). If that cannot be proven without touching pre-existing staged work, stop.
5. Use the repo's commit convention and make one scoped commit. Verify the hash and the clean worktree afterward.

## Before pushing

1. Push only the requested branch. A normal push does not authorize `--force`, `--force-with-lease`, a history rewrite, or deleting a remote branch.
2. If the push is non-fast-forward or the branch diverged, stop and report. Do not rebase, merge, or force-push silently.
3. Verify the push on the remote and report the branch and hash.

A commit + push request does not authorize a PR, a merge, a tag, a hosted release, or a deploy. Report those as NOT RUN. If a repo helper does several of these at once, use narrower commands or stop and explain the mismatch.
