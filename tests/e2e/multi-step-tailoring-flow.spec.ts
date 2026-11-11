import * as allure from "allure-js-commons";
import { test, expect } from "../fixtures/test-fixtures";
import { LandingPage } from "../pages/LandingPage";
import { AuthModalPage } from "../pages/AuthModalPage";
import { TailoringPage } from "../pages/TailoringPage";
import { ProfilePage } from "../pages/ProfilePage";
import { buildQaUser, buildCandidateProfile } from "../data/builders";
import { PARAMETERIZED_JOB_OFFERS } from "../data/job-offers";

test.describe("E2E UI - Wielokrokowy Kreator Dopasowania i Syntezy CV", () => {
  test.beforeEach(async () => {
    await allure.parentSuite("Testy E2E UI");
    await allure.suite("Kreator Dopasowania");
    await allure.subSuite("Wielokrokowy Proces Syntezy");
    await allure.epic("Inteligentny Kreator i Synteza CV");
    await allure.feature("End-to-End Wizard: Krok 1 -> Krok 2 -> Krok 3 -> PDF");
  });

  test("Kompletna ścieżka E2E: Analiza oferty, Synteza DRAFT-u, Audyt Anti-AI, Rafinacja Promptem i Pobranie PDF @smoke @regression @ui", async ({
    page,
    cleanup,
  }) => {
    void cleanup;
    await allure.story("Ścieżka krytyczna: od oferty do gotowego pliku PDF z weryfikacją jakości");

    const landing = new LandingPage(page);
    const authModal = new AuthModalPage(page);
    const tailoring = new TailoringPage(page);
    const profilePage = new ProfilePage(page);
    const testUser = buildQaUser();
    const candidateData = buildCandidateProfile();

    const sampleJobOffer = `
      Szukamy Senior QA Automation Engineera do zespołu platformy e-commerce.
      Wymagania:
      - Doświadczenie w Playwright z TypeScript.
      - Testowanie API (REST) w Postman lub SoapUI.
      - Znajomość relacyjnych baz danych SQL (PostgreSQL).
      - Integracja z pipeline'ami CI/CD w GitHub Actions.
      - Praca w metodyce Agile/Scrum oraz obsługa Jira (Xray).
    `;

    await test.step("Krok 1: Rejestracja nowego użytkownika i uzupełnienie profilu bazowego", async () => {
      await landing.open();
      await landing.clickRegister();
      await authModal.registerUser(testUser.email, testUser.password, testUser.fullName);
      await expect(page.locator("#appDashboard")).toBeVisible({ timeout: 10_000 });

      // Zapisujemy pełny profil bazowy
      await profilePage.open();
      await profilePage.fillBaseProfile(candidateData);
      await profilePage.save();

      // Wracamy do zakładki Dopasowanie
      await page.locator("#authenticatedNavTabs .nav-btn", { hasText: "Dopasowanie & Draft" }).click();
      await expect(page.locator("#tab-tailor")).toBeVisible();
    });

    await test.step("Krok 2: Wklejenie treści oferty i wykonanie KROK 1 (Analiza Oferty)", async () => {
      await tailoring.enterJobOffer(sampleJobOffer);
      await tailoring.step1AnalyzeOffer();

      // Weryfikacja karty wymagań z KROKU 1
      await expect(tailoring.jobSpecCard).toBeVisible();
      await expect(tailoring.specSeniorityBadge).toContainText(/Senior|Mid/i);
    });

    await test.step("Krok 3: Wykonanie KROK 2 (Wygenerowanie Dedykowanego CV DRAFT)", async () => {
      await tailoring.step2GenerateTailoredCv();

      // Weryfikacja jakościowa wskaźnika ATS
      await tailoring.expectAtsScoreAtLeast(60);

      // Weryfikacja podziału na 3 koszyki (A, B, C)
      await tailoring.expect3BucketsPopulated();

      // Weryfikacja wskaźnika Anti-AI
      await tailoring.expectAntiAiAuditPassed();
    });

    await test.step("Krok 4: Weryfikacja zawartości podglądu DRAFT CV wewnątrz ramki iframe", async () => {
      const summaryText = await tailoring.getIframeSummaryText();
      expect(summaryText.length).toBeGreaterThan(40);

      // Asercja Anti-AI: brak żargonu botów
      expect(summaryText.toLowerCase()).not.toContain("delve");
      expect(summaryText.toLowerCase()).not.toContain("testament to");
      expect(summaryText.toLowerCase()).not.toContain("dynamiczny profesjonalista");

      // Sprawdzenie obecności kluczowych kategorii w podglądzie
      const categories = await tailoring.getIframeSkillsCategories();
      expect(categories.length).toBe(3);
    });

    await test.step("Krok 5: KROK 3 (Interaktywna rafinacja za pomocą Prompt Refinera)", async () => {
      await tailoring.step3RefinePrompt("Wzmocnij akcent na Playwright APIRequestContext w sekcji umiejętności");
      // Sprawdzenie, że podgląd nadal funkcjonuje prawidłowo po rafinacji
      const summaryAfterRefine = await tailoring.getIframeSummaryText();
      expect(summaryAfterRefine.length).toBeGreaterThan(30);
    });

    await test.step("Krok 6: Pobranie wygenerowanego pliku PDF i weryfikacja zdarzenia downloadu", async () => {
      const downloadPromise = page.waitForEvent("download", { timeout: 30_000 });
      await tailoring.downloadPdfBtn.click();
      const download = await downloadPromise;

      const filename = download.suggestedFilename();
      expect(filename).toMatch(/\.pdf$/i);
    });
  });
});
