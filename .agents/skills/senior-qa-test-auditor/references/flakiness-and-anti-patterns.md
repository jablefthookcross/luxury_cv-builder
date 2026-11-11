# Flakiness & Anti-Patterns Guide

## 1. Top 5 Causes of Playwright Flakiness

1. **Sleep / Arbitrary Pauses**:
   - *Bad*: `await page.waitForTimeout(3000);`
   - *Good*: `await expect(page.locator('#successModal')).toBeVisible();`

2. **Non-Retrying Boolean Checks**:
   - *Bad*: `expect(await page.locator('.item').isVisible()).toBe(true);`
   - *Good*: `await expect(page.locator('.item')).toBeVisible();`

3. **Unhandled Native Dialogs**:
   - Browser `alert()`, `confirm()`, or `prompt()` freeze the page execution unless an event listener accepts/dismisses them before triggering.
   - *Fix*: Register `page.on('dialog', d => d.accept())` in base Page Object constructor.

4. **Shared Mutable Test State**:
   - Multiple tests reading and writing the same user record cause race conditions when run with `workers: 2` or higher.
   - *Fix*: Generate a dedicated test user per test using timestamp + random integer.

5. **Leaked Test Data**:
   - Tests failing to delete created resources cause foreign key errors and unique constraint collisions in subsequent test runs.
   - *Fix*: Dedicated cleanup fixtures using administrative endpoints (`POST /admin/cleanup`).
