#!/usr/bin/env python3
"""One rule lives in one place. A sentence copied into two rule files costs context twice and drifts
when only one copy is edited. Point to the home section instead of restating it. Scans every rule,
skill, agent and doc markdown file plus the str constants of hooks; flags (a) an identical sentence in
two files and (b) a run of SHINGLE consecutive normalized words shared by two files."""
import collections, pathlib, re, sys
from rulescan import root, markdown_files, hook_files, hook_strings, norm_words

# the AODD core set: the contract, the workflow, the docs and the core skills. The shingle check runs only here.
CORE = ("rules/ai-sdlc/", "rules/effort/", "rules/coding", "docs/", "agents/", "skills/ai-sdlc/", "skills/chief-of-staff/",
        "skills/agent-ops/", "skills/delivery-workflow/", "skills/housekeeping/",
        "hooks/", "optional/")  # plus rules/*.md and the root files, see is_core
ROOT_FILES = {"AGENTS.md", "README.md", "ARCHITECTURE.md", "CONTEXT.md"}
# sibling domain skills (stack and test-framework skills) share templated sections of their own; an identical sentence
# that occurs only among them is allowed. A sentence shared with any core file is still flagged.
SIBLING_SKILLS = ("skills/backend-dev/", "skills/frontend-dev/", "skills/performance-testing/", "skills/robotframework-testing/",
                  "skills/playwright-testing/", "skills/playwright-cli/", "skills/security/", "skills/test-scenario/",
                  "skills/uxui-designer/", "skills/macos-swiftui/",
                  "rules/playwright/", "rules/robot/")  # the last two: parent/child header lines repeat by design


def is_core(rel):
    return rel in ROOT_FILES or (rel.startswith("rules/") and rel.count("/") == 1) or rel.startswith(CORE)


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
def flagged(locs):
    files = {l.rsplit(':', 1)[0] for l in locs}
    return len(files) > 1 and not all(f.startswith(SIBLING_SKILLS) for f in files)


dupes = sorted(f"{sorted(locs)}: {key[:90]}" for key, locs in where.items() if flagged(locs))

shingles = collections.defaultdict(dict)  # shingle -> {file: first lineno}
for rel, ln, line in sources:
    if not is_core(rel):
        continue
    # a backticked path or command is a pointer to a home, not a copied rule; one-letter tokens are regex, not prose
    w = norm_words(re.sub(r"`[^`]*[./][^`]*`", " ", line))
    if sum(len(t) < 2 for t in w) > len(w) // 4 or (rel.startswith(("hooks/", "optional/")) and line.count("|") >= 3):
        continue  # regex, not prose
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
