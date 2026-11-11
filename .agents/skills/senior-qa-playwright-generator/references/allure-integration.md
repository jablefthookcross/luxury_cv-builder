# Allure Reporting Integration Guidelines

## Purpose
Allure provides readable, executive-ready test execution reports with execution trees, attachments, and hierarchical classification (Epic -> Feature -> Story).

---

## Best Practices

### 1. Test Metadata Decorators
Include semantic decorators inside the test body:
```typescript
import { test, expect } from "../fixtures/test-fixtures";
import * as allure from "allure-js-commons";

test("Dopasowanie profilu kandydata do oferty pracy wylicza wynik ATS i 3 kubełki", async ({ apiClient, authSession }) => {
  allure.epic("VitaeCraft - Silnik Dopasowania CV");
  allure.feature("Dopasowanie Profilu (/api/tailor)");
  allure.story("Kalkulacja 3 kubełków umiejętności i wyniku ATS");
  allure.severity("critical");

  await test.step("Krok 1: Wysłanie żądania dopasowania z ofertą pracy", async () => {
    // Action
  });

  await test.step("Krok 2: Weryfikacja kubełków umiejętności", async () => {
    // Assertions
  });
});
```

### 2. Generating & Viewing Reports
```bash
# Generate HTML report from allure-results
npx allure generate allure-results --clean -o allure-report

# Open local report in browser
npx allure open allure-report
```
