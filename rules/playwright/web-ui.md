# Playwright UI Testing — Rules & Architecture

## Contents

- [1. Web UI Structure & Architecture](#1-web-ui-structure--architecture)
- [2. Page Object Model Pattern (Layout-Based Architecture)](#2-page-object-model-pattern-layout-based-architecture)
- [3. Locator Strategy & Bi-Language Labels](#3-locator-strategy--bi-language-labels)
- [4. UI Synchronization & Assertions](#4-ui-synchronization--assertions)
- [5. Advanced UI Capabilities (Expert Tier)](#5-advanced-ui-capabilities-expert-tier)
- [6. Infrastructure & Scripts Standard (`package.json`)](#6-infrastructure--scripts-standard-packagejson)
- [7. Login / Auth Rules](#7-login--auth-rules)

Web UI automation standards for Playwright using Page Object Model (POM) and Component-Based Architecture.
Global standards (environment variables, cross-layer fixtures, zero hard wait, locator priority, mandatory tags) are defined centrally in `rules/playwright/pw-coding-standards.md`.

---

## 1. Web UI Structure & Architecture

### Folder Structure
```text
tests/web-testing/
├── tests-web/[system-kebab]/[feature-kebab]/[feature].spec.ts
├── pages/[system-kebab]/[feature-kebab]/[feature]Page.ts
├── helpers/[system-kebab]/[feature-kebab]/[feature]Helper.ts
├── fixtures/[system-kebab]/[feature-kebab]/[feature]Data.ts
└── fixtures/[system-kebab]/[feature-kebab]/[feature]Labels.ts
```
- **Shared UI components:** `pages/shared-pages/` or `pages/common/`
- **Cross-layer shared fixtures:** `tests/shared-fixtures/[system-kebab]/[feature-kebab]/`

### File Suffix Standards
- `*Page.ts` — Page Object representing a screen or major view
- `*Component.ts` — Reusable UI sub-component (Header, Sidebar, Modal, DatePicker)
- `*Helper.ts` — Multi-step UI workflow orchestrator
- `*Labels.ts` — Multi-language UI text dictionary
- `*Data.ts` — Test data fixtures

### Login System (Per-Feature)
- Shared login: `pages/common/loginPage.ts`
- Feature-specific login: `pages/[system-kebab]/[feature-kebab]/login/[feature]LoginPage.ts`
- Do not create ID sub-folders inside login modules.

---

## 2. Page Object Model Pattern (Layout-Based Architecture)

**🎯 Principle:** Use **Layout-Based Architecture** for all UIs by separating Navigation and Content Pages.

**⚠️ File Structure:** New flexible structure.

#### 📜 Layout-Based Pattern (MANDATORY)

**Structuring Rules:**

1. **BasePage:** Base class for the feature.
2. **Component Classes:** Separate reused UI parts (Sidebar, Navigation, Modal).
3. **NavigationPage:** Manages Navigation + Layout (Header, Sidebar).
4. **Content Pages:** Specific content area pages.
5. **Shared Components:** Globally shared components.

```typescript
// ✅ Pattern: Component-Based Architecture (Advanced)

// 1. Component Class - For Reusable UI Parts
export class NavigationComponent {
  private readonly nav = this.page.locator('nav');
  public readonly homeLink = this.nav.getByRole('link', { name: 'Home' });
  public readonly profileLink = this.nav.getByRole('link', { name: 'Profile' });
  public readonly searchInput = this.nav.getByPlaceholder('Search...');

  constructor(private page: Page) {}

  async search(query: string) {
    await this.searchInput.fill(query);
    await this.searchInput.press('Enter');
  }
}

// 2. Page Class - Composing Components
export class DashboardPage extends BasePage {
  public readonly nav: NavigationComponent;
  
  constructor(page: Page) {
    super(page);
    this.nav = new NavigationComponent(page);
  }

  async getTitle() {
    return await this.page.title();
  }
}
```

#### 🎯 Usage in Test

```typescript
// Test file
import { test, expect } from '@playwright/test';
import { FeaturePage } from '../pages/[SYSTEM_KEBAB]/[SYSTEM_FEATURE_KEBAB]/FeaturePage';

test.describe('[ID-1234] Document Management System', () => {
  test('[TC-001] should update personal information', async ({ page }) => {
    const featurePage = new FeaturePage(page);
    
    // Login and navigate
    const personalInfo = await featurePage.loginAndNavigateToPersonalInfo({
      username: 'test@example.com',
      password: 'password123'
    });
    
    // Update personal info
    await personalInfo.updatePersonalInfo({
      firstNameEN: 'John',
      lastNameEN: 'Doe',
      phoneNumber: '0812345678'
    });
    
    await personalInfo.saveChanges();
    
    // Verify changes
    await personalInfo.verifyPersonalInfo({
      firstNameEN: 'John',
      phoneNumber: '0812345678'
    });
  });
  
  test('[TC-002] should search and download documents', async ({ page }) => {
    const featurePage = new FeaturePage(page);
    
    // Navigate and search
    const documentList = await featurePage.navigateAndSearchDocuments('Time Sheet');
    
    // Verify and download
    await documentList.verifyDocumentExists('Time Sheet January 2026');
    await documentList.downloadDocument('Time Sheet January 2026');
  });
  
  test('[TC-003] should verify empty pending approval state', async ({ page }) => {
    const featurePage = new FeaturePage(page);
    
    // Navigate to pending approval
    const pendingApproval = await featurePage.navigation.navigateToPendingApproval();
    
    // Verify empty state
    await pendingApproval.verifyEmptyState();
    await pendingApproval.verifyPendingCount(0);
  });
});
```

### 4. Shared UI Helpers (Use Templates)

**🎯 Principle:** Utilize Templates from `@automation/webUi/` instead of writing custom helpers.

**📦 Source:** `{knowledge_root}/automation/webUi/`

#### Available Templates

| Template | Class | Features |
| :--- | :--- | :--- |
| `webUiAuth.template.ts` | LoginPage | Azure AD, 2FA, Stay signed in |
| `webUiDialog.template.ts` | ToastHelper | Success/Error/Warning/Info toasts |
| `webUiFile.template.ts` | FileUploadHelper | Upload/Download, Drag & Drop |
| `webUiForm.template.ts` | DropdownHelper | Dropdown, Multi-select, Search |
| `webUiNavigation.template.ts` | BreadcrumbHelper | Breadcrumb navigation |
| `webUiTable.template.ts` | PaginationHelper | Pagination controls |

**⚠️ Notes:**

- Templates are located in `{knowledge_root}/automation/webUi/`.
- Copy to `helpers/shared/` in the project.
- See examples in Section 3 (Full Example).

---

### 5. Categorizing Page Objects by Feature (Feature-Based)

**Problem:** Putting everything into a single file leads to:

- ❌ Massive Page Object (50+ methods).
- ❌ Massive Translation (100+ keys).
- ❌ Hard navigation.
- ❌ Hard maintenance.

#### Solution: Separate Files by Feature/Flow

```text
pages/userManagement/
├── loginPage.ts                      # Login flow
├── listPage.ts                       # List/Export/Import
├── formPage.ts                       # Create/Edit/Validation
```

**Requirements:**

- ✅ Separate files by Feature (Login, List, Form).
- ✅ Use descriptive names.
- ✅ Target 5-10 methods per file.
- ❌ DO NOT combine everything into one file (`all_in_one.ts`).

### 6. Additional UI Patterns

**📦 Source:** `{knowledge_root}/automation/webUi/`

| Template | Class | Use Case |
| :--- | :--- | :--- |
| `webUiCard.template.ts` | CardListHelper | Card/Kanban layout (sort, filter, empty state) |
| `webUiDrawer.template.ts` | DrawerHelper | Drawer/Sub-panel (open, close, overlay) |
| `webUiAppLauncher.template.ts` | AppLauncherHelper | 9Dot App Launcher, navigate across apps |

**⚠️ Note:** Copy to `helpers/shared/` in the project.

### 6. Advanced Fixtures & Patterns 🏗️

**🎯 Principle:** Extend the `test` object to include helpers, database connections, and authenticated pages ready for use.

#### 6.1 Multi-Role Auth (Login Once per Role) 👥

**Problem:** Repeated login in every test for different User Roles.

**Solution:** Use `globalSetup` to login once per role, store `storageState` files, reuse in all tests.

> **⚠️ Token vs Data:** Re-login is only required when **role/permission differs**. For
> fail cases, change the action/data on the UI instead — no re-login needed.

**globalSetup pattern:** in `auth.setup.ts`, one `setup('authenticate as <role>', ...)`
call per role — fill login form, assert redirect, `page.context().storageState({ path:
'playwright/.auth/<role>.json' })`. In `playwright.config.ts`, wire each role as its own
`projects` entry with `dependencies: ['setup']` and `use: { storageState:
'playwright/.auth/<role>.json' }`. Specs under that project run already logged in — no
per-test login step.

#### 6.2 Database Fixture 🗄️

> **📚 Full pattern & DbService implementation:** See `skills/playwright-testing/references/db-writer.md` for the Service Methods pattern; `skills/ai-sdlc/references/dev-qa-handoff.md` for the cross-platform DB strategy decision.

**⚠️ Notes:**

- Auth setup requires `auth.setup.ts` to create storage state first.
- DB pattern follows `skills/playwright-testing/references/db-writer.md` — seed/verify/cleanup with `testId` isolation.
- Use only when project complexity justifies it.

---

## 3. Locator Strategy & Bi-Language Labels

### Priority Order (Stability First)
1. `getByTestId('x')` — scope container or unique element (see `rules/data-testid-mapping.md` for naming rules)
2. `getByRole('button', { name: L.key })` — semantic controls with accessible names
3. `getByLabel(L.key)` — form fields with associated `<label>`
4. `getByPlaceholder(L.key)` — inputs without visible label
5. `locator('css')` — last resort only when semantic locator is impossible

### 🌐 Labels File Pattern (multi-language)
When testing applications supporting more than one language, decouple UI text into `[feature]Labels.ts`:

```typescript
// fixtures/[system-kebab]/[feature-kebab]/[feature]Labels.ts
export const orderLabels = {
  de: {
    btnSubmit: 'Bestellung bestätigen',
    txtUsername: 'Benutzername',
    msgSuccess: 'Erfolgreich gespeichert'
  },
  en: {
    btnSubmit: 'Confirm Order',
    txtUsername: 'Username',
    msgSuccess: 'Saved successfully'
  }
};
```

**Usage in Page Object or Test:**
```typescript
import { orderLabels } from '../../fixtures/order/orderLabels';
const L = orderLabels[process.env.LANG === 'de' ? 'de' : 'en'];

await page.getByRole('button', { name: L.btnSubmit }).click();
```

### 🔀 Hybrid Locator Pattern (Recommended)
Scope by testId to isolate the container, then target semantic controls inside it:
```typescript
await page.getByTestId('order-card-1001')
  .getByRole('button', { name: L.btnSubmit })
  .click();
```

### 🛑 Anti-Patterns (Zero Tolerance)
- ❌ `page.waitForTimeout()` — strictly forbidden. Use Web-First assertions or explicit event waits.
- ❌ `.nth(0)` or `.first()` without filtering — brittle index locators. Use `filter({ hasText: '...' })`.
- ❌ `{ force: true }` — bypasses actionability checks, masking real UI bugs (obscured/disabled elements).
- ❌ `waitForLoadState('networkidle')` — unreliable with streaming/polling. Wait for specific API response instead.
- ❌ Brittle XPath (`//div[2]/span[1]`) — breaks on any DOM restructure.

### WebSocket Testing Pattern
Wait for specific WebSocket frames rather than sleeping:
```typescript
const [message] = await Promise.all([
  page.waitForEvent('websocket', ws => {
    return new Promise(resolve => {
      ws.on('framereceived', frame => {
        const payload = JSON.parse(frame.payload as string);
        if (payload.event === 'order_confirmed') resolve(true);
      });
    });
  }),
  page.getByRole('button', { name: L.btnSubmit }).click()
]);
```

---

## 4. UI Synchronization & Assertions

- **Web-First Assertions:** Always use auto-retrying assertions (`await expect(locator).toBeVisible()`, `await expect(page).toHaveURL(...)`). Never use generic assertions like `expect(await locator.isVisible()).toBe(true)`.
- **Handling Loading Overlays:** When elements are covered by spinners/backdrops:
  ```typescript
  await page.locator('.loading-spinner').waitFor({ state: 'hidden' });
  await page.getByTestId('btn_submit').click();
  ```
- **Waiting for Async Data:** When UI depends on an API response:
  ```typescript
  await Promise.all([
    page.waitForResponse(res => res.url().includes('/api/v1/orders') && res.status() === 200),
    page.getByRole('button', { name: L.btnSearch }).click()
  ]);
  ```

---

## 5. Advanced UI Capabilities (Expert Tier)

### 1. Bot Detection Bypass
```typescript
test.use({
  launchOptions: {
    args: ['--disable-blink-features=AutomationControlled']
  }
});

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
  });
});
```

### 2. Time Manipulation (UI Time Travel)
Test time-dependent UI behaviors (countdowns, session timeouts) without waiting:
```typescript
await page.clock.install();
await page.goto('/flash-sale');
await page.clock.fastForward('01:00:00');
await expect(page.getByText('Sale Ended')).toBeVisible();
```

### 3. Network Fault Injection & Mocking
Intercept and mutate responses mid-flight to test error states:
```typescript
await page.route('**/api/v1/user/balance', async route => {
  const response = await route.fetch();
  const json = await response.json();
  json.balance = -1; // Fault injection
  await route.fulfill({ response, json });
});
```

---

## 6. Infrastructure & Scripts Standard (`package.json`)

All UI scripts MUST follow: `ui:[environment]:[SYSTEM_FEATURE_KEBAB]:[mode]`

```json
{
  "scripts": {
    "ui:sit": "cross-env LANG=en ENV=sit playwright test --config=playwright.config.ts --reporter=list",
    "ui:uat": "cross-env LANG=en ENV=uat playwright test --config=playwright.config.ts --reporter=list",
    "ui:sit:user-management:cliMode": "cross-env LANG=en ENV=sit playwright test --config=playwright.config.ts --reporter=list tests-web/user-management/",
    "ui:sit:user-management:guiMode": "cross-env LANG=en ENV=sit playwright test --config=playwright.config.ts --ui tests-web/user-management/",
    "ui:uat:user-management:cliMode": "cross-env LANG=en ENV=uat playwright test --config=playwright.config.ts --reporter=list tests-web/user-management/",
    "ui:uat:user-management:guiMode": "cross-env LANG=en ENV=uat playwright test --config=playwright.config.ts --ui tests-web/user-management/"
  }
}
```

---

## 7. Login / Auth Rules

- Login flow must follow real user steps — use `getByRole`/`getByPlaceholder` with accessible names.
- Never use `page.route()` to intercept OAuth, `waitUntil: 'networkidle'` for login, or `waitForTimeout()` instead of element waits.
- Use `storageState` only if the app supports cookie-based sessions; otherwise login per test via helper.
- If pipeline fails on login → compare with working project's config (pool, browser, shell) before changing login code.
- Pipeline environment: Windows agent + real Chrome (`BROWSER_CHANNEL: chrome`) + `powershell` steps.
