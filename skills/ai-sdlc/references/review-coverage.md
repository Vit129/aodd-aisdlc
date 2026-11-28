# Review coverage

Apply to every review of a diff, PR or branch, whichever skill does the analysis
(`9arm-skills:scrutinize`, a built-in `code-review`, or a plain review). A prompt-only
review tends to skip files on a large diff and to cite line numbers that drift from the
code. These four steps put hard limits on both.

## 1. Build the checklist with git, not judgement

```bash
git --no-pager diff --no-ext-diff --no-color --name-status <base>...<head>
```

- Workspace review: `git status --porcelain` (include untracked files).
- Merged PR: `<merge>^1..<merge>^2`.
- Every path in the output is one checklist row. Do not drop `.md`, `.json`, `.plist`
  or other config files by type: skills, rules and manifests are code here.
- Generated or vendored files (lockfiles, `dist/`, index outputs) may be skipped, but
  each still gets a row with its reason.

## 2. Review every row

- Each row ends as `reviewed` or `skipped: <concrete reason>`. None is left unmarked.
- On a large diff, work in batches of related files (one module, or code plus its
  tests). Do not stop after the first serious finding.
- For a deleted file, read the old side for removed interfaces callers may still use.

## 3. Verify every cited line before reporting

Re-read the cited range in the new file (`sed -n '<start>,<end>p' <path>` or Read with
offset/limit). If the code there is not what the finding describes, fix the number or
drop the finding. Never cite a line from memory of the diff hunk.

## 4. Report coverage with the findings

End the review with:

```
Coverage: <reviewed>/<total> files (<pct>%)
Skipped: <path>: <reason>, ...
```

A review without this line is incomplete. Behavior changes that are not bugs (a removed
option, a new default) go in their own short section.
