# Incident Record — Blameless Post-Incident Writeup

Where to write it, first match wins:
1. The CEO names a destination (ticket, PR): use it.
2. Project memory exists (`$AODD_MEMORY`, first root): `$AODD_MEMORY/<project>/knowledge/incidents/<slug>.md`,
   so every agent and later session can find it across projects.
3. Otherwise: `docs/incidents/<slug>.md` in the repository. In a public repository, keep
   secrets, customer data and internal hostnames out of it.

## Preconditions (refuse to draft without all four)

Do not draft an incident record until all four are present and verified:
1. **Reproduction:** how the failure was reproduced or observed.
2. **Root cause:** the verified underlying defect, not just the surface symptom.
3. **Fix:** the concrete change that resolved it.
4. **Validation:** real test or verification output after the fix.

If any of the four is missing, stop and name what is missing instead of filling gaps.

## Tone

Keep the record blameless: focus on systems, assumptions, missing checks, and interfaces,
never on who wrote or ran something.

## Required sections

```markdown
# Incident: <short title>

- **Date:** YYYY-MM-DD
- **Scope / Impact:** what failed and who/what was affected

## Root cause
The verified underlying cause.

## Mechanism
Step-by-step chain from trigger to failure, with file/symbol references.

## Fix
What changed and why it resolves the root cause.

## Validation
Commands run, tests added or updated, and honest coverage notes (state clearly what was
covered, what was mocked, and what was not tested).

## How it slipped through
Which test, review, invariant, or monitoring gap allowed the defect to reach runtime.

## Follow-ups
Concrete, owned actions to prevent recurrence (regression tests, guards, alerts, or docs).
```
