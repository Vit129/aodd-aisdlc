# JavaScript and TypeScript adapter

## Runner and scanning
Use the project's default runner (Vitest, Jest or `node:test`); the guard is an ordinary test in the default test command. Read each source file and strip comments before matching. Naive stripping can misinterpret `//` inside string literals; prefer the TypeScript compiler API or ESLint when available.

Parse import and require specifiers per core file and resolve them against the mapped io and ui paths, including aliases. Reject any that point into either path. The following illustrative JavaScript scanner expects a parser-backed `parseSpecifiers` and a resolver; it deliberately does not implement either:

```javascript
const path = require('node:path');

function checkCoreImports(files, readFile, parseSpecifiers, resolve) {
  const forbidden = ['src/io', 'src/ui'].map((p) => path.resolve(p));
  const problems = [];
  for (const file of files) {
    const source = readFile(file);
    // A parser must distinguish comments, strings and import syntax.
    for (const specifier of parseSpecifiers(source)) {
      const target = resolve(file, specifier);
      if (!target) continue;
      const absolute = path.resolve(target);
      const blocked = forbidden.some((dir) => {
        const relative = path.relative(dir, absolute);
        return relative === '' ||
          (!relative.startsWith('..' + path.sep) && relative !== '..' &&
           !path.isAbsolute(relative));
      });
      if (blocked) {
        problems.push(`${file}: use a core type or port; remove ${specifier}`);
      }
    }
  }
  return problems;
}
```

Supply files from `src/core/`, including nested modules. Test relative, aliased, static and dynamic imports and `require` as supported by the chosen parser and resolver; report unresolved specifiers instead of silently accepting them in a production guard.

## Literal checks
Record every forbidden code point in explicit ranges and verify that their union covers the entire intended block. For example, `[\u0E00-\u0E7F]` includes every code point in that block, including the currency symbol U+0E3F; splitting around it creates a hole. A fixture must contain one sample of each forbidden class, and a separate exhaustive fixture must contain every code point the guard claims to forbid and fail the guard. Use escapes when source text must be ASCII.

## Alternatives and baseline
ESLint `no-restricted-imports` or `no-restricted-syntax` can implement equivalent checks when configured for the same paths and syntax. It is a guard only when run by the default test command or CI; keep one source of truth for the policy.

A baseline entry can be `{ "rule": "example", "file": "src/core/example.js", "count": 0 }`. Compare violations by stable identity as well as counts: a new violation fails even if a different one disappears. A rising count fails; a falling count is reported with the affected rule and file so the checked-in baseline can shrink. Never automatically accept new violations.

## Negative controls
Put one violation per rule in `tests/fixtures/guard-negative/`. The test asserts that the scanner reports each violation; run the guard on each fixture and assert failure. Include the complete claimed character set for literal guards.

## Verification
The JavaScript example was checked with `node --check`. No TypeScript examples were compiled.
