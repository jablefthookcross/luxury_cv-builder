import * as allure from "allure-js-commons";
import { test, expect } from "../fixtures/test-fixtures";
import { TailoringPage } from "../pages/TailoringPage";
import { AuthModalPage } from "../pages/AuthModalPage";
import { LandingPage } from "../pages/LandingPage";
import { ProfilePage } from "../pages/ProfilePage";
import { buildQaUser, buildCandidateProfile } from "../data/builders";

test.describe("E2E UI - Weryfikacja Układu Wizualnego, Styli CSS i Typografii CV", () => {
  test.beforeEach(async () => {
    await allure.parentSuite("Testy E2E UI");
    await allure.suite("Jakość Wizualna");
    await allure.subSuite("Style CSS i Layout");
    await allure.epic("Jakość Wizualna i Spójność Typograficzna CV");
    await allure.feature("Style Layoutu i Brak Rozstrzelonego Tekstu (Justify Rivers)");
  });

  test("Podsumowanie zawodowe posiada wyrównanie do lewej (text-align: left) i text-wrap: pretty @regression @ui", async ({
    page,
    cleanup,
  }) => {
    void cleanup;
    await allure.story("Weryfikacja braku brzydkich dziur w tekście (brak text-align: justify)");

    const landing = new LandingPage(page);
    const authModal = new AuthModalPage(page);
    const tailoring = new TailoringPage(page);
    const profilePage = new ProfilePage(page);
    const testUser = buildQaUser();
    const candidateData = buildCandidateProfile();

    await test.step("Logowanie do aplikacji i uzupełnienie profilu", async () => {
      await landing.open();
      await landing.clickRegister();
      await authModal.registerUser(testUser.email, testUser.password, testUser.fullName);
      await expect(page.locator("#appDashboard")).toBeVisible({ timeout: 10_000 });

      await profilePage.open();
      await profilePage.fillBaseProfile(candidateData);
      await profilePage.save();

      await page.locator("#authenticatedNavTabs .nav-btn", { hasText: "Dopasowanie & Draft" }).click();
    });

    await test.step("Weryfikacja styli typograficznych w podglądzie DRAFT CV", async () => {
      await tailoring.verifyIframeLayoutStyles();
    });
  });

  test("Siatka CV zachowuje poprawny podział dwukolumnowy (280px pasek boczny) @regression @ui", async ({
    page,
    cleanup,
  }) => {
    void cleanup;
    await allure.story("Weryfikacja dwukolumnowego układu Grid CSS");

    const landing = new LandingPage(page);
    const authModal = new AuthModalPage(page);
    const tailoring = new TailoringPage(page);
    const testUser = buildQaUser();

    await landing.open();
    await landing.clickRegister();
    await authModal.registerUser(testUser.email, testUser.password, testUser.fullName);
    await expect(page.locator("#appDashboard")).toBeVisible({ timeout: 10_000 });

    const gridColumns = await tailoring.iframeBody.locator(".cv-wrapper").evaluate((el) => {
      const computed = window.getComputedStyle(el);
      return computed.gridTemplateColumns;
    });

    // Weryfikacja, że pierwsza kolumna to 280px
    expect(gridColumns).toMatch(/^280px\s+/);
  });

  test("Pasek boczny (.sidebar) zachowuje ciemne, profesjonalne tło i wysoki kontrast @regression @ui", async ({
    page,
    cleanup,
  }) => {
    void cleanup;
    await allure.story("Weryfikacja estetyki i kontrastu paska bocznego");

    const landing = new LandingPage(page);
    const authModal = new AuthModalPage(page);
    const tailoring = new TailoringPage(page);
    const testUser = buildQaUser();

    await landing.open();
    await landing.clickRegister();
    await authModal.registerUser(testUser.email, testUser.password, testUser.fullName);
    await expect(page.locator("#appDashboard")).toBeVisible({ timeout: 10_000 });

    const sidebarBg = await tailoring.iframeBody.locator(".sidebar").evaluate((el) => {
      const computed = window.getComputedStyle(el);
      return computed.backgroundColor;
    });

    // rgb(15, 23, 42) odpowiada kolorowi hex #0f172a
    expect(sidebarBg).toMatch(/rgb\(15,\s*23,\s*42\)/);
  });
});
