# Architecture

See `README.md` for what the package is. `./install.sh` copies the files in this repo into an agent home.

## Layout

The folder-by-folder layout is in `AGENTS.md` under "Layout"; it is the one home for it.

## Public API

The hook names other tools depend on are listed in `AGENTS.md` under "Public API"; breaking one is a major version.

## Conventions

The conventions are in `AGENTS.md` under "Conventions".

## Structure deviations

- §1 tests: tests sit next to each hook and script (`hooks/test_*.py`, `scripts/test_*.py`, `adapters/test_*.py`, `optional/*/hooks/test_*.py`) instead of a `tests/` directory. The installer copies hooks flat into the agent home, so a separate `tests/` tree would have to be excluded from every install. Revisit when `install.sh` can skip a test directory without special-casing.

## Commit preparation

The commit and graph rules are in `rules/aodd/git-ops.md`. `scripts/graphify_commit.py` is the helper the release runner uses.
