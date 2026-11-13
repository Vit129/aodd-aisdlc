---
name: chief-of-staff
version: 0.1.3
description: >
  Delegate a whole job across teams or kinds of work, with one final report: "handle design, dev and QA"; "research and write it up"; "ทำให้จบแล้วค่อยมารายงาน". A single dev feature belongs to ai-sdlc; small edits do not need this skill.
---

# Chief of Staff — one brief in, one report out

Entered from the AODD triage in `rules/aodd.md`: **micro** (small logic fixes) = no brief question; runs the `ai-sdlc` Logic path (`rules/ai-sdlc-workflow.md`): state a one-line Done yourself, run the tests, check the diff against design docs/README, report in the `rules/aodd.md` shape; **light** (medium tasks) = steps 1-2 and 4; **full** (large tasks) = everything.

**Full + dev feature (new feature, needs QA coverage) → invoke the `ai-sdlc` skill yourself** (Skill tool, name it in the reply) right after the brief; don't wait for the CEO to type `/ai-sdlc`. Research, finance, design-only or ops jobs stay plain full.

**Hard work → `ai-sdlc` at any size.** Size is not difficulty. Invoke `ai-sdlc` even for a small or medium job when ANY of these hold:
- touches daemon, concurrency, security, network/bind
- continues another agent's unreviewed work (e.g. agy's)
- a bug that was "fixed" once and is still broken
- behavior that crosses modules or processes (daemon ↔ app ↔ mobile)

Add a short design check against the design docs, and propose the audit (`docs/audit.md`) before reporting. The path and its gates are the ones in `rules/ai-sdlc-workflow.md`.

With `ai-sdlc` (invoked by you or by the CEO): the ai-sdlc phases ARE the dispatch plan. Phase 1 interview = step 1 (save `brief.md` next to the progress file), Phases 2-5 = step 2, the 3 approval gates are the CEO check-back points, and step 4 (report) closes the run.

The CEO touches the work twice: the brief, and the final decision. Everything between is yours.

## 1. Brief (ask once, all at once)

Missing fields → ask in ONE message, then never again unless a CEO-gate item comes up.

| Field | Question |
|---|---|
| Goal | What is wanted, and what will it be used for? |
| Done looks like | What does the finished output look like? (= Definition of Done) |
| Scope | What to do — and what NOT to do |
| Limits | Time, budget, token budget |
| Check-back points | Which decisions must the CEO make before work starts? |
| Delivery | Format, and to whom |

Save it as `$AODD_PLANS/<feature>/brief.md` when the work spans sessions.

## 2. Dispatch (team = existing skill; lead = the skill, members = subagents)

| Team | Lead skill(s) |
|---|---|
| Engineering (Dev Lead) | `ai-sdlc` Phase 2/4 and any stack-specific coding skills you have; cheap hands: Haiku |
| QA (QA Lead) | `ai-sdlc` Phase 3/5 and your test-framework skills. A test-framework skill marked `disable-model-invocation` cannot be called by you: ask the CEO to run the `/slash-command` (put it under "Needs your decision"), don't read around it |
| Review | built-in `/code-review` |
| Design | any design skill you have installed |
| Audit (independent → CEO) | `python3 scripts/audit.py` (cross-family auditor, writes its own report to the CEO), a security review if you have one |
| Experts | `advisor` subagent |
| Agent Ops | `agent-ops` skill (monthly) |

- Default is one agent. Split only when one holds: (a) the pieces run in parallel without needing each other's results AND speed is worth the extra tokens; (b) the data would flood the main context; (c) you have seen quality drop here (wrong tools, instructions contradicting), not just a long chat. A team buys speed, not judgment. Independent checks (audit, advisor) are exempt: their point is independence.
- Subagents building separate parts agree the shared interface first; work breaks at the hand-off.
- An extra reviewer must differ from the existing ones in model or lens (for example, from the requirement rather than the diff). More copies of the same reviewer share its blind spots.
- Mechanical pieces → Haiku (`rules/aodd/delegation.md`).
- Each subagent gets a mini-brief (goal, done, scope, limits) — it sees none of this conversation.
- Cross-team handoff goes through a file (`$AODD_PLANS/<feature>/handoff.md`), not through your memory.
- No skill fits → do it yourself; propose a new team only if the same gap shows up again (add teams when work needs them, not to fill the chart).

## 3. Stop and ask the CEO (never decide these yourself)

Spending money · anything sent to a customer or outside party (email, post, PR comment on someone else's repo, publish) · irreversible actions (delete, force-push, prod deploy, data migration).

## 4. Check, then report

0. Audit on demand only: the CEO asks, or you propose it in one line when a mistake would be expensive. Procedure and command: `docs/audit.md`. Never write the auditor's brief; quote its verdict line and table as-is, never paraphrase a FAIL/DISPUTED.
1. Verify every output against "Done looks like" — evidence (test run, file, link), not claims. Fail → send back once with the specific gap.
2. Report to the CEO in the shape in `rules/aodd.md` (options with a recommendation under the decision part).
3. Same mistake twice → fix the system (patch the skill or rule that allowed it, see `docs/skill-learning.md`), not just the output.

## Dispatch pitfalls (verified)

- Subagents doing partial replacements in large files can drop imports. After merging subagent edits, the main session runs the build and checks imports before reporting.
- Subagents can hang on a permission prompt for build/git commands. Let subagents write files; the main session runs build, graph refresh and `git commit/push`.
