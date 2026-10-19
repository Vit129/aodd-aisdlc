#!/usr/bin/env python3
"""Every `rules/...md` path named in backticks by a rule, skill or doc must exist (lazy-loaded files are only reachable by these links)."""
import pathlib, re, sys

root = pathlib.Path(__file__).resolve().parent.parent
files = [*root.glob("rules/**/*.md"), *root.glob("skills/**/*.md"), *root.glob("optional/**/*.md"), root / "README.md", root / "AGENTS.md"]
missing = sorted(
    f"{f.relative_to(root)} -> {p}"
    for f in files if f.is_file()
    for p in set(re.findall(r"`(rules/[\w./-]+\.md)`", f.read_text(encoding="utf-8")))
    if not (root / p).exists() and not list(root.glob(f"optional/*/{p}"))
)
if missing:
    sys.exit("broken rule links:\n" + "\n".join(missing))
print("ok - rule links resolve")
