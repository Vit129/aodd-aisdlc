# Architecture map

## Stack
- Language: <language>
- UI framework: <framework or none>
- Build tool: <build tool>
- Test runner: <test runner>
- CI: <CI system or none>

## Adapter
<Relative link to the matching references/layering/adapter-*.md>

## Role to path
Mark a missing role explicitly as `not present`; map every top-level source folder.

| Role | Path | Notes |
|---|---|---|
| core | <path or not present> | <notes> |
| io | <path or not present> | <notes> |
| state | <path or not present> | <notes> |
| ui | <path or not present> | <notes> |
| composition root | <path or not present> | <notes> |
| tests | <path or not present> | <notes> |

## Guards
| File | Checks | Run by (command) | Negative-control fixture |
|---|---|---|---|
| <path> | <checks> | <command> | <path> |

## Baseline
- File path: <path>
- Count per rule: <rule and count>
- Date: <date>

Empty for a new project. Track violations by identity and only shrink the baseline.

## Literal policy
| Kind | Allowed file | Guard |
|---|---|---|
| <kind> | <path> | <path> |

## Known deviations
| Path | Reason | Planned removal |
|---|---|---|
| <path> | <reason> | <date or condition> |

Record every deviation; no silent exceptions.

## Commands
- Test: <command>
- Lint or typecheck: <command>
- Build: <command>
- CI job name: <name or none>

## Last verified
- Date: <date>
- Command: <command>
