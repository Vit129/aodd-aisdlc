# aodd-aisdlc

Two things for Claude Code that work together:

- **AODD** (Agent-Operated, Human-Decided): an operating contract. You are the CEO. The main agent is your chief of staff. Cheap models do the mechanics. An independent auditor from another model family checks every claim of "Done" before it reaches you.
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
| `rules/ai-sdlc-workflow.md` | the 5-phase workflow spine and approval gates |
| `skills/chief-of-staff`, `skills/ai-sdlc` (+ `references/`), `skills/agent-ops` | orchestrator, workflow, monthly team review |
| `agents/auditor.md`, `agents/advisor.md` | independent auditor, second-opinion expert |
| `hooks/done-gate.py` | Stop hook: no "Done" with open checkboxes or without a passing audit |
| `hooks/auditor-readonly.py` | PreToolUse hook: an auditor run cannot write |
| `hooks/skill-capture-nudge.py` | Stop/PostToolUse hook: turns a user correction or fix commit into a skill patch |
| `scripts/audit.py` | runs the cross-family audit and writes the report |
| `scripts/check_agy_proposal.py` | rejects another agent's skill proposal that lacks evidence |
| `docs/skill-learning.md` | how skills improve themselves |
| `install.sh` | installs into Claude Code (and Codex with `--codex`) |
| `AGENTS.md`, `CLAUDE.md` | guide for working on this repo itself (`CLAUDE.md` is one line: `@AGENTS.md`) |

## Requirements

- Claude Code
- Python 3.10+ (standard library only)
- git
- `gh` CLI for the PR steps of the Haiku ops runner (any other git host works if you adapt that step)
- Optional: the OpenAI Codex CLI (`codex`) as a Codex target and as a cross-family auditor.
- Optional: the Antigravity `agy` CLI for cross-family audits. Without agy or Codex `audit.py` falls back to Claude Opus and says so in the report (`auditor: claude-opus (agy/codex not installed, same-family)`). Override binaries with `AGY_BIN`, `CODEX_BIN` and `CLAUDE_BIN`.

## Install

```bash
git clone <this repo> aodd-aisdlc && cd aodd-aisdlc
./install.sh --dry-run          # see what would change
./install.sh --claude-md        # copy files, register hooks, import rules/aodd.md in CLAUDE.md
```

- Target is `~/.claude`; set `CLAUDE_HOME` for another location.
- Existing files that differ are printed as `UPDATE` and the old content is kept as `<file>.aodd-bak`. Nothing is deleted.
- Hooks are added to `settings.json` additively and idempotently (a `settings.json.aodd-bak` is made once). Each command is fail-open: `f=...; [ -f "$f" ] || exit 0; exec python3 "$f"`, so removing a hook file never breaks Claude Code.
- All state lives under `AODD_HOME` (default `~/.aodd`), each part movable with an optional env var (set them in `settings.json` `env` or your shell). `hooks/_aodd_paths.py` is the one resolver all hooks and scripts use (installed with them):

  | Variable | Default | Holds |
  |---|---|---|
  | `AODD_HOME` | `~/.aodd` | root of the three below |
  | `AODD_REPORTS` | `$AODD_HOME/pending-reports` | audit and agent-ops reports, agy proposals; decided ones in `done/` |
  | `AODD_STATE` | `$AODD_HOME/state` | hook state (`skill-capture/` markers) |
  | `AODD_PLANS` | `$AODD_HOME/plans` | `<feature>/` briefs, `ai-sdlc-task-progress.md`, handoffs. May contain `{project}`, the git repo folder name of the session's working directory, e.g. `/notes/{project}/plans` |

  `python3 hooks/_aodd_paths.py reports|state|plans [cwd]` prints the resolved path.
- **Your own agent-ops steps**: if `$AODD_HOME/extensions/agent-ops.md` exists, the agent-ops skill also follows it. That is the only extension hook; there is no plugin framework.
- **Optional post-merge hook** (off unless you enable it): `git config core.hooksPath scripts/git-hooks` makes `scripts/git-hooks/post-merge` run `./install.sh` after a merge or pull that changes this repo's main branch, then, only if `AODD_POST_INSTALL` is set, that command (for example a script that mirrors the installed files to other tools). One runner at a time (a `mkdir` lock, 30 s debounce), output in `$AODD_STATE/post-merge.log`, never blocks git. It runs `install.sh` as the current checkout, so it only installs what you merged.
- Without `--claude-md`, add the line `@rules/aodd.md` to your `CLAUDE.md` yourself, or the contract will not load.

### Companion plugins (optional, installed separately, not copied here)

- **mattpocock-skills**: in Claude Code, `/plugin install mattpocock-skills@claude-plugins-official` (marketplace `claude-plugins-official`). Provides `grilling`, `research`, `tdd`, `code-review`, `domain-modeling`, `codebase-design`, which the workflow calls in its phases. Some of its sub-skills are `disable-model-invocation`; the workflow says where to do the work directly instead.
- **9arm-skills**: upstream repo `github.com/thananon/9arm-skills` (`debug-mantra`, `post-mortem`, `scrutinize`, ...). Install with `npx skills add thananon/9arm-skills -g -y`. The upstream repo ships no Claude Code marketplace manifest; to use it as a plugin, wrap it in a one-plugin local marketplace whose plugin source is that GitHub repo.
- **graphify** (code knowledge graph for code navigation): `uv tool install graphifyy` (PyPI package `graphifyy`), or `pip install graphifyy`. Add the `mcp` extra (`graphifyy[mcp]`) if you want the MCP server; check the extra against the version of `mcp` you run. Then `graphify update .` in a project. The workflow only uses it when `graphify-out/` exists.

## How the audit works

`python3 scripts/audit.py --transcript <session.jsonl> --repo <repo> --claims "<your Done claims>"`

1. **The worker never writes the brief.** `audit.py` builds it from the CEO's own messages (verbatim, from the transcript), the git log and diff of the session (including uncommitted and untracked files), and the worker's claims, labelled untrusted.
2. **Cross-family auditor.** The auditor is a different model family than the worker:

   | Worker | Auditor |
   |---|---|
   | Claude Opus / Fable | agy |
   | agy | Claude Opus |
   | Claude Sonnet / Haiku | Claude Opus |
   | Codex | Claude Opus |
   | Claude Opus / Fable, `agy` not installed, Codex installed | Codex |
   | Claude Opus / Fable, neither installed | Claude Opus, reported as same-family |

3. **Verifier and the DISPUTED rule.** agy and Codex sometimes invent evidence, so when either audits, a cold Claude Opus re-checks every row. They have also caught real Claude mistakes, so a Claude verifier may not clear their FAIL on its own: auditor FAIL + verifier PASS = **DISPUTED**, and the CEO decides. The verifier can only add failures, never erase one silently. Combined verdicts: PASS, FAIL, DISPUTED, UNVERIFIABLE.
4. **Read-only, void on write.** The auditor runs with `AODD_AUDITOR=1`; `hooks/auditor-readonly.py` denies edits and Bash commands that write files or git history. Afterwards `audit.py` compares `git status` and `HEAD` and the reports directory; any change voids the audit (verdict FAIL, "Audit void").
5. **Report.** Written to `$AODD_REPORTS/audit-<date>-<sid8>.md` with a `verdict:` frontmatter line. Exit code 0 = PASS, 1 = FAIL/DISPUTED/UNVERIFIABLE, 2 = could not run.

### done-gate behaviour

`hooks/done-gate.py` is a Stop hook. It blocks stopping once per stop cycle, and only for progress files this session wrote to:

- a touched `ai-sdlc-task-progress.md` still has `- [ ]` boxes: finish them or say plainly the feature is not done;
- every box is ticked but no audit report exists for this session: run `audit.py` first;
- no progress file but the session edited 5 or more files (AODD medium): same audit requirement;
- the audit verdict is FAIL / UNVERIFIABLE / DISPUTED: report it to the CEO as it is.

It fails open on any error. `DONE_GATE_AUDIT=0` disables the audit requirement.

## Skill capture (self-improving skills)

`hooks/skill-capture-nudge.py` asks the agent to patch the governing skill, but only when the session has at least 20 tool calls and one of two signals: a **user correction** (English or Thai phrases such as "no", "wrong", "too long", "ไม่ใช่", "ยาวไป") or a **`fix:` / `revert:` commit**. Ordinary tool errors do not count. It nudges again only after 40 more tool calls with a new signal, and right after a fix commit it reminds in the moment. The procedure (where to write the lesson, verified-only, generalize, bump version) is `docs/skill-learning.md`. Disable with `CLAUDE_SKILL_CAPTURE=0`.

### Proposals from other agents (evidence gate)

Another agent (agy, Codex) never edits its synced copy of a skill. It writes `agy-proposal-<date>-<slug>.md` into `$AODD_REPORTS/`. `scripts/check_agy_proposal.py <file>` auto-rejects it unless it carries all of these fields, each non-trivial:

`Project`, `Repo` (a real git repo), `What` (targets a file under `.claude/`), `Analysis`, `Code`, `Test`, `Fix`, `Verified` (must differ from `Test`), `Commit` (a hash that exists in `Repo`), `Proposed change`.

It proves the evidence is present and the commit is real, not that the content is honest; the triage (the `agent-ops` skill) and the CEO still judge it.

## Codex

`./install.sh --codex` installs into `${CODEX_HOME:-~/.codex}` in addition to the Claude install (`--dry-run` covers it).

| Part | Status under Codex |
|---|---|
| Skills (`skills/`) and agents (`agents/`) | copied; Codex reads skills from `$CODEX_HOME/skills` |
| `rules/aodd.md` + `rules/ai-sdlc-workflow.md` | inlined in `$CODEX_HOME/AGENTS.md` between `<!-- aodd:begin -->` and `<!-- aodd:end -->` (Codex has no `@import`); a re-run replaces that block, text outside it is untouched; `AGENTS.md.aodd-bak` is made once |
| `scripts/audit.py` | supported: a Codex session transcript is detected (worker `codex`), and Codex can be the auditor (table above): `codex exec -s read-only --ephemeral -C <repo> -` with the prompt on stdin. Binary: `CODEX_BIN` (default `codex`). `--auditor codex` forces it |
| Hooks in `$CODEX_HOME/hooks.json` | registered for `PreToolUse`, `Stop`, `PostToolUse` (same fail-open commands; `hooks.json.aodd-bak` made once). Codex hook input uses the same field names as Claude, so no adapter is needed (see Verified below) |

Verified (Codex CLI 0.154, live run in a throwaway `CODEX_HOME`, `codex exec --dangerously-bypass-hook-trust`, and by tests):

- Hook input: `PreToolUse` receives `session_id`, `transcript_path`, `cwd`, `tool_name`, `tool_input`, `tool_use_id`. A file edit arrives as `tool_name: apply_patch` with `tool_input: {"command": "<patch text>"}`; the shell tool arrives as `tool_name: Bash` with `tool_input: {"command": ...}`.
- `auditor-readonly.py` (`AODD_AUDITOR=1`): the `apply_patch` edit was denied live (file not created, `git status` unchanged, Codex logged "Command blocked by PreToolUse hook"); `Bash` writes go through the same regex as under Claude.
- `done-gate.py` and `skill-capture-nudge.py` read the Codex rollout (`~/.codex/sessions/.../rollout-*.jsonl`: `{timestamp, type, payload}`): edited files come from `apply_patch` headers (`*** Add|Update|Delete File: <path>`), shell commands from `exec_command` (`arguments` JSON with `cmd`), user messages from `message`/`user`/`input_text` (injected `<...>` and `# AGENTS.md` blocks skipped). The shapes were read from real rollouts; the gates themselves are covered by `hooks/test_done_gate.py` and `hooks/test_skill_capture_nudge.py` with synthetic records of that shape, not by a full interactive Codex session.
- Codex may ask you to trust newly added hooks on first run.
- Transcript detection, auditor selection, the auditor command, install and re-install: `scripts/test_audit.py`, `scripts/test_install.py`.

Limits: Codex tool errors are not counted by the skill-capture hook (they are not a nudge signal anyway); a file written by a shell command (not `apply_patch`) is not counted toward the done-gate "medium" file count, same as under Claude.

## Tests

```bash
for t in hooks/test_*.py scripts/test_*.py; do python3 "$t"; done    # each prints "ok"
```

Tests point `AODD_HOME` at a temp directory and use stub models; no network, no `agy`, no real Claude calls.

## Uninstall

Delete the files this repo copied (for Codex: from `$CODEX_HOME`, also the block between the `aodd:begin` and `aodd:end` markers in `AGENTS.md` and the hook entries in `hooks.json`) (`skills/{chief-of-staff,ai-sdlc,agent-ops}`, `agents/{auditor,advisor}.md`, `rules/{aodd,ai-sdlc-workflow}.md`, `hooks/{done-gate,auditor-readonly,skill-capture-nudge}.py`, `scripts/{audit,check_agy_proposal}.py`, `docs/skill-learning.md`) from your Claude home, remove the four hook entries that point at them from `settings.json` (or restore `settings.json.aodd-bak`), remove the `@rules/aodd.md` line from `CLAUDE.md`, and optionally delete `~/.aodd`. Because the hook commands are fail-open, deleting only the hook files already makes them inert.

## License

MIT, see `LICENSE`.
