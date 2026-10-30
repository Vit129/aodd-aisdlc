# aodd-aisdlc

Two things for Claude Code that work together:

- **AODD** (AI Orchestration Driven Development): an operating contract. You are the CEO. The main agent is your chief of staff / orchestrator. Cheap models do the mechanics. An independent auditor from another model family checks every claim of "Done" before it reaches you.
- **ai-sdlc**: a Dev/QA feature workflow. Interview, architect, QA design (tests RED), dev (GREEN), QA verify, with three real approval gates.

## The flow

```
you (CEO) ── one brief ──> chief-of-staff ──> ai-sdlc phases (large work) / direct work (small)
                                │                    │
                       Haiku does git/ops,     Gate 1 design · Gate 2 scenarios · Gate 3 seams
                       lookups, test runs               │
                                └── Done claim ──> scripts/audit.py (other model family, read-only)
                                                          │
                          hooks/done-gate.py blocks "Done" until the audit ran and passed
                                                          │
                                  Result / Evidence / Needs your decision ──> you
```

Size decides ceremony (`rules/aodd.md`): small work is just done; medium work gets a brief question, dispatch and an audit; large work runs the full `ai-sdlc` spine. Anything that spends money, reaches an outside party or is irreversible always stops for you.

## What is in the box

| Path | What |
|---|---|
| `rules/aodd.md` | the AODD contract: triage, boss reporting shape, model split, cheap-model delegation, Haiku ops runner |
| `rules/ai-sdlc-workflow.md` | the 5-phase workflow spine and approval gates; per-phase detail in `skills/ai-sdlc/phases/`, loaded only when you reach that phase |
| `skills/chief-of-staff`, `skills/ai-sdlc` (+ `references/`), `skills/agent-ops` | orchestrator, workflow, monthly team review |
| `skills/reverse-engineer-anything` | [REA](https://github.com/morluto/rea) skill for shipped binaries, Electron/JS apps, Android, firmware; the installer also runs `rea setup --client <claude_code, codex, antigravity> --yes` for each agent you install into (`rea` on PATH, else `npx -y rea-agents@6.8.0`, needs Node; `--dry-run` passes `--dry-run`). Later, no reinstall needed: `python3 scripts/rea_check.py` reports installed vs latest and `rea doctor` per agent, `--update` upgrades `rea-agents` and re-registers what is stale |
| `agents/auditor.md`, `agents/advisor.md` | independent auditor, second-opinion expert |
| `hooks/done-gate.py` | Stop hook: no "Done" with open checkboxes or without a passing audit |
| `hooks/auditor-readonly.py` | PreToolUse hook: an auditor run cannot write |
| `hooks/skill-capture-nudge.py` | Stop/PostToolUse hook: turns a user correction or fix commit into a skill patch |
| `hooks/secret-read-guard.py` | PreToolUse hook: secret files (`.env`, keys, configs with tokens) are never printed or edited by the agent; `--show <file>` gives a masked view |
| `hooks/coding-rules-gate.py` | PreToolUse/PostToolUse hook: the first code edit of a session waits until `rules/coding.md` (if you have one) and the project's `ARCHITECTURE.md` were read |
| `hooks/dirty-branch-switch-guard.py` | PreToolUse hook: no branch switch or new worktree while earlier work is uncommitted |
| `hooks/graphify-guard.py` | graph-first lookup gate and graph refresh; a silent no-op unless `graphify-out/graph.json` exists |
| `hooks/work-log.py` | Stop hook: one record per session (tokens, tool calls, rework signals); `--report YYYY-MM` |
| `scripts/skill_learning_report.py`, `scripts/agent_ops_gather.py` | the curator (stale/archive/merge candidates, capture yield) and the agent-ops input gatherer |
| `optional/` | the modules below, each in `optional/<module>/{skills,rules,hooks,scripts,schedules}/` |
| `scripts/audit.py` | runs the cross-family audit and writes the report |
| `scripts/check_agy_proposal.py` | rejects another agent's skill proposal that lacks evidence |
| `docs/skill-learning.md` | how skills improve themselves |
| `install.sh` | installs into Claude Code (and Codex with `--codex`, Antigravity with `--agy`; see `docs/antigravity.md`) |
| `AGENTS.md`, `CLAUDE.md` | guide for working on this repo itself (`CLAUDE.md` is one line: `@AGENTS.md`) |

## Requirements

- Claude Code
- Python 3.10+ (standard library only)
- git
- `gh` CLI for the PR steps of the Haiku ops runner (any other git host works if you adapt that step)
- Optional: the OpenAI Codex CLI (`codex`) as a Codex target and as a cross-family auditor.

## Install

```bash
git clone https://github.com/<owner>/aodd-aisdlc.git && cd aodd-aisdlc
./install.sh --claude-md        # copy files, register hooks, import rules/aodd.md in CLAUDE.md
```

`./install.sh --detect` lists the coding agents on this machine (Claude Code, Codex, Antigravity, Gemini CLI, Cursor, Copilot, OpenCode, Hermes, Kiro, Aider, Goose, Grok, Pi, OpenClaw; found by binary on PATH or home dir). A terminal install offers Codex and Antigravity when found; the others are listed as having no installer yet. It also warns when `codex` is not present, since the cross-family audit then falls back to a Claude auditor.

Update: `git pull && ./install.sh` (re-running is safe; changed files are kept as `.aodd-bak`). To make it automatic after every pull, enable the post-merge hook (below).

In a terminal the installer asks about each optional module (one line each, default no) and, for `schedules`, which times to use. To skip the questions:

| Flag | Effect |
|---|---|
| `--with agent-memory,schedules` | install exactly these modules (core is always installed) |
| `--all` / `--core-only` | every module / none |
| `--yes` | ask nothing: core only unless `--with`/`--all` is given; schedules use their default times |
| `--dry-run` | print everything, write nothing (also previews the schedule entries) |
| `--claude-md`, `--codex` | import the contract in `CLAUDE.md`; also install into `${CODEX_HOME:-~/.codex}` |

Modules are additive: add one later with `./install.sh --with <module>`; modules you do not name are left as they are.

- Target is `~/.claude`; set `CLAUDE_HOME` for another location.
- Existing files that differ are printed as `UPDATE` and the old content is kept as `<file>.aodd-bak`. Nothing is deleted. `--no-backup` (or `AODD_NO_BACKUP=1`, e.g. when another tool already mirrors these files) makes no `.aodd-bak` files at all.
- Hooks are added to `settings.json` additively and idempotently (a `settings.json.aodd-bak` is made once). Each command is fail-open: `f=...; [ -f "$f" ] || exit 0; exec python3 "$f"`, so removing a hook file never breaks Claude Code.
- All state lives under `AODD_HOME` (default `~/.aodd`), each part movable with an optional env var (set them in `settings.json` `env` or your shell). `hooks/_aodd_paths.py` is the one resolver all hooks and scripts use (installed with them):

  | Variable | Default | Holds |
  |---|---|---|
  | `AODD_HOME` | `~/.aodd` | root of the three below |
  | `AODD_REPORTS` | `$AODD_HOME/pending-reports` | audit and agent-ops reports, agy proposals; decided ones in `done/` |
  | `AODD_STATE` | `$AODD_HOME/state` | hook state (`skill-capture/` markers) |
  | `AODD_PLANS` | `$AODD_HOME/plans` | `<feature>/` briefs, `ai-sdlc-task-progress.md`, handoffs. May contain `{project}`, the git repo folder name of the session's working directory, e.g. `/notes/{project}/plans` |
  | `AODD_WORKLOG` | `$AODD_HOME/work-log` | Work Log, one `<YYYY-MM>.jsonl` per month; if you set it and its parent folder is missing, entries go to `$AODD_STATE/work-log/` with a `note` field |
  | `AODD_WORKLOG_SKIP` | empty | path globs (`:`-separated) of session folders the Work Log must not record |
  | `AODD_MEMORY` | `$AODD_HOME/memory` | agent-memory module: `knowledge/*.md`, `<project>/SESSION-TOPICS.md`; may be a `:`-separated list of roots (the first is where notes are written, all are searched) |
  | `AODD_WORKSPACE` | the Claude home | agent-memory module: folders (`:`-separated) where the report queue is shown at session start |
  | `AODD_RECALL_EXTRA` | empty | memory-recall: `:`-separated globs under each memory root of extra files to search (e.g. `*/PLAYBOOK.md`); a repo's own `agent-memory/` is searched when present |
  | `AODD_DIGEST` | `$AODD_MEMORY/{project}/SESSION-TOPICS.md` | session-start: path template (with `{project}`) of the last-session digest |
  | `AODD_PROJECT_ALIASES` | empty | session-start: `name=alias,...`, a project folder `name` also reads the digest stored under `alias` |
  | `AODD_REPORT_KINDS` | `agent-ops,housekeeping,pending-work` | session-start: comma list of report kinds (`<kind>-*.md` in `$AODD_REPORTS`) announced once |
  | `AODD_AGY_TRANSCRIPTS` | `~/.gemini/antigravity/brain`, `~/.gemini/antigravity-cli/brain` | agent-ops gather: `:`-separated Antigravity transcript dirs for its usage section; nothing found, no section |
  | `AODD_REPOS` | empty | schedules and the curator: folders holding your git repos (pending-work report, project-scoped skills) |

  The installer writes the `AODD_*` path variables to `settings.json` `env` only for those you have set in your shell when you run it (an existing different value is kept and reported); unset ones stay at their defaults.

  `python3 hooks/_aodd_paths.py reports|state|plans [cwd]` prints the resolved path.
- **Your own agent-ops steps**: if `$AODD_HOME/extensions/agent-ops.md` exists, the agent-ops skill also follows it. That is the only extension hook; there is no plugin framework.
- **Optional post-merge hook** (off unless you enable it): `git config core.hooksPath scripts/git-hooks` plus `AODD_AUTO_INSTALL=1` in your environment makes `scripts/git-hooks/post-merge` run `./install.sh` after a merge or pull that changes this repo's main branch, then, only if `AODD_POST_INSTALL` is set, that command (for example a script that mirrors the installed files to other tools). One runner at a time (a `mkdir` lock, 30 s debounce), output in `$AODD_STATE/post-merge.log`, never blocks git. It runs `install.sh` as the current checkout, so it only installs what you merged.
- Without `--claude-md`, add the line `@rules/aodd.md` to your `CLAUDE.md` yourself, or the contract will not load.

### Companion plugins (optional, installed separately, not copied here)

- **9arm-skills**: upstream repo `github.com/thananon/9arm-skills` (`debug-mantra`, `post-mortem`, `scrutinize`, ...). Install with `npx skills add thananon/9arm-skills -g -y`. The upstream repo ships no Claude Code marketplace manifest; to use it as a plugin, wrap it in a one-plugin local marketplace whose plugin source is that GitHub repo.
- **graphify** (code knowledge graph for code navigation): `uv tool install graphifyy` (PyPI package `graphifyy`), or `pip install graphifyy`. Add the `mcp` extra (`graphifyy[mcp]`) if you want the MCP server; check the extra against the version of `mcp` you run. Then `graphify update .` in a project. The workflow only uses it when `graphify-out/` exists.

## Optional modules

Core works alone. Each module is a folder `optional/<module>/` with its own `skills`, `rules`, `hooks`, `scripts`, `schedules`; its hooks are registered only when you choose it.

| Module | Gives you | Details |
|---|---|---|
| `agent-memory` | agents recall past decisions and lessons across sessions and projects | `memory-recall.py` (UserPromptSubmit) adds up to 5 pointers + a one-line gist from `knowledge/*.md` under `$AODD_MEMORY` and from Claude's auto-memory notes; `memory-write-scan.py` (PreToolUse) refuses to store a real credential or an injection phrase in a memory file; `session-start-recent.py` (SessionStart) shows the project's last session digest and, in the workspace only, new reports, agent proposals and audits that need you |
| `schedules` | weekly team review, cleanup report and backups run by themselves at times you pick | `scripts/install-schedules.py` writes cron lines (Linux) or launchd agents (macOS) with absolute paths resolved at install time; jobs run `scripts/aodd_job.py` |

Add one later: `./install.sh --with agent-memory` (or `--with agent-memory,schedules`).

Not included: cross-session full-text search (`session_search`) and the unified `recall.py`. The indexer reads five tools' private transcript formats and the unified query needs graphify and an embedding model; neither is self-contained enough to ship neutral.

### Schedules

| Job | Default time | Produces |
|---|---|---|
| `agent-ops` | Monday 09:00 | `agent-ops-<date>.md` in `$AODD_REPORTS`: at most 5 proposed team changes, each with its evidence (Haiku writes it from the gathered Work Log, skill usage and curator output) |
| `housekeeping` | Monday 09:15 | `housekeeping-<date>.md`: old transcripts, stale hook state and `.aodd-bak` files that could be cleared; it deletes nothing |
| `pending-work` | daily 08:45 | `pending-work-<date>.md`: uncommitted work, unpushed commits and unmerged branches in the repos under `$AODD_REPOS`; written only when something is pending, no model |
| `memory-backup` | daily 22:00 | a git commit (and a push when a remote is set) of `$AODD_MEMORY`; needs the `agent-memory` module; skipped when the folder is not a git repo |

- Model jobs run `claude -p --model haiku --tools ""` with the prompt on stdin: the model sees only the gathered data and has no permission to write. The wrapper writes the report; a failed or empty model answer writes nothing and exits 1, so the log shows it and the next run retries.
- Logs: `$AODD_STATE/logs/<job>.log`. Reports show up once at the next session start in the workspace (agent-memory module).
- Change times by re-running: `python3 <claude home>/scripts/install-schedules.py --set agent-ops="fri 17:30" --set housekeeping=off` (`HH:MM`, optionally `daily` or a weekday first). Entries are replaced in place, so it is safe to repeat. `--dry-run` prints what would be written; `--list` shows jobs and defaults.
- Run a job by hand through the same wrapper: `python3 <claude home>/scripts/aodd_job.py agent-ops`.

## How the audit works

Every Medium+ Done claim is checked by an independent auditor that never sees the worker's argument (a different model: another family for Opus/Fable work, Opus for Sonnet/Haiku work); the brief is built from your own messages and the diff, and a FAIL or DISPUTED verdict goes to you as is. Details, auditor selection and the report format: [docs/audit.md](docs/audit.md).

## Skill capture (self-improving skills)

After a user correction or a `fix:` commit, a Stop hook asks the agent to patch the skill that governs the work; other agents raise evidence-gated proposals instead. Details: [docs/skill-learning.md](docs/skill-learning.md).

## Codex

`./install.sh --codex` also installs into `${CODEX_HOME:-~/.codex}` (skills, agents, inlined rules, hooks, Codex as auditor). What works and what was verified: [docs/codex.md](docs/codex.md).

## Release

After the release gates pass, run `python3 scripts/release.py [patch|minor|major]` from a clean, synchronized `main`. It updates `VERSION` and `CHANGELOG.md`, commits and tags the release, pushes it, and creates the GitHub Release. Use `--dry-run` to preview. If a prior run stopped after creating the release commit or tag, rerun the command to complete that same version. Requires `git-cliff` and an authenticated `gh` CLI.

## Tests

```bash
for t in hooks/test_*.py scripts/test_*.py adapters/test_*.py optional/*/hooks/test_*.py optional/*/scripts/test_*.py; do python3 "$t"; done
```

Tests point `AODD_HOME` at a temp directory and use stub models; no network, no `agy`, no real Claude calls.

## Uninstall

Delete the files this repo copied (for Codex: from `$CODEX_HOME`, also the block between the `aodd:begin` and `aodd:end` markers in `AGENTS.md` and the hook entries in `hooks.json`) from your Claude home, remove the matching hook entries from `settings.json` (or restore `settings.json.aodd-bak`) and the `@rules/aodd.md` line from `CLAUDE.md`, and optionally delete `~/.aodd`. Because the hook commands are fail-open, deleting only the hook files already makes them inert.

- **Core**: `skills/{chief-of-staff,ai-sdlc,agent-ops,reverse-engineer-anything}`, `agents/{auditor,advisor}.md`, `rules/{aodd,ai-sdlc-workflow}.md`, `hooks/{done-gate,auditor-readonly,skill-capture-nudge,secret-read-guard,coding-rules-gate,dirty-branch-switch-guard,graphify-guard,work-log,_aodd_paths,_aodd_secrets}.py`, `scripts/{audit,check_agy_proposal,skill_learning_report,agent_ops_gather}.py`, `docs/skill-learning.md`, plus the `env` keys you had it write.
- **agent-memory**: `hooks/{memory-recall,memory-write-scan,session-start-recent}.py` and the three entries (`UserPromptSubmit`, `SessionStart`, and `memory-write-scan` under `PreToolUse`) in `settings.json`. Your `$AODD_MEMORY` notes are yours; the installer never touches them.
- **schedules**: first `python3 <claude home>/scripts/install-schedules.py --uninstall` (removes the `# aodd:begin` ... `# aodd:end` cron block or the `com.aodd.*` launch agents; `--dry-run` previews), then delete `scripts/{install-schedules,aodd_job}.py` and `schedules/`.

## Contributors

Developed and maintained by the **aodd-aisdlc contributors** and **Claude** (Anthropic).

## License

Apache License 2.0, see `LICENSE` and `NOTICE`. Releases up to v0.3.6 were published under MIT and remain
available under those terms (`LICENSE-MIT`).
