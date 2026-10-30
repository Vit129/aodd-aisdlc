---
name: delivery-workflow
description: Use when asked to carry a software project through delivery stages such as dev/preview, test, commit and push, release, deploy, or recovery. Runs only the requested stages, follows the repository's own entrypoint, and stops before publishing if a gate fails.
metadata:
  short-description: Run project delivery stages safely
---

# Delivery Workflow

Run the delivery stages the user asked for, through the repository's own entrypoint (`make start`, `npm start`, or the script it calls). Trace the entrypoint before running it. A menu label or a final success message does not prove what ran.

## Required in every repo

These are the setup targets. A repo that lacks one is fixed in its own repo, not worked around in the skill.

1. Entrypoint: `make start` or `npm start` (or the repo's documented equivalent).
2. Graphify: `graphify-out/` present and refreshed before any commit or release.
3. Dev/preview: a local dev or isolated preview that has no release side effects.
4. Release gate: a declared test command (and build) that must pass before anything is published. If QA exists, its test layers are named in the repo's adapter.
5. Version scheme: semver in every surface that shows it, plus a build number where the app needs one.
6. Living docs (PRODUCT / ARCHITECTURE / DESIGN / CONTEXT) updated before a release starts when the change affects them.

If the repo is missing one of these, report it as a gap. Do not invent the missing piece.

## Stages

Each stage is requestable on its own. A full cycle composes them and keeps each boundary.

| Stage | Boundary |
|---|---|
| Dev / preview | Local only. No commit, tag, or deploy. |
| Test / QA | Runs the declared gates and reports evidence. Does not change code unless asked. |
| Commit + push | Graphify refresh, then scoped commit and push to the intended branch. Stops before merge. |
| Merge | Only in a full cycle or when asked. Uses the repo's review/CI policy. Never `--admin`. |
| Release | Version candidate → metadata commit → checks on that exact commit → push + tag → GitHub release page. |
| Deploy / install | Deploys the identified release to a named target, then verifies it is serving. |
| Recovery | Finds which boundary completed and finishes only the missing step for the same candidate. |

## Version contract

Show the preflight table before any mutation:

```
current:  1.0.0  (build 7)
patch:    1.0.1  (build 8)
minor:    1.1.0  (build 8)
major:    2.0.0  (build 8)
skip:     1.0.0  (build 8)   <- semver unchanged; build +1 only if the repo has one
```

Compute the candidates with the repo's own function (for example the repo's own version helper or release script), not by hand. If the repo has no build number, show `(no build number)`.

| Choice | Semver | Build | Changelog | Tag + GitHub release | Deploy | Ends at |
|---|---|---|---|---|---|---|
| `patch` / `minor` / `major` | new | +1 if present | new release entry | yes | yes, if requested | tag + release page (and a verified deploy when requested) |
| `skip` | unchanged | +1 if present | add entry under `Unreleased`; no version heading | **no** | yes, if requested | merged + deployed + live matches the intended commit |

Rules that follow from this:
- `skip` never creates or moves a tag and never creates a release page. The deployed build is identified by its commit SHA and build number.
- A published tag is never moved or deleted. `git tag -f` and `git push --force` on a tag are not allowed.
- A repo whose helper cannot express `skip` (for example, patch-only) reports `skip` as unsupported, not as an approximation.

## Candidate and rollback

- Before the tag is pushed, the version and build are candidates. A failure can revert the local metadata; nothing has been published.
- After the tag is pushed, do not rewind. Resume the same candidate until the release page and the deploy are verified, or report the exact state and stop. Do not reuse the number for a different commit.
- Record the candidate (version, build, source commit, target) before the first mutation. Where the repo has a release manifest (for example `release-manifest.json`), use it. Otherwise state it in the report.

## Gates and failures

- Before publishing (tag push, release, deploy), build and the release-gate tests must pass on the exact commit being published. A failure stops the publish. It does not block a WIP commit on a feature branch or local development.
- Known-failing tests are declared in the repo's adapter with a reason. An undeclared failure is a failure. A skipped test is reported as NOT RUN, not PASS.
- If the repo's order differs from this (for example, it merges to main before its final build), report it as a known gap with file:line evidence. Do not rewrite the repo's route without the user's decision.

## Version-surface parity

Before publishing, every surface that shows the version must match the candidate: package/manifest files, app constants, changelog, and generated notes. Also check any shared backend or package:
- Shared package: the pinned commit matches the one the release was built against.
- App and daemon: the marketing version, build, and daemon/IPC protocol match what is installed. A mismatch blocks the release.

## Done means

- Semver release (`patch`/`minor`/`major`): remote tag points to the release commit, the GitHub release exists with the same tag, and the deployed build reports the candidate version. Check the live target, not only the command's exit code.
- `skip`: the commit is merged to main, the deploy is verified against that commit, and no tag or release was created.
- Report each stage as PASS, FAIL, BLOCKED, or NOT RUN, with the command and output. Finish with the last completed version and build, plus any pending candidate and its missing step.

## Approval and external effects

- A requested stage authorizes only that stage. A full cycle authorizes its merge, release, and deploy only in the target it names. Anything outside the plan needs a stop and a question.
- Never use `--admin` to merge, never force-push a tag, and never let a default select production. State the deploy target before deploying.
- Do not spend money, contact outside parties, or migrate production data without explicit approval.

## References

- Tracing an entrypoint: [references/script-tracing.md](references/script-tracing.md)
- Dev / preview and test: [references/dev-test.md](references/dev-test.md)
- Commit and push: [references/commit-push.md](references/commit-push.md)
- Release and deploy: [references/release-deploy.md](references/release-deploy.md)
- Full cycle: [references/full-cycle.md](references/full-cycle.md)
- Partial failure and recovery: [references/recovery.md](references/recovery.md)
