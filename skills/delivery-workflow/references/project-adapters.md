# Project adapters

The shared workflow in [SKILL.md](../SKILL.md) is the same for every repo. Each repo supplies its own commands. Fill this table once per repo (in that repo's own `AGENTS.md`, or the private memory for personal projects), and check each row before relying on it.

## Adapter template

| Stage | What to record |
|---|---|
| Entrypoint | the command a user runs (`make start`, `npm start`) and what it calls |
| Dev server / test server | command and port for each; a test server must not publish |
| Commit + push | the helper or command, and whether it refreshes Graphify first |
| Full cycle | the helper, and which of `patch` / `minor` / `major` / `skip` it accepts |
| Release metadata | the files that hold the version, and the helper that bumps them |
| Changelog | the single generator (cliff or the release tool), and the file it writes |
| Release + deploy | the publish target, and the deploy command for each named target |
| Tests / build | the commands the release gate runs |
| Gaps | anything the table above cannot express: no `skip`, a non-interactive default, two changelog generators, Graphify missing from the commit path |

A row that is not checked is written as "not checked", not as a value.
