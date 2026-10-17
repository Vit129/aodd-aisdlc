# Changelog

All notable changes to aodd-aisdlc are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and it follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).
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

