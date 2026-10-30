# Tracing a Delivery Entrypoint

Use before running a lifecycle menu, release helper, deploy helper, or full-cycle command. The goal is to learn the repo's real behavior from its code, so the agent does not depend on the user describing it.

## 1. Follow the full call chain

1. Find the entrypoint: a `start` menu, a Make or package-script target, a shell script, or a CI workflow. Read its argument parser and dispatch.
2. For each selected branch, follow every helper it calls (package scripts, shell/Node/Python scripts, Make targets, CI steps) down to the actual commands. Record the ordered chain with file and line references.
3. Read the helpers' implementations, not just their names or help text. Look for: prompts and silent defaults, broad staging, version defaults, suppressed failures (`|| true`, `2>/dev/null`), admin or bypass merge flags, forced refs, branch deletion, production targets, service restarts, and rollback scope.
4. Check which behaviors are actually tested. A running dev server is not a passing suite. A build is not a test run. A deploy CLI's success is not a live-revision check.
5. Compare repo state: version files, changelog top entry, tags and their targets, hosted release, deploy manifest or Pages metadata, live version, and any shared dependency commit. The version baseline is the last completed release.

## 2. Write the evidence map

Summarize the selected flow once, and reuse it in the plan and the final report:

| Stage | Entrypoint / helper | Actual action | Gate / evidence | Side effect or gap |
|---|---|---|---|---|
| Dev / preview | | | | |
| Test / QA | | | | |
| Version / docs | | | | |
| Commit / push / merge | | | | |
| Tag / hosted release | | | | |
| Deploy / install | | | | |
| Live verification | | | | |

Do not write project-specific command cookbooks into this skill. Discover the commands from the checkout each time.

## 3. Capability profile

| Capability | Record |
|---|---|
| QA | Automated suites, architecture guards, CI checks, or none. Name the human acceptance owner if there is no automated QA. |
| Dev / preview | Whether it is isolated from production data and services, its mode and target, and whether a person inspects it. |
| Version identity | Semver, any separate build number, and every file that carries a version (app, CLI, daemon, package, generated notes, manifest). |
| Release publication | Changelog generator and range, tag, hosted release and assets, package publishing. |
| Deploy / install | Hosting target, backend components, local install, restart effects, live verification. |
| Shared code | Local packages or shared dependencies, and the exact commit or version used to build and deploy. |

Do not require a QA suite the repo lacks. Do not describe a preview as automated QA.

## 4. Demonstrate only when reading leaves a question

- Start with help output, unit tests with stubs, and a dry-run whose implementation you have read.
- A dry-run counts as safe only if every branch it reaches avoids writes, network mutations, installs, restarts, pushes, tags, merges, and deploys. Do not infer that from the name `--dry-run`.
- If a menu's behavior still needs confirmation, start it in a TTY to see the options, then exit without selecting any action. Never send input that could select an action.
- If behavior cannot be observed safely, use a temporary isolated copy with stubbed commands. Do not point it at real credentials or remotes, and remove what it created.
- If nothing establishes the behavior, mark it unknown and stop before the mutation that depends on it.

## 5. Decide whether the helper is safe to run as is

Do not run a helper as is if it commits before required docs or QA, merges before checks, defaults a version or target silently, skips required tests, stages unrelated files, tags, publishes a release, or installs new source under `skip` (deploying the already-merged current commit under `skip` is allowed, see SKILL.md), installs before publish or verification, retags an existing version, or reports success after a suppressed failure. Use narrower supported steps that keep the identity and order, or stop at the first unsafe boundary and report what is missing.
