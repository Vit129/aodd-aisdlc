# Python adapter

**Status: NEW, not used in any surveyed project; verify before adopting.**

Use pytest in the default test command. Parse each module under `app/core/` using `ast`, not regex. Collect `Import` and `ImportFrom` module names and reject imports of `app/io/` and `app/ui/` package prefixes. Also reject direct `open` calls, modules such as `requests`, `socket` and `subprocess`, and `os.environ` access. Resolve relative imports in a production guard; account for aliases, alternate builtins access and other I/O APIs according to project policy.

```python
import ast
from pathlib import Path

DENIED = ("app.io", "app.ui", "requests", "socket", "subprocess")


def scan(path):
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    issues = []
    aliases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [item.name for item in node.names]
            aliases.update({item.asname or item.name: item.name for item in node.names})
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""]
        else:
            names = []
        if any(name == prefix or name.startswith(prefix + ".")
               for name in names for prefix in DENIED):
            issues.append("import: use a core type or port")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "open":
                issues.append("open: move file access to io")
        if isinstance(node, ast.Attribute) and node.attr == "environ":
            if isinstance(node.value, ast.Name) and aliases.get(node.value.id) == "os":
                issues.append("environ: pass configuration through a port")
    return issues


def test_negative_control():
    issues = scan("tests/fixtures/guard_negative/example.py")
    for rule in ("import:", "open:", "environ:"):
        assert any(issue.startswith(rule) for issue in issues), rule
```

The fixture must include each denied package prefix and module, `open`, and environment access; assert each distinct case is reported. The example groups denied imports and is a starting point, not a complete purity proof. Production checks must handle relative imports, `from os import environ`, import aliases and traversal order; check each core module and supply a fixture for every supported form. A negative-control test runs the scanner on each known-bad fixture and asserts each rule reports; the guard must fail for each fixture.

AST scanning cannot see dynamic imports such as `importlib` with a variable name. It also cannot prove that called functions are pure. Review these gaps and add project-specific checks.

The example was checked with `python3 -m py_compile`.
