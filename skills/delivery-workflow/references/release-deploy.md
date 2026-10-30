# Release and Deploy

Use for a release+deploy stage, a deploy-only stage, or a skip. The version contract is in [SKILL.md](../SKILL.md#version-contract). This file covers the order of operations.

## 1. Preflight

- Trace the entrypoint and every helper it calls (see [script-tracing.md](script-tracing.md)). Check for dry-run and resume support, and what each one skips or changes.
- Check branch, worktree, local and remote refs, tags, hosted releases, and the live revision.
- Show the preflight version table before any mutation: last completed version and build, the candidate for each choice, and the target. For `skip`, show `semver unchanged` and the build number if the repo has one.
- Look for a pending candidate: a version written to the repo's release manifest or state, a tag without a release, a release without a verified deploy, or a live version that differs. If one exists, resume it only when recovery was requested. Otherwise report it and ask. Do not allocate a new number over it.
- If the request does not name the choice (patch, minor, major, or skip) or the target, ask once. Never trust a non-TTY default.

## 2. Candidate and record

Before any version file changes, record the candidate: baseline, semver, build (if any), bump type, source commit, shared dependency commit, target, and stage status. Use the repo's release manifest if it has one. If it has none, keep the record in the report and, if the repo allows, a file under the repo's ignored state directory.

## 3. Validate the exact commit

1. Prepare the metadata (version fields, build number, changelog, generated notes) and commit it as a local candidate commit. Stage explicit paths only.
2. Run the release gates on that exact commit: build, the test command the repo declares as its release gate, and any security or audit check the repo requires.
3. A failed gate stops the publish. Keep the candidate. Fix the source and metadata, make a new local candidate commit, and rerun the affected gates. Do not roll back metadata and bump again.

## 4. Publish (semver release only)

1. Push the validated commit and create the tag on that same commit.
2. Create the hosted release for that tag, with notes generated from the previous completed tag.
3. Never move, delete, or force-push a published tag. A tag that already exists for another commit is a stop condition.

`skip` does not reach this step. It creates no tag and no release page.

## 5. Deploy or install

1. Name the target before starting. Stage before production when both exist. Production is a separate approval boundary unless the user named it.
2. Deploy the artifact built from the same commit as the candidate. Do not deploy a different commit under the same identity.
3. A local app install or a service restart counts as production-like. Warn before any restart that stops running work, and get approval if the request did not clearly include it.
4. Do not run an install that replaces the running app without a backup of the old one, unless the repo's install path makes one.

## 6. Verify the live target

- Confirm the live version, build, and commit match the candidate. Check the layer the project exposes: the served version, a health endpoint, or the installed app and daemon.
- A CLI exit code proves only that the command finished.
- For components that must match each other (front end and back end, app and daemon, package and consumer), check each one and check that they agree.
- For `skip`: the merged commit is on main, and the live target reports that commit. No tag or release is expected.
- For a semver release: the remote tag points to the release commit, the hosted release exists, and the live target reports the candidate version.

Mark the candidate complete only after every configured target verifies. Until then, the baseline does not advance.

## 7. Report

Give each stage PASS, FAIL, BLOCKED, or NOT RUN, with the command and output. Give the version and build at each release-bearing stage, the target, the live evidence, and the last completed version. If a candidate is still pending, give its exact identity and the next missing step.
