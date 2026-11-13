#!/usr/bin/env python3
"""One rule lives in one place. A sentence copied into two rule files costs context twice and drifts
when only one copy is edited. Point to the home section instead of restating it. Scans every rule,
skill, agent and doc markdown file plus the str constants of hooks; flags (a) an identical sentence in
two files and (b) a run of SHINGLE consecutive normalized words shared by two files."""
import collections, pathlib, re, sys
from rulescan import root, markdown_files, hook_files, hook_strings, norm_words

MIN_CHARS = 60  # shorter lines are headings, table cells and pointers
SHINGLE = 8
# normalized word runs that are allowed to recur (boilerplate frontmatter, license text, ...); keep tiny
ALLOW = [
    "name description version",
]

sources = []  # (rel, lineno, text)
for f in markdown_files():
    rel = f.relative_to(root).as_posix()
    for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
        sources.append((rel, i, line))
for f in hook_files():
    rel = f.relative_to(root).as_posix()
    for ln, s in hook_strings(f, docstrings=False):
        for j, line in enumerate(s.splitlines()):
            sources.append((rel, ln + j, line))

where = collections.defaultdict(set)
for rel, ln, line in sources:
    for s in re.split(r"(?<=[.!?])\s+", line):
        key = re.sub(r"\W+", " ", s.lower()).strip()
        if len(key) > MIN_CHARS:
            where[key].add(f"{rel}:{ln}")
dupes = sorted(f"{sorted(locs)}: {key[:90]}" for key, locs in where.items() if len({l.rsplit(':', 1)[0] for l in locs}) > 1)

shingles = collections.defaultdict(dict)  # shingle -> {file: first lineno}
for rel, ln, line in sources:
    w = norm_words(line)
    for i in range(len(w) - SHINGLE + 1):
        sh = " ".join(w[i:i + SHINGLE])
        if not any(a in sh or sh in a for a in ALLOW):
            shingles[sh].setdefault(rel, ln)
pairs = collections.defaultdict(list)
for sh, d in shingles.items():
    if len(d) > 1:
        fs = sorted(d)
        for a in range(len(fs)):
            for b in range(a + 1, len(fs)):
                pairs[(f"{fs[a]}:{d[fs[a]]}", f"{fs[b]}:{d[fs[b]]}")].append(sh)
overlap = sorted(f"{a} <-> {b}: {len(v)} shared, e.g. '{v[0]}'" for (a, b), v in pairs.items())

if dupes or overlap:
    sys.exit(f"{len(dupes)} repeated sentence(s), {len(overlap)} {SHINGLE}-word overlap(s):\n"
             + "\n".join(["repeated sentences:", *dupes, "overlaps:", *overlap]))
print("ok - no rule sentence is repeated across rule files")
