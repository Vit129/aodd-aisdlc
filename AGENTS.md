# Working on aodd-aisdlc

This repo is an installable package for Claude Code and OpenAI Codex: AODD (an operating contract where a human decides, cheap models do mechanics, and an independent cross-family auditor checks every "Done") plus ai-sdlc (a Dev/QA feature workflow with three approval gates). `./install.sh` copies it into an agent home; the files here are what gets installed. See `README.md`.

## Layout

- `rules/` the AODD contract and the ai-sdlc workflow spine (inlined into Codex `AGENTS.md`, imported by Claude `CLAUDE.md`)
- `skills/` chief-of-staff, ai-sdlc (+ `references/`), agent-ops, reverse-engineer-anything (REA; install.sh also runs `rea setup` per client, core not a module)
- `agents/` auditor and advisor subagent definitions
- `hooks/` core hooks: done-gate, auditor-readonly, skill-capture-nudge, secret-read-guard, coding-rules-gate, dirty-branch-switch-guard, graphify-guard, work-log, subagent-rules (Claude only); `_aodd_paths.py` (path resolver) and `_aodd_secrets.py` (credential shapes) are imported by the others
- `scripts/` `audit.py` (cross-family audit), `check_agy_proposal.py`, `skill_learning_report.py` (curator), `agent_ops_gather.py`, `rea_check.py` (REA version/registration check, `--update` to fix), install test
- `optional/<module>/{skills,rules,hooks,scripts,schedules}/` modules the installer adds only when chosen: `agent-memory` (memory-recall, memory-write-scan, session-start-recent) and `schedules` (`aodd_job.py` runner, `install-schedules.py`, `schedules/jobs.json` + prompt templates). Everything under a module is installed flat into the same top-level folder as core (`optional/schedules/scripts/x.py` -> `<home>/scripts/x.py`); a module hook finds `_aodd_paths.py` next to itself when installed and in the repo's `hooks/` when run from here
- `docs/` skill-learning procedure
- `scripts/git-hooks/` `pre-commit` (neutrality scan) and an optional `post-merge` (re-install after main changes, then `AODD_POST_INSTALL`; active only when `core.hooksPath` points here AND `AODD_AUTO_INSTALL=1`)
- `install.sh` installer (`--dry-run`, `--detect`, `--claude-md`, `--codex`, `--agy`, `--with <modules>`, `--all`, `--core-only`, `--yes`)

## Check your change

```bash
for t in hooks/test_*.py scripts/test_*.py adapters/test_*.py optional/*/hooks/test_*.py optional/*/scripts/test_*.py; do python3 "$t"; done    # each prints "ok"
python3 -m py_compile hooks/*.py scripts/*.py adapters/*.py optional/*/hooks/*.py optional/*/scripts/*.py && bash -n install.sh install-agy.sh
T=$(mktemp -d); CLAUDE_HOME=$T/c AODD_HOME=$T/a CODEX_HOME=$T/x ./install.sh --dry-run --all --codex   # install preview, writes nothing
```

`scripts/test_install.py` also does real installs into temp homes (core, modules, idempotency); it sets `AODD_SCHEDULES_DRY_RUN=1` so no crontab or LaunchAgent is ever written. Never run a real `install-schedules.py` in tests: point `AODD_CRONTAB` at a fake binary and `AODD_LAUNCHAGENTS_DIR` at a temp dir, as `optional/schedules/scripts/test_install_schedules.py` does.

## Conventions

- Python is standard library only (3.10+). No new dependency.
- A module never changes core behaviour: its hooks are registered only when chosen, and a core file never imports from `optional/`.
- Hooks fail open: any error means allow, and installed hook commands exit 0 if the file is gone.
- Every hook and script has a `test_*.py` next to it. Tests use stub models, never network or real CLIs.
- State lives only under `AODD_HOME` (default `~/.aodd`), moved piecemeal by `AODD_REPORTS`, `AODD_STATE`, `AODD_PLANS` (may contain `{project}`), `AODD_WORKLOG`, `AODD_MEMORY` (an os.pathsep list is allowed); also `AODD_RECALL_EXTRA` (extra globs memory-recall searches under each memory root), `AODD_DIGEST` (session digest path template with `{project}`), `AODD_PROJECT_ALIASES` (`name=alias,...`), `AODD_REPORT_KINDS` (report kinds announced at session start), `AODD_AGY_TRANSCRIPTS` (Antigravity transcript dirs for the agent-ops gather), `AODD_WORKLOG_SKIP` (path globs the Work Log skips), `AODD_WORKSPACE` (where the session-start queue shows, default the Claude home), `AODD_REPOS` (folders of git repos for the pending-work job and project skills). Others set by tests/tools only: `AODD_SCHEDULES_DRY_RUN`, `AODD_LAUNCHAGENTS_DIR`, `AODD_CRONTAB`, `AODD_CODING_RULES`, `AODD_REA_CMD`. Read paths only through `hooks/_aodd_paths.py` (install.sh copies it next to the hooks); tests point `AODD_HOME` at a temp dir and clear the others.
- install.sh never deletes; a differing file is kept as `<file>.aodd-bak` (`--no-backup` / `AODD_NO_BACKUP=1` turns every backup off).
- Keep the package neutral: no personal names, machine paths, project names or dated provenance. Check with
  `grep -rniE '/Users/|/home/|@[a-z0-9-]+\.(com|dev)' . -I --exclude-dir=.git` plus the names you know to avoid.
- Do not push or commit to `main` without the owner's say-so.

## Public API (adapters depend on it)

Other tools wrap these hooks by loading them by path, so these names are a contract. `hooks/test_public_api.py` fails if one disappears; renaming or removing one is a breaking change (major version).

- `hooks/skill-capture-nudge.py`: `CORRECTION`, `DOC`, `FIX_COMMIT`, `FIX_NOTE`, `INTERVAL`, `MIN_TOOL_CALLS`, `SKILL_BASH_WRITE`, `SKILL_FILE`, `SKILL_MD`, `STATE_DIR`, `skill_path`, `_text`, `scan`, `decide`
- `hooks/done-gate.py`: `decide(payload, reports=...)`, `scan`, `audit_report`
- `scripts/check_agy_proposal.py`: `problems(text)`
- `hooks/_aodd_paths.py`: `home()`, `reports()`, `state()`, `plans(cwd)`, `project(cwd)`, `worklog()`, `memory()`, `memory_dirs()`, `claude_home()`, `workspace_dirs()`, `session_id(transcript)`
- Extension point: `$AODD_HOME/extensions/agent-ops.md`, read by the agent-ops skill when present. The only one.

## Versioning and releases
- `VERSION` holds the current semver; `CHANGELOG.md` is generated by git-cliff from Conventional Commits (`cliff.toml`): `feat` → Added, `fix` → Fixed, `refactor`/`perf` → Changed, `docs` → Documentation; `test`/`chore`/`build`/`ci`/`style` are skipped.
- Release: run `python3 scripts/release.py [patch|minor|major]` from a clean, synchronized `main` after the release gates pass. It updates `VERSION` and `CHANGELOG.md`, commits, tags, pushes, and creates the GitHub Release; rerunning completes a pending tag/release instead of bumping again. Use `--dry-run` to preview. The manual equivalent is bump `VERSION`, run `git-cliff --tag vX.Y.Z --output CHANGELOG.md`, commit `chore(release): vX.Y.Z`, tag, push, then `gh release create` with generated notes.
- Pre-commit neutrality scan: `git config core.hooksPath scripts/git-hooks` once per clone; put your own names/paths to block in `.git/aodd-private-names` (one regex per line, never committed).
