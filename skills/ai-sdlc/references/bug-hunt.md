# Bug Hunt — Root-Cause Debugging Discipline

Load before diagnosing or proposing a fix for any bug or failing test.

## 1. Clarify before guessing

If the symptom, expected behavior, environment, or reproduction steps are unclear, stop and
ask the user using the Phase 1 interview (`skills/ai-sdlc/phases/phase1-interview.md`),
one question at a time, before forming any hypothesis.

## 2. Reproduce first

- Run the failing case yourself and capture the exact error, exit code, or wrong output.
- **Flaky failure:** increase the reproduction rate first (repeat runs, isolate timing, seed
  randomness, or strip unrelated setup) until it fails reliably enough to test a hypothesis.
- **No reproduction:** stop and ask the user for missing environment details, logs, or steps
  rather than guessing at a fix.

## 3. Trace the fail path

Follow the actual execution from the entry point to the failure. Prefer direct observation in
this order:
1. **Debugger** (breakpoints, stack frames, live variable inspection).
2. **Source trace** (read callers, callees, state mutations, and config in the actual path).
3. **Tagged instrumentation** (temporary, clearly tagged logs removed before finishing).

## 4. Ranked hypotheses and experiment ledger

List 3 to 5 ranked hypotheses for why the traced path fails. Test the cheapest disproof first.
Keep a short experiment ledger as you go:

| # | Hypothesis | Cheapest disproof | Result | Status |
|---|---|---|---|---|
| 1 | ... | ... | ... | ruled out / confirmed |

Never stack multiple speculative edits at once; test one variable per step.

## 5. Cross-check every clue before a fix

Before writing a fix, verify that your confirmed root cause explains every observed symptom,
log line, and caller in the blast radius. Then follow the Logic path in
`rules/ai-sdlc-workflow.md`: write a failing regression test (RED), apply the minimal fix
(GREEN), and confirm no other callers or invariants broke.
