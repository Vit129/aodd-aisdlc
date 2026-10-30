# Recovery

Use after a test, commit/push, release, or deploy step failed partway. Start by observing state. Do not rerun a version-bumping command to find out what happened.

## 1. Establish the actual state

Check each surface and record what it shows:
- Worktree, staged diff, and local/remote branch heads.
- Version files, changelog top entry, and generated notes.
- Tags and the commit each one points to.
- Hosted release (and its assets) and the deployed target's live version.
- The release manifest or pending-release marker, if the repo has one.

Do not assume the last printed line matches remote state. A dry-run may not model every side effect, so check its implementation before you trust it.

## 2. Choose the narrowest safe step

- **Before the tag is pushed:** the candidate is still local. Keep it. Revert only local metadata that this run wrote, and never overwrite user edits.
- **Checks failed after the merge:** run the gates on the merged commit. Do not tag or deploy yet.
- **Commit pushed, tag missing:** confirm the commit is the intended release commit on the expected branch. Create the tag only if the release was authorized.
- **Tag pushed, release or deploy failed:** resume the same candidate (same version, same commit). Create only the missing release or deploy step.
- **Deploy failed or target unhealthy:** check whether the target changed. Roll back only with the repo's documented mechanism, to the last known good identity.
- **Ownership or identity is ambiguous:** stop and ask. Do not pick a new version.

## 3. Never

- Start a new version while a candidate is still pending.
- Move, delete, or force-push a published tag.
- Hide an error or report success from an exit code alone.
- Retry more than the single missing idempotent step. If that retry fails, stop and report.

## 4. Report

State the last confirmed good stage, the failed stage with its output, whether production changed, the current version/build/commit identity, and the next safe action. Mark what was verified and what was inferred.
