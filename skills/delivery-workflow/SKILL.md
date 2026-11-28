---
name: delivery-workflow
description: Use after coding or when delivering any file change through preview, test, commit, push, release, deploy or recovery. Non-coding changes use skip without a version bump unless requested otherwise. Runs authorized stages through the repository entrypoint and stops publication on a failed gate.
metadata:
  short-description: Run project delivery stages safely
---

# Delivery Workflow

Run the delivery stages the user asked for, through the repository's own entrypoint (`make start`, `npm start`, or the script it calls). Trace the entrypoint before running it. A menu label or a final success message does not prove what ran.

The parent contract routes coding tasks here automatically; other file changes use this same process in `skip` mode.
Entering the workflow is not permission to merge, publish or deploy: run only the authorized stages and report pending ones.

## Required in every repo

These are the setup targets. A repo that lacks one is fixed in its own repo, not worked around in the skill.

1. Entrypoint: `make start` or `npm start` (or the repo's documented equivalent).
2. Dev / test server: a local dev server and, where the repo has one, a separate test server on its own port. Neither has release side effects.
3. Release gate: declared verification requirements, including the test command and build where the project requires them. Evidence reuse follows `rules/ai-sdlc-workflow.md` § Verification evidence. If QA exists, its test layers are named in the repo's adapter.
4. Version scheme: semver in every surface that shows it, plus a build number where the app needs one.
5. Living docs (PRODUCT / ARCHITECTURE / DESIGN / CONTEXT) updated before a release starts when the change affects them.
6. Changelog: `CHANGELOG.md` exists, and its generator is declared (`cliff.toml` / git-cliff or the repo's own tool). Every commit that changes behaviour adds its entry; a semver release generates the version heading, `skip` writes under `Unreleased`. Only one generator per repo.

If the repo is missing one of these, report it as a gap. Do not invent the missing piece. Per-repo values (commands, ports, version files, changelog generator) and the gaps found in real repos are in [references/project-adapters.md](references/project-adapters.md).

## Stages

Each stage is requestable on its own. A full cycle composes them and keeps each boundary.

| Stage | Boundary |
|---|---|
| Dev / preview | Local only. No commit, tag, or deploy. |
| Test / QA | Runs the declared gates and reports evidence. Does not change code unless asked. |
| Commit + push | Scoped commit and push to the intended branch. Stops before merge. |
| Merge | Only in a full cycle or when asked. Uses the repo's review/CI policy. Never `--admin`. |
| Release | Version candidate → metadata commit → validate evidence for that candidate → push + tag → GitHub release page. |
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
- Code and shipped workflows, skills, rules, or configuration that change agent behavior require this release workflow and a `patch` / `minor` / `major` choice from the user. Pure wording or documentation changes default to `skip`. An explicit version request takes precedence. Apply the repository package version to its shipped workflow and skill changes; preserve any existing independent component version scheme. A missing required choice is asked once.
- `skip` never creates or moves a tag and never creates a release page. The deployed build is identified by its commit SHA and build number.
- A published tag is never moved or deleted. `git tag -f` and `git push --force` on a tag are not allowed.
- A repo whose helper cannot express `skip` (for example, patch-only) reports `skip` as unsupported, not as an approximation.

## Candidate and rollback

- Before the tag is pushed, the version and build are candidates. A failure can revert the local metadata; nothing has been published.
- After the tag is pushed, do not rewind. Resume the same candidate until the release page and the deploy are verified, or report the exact state and stop. Do not reuse the number for a different commit.
- Record the candidate (version, build, source commit, target) before the first mutation. Where the repo has a release manifest (for example `release-manifest.json`), use it. Otherwise state it in the report.

## Gates and failures

- Before publishing (tag push, release, deploy), verify covering PASS scenario results and any explicitly required project gates for the candidate. Reuse valid results as defined in `rules/ai-sdlc-workflow.md` § Verification evidence; run only missing or invalidated checks, with no separate Test-Before-Deliver run. A required build still needs an identified artifact from the delivered inputs. A failure stops the publish. It does not block a WIP commit on a feature branch or local development.
- Known-failing tests are declared in the repo's adapter with a reason. An undeclared failure is a failure. A skipped test is reported as NOT RUN, not PASS.
- If the repo's order differs from this (for example, it merges to main before its final build), report it as a known gap with file:line evidence. Do not rewrite the repo's route without the user's decision.

## Version-surface parity

Before publishing, every surface that shows the version must match the candidate: package/manifest files, app constants, changelog, and generated notes. Also check any shared backend or package:
- Shared package: the pinned commit matches the one the release was built against.
- App and daemon: the marketing version, build, and daemon/IPC protocol match what is installed. A mismatch blocks the release.

## Tag and GitHub release

- Verify the tag on the remote: `git ls-remote --tags origin <tag>` must show the release commit. Verify the release page: `gh release view <tag>` must show the same tag and the changelog notes.
- Find out where the release is created before relying on it. If the repo has no workflow that runs on tag push, the release page exists only when the machine that ran the helper completed it. Check the repo's workflows for a tag trigger, and do not assume CI published it.
- A helper that moves an existing tag (`git tag -f`, `git push --force` of a tag) breaks the version contract. Report it as a gap in the repo's adapter and do not run it.

## Release procedure and tooling

This section is the single source for release and deploy requirements. The references `rules/coding/release.md` and `references/release-deploy.md` point here.

### Preflight

- Trace the entrypoint and every helper it calls (see [references/script-tracing.md](references/script-tracing.md)). Check for dry-run and resume support, and what each one skips or changes.
- Check branch, worktree, local and remote refs, tags, hosted releases, and the live revision.
- Show the preflight version table before any mutation: last completed version and build, the candidate for each choice, and the target. For `skip`, show `semver unchanged` and the build number if the repo has one.
- Look for a pending candidate: a version written to the repo's release manifest or state, a tag without a release, a release without a verified deploy, or a live version that differs. If one exists, resume it only when recovery was requested. Otherwise report it and ask. Do not allocate a new number over it.
- If the request does not name the choice (patch, minor, major, or skip) or the target, ask once. Never trust a non-TTY default.

### Candidate and validation

- Before any version file changes, record the candidate: baseline, semver, build (if any), bump type, source commit, shared dependency commit, target, and stage status. Use the repo's release manifest if it has one. If it has none, keep the record in the report and, if the repo allows, a file under the repo's ignored state directory.
- Prepare metadata (version fields, build number, changelog, generated notes) and commit it as one local candidate commit. Stage explicit paths only; see [references/commit-push.md](references/commit-push.md).
- Match existing PASS scenario and required gate results to that candidate using `rules/ai-sdlc-workflow.md` § Verification evidence. Record the tested revision, relevant inputs and any unchanged inputs carried forward from an earlier revision. Run only missing or invalidated checks. If a build is required, identify the artifact built from candidate inputs and include any security or audit check required by the repo.
- A failed gate stops publishing. Keep the candidate. Fix source and metadata, make a new local candidate commit, and rerun affected gates. Do not roll back metadata and bump again.
- Known-failing tests are declared in the repo's adapter with a reason. An undeclared failure is a failure. A skipped test is reported as NOT RUN, not PASS.
- If the repo's stage order differs, report the gap with file:line evidence. Do not rewrite the repo's route without the user's decision.

### Release notes and gates

- `git-cliff` is the default for `CHANGELOG.md` and GitHub Release notes on new or unconfigured tagged-release pipelines. It parses commit types through `cliff.toml` (`feat` → Added, `fix` → Fixed, `refactor`/`perf` → Changed, `docs` → Documentation; `test`/`chore`/`build`/`ci`/`style` skipped). Keep an existing maintained tool when it generates the correct range from the last completed release. Do not migrate tools during an ordinary release. Skip changelog generation for repos with no GitHub Releases or a fork whose release pipeline belongs upstream. Check for an existing release script before adding one.
- Security gates include secret scan, dependency vulnerabilities, and SAST. For externally reachable apps, APIs, or ports, test auth and trust boundaries, including surfaces Phase 2 flagged.
- When the project has an NFR or performance budget, or the change touches a hot path, measure against it and compare with the last release. Use suitable measures such as API p95 and error rate, or bundle size and Core Web Vitals. If there is nothing to measure, state that in the release report.
- Propose an audit to the CEO. If approved, `scripts/audit.py --confirmed` must PASS on the final release diff. State when an audit is skipped. An earlier PASS remains valid only if relevant inputs and claims have not changed.
- Generate the version changelog with `git-cliff --tag vX.Y.Z --output CHANGELOG.md`, unless a maintained project tool is used.
- Do not swallow `gh release create` or `gh release edit` errors with `2>/dev/null`. Preserve stderr on failure and guard release notes length. GitHub caps a release body at 125000 characters.
- Do not use `--version X.Y.Z` to skip a version. Use `major`, `minor`, or `patch`. Use an explicit version only for a genuine exception, such as an externally required number or recovery from a botched tag, and state the reason in the release commit message.

### Publish, deploy, and recovery

- Before publishing, ensure every version surface (manifest, app constants, changelog, hosted release, and deployed artifact) refers to the same source commit. Record shared dependency commits when needed.
- Build committed source with locked dependencies. Pin and record any generated or external local input, or verify it is clean and synchronized. Never deploy bytes from uncommitted or moving sources.
- For a semver release, push the validated commit, create its tag on that commit, then create the hosted release using notes from the previous completed tag. A tag already pointing to another commit is a stop condition.
- `skip` creates no tag or release page. Deploy the already-merged commit only when asked, identified by commit SHA and build number if present.
- Name the target before deploying. Stage before production when both exist. Production requires explicit authorization unless the user named it. A local app install or service restart is production-like. Warn before stopping running work and get approval if the request did not include it.
- Do not install over a running app without a backup unless the install path makes one. After deployment, check `git status --porcelain`. Use `npm ci` in deploy hooks rather than `npm install` when a lockfile must remain unchanged.
- For deploy-only, deploy an identified tagged or released artifact to a named target. Arbitrary snapshots are separate, labelled actions outside production.
- On retry, inspect the existing version, commit, tag, hosted release, and deployment, then finish the missing step for that same candidate. Never bump because a publish or deploy step failed. Never force-push a production ref to recover.
- If failure occurs before the release commit and metadata edits are ambiguous, preserve them, report affected paths, and give a safe recovery path.
- Verify the live version, build, and commit (or equivalent health/revision signal). A successful CLI exit is not proof. Check every related component and confirm they agree.
- Mark a candidate complete only when every configured target verifies. Until then, the baseline does not advance.
- Report each stage as PASS, FAIL, BLOCKED, or NOT RUN with command and output, release-bearing version/build, target, live evidence, last completed version, and any pending candidate with its next missing step.

## Done means

- Semver release (`patch`/`minor`/`major`): the remote tag is on the release commit, a GitHub release carries that tag, and the deployed build shows the candidate version. Check the live target, not only the command's exit code.
- `skip`: the commit is merged to main, the deploy is verified against that commit, and no tag or release was created.
- Report every stage as PASS, FAIL, BLOCKED or NOT RUN with the command and its output, then the last completed version and build and any pending candidate.

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
