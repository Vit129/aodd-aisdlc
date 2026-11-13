#!/usr/bin/env python3
"""Every `rules/...md`, `skills/...md`, `docs/...`, `hooks/...`, `scripts/...` path named in backticks by a rule, skill or doc must exist;
a "`file.md` § Heading" reference must match a real heading in that file; a backticked `/name` slash
command must be a skills/<name>/ dir or a companion skill named in README.md."""
import pathlib, re, sys

root = pathlib.Path(__file__).resolve().parent.parent
files = [*root.glob("rules/**/*.md"), *root.glob("skills/**/*.md"), *root.glob("optional/**/*.md"), *root.glob("docs/*.md"), root / "README.md", root / "AGENTS.md"]
# companion skills installed separately (named in README.md); everything else must be a skills/<name>/ dir
# slash commands are checked only where the contract and the core skills name them; a domain skill (uxui-designer's /polish,
# /audit, ...) defines its own sub-commands, so they are not skills/<name>/ dirs
SLASH_CHECKED = ("rules/", "skills/ai-sdlc/", "skills/chief-of-staff/", "skills/grill-plan/", "skills/agent-ops/",
                 "skills/delivery-workflow/", "skills/housekeeping/")
SLASH_ALLOW = {"code-review", "scrutinize", "post-mortem", "debug-mantra", "agy", "ai-sdlc"}
# backticked `/word` that is a URL path or placeholder, not a command
NOT_COMMANDS = {"orders", "products", "users", "tmp", "slash-command"}
PATH_RE = re.compile(r"`((?:rules|skills|docs|hooks|scripts)/[\w./-]+\.(?:md|py|sh|json))`")


def exists(p, rel=""):
    # a skill's own `scripts/x.py` or `references/x.md` resolves against that skill's dir
    skill = "/".join(rel.split("/")[:2]) if rel.startswith("skills/") else ""
    return (root / p).exists() or bool(list(root.glob(f"optional/*/{p}"))) or bool(skill and (root / skill / p).exists())


def headings(p):
    f = root / p if (root / p).exists() else next(iter(root.glob(f"optional/*/{p}")), None)
    if f is None or f.suffix != ".md":
        return None
    return [re.sub(r"\W+", " ", re.sub(r"^#+\s*", "", l).lower()).strip()
            for l in f.read_text(encoding="utf-8").splitlines() if l.startswith("#")]


bad = []
for f in files:
    if not f.is_file():
        continue
    rel = f.relative_to(root).as_posix()
    for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
        for p in set(PATH_RE.findall(line)):
            if not exists(p, rel) and "/<" not in p and "NNNN" not in p:
                bad.append(f"{rel}:{n}: missing path {p}")
        for m in re.finditer(r"`((?:rules|skills|docs)/[\w./-]+\.md)`[^`§\n]{0,40}?§\s*([^.,;:()`\n]+)", line):
            hs = headings(m.group(1))
            want = re.sub(r"\W+", " ", m.group(2).lower()).strip()
            if hs is not None and want and not any(h.startswith(want) or want.startswith(h) for h in hs if h):
                bad.append(f"{rel}:{n}: no heading '{m.group(2).strip()}' in {m.group(1)}")
        if rel.startswith(SLASH_CHECKED):
            for c in re.findall(r"`/([a-z][a-z0-9-]*)`", line):
                if c not in SLASH_ALLOW | NOT_COMMANDS and not (root / "skills" / c).is_dir() and not list(root.glob(f"optional/*/skills/{c}")):
                    bad.append(f"{rel}:{n}: unresolved slash command /{c}")
if bad:
    sys.exit(f"{len(bad)} broken rule link(s):\n" + "\n".join(sorted(bad)))
print("ok - rule links resolve")
