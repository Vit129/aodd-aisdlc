# Dev / Preview and Test / QA

These are related local stages with different goals. Dev/preview runs the app or built output for a person to look at. Test/QA checks behavior against requirements and failure cases. Project instructions take precedence where they are more specific.

## Dev / preview

1. Confirm the checkout and scope. Check the branch, worktree, and existing diff before editing.
2. Read the owning code, its callers, fixtures, and tests. For a feature, follow the repo's feature workflow instead of skipping its gates.
3. For a multi-file or architectural change, state a short plan first. Keep to the requested behavior and leave unrelated work alone.
4. Make the smallest complete change, with the tests and docs it requires. Review the diff for scope, generated files, secrets, and stray edits.
5. The preview must be isolated: no production services, no production state, no public deployment. Keep it running only while someone needs it.
6. A dedicated test-mode server is the QA environment, not a passing test. Confirm its mode, port, and service connections. Run the suites against it and report their results separately. Do not point browser tests at production to make them pass.
7. If the repo has no automated QA, say "manual preview / review" and name the person who must accept it. Do not imply automated QA exists.

Do not commit, push, tag, publish, or deploy unless the user asked for that stage. If the user asked only for development, stop after the relevant checks and report later stages as NOT RUN.

## Test / QA

1. Find the required checks in the project instructions, package scripts, Make targets, CI, and QA docs. Separate them into: unit and architecture checks, scenario or end-to-end tests, build and packaging checks, type checks, version-consistency guards, and live smoke checks.
2. Run only the checks that are relevant and allowed. Do not use a production entrypoint or any externally side-effecting command as a stand-in for a test.
3. On failure, report the exact output and whether it looks related. Do not make an unrequested fix. If a fix was requested, trace the failure and rerun the affected checks.
4. Report each layer on its own. A passing unit suite does not cover scenario tests, a production build, or a type check. Before trusting a script named "full release" or "full cycle", check whether it runs tests or only builds.
5. A skipped command is NOT RUN, not PASS. Do not add tests just to create activity.
