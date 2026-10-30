# Changelog

All notable changes to aodd-aisdlc are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and it follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).
## [0.6.1] - 2026-10-30

### Added
- Add rea module so reverse engineering is one install away on every agent (`c7022dd`)
- Make REA core and add rea_check.py to check and update it (`9f0acfc`)
- Automate versioned releases (`6164012`)

### Changed
- Consolidate decoupled pattern into single dev-qa-pattern canonical file (`e6cb28c`)

### Documentation
- Add decoupled core-ui-translator pattern and QA architecture guard (`4bcc919`)
- Extend decoupled pattern with behavioral QA Playwright standards (`166b40f`)
- Update NOTICE with Antigravity co-author (`db228ea`)
- Define release deployment integrity (`edefc68`)

### Fixed
- Drop MultiEdit from verifier's disallowed tools (`9c14325`)

## [0.6.0] - 2026-10-23

### Added
- Adopt ponytail v5 scope, review method and subagent rules (`9c4bf49`)

### Documentation
- Add design check, whole-repo audit, invariants in Phase 2 (`4806a02`)

## [0.5.0] - 2026-10-22

### Documentation
- Design subagents, living-docs sync, delivery gate (agy draft) (`01d9e24`)
- Keep role limits, scope subagents, one home for the release gate (`4e55ab1`)
- K6 NFRs from design, traceability at sign-off, terms after Gate 1 (`3eebd7d`)
- Pick the path by what changes, weigh it by a look at the code (`9253a41`)
- Give every path a QA side, not only dev (`690f85c`)

## [0.4.0] - 2026-10-22

### Added
- Resume unfinished work at session start, INDEX by script, read-before map (`cc7fb10`)
- Detect coding agents on the machine (`024d4da`)
- Inline the ponytail ladder and advisor tiering (`d0deae8`)

### Changed
- Drop the mattpocock-skills dependency (`220b015`)

### Documentation
- Once-guard every block path; gate plugin hooks on the project (`5c0c149`)
- Env switches also leak into installer subprocesses (`d870d72`)
- Relicense from MIT to Apache-2.0 (`2ff1b90`)
- Identity rewrite needs --replace-message for Co-authored-by trailers (`e3a4ba3`)
- Credit Claude as contributor (`533fe7e`)
- Remove --dry-run from install instructions (`43083e4`)
- List open PRs before a history rewrite (`86e78c7`)
- Say how to update in the Install section (`8577ecc`)
- Move audit, skill capture and Codex details to docs/ (`09a3ed4`)
- AODD stands for AI Orchestration Driven Development (`43e1bfa`)

### Fixed
- Ask for the medium audit once, not on every stop (`fe89504`)
- Antigravity adapter test clears AODD_NO_BACKUP before the install it checks (`192bc51`)
- Point workflow guide at the in-house handoff.md format (`506c7da`)
- Count typed slash commands; grep sub-command names when retiring (`c7ca74f`)

## [0.3.6] - 2026-10-21

### Added
- --no-backup / AODD_NO_BACKUP=1 opt-out for .aodd-bak files (`b6cce38`)

### Changed
- Install the ai-sdlc phase files under the skill, not under rules/ (`4fa3c1a`)

### Documentation
- Load workflow phases and playwright detail only when reached (`f26b6d2`)
- Point phase files at the file that now holds each referenced section (`9ada1d7`)
- Name the progress spec wherever a phase cites the Incremental Update Rule (`1bd4cea`)
- Link the hallmark sources by URL and check every skills/ link (`5ff5f14`)

### Fixed
- Audit Medium+ work per task, not per session (`dda2709`)
- Bake AODD_* from Claude settings env so launchd jobs use the real paths (`0996d06`)
- Keep the Phase 2 closing steps in the file that is always loaded (`c7239ad`)
- Load the Reuse-Table whenever it is mandatory, not only on reuse (`64d6fc7`)
- One trigger for the Reuse-Table, no dangling Step 0, Gate 1 by task size (`73f1c30`)

## [0.3.5] - 2026-10-17

### Documentation
- Verify each PR is merged before deleting its branch (`2b361fa`)

### Fixed
- Split the diff budget so a big new file cannot hide the edit; keep same-day audits as history (`bf5d121`)

## [0.3.4] - 2026-10-17

### Documentation
- Update AODD definition to AI Orchestrator Driven Development (`060a390`)
- Resolve paths via _aodd_paths, stash only the source to prove RED (`d11f558`)

### Fixed
- Resolve AODD_STATE through _aodd_paths so ${VAR} expands like the Python hooks (`ee4eb29`)

## [0.3.3] - 2026-10-17

### Fixed
- Expand $HOME in AODD_STATE (unexpanded settings env) (`1ca4dea`)
- Disambiguate audit session IDs, preserve diff stat, unify state and adapter hooks (`108c1ad`)

## [0.3.2] - 2026-10-17

### Added
- Split extra files into row and section chunks (`ecc7b26`)

### Documentation
- Unexpanded settings env; latest-report by name date (`384e618`)

### Fixed
- Expand $VARS and ~ in AODD_* env values (`b40072e`)
- Pick the audit by its date in the name, then mtime (`8b55da0`)

## [0.3.1] - 2026-10-17

### Added
- Multi-root memory, digest templates, report kinds, antigravity usage, work-log fallback (`0d6b80e`)

## [0.3.0] - 2026-10-17

### Added
- Add coding, product-design, gui, testing rules and link them from aodd/ai-sdlc (`077d5c4`)
- Add dev, QA, design, safety skills and the optional agent-memory module (`39f3d38`)
- Neutral guard hooks, work log and curator scripts (`16195f9`)
- Optional modules agent-memory and schedules (`f1e3c3a`)
- Add Antigravity adapter, installer, tests, and documentation (`7ef258a`)
- --agy runs install-agy.sh (Antigravity) (`db30138`)

### Documentation
- Drop remaining dated provenance (`3c59a84`)

### Fixed
- Back up AGENTS.md once, only when the aodd block changes it (`f444358`)
- Auto-install is opt-in (AODD_AUTO_INSTALL=1) (`e8ccdb3`)

## [0.2.0] - 2026-10-17

### Added
- Env layout, public API, agent-ops extension and optional post-merge hook (`426c60f`)

### Fixed
- Never copy scripts/git-hooks into the target home (`bdbb4c6`)
- Chmod only the files it copied, never the host's own hooks (`851e334`)
- Listing tags and stashes is a read (`d22884c`)

## [0.1.0] - 2026-10-16

### Added
- Initial release: AODD + ai-sdlc for Claude Code and Codex (`d75adf4`)
- Done-gate and skill-capture read Codex rollouts; auditor deny verified live (`bb16c85`)

