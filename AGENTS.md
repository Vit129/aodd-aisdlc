# Working on aodd-aisdlc

This repo is an installable package for Claude Code and OpenAI Codex: AODD (an operating contract where a human decides, cheap models do mechanics, and an independent cross-family auditor checks every "Done") plus ai-sdlc (a Dev/QA feature workflow with three approval gates). `./install.sh` copies it into an agent home; the files here are what gets installed. See `README.md`.

## Layout

- `rules/` the AODD contract and the ai-sdlc workflow spine (inlined into Codex `AGENTS.md`, imported by Claude `CLAUDE.md`)
- `skills/` chief-of-staff, ai-sdlc (+ `references/`), agent-ops
- `agents/` auditor and advisor subagent definitions
- `hooks/` Stop / PreToolUse / PostToolUse hooks (done-gate, auditor-readonly, skill-capture-nudge)
- `scripts/` `audit.py` (cross-family audit), `check_agy_proposal.py`, install test
- `docs/` skill-learning procedure
- `install.sh` installer (`--dry-run`, `--claude-md`, `--codex`)

## Check your change

```bash
for t in hooks/test_*.py scripts/test_*.py; do python3 "$t"; done    # each prints "ok"
python3 -m py_compile hooks/*.py scripts/*.py && bash -n install.sh
T=$(mktemp -d); CLAUDE_HOME=$T/c CODEX_HOME=$T/x ./install.sh --dry-run --codex   # install preview, writes nothing
```

`scripts/test_install.py` also does a real install into temp homes.

## Conventions

- Python is standard library only (3.10+). No new dependency.
- Hooks fail open: any error means allow, and installed hook commands exit 0 if the file is gone.
- Every hook and script has a `test_*.py` next to it. Tests use stub models, never network or real CLIs.
- State lives only under `AODD_HOME` (default `~/.aodd`); tests point it at a temp dir.
- install.sh never deletes; a differing file is kept as `<file>.aodd-bak`.
- Keep the package neutral: no personal names, machine paths, project names or dated provenance. Check with
  `grep -rniE '/Users/|/home/|@[a-z0-9-]+\.(com|dev)' . -I --exclude-dir=.git` plus the names you know to avoid.
- Do not push or commit to `main` without the owner's say-so.
