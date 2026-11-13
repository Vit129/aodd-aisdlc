"""Shared file set for the rule guard tests: markdown rule text plus str constants of hooks."""
import ast, pathlib, re

root = pathlib.Path(__file__).resolve().parent.parent
EXCLUDE = ("CHANGELOG.md", "graphify-out/", ".tmp/", ".kouen-worktrees/")


def _ok(p):
    r = p.relative_to(root).as_posix()
    return p.is_file() and not any(e in r or r == e for e in EXCLUDE)


def markdown_files():
    pats = ["rules/**/*.md", "skills/**/*.md", "agents/*.md", "docs/*.md"]
    fs = [f for pat in pats for f in root.glob(pat)]
    fs += [root / n for n in ("README.md", "ARCHITECTURE.md", "AGENTS.md", "CONTEXT.md")]
    return sorted({f for f in fs if _ok(f)})


def hook_files():
    return sorted(f for pat in ("hooks/*.py", "optional/*/hooks/*.py") for f in root.glob(pat)
                  if _ok(f) and not f.name.startswith("test_"))


def hook_strings(path, docstrings=True):
    """(lineno, text) for each str constant in a hook; docstrings=False drops them (never sent to a model)."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return []
    skip = set()
    if not docstrings:
        for n in ast.walk(tree):
            if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and ast.get_docstring(n, clean=False) is not None:
                skip.add(id(n.body[0].value))
    return [(n.lineno, n.value) for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in skip]


def text_units():
    """(relpath, lineno, text) for every line of markdown and every hook string constant (per line)."""
    out = []
    for f in markdown_files():
        rel = f.relative_to(root).as_posix()
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            out.append((rel, i, line))
    for f in hook_files():
        rel = f.relative_to(root).as_posix()
        for ln, s in hook_strings(f):
            for j, line in enumerate(s.splitlines()):
                out.append((rel, ln + j, line))
    return out


def norm_words(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).split()
