# Changelog / Release Automation

Sub-file of `rules/coding.md`; read when cutting a release.

**`git-cliff`** (`brew install git-cliff`) is the standard tool for `CHANGELOG.md` generation and GitHub Release notes on any project that publishes tagged releases — parses the Commit Style types above via `cliff.toml`'s `commit_parsers` (feat→Added, fix→Fixed, refactor/perf→Changed, docs→Documentation; test/chore/build/ci/style skipped). Skip it for repos with no GitHub Releases, or a fork whose release pipeline is upstream's to own — check for an existing release script before adding one.

**Release gate (before the bump and tag; one place, the workflow files point here):**
1. **Security / pen test:** secret scan, dependency vulnerabilities, SAST; for anything reachable from outside (web app, API, open port), test the auth and trust boundaries as an attacker would (`security` skill if installed).
2. **Performance:** when the project has a perf budget or the change touches a hot path: benchmark, endpoint latency/load, bundle size or Core Web Vitals against the last release. Nothing to measure → say so in the release notes, don't skip silently.
3. **Audit:** `scripts/audit.py` PASS on this diff (an earlier PASS counts if nothing changed since).
4. **Version + changelog:** semver bump, `git-cliff --tag vX.Y.Z --output CHANGELOG.md`, commit `chore(release): vX.Y.Z`, tag.

A typical per-project `scripts/release.sh` bumps the version (file convention varies: `package.json`/`pyproject.toml`/`Info.plist`/git-tag-only), runs `git-cliff --tag vX.Y.Z --output CHANGELOG.md`, tags, pushes, then `gh release create --notes "$NOTES"`.

**Never swallow `gh release create`/`gh release edit` errors with `2>/dev/null`** — capture stderr separately and print it on failure, or a broken release step silently ships empty-body releases. Also guard `$NOTES` length — GitHub's release-body cap is 125000 chars, and a wrong previous-tag range can silently dump full project history past that limit and 422 every time.

**Don't call `release.sh --version X.Y.Z` to skip ahead in the version sequence** — always drive the bump through `major`/`minor`/`patch` so the number tracks actual accumulated changes. `--version` exists for genuine exceptions (aligning to an externally-mandated number, recovering from a botched tag), not to make a release "feel" more milestone-worthy. If `--version` is genuinely the right call, say why in the release commit message.
