# Code Review Report Format

Sub-file of `rules/coding.md`; read when producing a code review.

Shared shape across every automated code-review checklist
(`backend-dev`, `frontend-dev`, `playwright-testing`, `robotframework-testing`) — found
duplicated near-verbatim across the coding-standards skills, extracted here as the one source.
Each skill's own checklist content (what to actually check) stays in that skill's own
reference file — this is only the process shape, report format, and severity-to-action
mapping.

**Process (after loading the platform's own coding-standards reference and checklist):**
check every file against the checklist → output the review report below → if
NEEDS_FIX and auto-fixable → fix immediately, re-review → if APPROVED → proceed
(to execution for QA test code, to PR for Dev code).

```markdown
### 🔍 [Skill] Code Review
- Spec Fidelity: ✅ MATCHES SPEC / ⚠️ GAPS / ❌ SCOPE CREEP — checked against the originating
  task/spec end-to-end, reported separately from the standards table below (clean code that
  doesn't match what was asked, and a faithful implementation that's badly written, are two
  different findings — don't conflate them)
- Status: APPROVED ✅ / NEEDS FIX ⚠️
- Files Reviewed: {N}
- [Framework: X / Platform: Android|iOS / Mode: API|Web UI — whichever applies]

| Severity | File | Issue | Fix |
|----------|------|-------|-----|
| 🔴 High | ... | ... | ... |
| 🟡 Med | ... | ... | ... |
| 🟢 Low | ... | ... | ... |

[Auto-Fixable: {Y/N} — QA test-code review only, not Dev code review]
Critical Blockers: {N}
```

Severity → action (Dev vs QA phrasing differs slightly, meaning is identical):

| Severity | Dev action (backend-dev/frontend-dev) | QA action (playwright/robotframework) |
|---|---|---|
| 🔴 High | Must fix before merge | Must fix before run |
| 🟡 Medium | Fix before PR approval | Fix before PR |
| 🟢 Low | Fix when convenient | Fix when convenient |

