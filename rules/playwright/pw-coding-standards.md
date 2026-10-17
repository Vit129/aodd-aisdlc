# Playwright Testing — Global Coding Standards

## Contents

- [1. Global Standards & Tooling Facts](#1-global-standards--tooling-facts)
- [2. Automation & Execution Strategy](#2-automation--execution-strategy)
- [3. Reference Links](#3-reference-links)
- [4. Test Structure Patterns (by Design Technique)](#4-test-structure-patterns-by-design-technique)

Shared environment, tooling, and architectural facts for Playwright test automation across API and Web UI.

---

## 1. Global Standards & Tooling Facts

### Environment Configuration
- Environment files: `.env`, `.env.local`, `.env.sit`, `.env.uat` (loaded via `dotenv.config({ path: \`.env.\${process.env.ENV || 'sit'}\` })`).
- **Sensitive data (MUST be in `.env`):** credentials, tokens, passwords, secrets, login emails, API keys, OAuth URLs.
- **Non-sensitive business data (MUST be in `.ts` fixture):** `companyCode`, `customerCode`, `invoiceNumber`, `productCode`, user roles.
- `process.env.X` inside fixture files is allowed ONLY for sensitive data. Business data must be hardcoded in fixtures.
- **Double Login Rule:** If a feature requires SSO + project-level auth, SSO credentials/URL go in `.env`; project-level user identifiers go in `fixtures/`.

### Test Data & Fixtures
- Test data files live in `fixtures/[system-kebab]/[feature-kebab]/[featureCamel]Data.ts`.
- **Cross-Layer Shared Fixtures:** Data used across both API and Web UI MUST live in `tests/shared-fixtures/[system-kebab]/[feature-kebab]/` as a single source of truth.
- Dynamic data: Use `Date.now()` or `Math.random()` for dynamic identifiers (reference numbers, unique emails).

### Locators & Wait Rules
- **Zero hard wait (MANDATORY):** `waitForTimeout()` is strictly forbidden. Use Playwright Web-First Assertions (`await expect(...)...`) or explicit wait conditions (`waitForResponse`, `waitForURL`).
- **Locator Priority Order:**
  1. `getByTestId('x')` — scope container or unique element (see `rules/data-testid-mapping.md` for naming rules)
  2. `getByRole('button', { name: L.key })` — buttons, links, headings (using `Labels.ts` for text)
  3. `getByLabel(L.key)` — form controls with associated `<label>`
  4. `getByPlaceholder(L.key)` — inputs without visible label
  5. `locator('css')` — last resort only when semantic locator is impossible. Never use raw XPath or `.nth()` without filter.

### Mandatory Naming & Tags
- **Describe Block:** MUST include `[TS-xxxx]` or `[ID-xxxx]` scenario/feature ID.
  ```typescript
  test.describe('@Critical [TS-0001] User Authentication', () => { ... });
  ```
- **Test Case:** MUST include `[TC-xxxx]` testcase ID prefix.
  ```typescript
  test('[TC-0001] User logs in successfully with valid credentials @Feature @Important @Scenario', async ({ page }) => { ... });
  ```
- **Mandatory Tags:**
  - `@Important`: `Critical` | `High` | `Medium` | `Low`
  - `@Scenario`: `Success` | `Alternative` | `Error`
  - `@Feature`: feature name identifier

### Project Structure & Layer Roles
```
tests/api-testing/
├── tests-api/[system-kebab]/[feature-kebab]/[feature].spec.ts
├── helpers/[system-kebab]/[feature-kebab]/[feature]Helper.ts
├── schemas/[system-kebab]/[feature-kebab]/[feature]Schema.ts
└── fixtures/[system-kebab]/[feature-kebab]/[feature]Data.ts

tests/web-testing/
├── tests-web/[system-kebab]/[feature-kebab]/[feature].spec.ts
├── pages/[system-kebab]/[feature-kebab]/[feature]Page.ts
├── helpers/[system-kebab]/[feature-kebab]/[feature]Helper.ts
├── fixtures/[system-kebab]/[feature-kebab]/[feature]Data.ts
└── fixtures/[system-kebab]/[feature-kebab]/[feature]Labels.ts

tests/shared-fixtures/
└── [system-kebab]/[feature-kebab]/[feature]SharedData.ts
```
- **Terminology:**
  - **Service:** Atomic API callers (`UserService.ts`), single responsibility, returns typed response.
  - **Page:** Encapsulates UI elements and interactions for a page or component (`LoginPage.ts`).
  - **Helper:** Orchestrates multi-step business flows combining services or pages (`CheckoutHelper.ts`).

### Architecture-First for QA
Before writing a suite, declare the layer split: Page Objects (`pages/`), Helpers (`helpers/`), Test Fixtures (`fixtures/`), Test Specs (`tests-*/`). Size target and the no-monolith rule: § Anti-Monolith & Separation Pattern in `rules/coding.md`.

---

## 2. Automation & Execution Strategy

### Priority & Scope
| Priority | API Automation | Web UI Automation | Strategy |
| :--- | :--- | :--- | :--- |
| **Critical** | Mandatory | Mandatory | E2E Full Coverage |
| **High** | Mandatory | Mandatory | Core flows |
| **Medium** | Mandatory | Optional | API first; UI secondary |
| **Low** | Mandatory | Skip | API contract only |

### Hybrid Execution Strategy
- **High-Speed Auth:** Do not perform UI login in every test. Authenticate via API `POST /login`, generate `storageState.json`, and inject into browser context (except for tests verifying the login UI itself).
- **API Setup for UI Tests:** Seed preconditions via API calls before UI execution to keep UI tests atomic, fast, and resilient.
- **Worker-Scoped Fixtures:** For expensive setup (database connection, master data seeding), use `scope: 'worker'` to execute once per Worker.
- **Test Independence:** Every test must manage its own state (create and clean up its data in `afterEach`). Tests must run in parallel without order dependency.

### `playwright-cli` Session Continuity (exploration / verification rounds)
A headless `playwright-cli` session shuts down after 1 hour idle; if a context compaction or long pause exceeds that, the browser dies and every element ref is lost. Open each round with both flags:

```bash
playwright-cli -s={feature} open <app-url> --idle-timeout=0 --persistent
```

- Pass the flags on the `open` that starts the round, and reuse the same `-s={feature}` name for every later command.
- `--persistent` keeps the profile (cookies/login) on disk at `~/Library/Caches/ms-playwright/daemon/<hash>/ud-{session}-chrome`; it survives `close`, only `delete-data` removes it.
- If only auth needs to survive, `state-save auth.json` / `state-load auth.json` is lighter.

---

## 3. Reference Links

- 🌐 **Web UI Detailed Rules & Templates:** `rules/playwright/web-ui.md`
- 🔌 **API Detailed Rules & Templates:** `rules/playwright/api.md`
- 🏷️ **data-testid Naming Standard:** `rules/data-testid-mapping.md`

---

## 4. Test Structure Patterns (by Design Technique)

> These patterns define HOW to structure test code when implementing scenarios designed with specific techniques.
> EP and BVA need no special pattern — use standard AAA with inline values.

### 1. Base-Choice (BC) Pattern

**When:** Scenario set has 1 base E2E + N variations (1 param changed per variation).

**Structure:**

```typescript
test.describe('@Critical @CreateOrder Base-Choice Coverage', () => {
  const baseData = { amount: 100, paymentMethod: 'cash', deliveryType: 'standard' };

  test('create order with all default values [Base]', async ({ api }) => {
    const res = await api.createOrder(baseData);
    expect(res.status).toBe(201);
  });

  const variations = [
    { name: 'credit card payment', override: { paymentMethod: 'credit' } },
    { name: 'express delivery', override: { deliveryType: 'express' } },
    { name: 'zero amount (boundary)', override: { amount: 0 }, expectFail: true },
  ];

  for (const v of variations) {
    test(`create order with ${v.name} [Variation]`, async ({ api }) => {
      const data = { ...baseData, ...v.override };
      const res = await api.createOrder(data);
      if (v.expectFail) {
        expect(res.status).toBe(400);
      } else {
        expect(res.status).toBe(201);
      }
    });
  }
});
```

**Rules:**
- Base test is always first and explicitly named `[Base]`
- Variations use spread override pattern: `{ ...baseData, ...v.override }`
- Use `for...of` loop, NOT `test.describe.each` (better readability in reports)

### 2. Multiple-Choice (MC) Pattern — Data-Driven from Fixture

**When:** Pairwise/combinatorial matrix generated externally (PICT tool).

**Structure:**

```typescript
import combos from '../fixtures/order/pairwiseCombinations.json';

test.describe('@High @CreateOrder Pairwise Coverage', () => {
  for (const combo of combos) {
    test(`create order: ${combo.label} [Combo]`, async ({ api }) => {
      const res = await api.createOrder(combo.data);
      expect(res.status).toBe(combo.expectedStatus);
    });
  }
});
```

**Rules:**
- Combination matrix generated OUTSIDE test code (PICT output → committed JSON file)
- JSON fixture location: `fixtures/[system-kebab]/[feature]Combinations.json`
- Each combo object must have: `label`, `data`, `expectedStatus`
- NEVER generate combinations inside test code

### 3. State Transition (ST) Pattern

**When:** Feature has explicit states with transitions.

**Structure:**

```typescript
test.describe('@Critical @OrderLifecycle State Transitions', () => {
  test('transition: pending → confirmed [State]', async ({ api, orderHelper }) => {
    // Arrange — use API helper to reach starting state
    const order = await orderHelper.setupInState('pending');

    // Act — trigger transition
    const res = await api.confirmOrder(order.id);

    // Assert — verify new state AND side effects
    expect(res.status).toBe(200);
    expect(res.body.state).toBe('confirmed');
    expect(res.body.confirmedAt).toBeTruthy();
  });

  test('invalid transition: cancelled → confirmed [State]', async ({ api, orderHelper }) => {
    const order = await orderHelper.setupInState('cancelled');
    const res = await api.confirmOrder(order.id);
    expect(res.status).toBe(422);
    expect(res.body.error).toContain('invalid transition');
  });
});
```

**Rules:**
- NEVER navigate through UI to reach a state — use `setupInState(targetState)` API helper
- `setupInState` helper lives in `helpers/[feature]Helper.ts`
- Each test asserts BOTH: new state value + side effects (timestamps, notifications, etc.)
- Invalid transition tests assert rejection (422/400) with clear error message

### 4. Transition Tree / W-method Pattern

**When:** Complex state machine requiring systematic full-path coverage.

**Structure:**

```typescript
import paths from '../fixtures/payment/transitionTreePaths.json';

test.describe('@Critical @PaymentFSM W-method Coverage', () => {
  for (const path of paths) {
    test(`path: ${path.label} [W-method]`, async ({ api, paymentHelper }) => {
      let current = await paymentHelper.setupInState(path.steps[0].fromState);

      for (const step of path.steps) {
        const res = await paymentHelper.triggerEvent(current.id, step.event);
        expect(res.body.state).toBe(step.toState);
        current = res.body;
      }

      // Final state verification
      expect(current.state).toBe(path.finalState);
      for (const check of path.verify) {
        expect(current[check.field]).toBe(check.expected);
      }
    });
  }
});
```

**Rules:**
- Paths stored as committed JSON fixture (generated from FSM diagram)
- Fixture location: `fixtures/[system-kebab]/transitionTreePaths.json`
- Each path object: `{ label, steps: [{ fromState, event, toState }], finalState, verify: [{ field, expected }] }`
- State model diagram MUST exist in `$AODD_PLANS/<feature>/outputs/inception/planning/` BEFORE writing path fixtures
- Use generic walker loop — don't hardcode state sequences in test code

### 5. Helper Requirements for State-Based Tests

Every stateful feature requires a helper class:

```typescript
// helpers/orderHelper.ts
export class OrderHelper {
  constructor(private api: ApiClient) {}

  async setupInState(targetState: string): Promise<Order> {
    // Use API shortcuts to reach target state directly
    // e.g., pending → create; confirmed → create + confirm; shipped → create + confirm + ship
  }

  async triggerEvent(orderId: string, event: string): Promise<ApiResponse> {
    // Map event names to API calls
  }
}
```

**Rules:**
- One helper per stateful feature
- `setupInState` uses fastest API path (no UI)
- `triggerEvent` maps event name → API call (used by W-method walker)
- Helper registered as Playwright fixture for DI

### 6. Security Testing Patterns

> **Full rules in dedicated skill:** the `security` skill (`skills/security/SKILL.md`)
> Covers: unauthorized access, permission matrix, IDOR, injection, rate limit, file upload, mobile.
> Load when Pre-flight Q5 = Yes or feature has auth/permission/user input.

**Quick reference:**
- Tag: `@Security` on every security test
- Fixtures: `fixtures/security/` (permissionMatrix, injectionPayloads, expiredTokens)
- Pipeline: `continueOnError: false` — security failures BLOCK pipeline
