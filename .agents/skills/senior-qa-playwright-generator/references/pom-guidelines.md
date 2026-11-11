# Page Object Model (POM) Guidelines

## Purpose
The Page Object Model abstracts UI elements and interactions away from test logic, making test suites resilient to DOM changes and highly maintainable.

---

## Architecture Standards

### 1. BasePage Inheritance
Every Page Object must extend `BasePage`:
```typescript
import { Page, Locator } from "@playwright/test";

export abstract class BasePage {
  constructor(protected readonly page: Page) {
    // Automatically accept native browser dialogs (alert, confirm)
    this.page.on("dialog", async (dialog) => {
      await dialog.accept();
    });
  }

  async goto(path = "/"): Promise<void> {
    await this.page.goto(path);
  }

  async setLocalStorageToken(token: string): Promise<void> {
    await this.page.evaluate((jwt) => localStorage.setItem("access_token", jwt), token);
  }
}
```

### 2. Page Class Structure
```typescript
import { Page, Locator, expect } from "@playwright/test";
import { BasePage } from "./BasePage";

export class ProfilePage extends BasePage {
  // Locators defined as read-only properties
  readonly fullNameInput: Locator;
  readonly roleInput: Locator;
  readonly saveButton: Locator;

  constructor(page: Page) {
    super(page);
    this.fullNameInput = page.locator("#fullName");
    this.roleInput = page.locator("#targetRole");
    this.saveButton = page.getByRole("button", { name: /Zapisz Profil/i });
  }

  // High-level user interaction methods
  async fillBasicInfo(name: string, role: string): Promise<void> {
    await this.fullNameInput.fill(name);
    await this.roleInput.fill(role);
  }

  async saveProfile(): Promise<void> {
    await this.saveButton.click();
  }
}
```

### 3. Locator Selection Hierarchy
1. `getByRole(role, { name })` - Accessibility tree matches real user perception.
2. `getByLabel(text)` - Form input associations.
3. `getByPlaceholder(text)` - Clear visual input hints.
4. `getByTestId(id)` - Stable hooks for non-semantic elements.
5. `locator('#id')` - Unique DOM ID.
6. ❌ Avoid: Deep CSS paths (`div.wrapper > div:nth-child(2) > span`), XPath expressions, text matching that changes with i18n without regex.
