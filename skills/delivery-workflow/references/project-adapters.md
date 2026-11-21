# Project adapters

The shared workflow in [SKILL.md](../SKILL.md) is the same for every repo. Each repo supplies its own commands. Fill this table once per repo (in that repo's own `AGENTS.md`, or the private memory for personal projects), and check each row before relying on it.

## Adapter template

| Stage | What to record |
|---|---|
| Entrypoint | the command a user runs (`make start`, `npm start`) and what it calls |
| Dev server / test server | command and port for each; a test server must not publish |
| Commit + push | the helper or command |
| Full cycle | the helper, and which of `patch` / `minor` / `major` / `skip` it accepts |
| Release metadata | the files that hold the version, and the helper that bumps them |
| Changelog | the single generator (cliff or the release tool), and the file it writes |
| Release + deploy | the publish target, and the deploy command for each named target |
| Tests / build | the commands the release gate runs |
| Gaps | anything the table above cannot express: no `skip`, a non-interactive default, two changelog generators |

A row that is not checked is written as "not checked", not as a value.

## Gaps seen across repos

Each repo's real adapter row lives in that repo's own `AGENTS.md`, or in the private memory for personal projects. The table above is the template only. These gaps came from checking several repos against this skill:

1. A template alone does not show which command is the release. Each repo needs a filled row before its release runs.
2. "Build number where the app needs one" has no field name or location rule. Define one field name and one file for it.
3. The release manifest has no shape. Several repos keep the version in different files with different fields. Define a minimal manifest (`version`, `build`) and say which file holds it.
4. Two changelog generators in one repo are not flagged or migrated by any step. The skill should name the generator to keep and the one to remove.
5. A repo with no CI, and a static site with a backend script, have no matching profile in `project-blueprint/references/release-profiles.md`. Add a profile for each.
