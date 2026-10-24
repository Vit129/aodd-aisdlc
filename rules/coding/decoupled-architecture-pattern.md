# The Decoupled Core-UI-Translator Architecture Pattern (with Automated Architecture Guard)

> **Pattern Type:** Architectural & Engineering Standard (Dev & QA)  
> **Status:** Active Standard across all personal and production repositories  
> **Principle:** "A Pattern, not a copy-paste template" — defines invariants, boundaries, responsibilities, and automated test barriers rather than rigid boilerplate.

---

## 1. Intent & Problem Statement

### The Problem with "Template Copying"
When teams or LLM agents "copy a template", they duplicate boilerplate without understanding layer boundaries:
- Domain calculation formulas get copy-pasted into React/Vue components and tightly coupled to hooks, local state, or DOM APIs.
- Human-facing text literals (Thai/English) get embedded directly into JSX markup or hidden inside `|| 'Fallback'` statements.
- Design tokens erode as developers scatter raw `#hex` codes, arbitrary Tailwind classes (`text-[11px]`), and inline `fontSize: 14` throughout components.
- When logic bugs are fixed in one screen or repository, other places drift and retain the bug.
- Manual code review checklists fail to catch subtle regressions across hundreds of files.

### The Pattern Solution
This pattern enforces a **5-Layer Separation of Concerns** backed by a **Continuous QA Architecture Guard**:
1. **Domain Core (`*-core` / `logic/`):** Pure mathematical & business rules (zero DOM, zero framework dependencies).
2. **Design Tokens (`config/colors.*`, `config/typography.*`):** Central visual contract (zero raw hex or font sizes in components).
3. **Translator Dictionary (`strings.*`, `translations/`):** Central textual contract (zero language literals in logic or UI).
4. **Presentation UI (`ui/`, `components/`):** Visual assembly & event dispatching (delegates math to Core, styling to Tokens, labels to Translator).
5. **QA Architecture Guard (`tests/architectureGuard.test.*`):** Automated static/regex assertions running in CI/Vitest that fail immediately if any layer boundary is breached.

---

## 2. The 5 Structural Layers

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      5. QA Architecture Guard                           │
│     (Automated regex/AST scanner running in unit test runner < 100ms)    │
│   • 0 Missing Keys  • 0 Language Literals  • 0 Hex  • 0 Raw Font Sizes  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ verifies invariants
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         4. Presentation UI                              │
│              (React / Vue / Svelte / SwiftUI / Flutter)                 │
│         Visual composition only • Dispatches user actions               │
└──────────────┬─────────────────────┬─────────────────────┬──────────────┘
               │                     │                     │
               ▼                     ▼                     ▼
┌─────────────────────────┐ ┌─────────────────┐ ┌─────────────────────────┐
│     1. Domain Core      │ │ 2. Design Tokens│ │ 3. Translator / Strings │
│   (Math / Rules / DCA)  │ │ (Colors / Fonts)│ │  (TH_STRINGS / EN_...)  │
│  • Pure Functions       │ │ • Semantic Hex  │ │ • Single source of text │
│  • Headless & Portable  │ │ • Type Scale    │ │ • Parameterized Labels  │
│  • Zero DOM or React    │ │ • Theme Mapping │ │ • Zero hardcoded text   │
└─────────────────────────┘ └─────────────────┘ └─────────────────────────┘
```

---

## 3. Dev Implementation Pattern (How to Build It)

### Rule 1: The Headless Domain Core
- **Placement:** `src/logic/<domain>Logic.js` or extracted shared package `packages/<domain>-core`.
- **Placement Test:** *Can this function run in a plain Node/Python process without a browser, DOM, React context, or network mocks?* If yes → belongs in Core.
- **Language Decoupling:** Core logic must NEVER hardcode human language strings. If a calculation produces labeled output (e.g. breakdown items, prompt templates), it must accept an optional `labels` parameter with sensible defaults imported from a string module:
  ```typescript
  // GOOD: Core math accepts customizable label overrides
  export function calculateDeductions(
    inputs: TaxInputs,
    rules: TaxYearRules,
    labels: DeductionLabels = DEFAULT_DEDUCTION_LABELS
  ): DeductionResult { ... }
  ```
- **Formula Parsing:** User formula inputs (e.g. `"65000+2500"`) must be evaluated through a safe arithmetic parser (`evalExpression`) in Core, never through raw `eval()`.

### Rule 2: Single Source of Visual Truth (Tokens)
- **Colors:** All colors must resolve from `COLORS.*` or semantic CSS variables (`var(--bg)`, `var(--surface)`).
  - *Canvas/Charts:* When libraries (e.g. Chart.js, Canvas) require string values, pass `COLORS.MINT` or `withOpacity(COLORS.BLUE, 0.4)` — never inline `'#10b981'` or `'rgba(16, 185, 129, 0.2)'`.
- **Typography:** All font styles must resolve from `TYPOGRAPHY.*`.
  - Forbid numeric font sizes: `fontSize: 14` ❌ ➔ `fontSize: TYPOGRAPHY.TEXT_TITLE` or `TYPOGRAPHY.SIZE_H2` ✅.
  - Forbid arbitrary Tailwind px values: `className="text-[10px]"` ❌ ➔ `fontSize: TYPOGRAPHY.TEXT_MICRO` ✅.
  - Forbid raw font stacks: `fontFamily: 'monospace'` ❌ ➔ `fontFamily: TYPOGRAPHY.FONT_MONO` ✅.

### Rule 3: Single Source of Textual Truth (Translator)
- Every user-visible word, button label, table header, aria-label, and AI prompt template lives in the translation dictionary (`strings.js` or `translations/*.js`).
- **Dynamic interpolations:** Use pure formatter functions:
  ```javascript
  // GOOD: Function token in translation dictionary
  LBL_MONTHS_LEFT: (months) => `${months} เดือนที่เหลือ`,
  MSG_CO_PVD: (formattedAmount) => `บริษัทสมทบให้ ${formattedAmount} ตลอดปี`,
  ```
- **No Inline Fallbacks:** Never write `label || 'ประกันสังคม'` in a component. If the translation key is missing, the test suite must fail rather than silently falling back to a hardcoded string.

### Rule 4: Shared UI Primitives (`*-ui`)
- When UI elements are reused across distinct applications (e.g. `Card`, `MoneyInput`, `BreakdownTile`, `ChipButton`, `ProgressBar`, `Stepper`), extract them to a shared package (`@<scope>/<domain>-ui`).
- Shared components must remain token-injected and headless-compatible, relying on CSS variables or imported token defaults.

---

## 4. QA Verification Pattern (How to Guard It)

Instead of relying on human vigilance or manual review checklists, QA implements an automated **Architecture Guard** test file (`tests/architectureGuard.test.js` or `tests/architecture_guard_test.py`).

### The 4 Canonical Automated Invariants

```javascript
describe('Architecture Guard (Logic / UI / Translator / Tokens)', () => {
  const allSrcFiles = getAllSourceFiles('src');

  // Guard 1: Zero Missing Translation Keys
  it('enforces that all referenced UI string keys exist in translation dictionary', () => {
    const missing = [];
    for (const file of allSrcFiles) {
      const code = stripComments(fs.readFileSync(file, 'utf8'));
      for (const m of code.matchAll(/\b(?:STRINGS|UI_STRINGS)\.([A-Z0-9_]+)\b/g)) {
        if (!(m[1] in STRINGS)) missing.push(`${file}: ${m[1]}`);
      }
    }
    expect(missing).toEqual([]);
  });

  // Guard 2: Zero Hardcoded Language Literals Outside Translation Files
  it('enforces zero hardcoded language characters outside designated strings files', () => {
    const violations = [];
    const languageRegex = /[\u0E01-\u0E3A\u0E40-\u0E7F]/; // Thai Unicode range
    for (const file of allSrcFiles) {
      if (isTranslationFile(file)) continue;
      const lines = stripComments(fs.readFileSync(file, 'utf8')).split('\n');
      lines.forEach((line, idx) => {
        if (languageRegex.test(line)) violations.push(`${file}:${idx + 1}: ${line.trim()}`);
      });
    }
    expect(violations).toEqual([]);
  });

  // Guard 3: Zero Hardcoded #Hex Colors Outside Design Tokens
  it('enforces zero #hex color literals outside config/colors', () => {
    const violations = [];
    const hexRegex = /#[0-9a-fA-F]{3,8}\b/;
    for (const file of allSrcFiles) {
      if (isColorConfigFile(file)) continue;
      const lines = stripComments(fs.readFileSync(file, 'utf8')).split('\n');
      lines.forEach((line, idx) => {
        if (hexRegex.test(line)) violations.push(`${file}:${idx + 1}: ${line.trim()}`);
      });
    }
    expect(violations).toEqual([]);
  });

  // Guard 4: Zero Hardcoded Font Sizes or Inline Font Stacks
  it('enforces that all fontSize and fontFamily reference TYPOGRAPHY tokens', () => {
    const violations = [];
    const fontRegex = /\b(fontSize|fontFamily)\s*:(?!\s*TYPOGRAPHY\.)/;
    for (const file of allSrcFiles) {
      if (isTypographyConfigFile(file)) continue;
      const lines = stripComments(fs.readFileSync(file, 'utf8')).split('\n');
      lines.forEach((line, idx) => {
        if (fontRegex.test(line)) violations.push(`${file}:${idx + 1}: ${line.trim()}`);
      });
    }
    expect(violations).toEqual([]);
  });
});
```

---

## 5. Anti-Patterns & Traps

| Anti-Pattern | Why It Fails | Pattern Solution |
|---|---|---|
| **The Inline Fallback Trap** (`UI_STRINGS.FOO \|\| 'Default'`) | Masking missing keys. Defeats bilingual translation and leaks untracked strings into the UI. | Remove fallback. If key is missing, let Architecture Guard fail in CI. |
| **The Chart/Canvas Hex Trap** (`backgroundColor: '#10b981'`) | Breaks dark/light theme switching and fractures color updates. | Import `COLORS` and use `COLORS.EMERALD` or `withOpacity(COLORS.EMERALD, 0.2)`. |
| **The Template Duplication Trap** (Copying a calculation helper into 3 components) | Calculation drift. When tax laws or formulas update, duplicate files diverge. | Extract logic to `*-core` or `src/logic/` with 100% unit test coverage. |
| **The Arbitrary CSS Override Trap** (`text-[10.5px]`, `fontSize: 13`) | Destroys typographical rhythm and causes visual clutter. | Map to nearest semantic type scale token (`TYPOGRAPHY.TEXT_MICRO` or `TEXT_LABEL`). |
| **The Monolithic State-Math Hook** (Mixing 400 lines of tax math inside a React hook) | Impossible to test in headless CI without DOM mocks. | Separate into pure calculation functions (`taxLogic.js`) called by a slim state hook (`useTaxState.js`). |

---

## 6. Definition of Done Checklist (Dev & QA)

A feature adhering to this pattern is only **Done** when:
- [ ] **Pure Core:** All business calculations and validation formulas live in headless modules with 100% unit test coverage.
- [ ] **Zero Language Literals:** All UI text, error alerts, and aria-labels are declared in translation files.
- [ ] **Zero Rogue Hex:** All color styles resolve through semantic tokens or CSS variables.
- [ ] **Zero Rogue Fonts:** All font sizes and stacks resolve through typography tokens.
- [ ] **Automated Guard Green:** `tests/architectureGuard.test.*` executes and passes cleanly with 0 violations.
