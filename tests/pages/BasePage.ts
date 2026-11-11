import { Page, Locator } from "@playwright/test";

export abstract class BasePage {
  constructor(protected readonly page: Page) {
    this.page.on("dialog", async (dialog) => {
      try {
        await dialog.accept();
      } catch (_) {}
    });
  }

  async goto(path: string = "/"): Promise<void> {
    await this.page.goto(path);
  }

  async waitForPageReady(): Promise<void> {
    await this.page.waitForLoadState("domcontentloaded");
  }

  async getTitle(): Promise<string> {
    return this.page.title();
  }

  async setLocalStorage(key: string, value: string): Promise<void> {
    await this.page.evaluate(
      ([k, v]) => localStorage.setItem(k, v),
      [key, value]
    );
  }

  async getLocalStorage(key: string): Promise<string | null> {
    return this.page.evaluate((k) => localStorage.getItem(k), key);
  }

  async clearLocalStorage(): Promise<void> {
    await this.page.evaluate(() => localStorage.clear());
  }
}
