#!/usr/bin/env python3
"""One rule lives in one place. The always-loaded rule files are read on every session, so a sentence
copied into two of them costs context twice and drifts when only one copy is edited. Point to the
home section instead of restating it."""
import collections, pathlib, re, sys

root = pathlib.Path(__file__).resolve().parent.parent
ALWAYS_LOADED = ["rules/aodd.md", "rules/ai-sdlc-workflow.md", "rules/coding.md"]
MIN_CHARS = 60  # shorter lines are headings, table cells and pointers

where = collections.defaultdict(set)
for rel in ALWAYS_LOADED:
    for s in re.split(r"(?<=[.!?])\s+|\n", (root / rel).read_text(encoding="utf-8")):
        key = re.sub(r"\W+", " ", s.lower()).strip()
        if len(key) > MIN_CHARS and "§" not in s:  # "see `file` § Section" is a pointer, the fix itself
            where[key].add(rel)
dupes = sorted(f"{sorted(files)}: {key[:90]}" for key, files in where.items() if len(files) > 1)
if dupes:
    sys.exit("sentences repeated across always-loaded rules:\n" + "\n".join(dupes))
print("ok - no rule sentence is repeated across always-loaded rules")
