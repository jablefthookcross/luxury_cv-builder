# Fixtures and Data Isolation Guidelines

## Purpose
Tests must be 100% independent. Each test creates its own test user, sets up state explicitly, and cleans up after itself. Never rely on shared accounts or leftover database records.

---

## Pattern: Custom Playwright Fixtures

Extend `baseTest` in `tests/fixtures/test-fixtures.ts`:

```typescript
import { test as baseTest, expect } from "@playwright/test";
import { ApiClient } from "../services/api.client";
import { buildQaUser, QaUser } from "../data/builders";

interface TestFixtures {
  apiClient: ApiClient;
  testUser: QaUser;
  authSession: { user: QaUser; token: string };
}

export const test = baseTest.extend<TestFixtures>({
  apiClient: async ({ request }, use) => {
    await use(new ApiClient(request));
  },

  testUser: async ({ apiClient }, use) => {
    const user = buildQaUser();
    // Register user
    const regRes = await apiClient.auth.register(user.email, user.password);
    expect(regRes.status()).toBe(201);

    // Hand user to test
    await use(user);

    // Teardown: Clean up user from database
    await apiClient.admin.cleanupUser(user.email);
  },

  authSession: async ({ apiClient, testUser }, use) => {
    const { response, token } = await apiClient.auth.login(testUser.email, testUser.password);
    expect(response.status()).toBe(200);
    expect(token).toBeTruthy();

    await use({ user: testUser, token });
  },
});

export { expect };
```

---

## Data Builders Pattern

Use factories with random salts:
```typescript
export function buildQaUser(overrides?: Partial<QaUser>): QaUser {
  const timestamp = Date.now();
  const rand = Math.floor(Math.random() * 100000);
  return {
    email: `qa_user_${timestamp}_${rand}@vitaecraft.local`,
    password: `P@ssword123!_${rand}`,
    fullName: `Tester QA ${rand}`,
    targetRole: "Senior QA Automation Engineer",
    ...overrides,
  };
}
```
