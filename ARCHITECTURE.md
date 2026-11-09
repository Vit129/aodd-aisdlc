# Architecture

aodd-aisdlc is an installable package for Claude Code and OpenAI Codex. AODD is the operating contract (a human decides, cheap models do the mechanics, an independent cross-family auditor checks the work on demand); ai-sdlc is the Dev/QA feature workflow with three approval gates. `./install.sh` copies the files into an agent home; the files in this repo are what gets installed.

## Layout

- `rules/`: the AODD contract and the ai-sdlc workflow spine (inlined into Codex `AGENTS.md`, imported by Claude `CLAUDE.md`).
- `skills/`: chief-of-staff, ai-sdlc (with `references/`), agent-ops, reverse-engineer-anything.
- `agents/`: auditor and advisor subagent definitions.
- `hooks/`: core hooks (done-gate, auditor-readonly, skill-capture-nudge, secret-read-guard, coding-rules-gate, dirty-branch-switch-guard, graphify-guard, work-log, subagent-rules). `_aodd_paths.py` (path resolver) and `_aodd_secrets.py` (credential shapes) are imported by the others.
- `scripts/`: `audit.py` (cross-family audit), `check_agy_proposal.py`, `skill_learning_report.py` (curator), `agent_ops_gather.py`, `rea_check.py`, and the install test.
- `optional/<module>/{skills,rules,hooks,scripts,schedules}/`: modules the installer adds only when chosen (`agent-memory`, `schedules`). A core file never imports from `optional/`.
- `adapters/`: other-tool adapters that load the hooks by path.
- `docs/`: the skill-learning procedure.
- `scripts/git-hooks/`: `pre-commit` (neutrality scan) and an optional `post-merge` (re-install after main changes).
- `install.sh` and `install-agy.sh`: installers. `install.sh` never deletes; a differing file is kept as `<file>.aodd-bak`.

## Public API

Other tools load these hooks by path, so the names are a contract. `hooks/test_public_api.py` fails if one disappears; renaming or removing one is a breaking change (major version). The list is in `AGENTS.md` under "Public API".

## Conventions

- Python is standard library only (3.10+). Hooks fail open. Every hook and script has a `test_*.py` next to it. Tests use stub models, never network or real CLIs.
- State lives only under `AODD_HOME` (default `~/.aodd`). Read paths only through `hooks/_aodd_paths.py`.

## Structure deviations

- §1 tests: tests sit next to each hook and script (`hooks/test_*.py`, `scripts/test_*.py`, `adapters/test_*.py`, `optional/*/hooks/test_*.py`) instead of a `tests/` directory. The installer copies hooks flat into the agent home, so a separate `tests/` tree would have to be excluded from every install. Revisit when `install.sh` can skip a test directory without special-casing.

## Commit preparation

`scripts/graphify_commit.py` provides synchronous refresh, tracked graph staging, and a prepared-index commit. The release runner reuses its preparation after version/changelog edits. Delivery and ai-sdlc use the same-commit contract for normal, docs, GREEN, and release commits. Refresh failure blocks commit/push; only the redundant Graphify post-commit hook is suppressed.
