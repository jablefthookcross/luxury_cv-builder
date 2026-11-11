import { Locator, Page, expect } from "@playwright/test";
import { BasePage } from "./BasePage";

export class LandingPage extends BasePage {
  readonly welcomeScreen: Locator;
  readonly welcomeTitle: Locator;
  readonly welcomeSubtitle: Locator;
  readonly registerDirectBtn: Locator;
  readonly loginDirectBtn: Locator;
  readonly swaggerApiLink: Locator;
  readonly btnAuthHeader: Locator;

  constructor(page: Page) {
    super(page);
    this.welcomeScreen = page.locator("#welcomeScreen");
    this.welcomeTitle = page.locator(".welcome-title");
    this.welcomeSubtitle = page.locator(".welcome-subtitle");
    this.registerDirectBtn = page.getByRole("button", { name: /Zarejestruj się i Zacznij Darmowo/i });
    this.loginDirectBtn = page.getByRole("button", { name: /Mam już konto \(Zaloguj się\)/i });
    this.swaggerApiLink = page.getByRole("link", { name: /Swagger API/i });
    this.btnAuthHeader = page.locator("#btnAuthHeader");
  }

  async open(): Promise<void> {
    await this.goto("/");
    await this.welcomeScreen.waitFor({ state: "visible" });
  }

  async expectLandingVisible(): Promise<void> {
    await expect(this.welcomeScreen).toBeVisible();
    await expect(this.welcomeTitle).toContainText("Single-Page CV");
  }

  async clickRegister(): Promise<void> {
    await this.registerDirectBtn.click();
  }

  async clickLogin(): Promise<void> {
    await this.loginDirectBtn.click();
  }
}
