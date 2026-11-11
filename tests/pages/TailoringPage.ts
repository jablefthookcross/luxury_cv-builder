import { Locator, Page, FrameLocator, expect } from "@playwright/test";
import { BasePage } from "./BasePage";

export class TailoringPage extends BasePage {
  readonly jobDescriptionInput: Locator;
  readonly cleanTextBtn: Locator;
  readonly cvLanguageSelect: Locator;
  readonly cvTemplateSelect: Locator;
  readonly aiProviderSelect: Locator;
  readonly targetRoleInput: Locator;

  // Buttons
  readonly analyzeJobBtn: Locator;
  readonly runTailorBtn: Locator;
  readonly resetDraftBtn: Locator;
  readonly refineInput: Locator;
  readonly applyRefineBtn: Locator;
  readonly downloadPdfBtn: Locator;
  readonly saveModalOpenBtn: Locator;

  // Widgets & Cards
  readonly jobSpecCard: Locator;
  readonly specSeniorityBadge: Locator;
  readonly specPrimaryBadges: Locator;
  readonly atsPlaceholderCard: Locator;
  readonly atsWidget: Locator;
  readonly scoreValue: Locator;
  readonly matchedBadges: Locator;
  readonly bucketsWidget: Locator;
  readonly bucketABadges: Locator;
  readonly bucketBBadges: Locator;
  readonly bucketCBadges: Locator;
  readonly auditWidget: Locator;
  readonly antiAiScoreVal: Locator;
  readonly atsReadinessVal: Locator;

  // Iframe preview
  readonly previewIframe: Locator;
  readonly iframeBody: FrameLocator;

  constructor(page: Page) {
    super(page);
    this.jobDescriptionInput = page.locator("#jobDescription");
    this.cleanTextBtn = page.locator(".btn-clean-micro");
    this.cvLanguageSelect = page.locator("#cvLanguage");
    this.cvTemplateSelect = page.locator("#cvTemplate");
    this.aiProviderSelect = page.locator("#aiProvider");
    this.targetRoleInput = page.locator("#targetRole");

    this.analyzeJobBtn = page.locator("button:has(#analyzeBtnText)");
    this.runTailorBtn = page.locator("button:has(#tailorBtnText)");
    this.resetDraftBtn = page.locator("button:has-text('Przywróć Czysty Profil')");
    this.refineInput = page.locator("#refinePromptInput");
    this.applyRefineBtn = page.locator("button:has(#refineBtnText)");
    this.downloadPdfBtn = page.locator("#btnDownloadPdf");
    this.saveModalOpenBtn = page.getByRole("button", { name: /Zapisz do Moich CV/i });

    this.jobSpecCard = page.locator("#jobSpecCard");
    this.specSeniorityBadge = page.locator("#specSeniorityBadge");
    this.specPrimaryBadges = page.locator("#specPrimaryBadges");
    this.atsPlaceholderCard = page.locator("#atsPlaceholderCard");
    this.atsWidget = page.locator("#atsWidget");
    this.scoreValue = page.locator("#scoreValue");
    this.matchedBadges = page.locator("#matchedBadges");
    this.bucketsWidget = page.locator("#bucketsWidget");
    this.bucketABadges = page.locator("#bucketABadges");
    this.bucketBBadges = page.locator("#bucketBBadges");
    this.bucketCBadges = page.locator("#bucketCBadges");
    this.auditWidget = page.locator("#auditWidget");
    this.antiAiScoreVal = page.locator("#antiAiScoreVal");
    this.atsReadinessVal = page.locator("#atsReadinessVal");

    this.previewIframe = page.locator("#previewIframe");
    this.iframeBody = page.frameLocator("#previewIframe");
  }

  async enterJobOffer(text: string): Promise<void> {
    await this.jobDescriptionInput.fill(text);
  }

  async setLanguage(lang: "pl" | "en"): Promise<void> {
    await this.cvLanguageSelect.selectOption(lang);
  }

  async step1AnalyzeOffer(): Promise<void> {
    await this.analyzeJobBtn.click();
    await expect(this.jobSpecCard).toBeVisible({ timeout: 25_000 });
  }

  async step2GenerateTailoredCv(): Promise<void> {
    await this.runTailorBtn.click();
    await expect(this.atsWidget).toBeVisible({ timeout: 35_000 });
    await expect(this.bucketsWidget).toBeVisible();
    await expect(this.auditWidget).toBeVisible();
  }

  async step3RefinePrompt(instruction: string): Promise<void> {
    await this.refineInput.fill(instruction);
    await this.applyRefineBtn.click();
    // Wait for the refine spinner to disappear
    await expect(this.page.locator("#refineSpinner")).toBeHidden({ timeout: 25_000 });
  }

  async expectAtsScoreAtLeast(minScore: number): Promise<void> {
    await expect(this.atsWidget).toBeVisible();
    const scoreText = await this.scoreValue.textContent();
    const scoreNum = parseInt(scoreText?.replace("%", "") || "0", 10);
    expect(scoreNum).toBeGreaterThanOrEqual(minScore);
  }

  async expect3BucketsPopulated(): Promise<void> {
    await expect(this.bucketsWidget).toBeVisible();
    const bucketACount = await this.bucketABadges.locator(".kw-badge").count();
    const bucketBCount = await this.bucketBBadges.locator(".kw-badge").count();
    expect(bucketACount).toBeGreaterThan(0);
    expect(bucketBCount).toBeGreaterThan(0);
  }

  async expectAntiAiAuditPassed(): Promise<void> {
    await expect(this.auditWidget).toBeVisible();
    await expect(this.antiAiScoreVal).toContainText(/100%|Autentyczny/i);
    await expect(this.atsReadinessVal).toContainText(/100%|Bezpieczny/i);
  }

  async getIframeCandidateTitle(): Promise<string> {
    const el = this.iframeBody.locator(".candidate-title");
    await el.waitFor({ state: "visible" });
    return (await el.textContent()) || "";
  }

  async getIframeSummaryText(): Promise<string> {
    const el = this.iframeBody.locator(".summary-p");
    await el.waitFor({ state: "visible" });
    return (await el.textContent()) || "";
  }

  async getIframeSkillsCategories(): Promise<string[]> {
    const cats = this.iframeBody.locator(".skill-cat-name");
    return cats.allTextContents();
  }

  async verifyIframeLayoutStyles(): Promise<void> {
    // Assert summary is strictly left-aligned with no justification rivers
    const summaryAlign = await this.iframeBody.locator(".summary-p").evaluate((el) => {
      const computed = window.getComputedStyle(el);
      return computed.textAlign;
    });
    expect(summaryAlign).toBe("left");

    // Assert grid structure exists in .cv-wrapper
    const cvDisplay = await this.iframeBody.locator(".cv-wrapper").evaluate((el) => {
      const computed = window.getComputedStyle(el);
      return computed.display;
    });
    expect(cvDisplay).toBe("grid");
  }
}
