import { Locator, Page, expect } from "@playwright/test";
import { BasePage } from "./BasePage";

export class AuthModalPage extends BasePage {
  readonly authModal: Locator;
  readonly modalTitle: Locator;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly fullNameInput: Locator;
  readonly fullNameGroup: Locator;
  readonly submitBtn: Locator;
  readonly toggleBtn: Locator;
  readonly alertBox: Locator;
  readonly closeBtn: Locator;

  constructor(page: Page) {
    super(page);
    this.authModal = page.locator("#authModal");
    this.modalTitle = page.locator("#authModalTitle");
    this.emailInput = page.locator("#authEmail");
    this.passwordInput = page.locator("#authPassword");
    this.fullNameInput = page.locator("#authFullName");
    this.fullNameGroup = page.locator("#authFullNameGroup");
    this.submitBtn = page.locator("#authSubmitBtn");
    this.toggleBtn = page.locator("#authToggleBtn");
    this.alertBox = page.locator("#authAlert");
    this.closeBtn = page.locator("#authModal button:has-text('✕')");
  }

  async expectModalOpen(): Promise<void> {
    await expect(this.authModal).toBeVisible();
  }

  async switchToRegister(): Promise<void> {
    const text = await this.toggleBtn.textContent();
    if (text?.includes("Rejestracja")) {
      await this.toggleBtn.click();
    }
    await expect(this.fullNameGroup).toBeVisible();
  }

  async switchToLogin(): Promise<void> {
    const text = await this.toggleBtn.textContent();
    if (text?.includes("Logowanie")) {
      await this.toggleBtn.click();
    }
    await expect(this.fullNameGroup).toBeHidden();
  }

  async fillForm(email: string, password: string, fullName?: string): Promise<void> {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    if (fullName) {
      await this.fullNameInput.fill(fullName);
    }
  }

  async submit(): Promise<void> {
    await this.submitBtn.click();
  }

  async registerUser(email: string, password: string, fullName: string): Promise<void> {
    await this.switchToRegister();
    await this.fillForm(email, password, fullName);
    await this.submit();
  }

  async loginUser(email: string, password: string): Promise<void> {
    await this.switchToLogin();
    await this.fillForm(email, password);
    await this.submit();
  }

  async expectSuccessToast(expectedText?: string): Promise<void> {
    await expect(this.alertBox).toBeVisible();
    if (expectedText) {
      await expect(this.alertBox).toContainText(expectedText);
    }
  }

  async expectErrorAlert(expectedError: string): Promise<void> {
    await expect(this.alertBox).toBeVisible();
    await expect(this.alertBox).toContainText(expectedError);
  }
}
