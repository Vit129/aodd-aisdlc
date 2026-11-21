# Layering principles

## Purpose
Keep rules pure, put I/O at the edges, and keep presentation thin.
Enforce every rule with an automated guard.

## Roles, not folder names
- **core:** pure rules; no I/O or framework.
- **io:** external boundaries, including storage, network, device and process.
- **state:** holds app state and calls core; no rendering.
- **ui:** renders and dispatches only; no rules or direct I/O.
- **composition root:** the single place that wires io into the app; the only file or target allowed to import both io and ui.

## Dependencies
| From | Allowed dependencies |
|---|---|
| core | Nothing from io, state or ui. |
| io | Core types only. |
| state | Core; access io only through ports. |
| ui | Core types and state; receive ports wired by the composition root, never import io directly. |

## Literal policy
The project map records which literal kinds are restricted, such as human-language text, colours or font sizes. Each chosen kind has one allowed place and an enforcing guard.

## Guard rules
- Run each automated guard in the project's default test command.
- Each guard has a known-bad fixture that must fail as a negative control.
- Failure messages name the fix, for example: "use the core helper; do not inline the formula".
- A recurring bug gets a guard, not a reminder in prose.

## Baseline (ratchet)
For an existing project, check in current violations as a baseline. The count for each rule and file may only shrink; a new violation fails, even if another is removed. Report reductions so the baseline can be updated.

## Project map as guard input
`ARCHITECTURE.md` maps roles to paths. A guard checks that each mapped path exists and every top-level source folder is mapped; explicitly absent roles are excluded from path checks.

## Stack adapters
Implement guards using [JavaScript/TypeScript](adapter-js-ts.md), [Python](adapter-python.md), or [Swift](adapter-swift.md). For an uncovered stack, write an adapter from these rules, mark it "new", and add a negative control. Apps Script and other stacks are not yet covered.

## Day one: new projects
Before the first feature, require all of the following:
- [ ] Project map from [the template](project-map-template.md), with a role-to-path table.
- [ ] Exactly one composition root.
- [ ] Architecture guard for core-to-io/ui imports, run by the default test command.
- [ ] Negative-control fixture proving that guard fails.
- [ ] Empty baseline file for each guard that uses one.
- [ ] CI runs the default test command, or an explicit note says CI does not exist.
- [ ] For each chosen literal policy, one guard and one allowed file.

## Project policy, not verified here
Coverage percentages, bans on inline fallback values and bans on fixed waits are optional project policies. This reference does not establish that they are proven or common practice.

## Tagging
See [dev/QA pattern section 1](../dev-qa-pattern.md#1-tagging-layer-kind) for `[LAYER-KIND]`.
