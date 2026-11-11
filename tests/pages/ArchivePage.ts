import { Locator, Page, expect } from "@playwright/test";
import { BasePage } from "./BasePage";

export class ArchivePage extends BasePage {
  readonly navSavedBtn: Locator;
  readonly tabSaved: Locator;
  readonly refreshBtn: Locator;
  readonly savedGrid: Locator;

  constructor(page: Page) {
    super(page);
    this.navSavedBtn = page.getByRole("button", { name: /Moje CV-ki \(Archiwum\)/i });
    this.tabSaved = page.locator("#tab-saved");
    this.refreshBtn = page.getByRole("button", { name: /Odśwież Listę/i });
    this.savedGrid = page.locator("#savedCVsGrid");
  }

  async open(): Promise<void> {
    await this.navSavedBtn.click();
    await expect(this.tabSaved).toBeVisible();
  }

  async expectArchiveLoaded(): Promise<void> {
    await expect(this.savedGrid).toBeVisible();
  }

  async getSavedCardsCount(): Promise<number> {
    return this.savedGrid.locator(".archive-card").count();
  }
}
