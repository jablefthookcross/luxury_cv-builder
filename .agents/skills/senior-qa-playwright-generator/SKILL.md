---
name: senior-qa-playwright-generator
description: >-
  Senior QA Automation Engineer skill to generate rock-solid, production-grade Playwright tests in TypeScript.
  Use this skill whenever designing, generating, or refactoring Playwright E2E UI and API tests, implementing
  Page Object Models (POM), authoring API service clients, creating test fixtures, or integrating Allure reporting.
---

# Senior QA Playwright Test Generator

This skill guides the creation of enterprise-grade automated tests in **Playwright Test** with **TypeScript**, strictly adhering to Senior SDET / QA Architect standards.

---

## 1. Core Architectural Pillars

When generating or refactoring test suites, you must enforce the following four pillars:

```text
┌────────────────────────────────────────────────────────┐
│                      Playwright Test                   │
│   (Business Polish Names, Allure Epics & test.step)    │
└───────────────────────────┬────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        ▼                                       ▼
┌───────────────────────┐             ┌───────────────────────┐
│  Page Object Model    │             │  API Service Clients  │
│  (UI Locators & Flow) │             │  (HTTP / Auth / CRUD) │
└───────────┬───────────┘             └───────────┬───────────┘
            │                                     │
            └───────────────────┬─────────────────┘
                                ▼
┌────────────────────────────────────────────────────────┐
│             Fixtures & Isolated Data Builders          │
│         (Atomic User Creation & Admin Teardown)        │
└────────────────────────────────────────────────────────┘
```

---

## 2. Step-by-Step Test Creation Workflow

### Step 1: Define Test Data & Builders
1. Never hardcode inline test objects across specs.
2. Use or extend factory functions in `tests/data/builders.ts`:
   - `buildQaUser()`: Generates unique email (`qa_test_${timestamp}_${rand}@vitaecraft.local`), password, and credentials.
   - `buildCandidateProfile()`: Generates valid schema-compliant master CV data.
3. For Anti-AI assertions, reference rules in `tests/data/anti-ai-rules.ts`.

### Step 2: Implement or Extend API Clients (`tests/services/`)
1. Backend calls should never use ad-hoc `request.post('/url')` duplicated across tests.
2. Encapsulate endpoints in dedicated service classes:
   - `AuthClient`: Registration, login, token extraction, status checks.
   - `ProfileClient`: Get, save, update, delete master profile.
   - `TailorClient`: Analyze job, tailor CV, refine prompt, export PDF.
   - `AdminClient`: Admin cleanup with `x-admin-secret`.
3. Methods must return strongly typed responses and handle status code validations.

### Step 3: Implement or Extend Page Objects (`tests/pages/`)
1. Every page inherits from `BasePage.ts`.
2. Locators are private or read-only public properties initialized in the constructor.
3. Prefer semantic locators:
   - `this.page.getByRole('button', { name: '...' })`
   - `this.page.getByLabel('...')`
   - `this.page.getByPlaceholder('...')`
   - `this.page.locator('#specificId')`
4. Encapsulate complete user actions (e.g. `fillLoginForm(email, pass)`, `submit()`, `verifySuccess()`).
5. Never put assertions inside Page Object action methods; return state or locators for test assertions, OR provide semantic assertion methods like `expectSaveSuccess()`.

### Step 4: Utilize Playwright Custom Fixtures (`tests/fixtures/`)
1. Extend `baseTest` in `tests/fixtures/test-fixtures.ts`.
2. Expose fixtures:
   - `apiClient`: Pre-configured `ApiClient` instance.
   - `testUser`: Freshly generated unique user object.
   - `authSession`: Registered and logged-in user with active JWT session.
   - `cleanup`: Automated teardown hook executing `adminClient.cleanupUser(...)` in `test.afterEach`.

### Step 5: Author the Spec with Allure Metadata & Polish Descriptions
1. Use descriptive Polish titles that business stakeholders can read in reports.
2. Include Allure annotations:
   ```typescript
   test("Użytkownik rejestruje nowe konto i konfiguruje profil bazowy", async ({ page, testUser }) => {
     allure.epic("VitaeCraft - Zarządzanie Tożsamością");
     allure.feature("Rejestracja i Profil");
     allure.story("Tworzenie profilu bazowego kandydata");
     allure.severity("critical");

     await test.step("Krok 1: Otwarcie modalu i rejestracja", async () => { ... });
     await test.step("Krok 2: Wypełnienie formularza profilu", async () => { ... });
     await test.step("Krok 3: Weryfikacja zapisu i trwałości danych", async () => { ... });
   });
   ```

---

## 3. Anti-Flakiness Rules Checklist

- [ ] **No Hardcoded Sleep**: Absolutely no `page.waitForTimeout()` or `sleep()`.
- [ ] **Web-First Assertions**: Use `await expect(locator).toBeVisible()`, not `expect(await locator.isVisible()).toBe(true)`.
- [ ] **Handled Dialogs**: Use `BasePage` auto-dialog listener or explicit `page.once('dialog')` before triggering browser alerts.
- [ ] **Atomic Cleanup**: Ensure every created test account is cleaned up via `POST /admin/cleanup`.
- [ ] **Strict Typing**: No `any` types; all request payloads and responses must be typed.
- [ ] **CI Ready**: Ensure headless compatibility and deterministic data isolation.

---

## 4. References & Deep Dive Guides

- [Page Object Model Guidelines](./references/pom-guidelines.md)
- [API Service Client Guidelines](./references/api-service-guidelines.md)
- [Fixtures and Data Isolation](./references/fixtures-and-data-isolation.md)
- [Allure Reporting Integration](./references/allure-integration.md)
