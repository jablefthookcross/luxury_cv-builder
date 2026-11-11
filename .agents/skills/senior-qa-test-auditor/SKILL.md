---
name: senior-qa-test-auditor
description: >-
  Senior QA Test Auditor and Code Reviewer skill for Playwright TypeScript suites.
  Use this skill to audit, review, and refactor automated tests, detecting anti-patterns, flakiness,
  brittle locators, unhandled alerts, missing cleanups, or weak assertions.
---

# Senior QA Test Auditor & Code Reviewer

This skill audits Playwright test suites for reliability, performance, determinism, and maintainability.

---

## Audit Checklist & Review Criteria

### 1. Flakiness Detection
- ❌ **Hardcoded timeouts**: Detect any `page.waitForTimeout()` or `setTimeout`.
  - *Fix*: Replace with web-first assertions or explicit locator waits (`locator.waitFor({ state: 'visible' })`).
- ❌ **Race conditions**: Submitting forms before inputs blur or before network requests settle.
  - *Fix*: Wait for network idle, response promise (`page.waitForResponse()`), or expected UI change.

### 2. Locator Stability
- ❌ **Brittle CSS / XPath**: Avoid selectors like `div.container > div:nth-child(3) > button`.
  - *Fix*: Migrate to `getByRole()`, `getByLabel()`, `getByPlaceholder()`, or `getByTestId()`.
- ❌ **Strict Mode Violations**: Locators resolving to multiple DOM nodes without `.first()` or specific scoping.
  - *Fix*: Scope locators within parent containers (e.g. `this.container.getByRole(...)`).

### 3. Assertion Quality
- ❌ **Non-retrying assertions**: Using `expect(await locator.isVisible()).toBe(true)`.
  - *Fix*: Use Playwright's web-first retrying assertions: `await expect(locator).toBeVisible()`.
- ❌ **Tautological assertions**: `expect(res.status).toBeDefined()`.
  - *Fix*: Exact status and schema validation: `expect(res.status()).toBe(200)`.

### 4. Test Independence & Teardown
- ❌ **Shared credentials across tests**: Multiple tests mutating the same user profile simultaneously.
  - *Fix*: Unique email generation per test via `buildQaUser()`.
- ❌ **Missing Cleanup**: Leftover database entries polluting successive test runs.
  - *Fix*: Always register teardown logic in fixture or `test.afterEach()`.

---

## References

- [Flakiness & Anti-Patterns Guide](./references/flakiness-and-anti-patterns.md)
