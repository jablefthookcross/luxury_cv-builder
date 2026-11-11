import { Locator, Page, expect } from "@playwright/test";
import { BasePage } from "./BasePage";
import { CandidateProfile } from "../data/builders";

export class ProfilePage extends BasePage {
  readonly navProfileBtn: Locator;
  readonly tabProfile: Locator;

  // Form Inputs
  readonly fullNameInput: Locator;
  readonly titleInput: Locator;
  readonly emailInput: Locator;
  readonly phoneInput: Locator;
  readonly locationInput: Locator;
  readonly linkedinInput: Locator;
  readonly githubInput: Locator;
  readonly summaryInput: Locator;

  // Buttons
  readonly addExperienceBtn: Locator;
  readonly addSkillBtn: Locator;
  readonly addLanguageBtn: Locator;
  readonly saveProfileBtn: Locator;
  readonly deleteProfileBtn: Locator;
  readonly btnEditForm: Locator;
  readonly btnEditJson: Locator;
  readonly jsonEditor: Locator;

  // Containers
  readonly experienceList: Locator;
  readonly skillsList: Locator;
  readonly languagesList: Locator;

  constructor(page: Page) {
    super(page);
    this.navProfileBtn = page.locator("#authenticatedNavTabs .nav-btn", { hasText: "Profil Bazowy" });
    this.tabProfile = page.locator("#tab-profile");

    this.fullNameInput = page.locator("#formFullName");
    this.titleInput = page.locator("#formTitle");
    this.emailInput = page.locator("#formEmail");
    this.phoneInput = page.locator("#formPhone");
    this.locationInput = page.locator("#formLocation");
    this.linkedinInput = page.locator("#formLinkedin");
    this.githubInput = page.locator("#formGithub");
    this.summaryInput = page.locator("#formSummary");

    this.addExperienceBtn = page.getByRole("button", { name: /Dodaj Stanowisko/i });
    this.addSkillBtn = page.getByRole("button", { name: /Dodaj Kategorię Umiejętności/i });
    this.addLanguageBtn = page.getByRole("button", { name: /Dodaj Język/i });
    this.saveProfileBtn = page.locator(".btn-save-action", { hasText: "Zapisz Profil Bazowy" });
    this.deleteProfileBtn = page.locator(".btn-danger-sm", { hasText: "Usuń Profil Bazowy" });
    this.btnEditForm = page.locator("#btnEditForm");
    this.btnEditJson = page.locator("#btnEditJson");
    this.jsonEditor = page.locator("#profileJsonEditor");

    this.experienceList = page.locator("#experienceCardsList");
    this.skillsList = page.locator("#skillsCardsList");
    this.languagesList = page.locator("#languagesCardsList");
  }

  async open(): Promise<void> {
    await this.navProfileBtn.click();
    await expect(this.tabProfile).toBeVisible();
  }

  async expectCleanProfile(expectedFullName?: string): Promise<void> {
    if (expectedFullName !== undefined) {
      await expect(this.fullNameInput).toHaveValue(expectedFullName);
    }
    await expect(this.titleInput).toHaveValue("");
    await expect(this.phoneInput).toHaveValue("");
    await expect(this.locationInput).toHaveValue("");
    await expect(this.summaryInput).toHaveValue("");
    expect(await this.experienceList.locator(".editor-card-item").count()).toBe(0);
    expect(await this.skillsList.locator(".editor-card-item").count()).toBe(0);
    expect(await this.languagesList.locator(".editor-card-item").count()).toBe(0);
  }

  async fillBaseProfile(data: CandidateProfile): Promise<void> {
    await this.fullNameInput.fill(data.personal_info.full_name);
    await this.titleInput.fill(data.personal_info.title);
    await this.emailInput.fill(data.personal_info.email);
    await this.phoneInput.fill(data.personal_info.phone);
    await this.locationInput.fill(data.personal_info.location);
    if (data.personal_info.linkedin) await this.linkedinInput.fill(data.personal_info.linkedin);
    if (data.personal_info.github) await this.githubInput.fill(data.personal_info.github);
    await this.summaryInput.fill(data.summary);
  }

  async save(): Promise<void> {
    await this.saveProfileBtn.click();
    await this.page.waitForTimeout(600);
  }
}
