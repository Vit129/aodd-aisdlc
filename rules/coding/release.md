# Changelog / Release Automation

Sub-file of `rules/coding.md`; read when cutting a release.

The order of stages, the version contract (patch / minor / major / skip, build numbers, rollback of an unfinished candidate), and the done criteria live in the `delivery-workflow` skill. This file keeps the tooling rules and gates that apply to every release, whichever skill or script runs it. When the two disagree, the skill wins for the order of stages and this file wins for tooling.

**`git-cliff`** (`brew install git-cliff`) is the default tool for `CHANGELOG.md` generation and GitHub Release notes on new or unconfigured tagged-release pipelines. It parses the Commit Style types above via `cliff.toml`'s `commit_parsers` (feat→Added, fix→Fixed, refactor/perf→Changed, docs→Documentation; test/chore/build/ci/style skipped). Keep an existing, maintained changelog or release tool when it is the project's established source of release notes and it generates the correct range from the last completed release. Do not migrate tools as part of an ordinary release. Skip changelog generation for repos with no GitHub Releases, or for a fork whose release pipeline belongs to upstream. Check for an existing release script before adding one.

**Release gates (run on the exact committed candidate, before pushing the commit or tag):**
1. **Security:** secret scan, dependency vulnerabilities, SAST. For anything reachable from outside (web app, API, open port), test the auth and trust boundaries, at least the surfaces Phase 2 flagged (`security` skill if installed).
2. **Performance:** when the project has an NFR or perf budget, or the change touches a hot path, measure against it (k6 with p95 and error-rate thresholds for an API; bundle size or Core Web Vitals for a front end) and compare with the last release. If there is nothing to measure, say so in the release notes. Do not skip silently.
3. **Audit:** `scripts/audit.py` PASS on the final release diff. An earlier PASS counts only if nothing relevant has changed since. Rerun after any metadata change.
4. **Version and changelog:** prepare the metadata and changelog, create the local release commit, then run the build and checks and the audit against that commit. Only then push the commit and create the tag. Use `git-cliff --tag vX.Y.Z --output CHANGELOG.md` unless a maintained tool is in use, as above.

**Deployment integrity (all production targets):**
- **One release identity:** the version shown by the app or package, the Git tag, the changelog, the hosted release, and the deployed artifact must all refer to the same source commit. If a manifest is needed to establish this, record the source commit and any shared dependency commit in it.
- **Reproducible inputs:** build the committed source with locked dependencies. A build that reads another local repo or a generated input must pin and record that input, or verify it is clean and in sync before publishing. Never deploy bytes from uncommitted or moving sources.
- **Validate before publishing:** nothing is pushed, tagged, released, or deployed until the gates above pass on the committed candidate. If the metadata or source changes after a check, rerun the affected checks and the audit.
- **Deploy only an identified release:** a deploy-only action deploys the artifact of a tagged or released source to a named target. Deploying an arbitrary snapshot is a separate, labelled action and stays out of the production path.
- **Retry the same release:** inspect which version, commit, tag, hosted release, and deployment already exist, and complete the missing step for that same version. Never bump to a new number because an earlier publish or deploy step failed. Never force-push or move a published tag, and never force-push a production ref to recover.
- **Preserve ambiguous work:** if a failure happens before the release commit and the worktree holds partial metadata edits, do not infer ownership from filenames and do not overwrite them. Report the affected paths and a safe recovery path.
- **Verify the live target:** after a deploy, check that the live target reports the intended version and source identity (or an equivalent health or revision signal). A successful CLI exit is not proof.
- **Skip:** `skip` keeps the semver unchanged and creates no tag and no GitHub release page. It deploys the already-merged commit only when asked, and that commit's build number, if the repo has one, is the only identity change. The skill defines the details.

**Never swallow `gh release create` or `gh release edit` errors with `2>/dev/null`.** Capture stderr and print it on failure, or a broken step ships an empty-body release silently. Also guard `$NOTES` length. GitHub caps a release body at 125000 characters, and a wrong previous-tag range can dump the full project history past that cap and fail every attempt.

**Do not call `--version X.Y.Z` to skip ahead in the version sequence.** Drive the bump with `major`, `minor`, or `patch` so the number tracks the real changes. `--version` is for genuine exceptions only, such as matching an externally required number or recovering a botched tag. If it is the right call, say why in the release commit message.
