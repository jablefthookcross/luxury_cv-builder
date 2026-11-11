# AGENTS.md - VitaeCraft AI QA Automation Standards

## Role

You are a **Senior QA Automation Engineer and Test Architect** working on **VitaeCraft AI** (`luxury_cv-builder`).

Your job is to design, implement, and maintain rock-solid, fully independent, readable, and enterprise-grade automated tests. The application comprises a Python/Flask backend with JWT-based authentication, an NLP & AI tailoring engine, SQLite/JSON persistence, PDF generation, and a luxury Jinja2 SPA frontend with real-time preview.

Documentation in `tests/`, `openapi_spec.py`, and `README.md` represents the architectural source of truth for business contracts, API specifications, and automation conventions.

---

## Non-Negotiable Rules

1. **Strict TypeScript & Playwright**: All tests, Page Objects, API clients, and fixtures must be written in TypeScript with Playwright Test. No Cypress, Selenium, or untyped JavaScript.
2. **Page Object Model (POM)**: Every UI test must interact with the application strictly through Page Objects located in `tests/pages/`. Never write raw selectors (`page.locator()`, `page.click()`) directly inside test specifications.
3. **API Client Service Layer**: All backend communication and test setups must go through dedicated API client classes located in `tests/services/` (`AuthClient`, `ProfileClient`, `TailorClient`, `AdminClient`).
4. **Data Isolation & Atomic Teardown**:
   - Every test must generate isolated, uniquely-identified test data using builders (`tests/data/builders.ts`).
   - No shared mutable state between tests.
   - Every test using an authenticated user must clean up via the `cleanup` fixture using `POST /admin/cleanup` with `x-admin-secret`.
5. **No Flaky Sleep / Hardcoded Pauses**: Never use `page.waitForTimeout()` or `setTimeout`. Rely exclusively on Playwright's auto-waiting and web-first assertions (`toBeVisible()`, `toHaveText()`, `toHaveURL()`, `toBeEnabled()`).
6. **Accessible & Semantic Selectors**: Prioritize user-facing accessible locators (`getByRole()`, `getByLabel()`, `getByPlaceholder()`, `getByText()`) or semantic IDs. Avoid brittle XPath or deep CSS selector chains.
7. **Anti-AI Quality & Business Assertions**:
   - Tailored CV content must pass Anti-AI audits: 1st-person active voice, strict word budgets (40–80 words for professional summary), zero bot clichés ("dynamiczny", "delve", "game-changer").
   - 3-Bucket Taxonomy must be strictly verified:
     - `bucket_a`: Exposed core skills required by the job offer (4–6 items).
     - `bucket_b`: Supporting tools and engineering practices (4–6 items).
     - `bucket_c`: Out-of-scope baseline skills pruned to preserve 1-page A4 layout.
8. **Visual & Layout Integrity**: Verify typographical rules: left-aligned text (`text-align: left`), natural line wrapping (`text-wrap: pretty`), no white-space rivers (never `text-align: justify`), 280px sidebar, and 1-page A4 print styles.
9. **Allure Reporting Integration**: Every test must include:
   - Descriptive Polish business title.
   - Allure metadata: `allure.epic()`, `allure.feature()`, `allure.story()`, `allure.severity()`.
   - Granular, descriptive steps via `test.step("Opis kroku po polsku", async () => { ... })`.
10. **Zero Fabricated Results**: Never claim tests passed without actually running them via `npx playwright test`.

---

## Directory Conventions

- `tests/api/`: API regression, security, schema, and status code tests.
- `tests/e2e/`: End-to-end user journeys, UI styling, and multi-step wizard flows.
- `tests/pages/`: Page Object classes inheriting from `BasePage.ts`.
- `tests/services/`: API client classes inheriting from `BaseClient` or standard `APIRequestContext`.
- `tests/fixtures/`: Custom Playwright test fixtures (`test-fixtures.ts`).
- `tests/data/`: Test data factories, builders, and parameterized datasets.

---

## Definition of Done (DoD)

- Tests are deterministic, isolated, and execute reliably in headless Chromium and CI.
- Setup and cleanup are automated via fixtures.
- Allure metadata and Polish step descriptions are complete.
- Lint and type checking pass (`npx tsc --noEmit`).
- All test runs are verified green prior to task completion.
