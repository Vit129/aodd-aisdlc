# Changelog / Release Automation

Sub-file of `rules/coding.md`; read when cutting a release.

**`git-cliff`** (`brew install git-cliff`) is the standard tool for `CHANGELOG.md` generation and GitHub Release notes on any project that publishes tagged releases — parses the Commit Style types above via `cliff.toml`'s `commit_parsers` (feat→Added, fix→Fixed, refactor/perf→Changed, docs→Documentation; test/chore/build/ci/style skipped). Skip it for repos with no GitHub Releases, or a fork whose release pipeline is upstream's to own — check for an existing release script before adding one.

**Pre-Release Gate (Mandatory before bumping & tagging):**
Every release or deploy must complete four checks before git-cliff runs:
1. **Security Scan:** Secrets scan, SAST, dependency vulnerability checks.
2. **Performance Check:** Benchmark runs, endpoint latency/load tests, or bundle/CWV checks.
3. **Cross-Family Audit (`scripts/audit.py`):** Independent review of diff vs brief (must be PASS).
4. **Version Bump & Changelog:** Drive bump through `major`/`minor`/`patch` (in `package.json`, `pyproject.toml`, `version.json`, or `Info.plist`), run `git-cliff --tag vX.Y.Z --output CHANGELOG.md`, tag, and push.

A typical per-project `scripts/release.sh` bumps the version (file convention varies: `package.json`/`pyproject.toml`/`Info.plist`/git-tag-only), runs `git-cliff --tag vX.Y.Z --output CHANGELOG.md`, tags, pushes, then `gh release create --notes "$NOTES"`.

**Never swallow `gh release create`/`gh release edit` errors with `2>/dev/null`** — capture stderr separately and print it on failure, or a broken release step silently ships empty-body releases. Also guard `$NOTES` length — GitHub's release-body cap is 125000 chars, and a wrong previous-tag range can silently dump full project history past that limit and 422 every time.

**Don't call `release.sh --version X.Y.Z` to skip ahead in the version sequence** — always drive the bump through `major`/`minor`/`patch` so the number tracks actual accumulated changes. `--version` exists for genuine exceptions (aligning to an externally-mandated number, recovering from a botched tag), not to make a release "feel" more milestone-worthy. If `--version` is genuinely the right call, say why in the release commit message.
