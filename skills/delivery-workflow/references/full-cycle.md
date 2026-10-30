# Full Cycle

Use when the user asks for the complete cycle: change → checks → commit → merge → release (or skip) → deploy → verify. The order below is the only route. A repo helper that does things in a different order is not run as is (see [script-tracing.md](script-tracing.md) §5). Use narrower steps that keep this order, or stop and report.

## 1. Select the cycle

- Confirm the requested choice: `patch`, `minor`, `major`, or `skip`. If it is missing and the change does not make it clear, ask once.
- Show the preflight table from [release-deploy.md](release-deploy.md) §1 and the target. Get explicit approval for that candidate before mutating anything.
- If a candidate is pending from an earlier run, stop and ask whether to resume it or defer this cycle.

## 2. Docs before code

Update the living docs the change affects (for example product, architecture, design, or context files) before running the start or release entrypoint. For a semver release, do not hand-edit CHANGELOG.md; the release step generates it. On `skip`, the `Unreleased` entry is written by hand (§5). If the change alters the release contract itself, update that contract first.

## 3. Build, test, Graphify

1. Implement the approved change. Keep its tests with it.
2. Run the dev or preview path for a person to inspect, if the repo has one.
3. Run the repo's required checks. If the repo has no automated QA, record that and get the named human acceptance.
4. Refresh Graphify before the commit (required setup; see commit-push.md).

## 4. Commit and merge

1. Commit the feature with explicit paths (see [commit-push.md](commit-push.md)). Commit graph output separately.
2. Push the feature branch. Merge to main only through the repo's review or CI path, and only after its required checks pass. Never use an admin or bypass flag.
3. Fetch main and confirm the merged commit is the one you expect. Everything after this step works from that commit.

## 5. Release or skip

**Semver (`patch`, `minor`, `major`):**
1. Prepare the candidate metadata and changelog as a local commit on the merged main (see [release-deploy.md](release-deploy.md) §3).
2. Run the release gates on that exact commit.
3. Push the commit, create the tag, create the hosted release (§4).
4. Deploy or install the same commit, then verify the live target (§5, §6).

**`skip`:**
1. On `skip`, add the change to CHANGELOG.md under an `Unreleased` heading, the same as any other change. Do not add a version heading, create a tag, or create a release page.
2. Run the build and release-gate tests on the merged commit.
3. Deploy or install that commit, then verify the live target reports it.
4. Report the build number if the repo has one. No tag, no release page.

## 6. Report

Report each stage PASS, FAIL, BLOCKED, or NOT RUN, with the commit, the version or build, the target, and the live evidence. End with the last completed version and build, and any pending candidate with its next missing step.
