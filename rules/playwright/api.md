# Playwright API Testing — Rules & Architecture

## Contents

- [1. API Testing Structure & Service Layer Architecture](#1-api-testing-structure--service-layer-architecture)
- [3. Assertions & Concurrency](#3-assertions--concurrency)
- [PART 6: Advanced Contract Testing (Gems)](#part-6-advanced-contract-testing-gems)
- [4. API Schema Definition (AJV)](#4-api-schema-definition-ajv)
- [5. Infrastructure & Scripts Standard (`package.json`)](#5-infrastructure--scripts-standard-packagejson)
- [6. Auth / Token Rules](#6-auth--token-rules)

API test automation standards for Playwright using Service Layer Architecture, AJV Schema validation, and mock isolation.
Global standards (environment variables, cross-layer fixtures, zero hard wait, locator priority, mandatory tags) are defined centrally in `rules/playwright/pw-coding-standards.md`.

---

## 1. API Testing Structure & Service Layer Architecture

### Folder Structure
```text
tests/api-testing/
├── tests-api/[system-kebab]/[feature-kebab]/[feature].spec.ts
├── helpers/[system-kebab]/[feature-kebab]/[feature]Helper.ts
├── schemas/[system-kebab]/[feature-kebab]/[feature]Schema.ts
└── fixtures/[system-kebab]/[feature-kebab]/[feature]Data.ts
```

### 1. Service Layer Pattern (Atomic Services)

```typescript
// ✅ CORRECT: Service Layer for API
export class UserService {
  constructor(private readonly request: APIRequestContext) {}
  
  async createUser(token: string, userData: User): Promise<APIResponse> {
    return await this.request.post('/api/users', {
      headers: { 'Authorization': `Bearer ${token}` },
      data: userData
    });
  }
}
```

### 2. Advanced API Mocking & Interception

**Goal:** Isolate tests and simulate edge cases/errors effectively.

#### 2.1 Conditional Mocking (Fallback)

```typescript
await page.route('**/api/v1/data', async route => {
  const response = await route.fetch();
  if (response.status() === 500) {
    // Fallback to mock data if SIT/UAT fails
    await route.fulfill({ json: { mock: 'data' } });
  } else {
    await route.continue();
  }
});
```

#### 2.2 GraphQL Interception (By Operation Name)

```typescript
await page.route('**/graphql', async route => {
  const payload = route.request().postDataJSON();
  if (payload.operationName === 'GetUserInfo') {
    await route.fulfill({ json: { data: { user: { name: 'Mock User' } } } });
  } else {
    await route.continue();
  }
});
```

### 3. API Service Architecture (Multi-Service Pattern)

**🎯 Principle:** Use **Multi-Service Architecture** for API by separating Services according to Business Domain.

#### 🏗️ Standard Structure

```typescript
// Individual Services
export class AuthService {
  private request: APIRequestContext;
  
  constructor(request: APIRequestContext) {
    this.request = request;
  }
  
  // 🔐 AUTH ENDPOINTS
  private readonly loginEndpoint = '/api/auth/login';
  private readonly refreshEndpoint = '/api/auth/refresh';
  private readonly logoutEndpoint = '/api/auth/logout';
  
  // 🔐 AUTH ACTIONS
  async login(credentials: LoginData): Promise<APIResponse> {
    return await this.request.post(this.loginEndpoint, { data: credentials });
  }
  
  async refreshToken(token: string): Promise<APIResponse> {
    return await this.request.post(this.refreshEndpoint, { data: { token } });
  }
  
  async logout(token: string): Promise<APIResponse> {
    return await this.request.post(this.logoutEndpoint, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
  }
}

export class UserService {
  private request: APIRequestContext;
  
  constructor(request: APIRequestContext) {
    this.request = request;
  }
  
  // 👤 USER ENDPOINTS
  private readonly usersEndpoint = '/api/users';
  private readonly profileEndpoint = '/api/accounts/profile';
  private readonly settingsEndpoint = '/api/accounts/settings';
  
  // 👤 USER ACTIONS
  async createUser(token: string, userData: UserData): Promise<APIResponse> {
    return await this.request.post(this.usersEndpoint, {
      headers: { 'Authorization': `Bearer ${token}` },
      data: userData
    });
  }
  
  async getProfile(token: string, userId: string): Promise<APIResponse> {
    return await this.request.get(`${this.profileEndpoint}/${userId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
  }
  
  async updateSettings(token: string, settings: UserSettings): Promise<APIResponse> {
    return await this.request.put(this.settingsEndpoint, {
      headers: { 'Authorization': `Bearer ${token}` },
      data: settings
    });
  }
}

export class OrderService {
  private request: APIRequestContext;
  
  constructor(request: APIRequestContext) {
    this.request = request;
  }
  
  // 📝 ORDER ENDPOINTS
  private readonly ordersEndpoint = '/api/orders';
  private readonly orderStatusEndpoint = '/api/orders/status';
  
  // 📝 ORDER ACTIONS
  async createOrder(token: string, orderData: OrderData): Promise<APIResponse> {
    return await this.request.post(this.ordersEndpoint, {
      headers: { 'Authorization': `Bearer ${token}` },
      data: orderData
    });
  }
  
  async getOrderStatus(token: string, orderId: string): Promise<APIResponse> {
    return await this.request.get(`${this.orderStatusEndpoint}/${orderId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
  }
}

// Main API Client
export class Helper {
  public auth: AuthService;
  public user: UserService;
  public order: OrderService;
  
  constructor(request: APIRequestContext) {
    this.auth = new AuthService(request);
    this.user = new UserService(request);
    this.order = new OrderService(request);
  }
  
  // High-level workflows
  async loginAndCreateOrder(credentials: LoginData, orderData: OrderData): Promise<void> {
    const authResponse = await this.auth.login(credentials);
    const { token } = await authResponse.json();
    await this.order.createOrder(token, orderData);
  }
  
  async getUserProfileWithOrders(credentials: LoginData, userId: string): Promise<any> {
    const authResponse = await this.auth.login(credentials);
    const { token } = await authResponse.json();
    
    const profile = await this.user.getProfile(token, userId);
    const orders = await this.order.getOrderStatus(token, userId);
    
    return {
      profile: await profile.json(),
      orders: await orders.json()
    };
  }
}
```

#### 🎯 Usage in Test

```typescript
// Test file
import { test, expect } from '@playwright/test';
import { Helper } from '../../helpers/[SYSTEM_KEBAB]/[SYSTEM_FEATURE_KEBAB]/[SYSTEM_FEATURE_CAMEL]Helper';

test.describe('API Tests', () => {
  test('should create order after successful login', async ({ request }) => {
    const helper = new Helper(request);
    
    // Use individual services
    const authResponse = await helper.auth.login(credentials);
    const userResponse = await helper.user.getProfile(token, userId);
    const orderResponse = await helper.order.createOrder(token, orderData);
    
    // Or use high-level workflow
    await helper.loginAndCreateOrder(credentials, orderData);
    
    expect(authResponse.status()).toBe(200);
    expect(orderResponse.status()).toBe(201);
  });
});
```

### 4. Advanced Fixtures & Patterns 🏗️

**🎯 Principle:** Extend the `test` object to include API helpers, database connections, and authenticated API clients ready for use.

#### 4.1 Multi-Role API Auth Fixture 👥

**Problem:** Repeated Login required in every API test for different User Roles.

**Solution:** Create a Fixture that is pre-logged in for each Role.

> **⚠️ Token vs Data:** Re-login is only required when **role/permission differs**.
> For fail cases, change the **parameters sent to the API** instead — no re-login needed.
>
> ```typescript
> // ✅ Same token, different data → different result (no re-login needed)
> helper.invoice.getInvoices(token, companyCode, customer.validCode)    // → 200 with data
> helper.invoice.getInvoices(token, companyCode, customer.invalidCode)  // → 200 empty
>
> // ✅ Different token only when role/permission differs
> helper.customer.getCustomers(mainToken, companyCode)      // → has customers
> helper.customer.getCustomers(noCustomerToken, companyCode) // → empty (different user)
> ```

**globalSetup Pattern (Login Once per Role):**

```typescript
// globalSetup.ts — login once, store all tokens
export default async function globalSetup() {
  const ctx = await request.newContext();

  // Main user token
  const mainRes = await ctx.post(process.env.LOGIN_URL!, { form: {
    ...oauthParams,
    username: process.env.TEST_USER_EMAIL!,
    password: process.env.TEST_USER_PASSWORD!,
  }});
  process.env.ACCESS_TOKEN = (await mainRes.json()).access_token;

  // Secondary user token (different role/permission)
  const user5Res = await ctx.post(process.env.LOGIN_URL!, { form: {
    ...oauthParams,
    username: process.env.TEST_USER5_EMAIL!,
    password: process.env.TEST_USER5_PASSWORD!,
  }});
  process.env.ACCESS_TOKEN_USER5 = (await user5Res.json()).access_token;

  await ctx.dispose();
}
```

**Usage in spec (read from process.env, no re-login):**

```typescript
test.beforeAll(async () => {
  token = process.env.ACCESS_TOKEN!;
  noCustomerToken = process.env.ACCESS_TOKEN_USER5!;
});
```

#### 4.2 Database Fixture (API Integration) 🗄️

> **📚 Full pattern & DbService implementation:** See `skills/playwright-testing/references/db-writer.md` for the Service Methods pattern; `skills/ai-sdlc/references/dev-qa-handoff.md` for the cross-platform DB strategy decision.

#### 4.3 API Response Cache Fixture 📦

For slow APIs/rate limits on infrequently-changing reference data: a `cachedAPI` fixture
wraps `request.get()`, checking a local `cache/<endpoint-key>.json` file before making a
real call, writing the response on first fetch. POSTs are never cached (they mutate
state) — pass through directly. Only build this when a specific test suite is genuinely
slow; most tests don't need it.

#### 4.4 API Mock Fixture (Test Isolation) 🎭

For error/edge-case scenarios, wrap § 2's `page.route()` patterns (success/error/delay
fulfill) in a `mockAPI` fixture (`mockSuccess`/`mockError`/`mockDelay` methods) so specs
don't repeat the same `route.fulfill()` boilerplate. Same mechanism as § 2.1, just
reusable across a suite.

**⚠️ Notes:**

- API Auth Fixture must have valid credentials for each environment.
- Database Fixture requires Prisma installation and connection configuration.
- Cache Fixture is ideal for infrequently changing reference data.
- Mock Fixture is suitable for error scenarios and edge cases.
- Use only when project complexity justifies it.

---


---

## 3. Assertions & Concurrency

### 1. API Response Assertions

#### 1.1 Assertions Best Practices

```typescript
// ✅ CORRECT - Specific API assertions
expect(response.status()).toBe(201);
expect(response.headers()['content-type']).toContain('application/json');

// ❌ WRONG - Generic assertions
expect(response.ok()).toBeTruthy();
```

#### 1.2 API Response Validation

```typescript
// ✅ Assert - Status Code
expect(response.status()).toBe(201);

// ✅ Assert - Response Headers
expect(response.headers()['content-type']).toContain('application/json');
expect(response.headers()['x-api-version']).toBe('v1');

// ✅ Assert - Response Body
const responseBody = await response.json();
expect(responseBody.id).toBeDefined();
expect(responseBody.name).toBe(userData.name);
expect(responseBody.email).toBe(userData.email);
expect(responseBody.createdAt).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/);

// ✅ Assert - Array Response
expect(Array.isArray(responseBody.items)).toBe(true);
expect(responseBody.items.length).toBeGreaterThan(0);
expect(responseBody.total).toBeGreaterThanOrEqual(responseBody.items.length);
```

### 2. 🚨 Common API Issues (Root Cause)

#### Issue 1: Network Timeout

**Problem:** API is slow or timeouts.

**Root Cause:**

- API Server is slow or unresponsive.
- High network latency.
- Slow database query.

**✅ Solution:**

```typescript
// Increase timeout for slow APIs
const response = await request.post('/api/heavy-operation', {
  data: largeData,
  timeout: 60000 // 60 seconds
});
```

#### Issue 2: Eventual Consistency (Data not ready)

**Problem:** API saves data asynchronously, so GET immediate after POST returns outdated data.

**✅ Solution (Advanced Gem: Predicate Waiting):**
```typescript
// 💎 Gem: Wait until JSON data contains expected value
await expect.poll(async () => {
  const res = await request.get('/api/status/123');
  const body = await res.json();
  return body.status;
}, {
  message: 'Wait for status to be COMPLETED',
  timeout: 10000,
}).toBe('COMPLETED');
```

#### Issue 3: Concurrent Request Testing (Race Conditions)

**Problem:** verify the system handles concurrent requests correctly, e.g. two users booking the same seat at the same time.

**✅ Solution: Promise.all() Pattern**

```typescript
test('[TC-007] Race condition — two requests book the same seat', async ({ request }) => {
  // Arrange
  await dbService.seed({ seatId: 'SEAT-001', status: 'Available' }, 'TC-007')

  // Act — fire 2 requests simultaneously
  const [res1, res2] = await Promise.all([
    apiService.book(request, { seatId: 'SEAT-001' }),
    apiService.book(request, { seatId: 'SEAT-001' }),
  ])

  // Assert — exactly 1 success, 1 conflict
  const statuses = [res1.status(), res2.status()].sort()
  expect(statuses).toEqual([200, 409])

  // Cleanup
  await dbService.cleanup('TC-007')
})
```

**Concurrent testing rules:**
- Always use `Promise.all()`, not sequential calls
- Sort statuses before asserting, because you cannot know which request wins
- Use the correct DB isolation level (SERIALIZABLE), otherwise the test passes but production breaks
- Seed data in `beforeEach`, not `beforeAll`, so each test starts from a clean state

**N concurrent requests:**
```typescript
// Test N requests simultaneously
const N = 5
const requests = Array.from({ length: N }, () =>
  apiService.deduct(request, { productId: 'P001', quantity: 1 })
)
const responses = await Promise.all(requests)
const statuses = responses.map(r => r.status()).sort()

// Only 1 should succeed (stock = 1)
expect(statuses.filter(s => s === 200)).toHaveLength(1)
expect(statuses.filter(s => s === 409)).toHaveLength(N - 1)
```

---

## PART 6: Advanced Contract Testing (Gems)

### 1. AJV Schema Validation (Full Body Contract)

Instead of checking field by field, validate the entire block using JSON Schema for 100% accuracy following COE standards.

```typescript
import { validateSchema } from '../../helpers/schema.validator';
import { userSchema } from '../../schemas/user/userSchema';

test('should match contract schema', async ({ request }) => {
  const response = await request.get('/api/user/me');
  const body = await response.json();
  
  // 💎 Gem: Validate entire body in one go using AJV
  validateSchema(body, userSchema);
});
```

### 2. Time Manipulation (Clock Mocking)

Used for testing time-dependent APIs like OTP expiry or Token expiration.

```typescript
test('should handle expired OTP', async ({ page, request }) => {
  // 💎 Gem: Freeze time
  await page.clock.install({ time: new Date(Date.UTC(2024, 0, 1, 10)) });
  
  await request.post('/api/otp/send');
  
  // 💎 Gem: Fast forward 15 minutes
  await page.clock.fastForward('15:00');
  
  const res = await request.post('/api/otp/verify', { data: { code: '1234' } });
  expect(res.status()).toBe(400); // Should be expired
});
```

### 3. API Performance Assertions (Efficiency Gem)

Not just passing, but "fast enough" to prevent Performance Regression in CI/CD.

```typescript
test('should meet Response Time criteria @Performance', async ({ request }) => {
  const startTime = Date.now();
  const response = await request.get('/api/resource');
  const duration = Date.now() - startTime;
  
  expect(response.status()).toBe(200);
  // 💎 Gem: Enforce speed (Response must be < 500ms)
  expect(duration, `API is too slow! Took ${duration}ms`).toBeLessThan(500);
});
```

```typescript
// Or use retry mechanism
let response;
for (let i = 0; i < 3; i++) {
  try {
    response = await request.get('/api/data');
    if (response.ok()) break;
  } catch (error) {
    if (i === 2) throw error; // Last attempt
    await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1))); // Exponential backoff
  }
}
```


---

## 4. API Schema Definition (AJV)

### 🎯 Purpose

Define API Request/Response structure using JSON Schema.

---

### 1️⃣ Basic Schema Structure

**📁 File: schemas/[SYSTEM_KEBAB]/[SYSTEM_FEATURE_KEBAB]/[SYSTEM_FEATURE_CAMEL]Schema.ts**

```typescript
// Request Schema
export const createDocumentRequestSchema = {
  type: 'object',
  required: ['title', 'type', 'status'],
  properties: {
    title: { type: 'string' },
    type: { type: 'string' },
    status: { type: 'string' },
    description: { type: 'string' },
    attachments: { type: 'array', items: { type: 'string' } }
  }
};

// Response Schema
export const createDocumentResponseSchema = {
  type: 'object',
  required: ['documentId', 'title', 'type', 'status', 'createdAt'],
  properties: {
    documentId: { type: 'string' },
    title: { type: 'string' },
    type: { type: 'string' },
    status: { type: 'string' },
    createdAt: { type: 'string' },
    createdBy: { type: 'string' }
  }
};

// List Response Schema
export const getDocumentsResponseSchema = {
  type: 'object',
  required: ['items', 'total', 'page', 'limit'],
  properties: {
    items: { type: 'array', items: createDocumentResponseSchema },
    total: { type: 'number' },
    page: { type: 'number' },
    limit: { type: 'number' }
  }
};

// Error Response Schema
export const errorResponseSchema = {
  type: 'object',
  required: ['error', 'message', 'statusCode'],
  properties: {
    error: { type: 'string' },
    message: { type: 'string' },
    statusCode: { type: 'number' },
    details: { type: 'array', items: { type: 'string' } }
  }
};
```

---

### 2️⃣ Optional: Advanced Validation

**If additional Validation Rules are needed:**

```typescript
// Advanced Schema (Optional)
export const createDocumentRequestSchema = {
  type: 'object',
  required: ['title', 'type', 'status'],
  properties: {
    title: { 
      type: 'string', 
      minLength: 1,        // Optional
      maxLength: 255       // Optional
    },
    type: { 
      type: 'string',
      enum: ['timesheet', 'approval', 'report']  // Optional
    },
    status: { 
      type: 'string',
      enum: ['draft', 'pending', 'approved']     // Optional
    },
    createdAt: { 
      type: 'string',
      format: 'date-time'  // Optional: email, date-time, uri, uuid
    }
  }
};
```

---

### 3️⃣ Common Patterns

```typescript
// Pagination
export const paginationSchema = {
  type: 'object',
  required: ['items', 'total', 'page', 'limit'],
  properties: {
    items: { type: 'array' },
    total: { type: 'number' },
    page: { type: 'number' },
    limit: { type: 'number' }
  }
};

// Success Response
export const successResponseSchema = {
  type: 'object',
  required: ['success', 'message'],
  properties: {
    success: { type: 'boolean' },
    message: { type: 'string' },
    data: { type: 'object' }
  }
};
```

---


---

## 5. Infrastructure & Scripts Standard (`package.json`)

### 📦 Package.json Scripts Generation

### 🎯 Script Format Standard

**MANDATORY: All generated scripts MUST follow this exact format:**

```text
api:[environment]:[SYSTEM_FEATURE_KEBAB]:[mode]
```

#### 📝 Format Components

1. **environment**: `sit` | `uat`
2. **feature**: `[SYSTEM_FEATURE_KEBAB]` (kebab-case, matches folder name e.g., `user-management`)
3. **mode**: `cliMode` | `guiMode`

### ✅ Correct Script Examples

```json
{
  "scripts": {
    "api:sit": "cross-env LANG=en ENV=sit playwright test --config=playwright.config.api.ts --reporter=list",
    "api:uat": "cross-env LANG=en ENV=uat playwright test --config=playwright.config.api.ts --reporter=list",
    "api:sit:user-management:cliMode": "cross-env LANG=en ENV=sit playwright test --config=playwright.config.api.ts --reporter=list tests-api/user-management/",
    "api:sit:user-management:guiMode": "cross-env LANG=en ENV=sit playwright test --config=playwright.config.api.ts --ui tests-api/user-management/",
    "api:uat:user-management:cliMode": "cross-env LANG=en ENV=uat playwright test --config=playwright.config.api.ts --reporter=list tests-api/user-management/",
    "api:uat:user-management:guiMode": "cross-env LANG=en ENV=uat playwright test --config=playwright.config.api.ts --ui tests-api/user-management/"
  }
}
```

### Generation Rules (MANDATORY)

1. Always generate BOTH environments (sit + uat) and BOTH modes (cliMode + guiMode) per feature.
2. `--config=playwright.config.api.ts` always; test dir `tests-api/[SYSTEM_KEBAB]/[SYSTEM_FEATURE_KEBAB]/`.
3. CLI mode → `--reporter=list`; GUI mode → `--ui`.
4. Prefix every script with `cross-env LANG=en ENV=<sit|uat>` (needs `npm install -D cross-env` for cross-platform compatibility).

---


---

## 6. Auth / Token Rules

- Token acquisition must be straightforward — call login endpoint, extract token, store in `process.env`
- Never over-engineer token management (no complex refresh logic, no interceptors, no middleware)
- If pipeline fails on auth → compare with working project's config before changing auth code
- Pipeline: credentials from `.env` only (no pipeline variables)
