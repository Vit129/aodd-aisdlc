# Course Check — Loop Breaking and Context-Budget Handoff

Use when work is spinning, repeated attempts fail, or the context window is filling up.

## Loop signals

Stop and run a course check if you notice any of these:
- Repeating the same failing command or test with minor tweaks.
- Re-reading the same files without forming a new, testable question.
- Circular reasoning or second-guessing a settled decision without new evidence.
- Making edits without first reading the failing path and verifying a hypothesis.

## 3-strikes rule

- **No blind edits:** never edit code just to see if a failure goes away.
- **3 strikes:** if three focused attempts on the same subproblem fail to advance understanding
  or turn a test green, stop immediately.
- **Pivot or escalate:** switch to `skills/ai-sdlc/references/bug-hunt.md` to re-trace from
  scratch, or escalate to the user with what was tried, what each attempt showed, and the
  concrete blocker.

## Bounded thinking

Cap exploration before acting: state the single question you are trying to answer, read only
the relevant slice, and decide the next concrete action. Do not hold long open-ended
speculation in context.

## Context-budget trigger

When context is nearly full or a multi-step task needs a clean continuation:
1. Write `$AODD_PLANS/[FEATURE]/handoff.md` following the Resume protocol in
   `skills/ai-sdlc/references/ai-sdlc-progress-spec.md` (State, Tried, Next, Open; under 30
   lines).
2. Update `[FEATURE]/ai-sdlc-task-progress.md` so completed boxes and the `Last updated`
   line are current.
3. Stop cleanly and tell the user the handoff file is ready for the next session.
