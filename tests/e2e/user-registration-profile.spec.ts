import * as allure from "allure-js-commons";
import { test, expect } from "../fixtures/test-fixtures";
import { LandingPage } from "../pages/LandingPage";
import { AuthModalPage } from "../pages/AuthModalPage";
import { ProfilePage } from "../pages/ProfilePage";
import { buildQaUser, buildCandidateProfile } from "../data/builders";

test.describe("E2E UI - Rejestracja Użytkownika i Zarządzanie Profilem Bazowym", () => {
  test.beforeEach(async () => {
    await allure.parentSuite("Testy E2E UI");
    await allure.suite("Ścieżka Użytkownika");
    await allure.subSuite("Rejestracja i Profil");
    await allure.epic("Zarządzanie Profilem Kandydata");
    await allure.feature("Rejestracja Konta i Czysty Profil Bazowy");
  });

  test("Rejestracja nowego kandydata odblokowuje kokpit, a profil bazowy jest czysty @smoke @regression @ui", async ({
    page,
    cleanup,
  }) => {
    void cleanup;
    await allure.story("Odblokowanie kokpitu i weryfikacja czystości nowego profilu");

    const landing = new LandingPage(page);
    const authModal = new AuthModalPage(page);
    const profilePage = new ProfilePage(page);
    const testUser = buildQaUser();

    await test.step("Krok 1: Wejście na stronę i otwarcie formularza rejestracji", async () => {
      await landing.open();
      await landing.clickRegister();
    });

    await test.step("Krok 2: Wypełnienie formularza i wysłanie rejestracji", async () => {
      await authModal.registerUser(testUser.email, testUser.password, testUser.fullName);
      await authModal.expectSuccessToast();
    });

    await test.step("Krok 3: Weryfikacja przejścia do kokpitu aplikacji po zalogowaniu", async () => {
      const appDashboard = page.locator("#appDashboard");
      await expect(appDashboard).toBeVisible({ timeout: 10_000 });

      const authBtn = page.locator("#btnAuthHeader");
      await expect(authBtn).toContainText(testUser.email);
    });

    await test.step("Krok 4: Przejście do zakładki 'Profil Bazowy' i weryfikacja czystości formularza", async () => {
      await profilePage.open();
      await profilePage.expectCleanProfile(testUser.fullName);
    });
  });

  test("Użytkownik może wypełnić dane profilu bazowego i zapisać je pomyślnie @regression @ui", async ({
    page,
    cleanup,
  }) => {
    void cleanup;
    await allure.story("Edycja i zapisywanie profilu bazowego kandydata");

    const landing = new LandingPage(page);
    const authModal = new AuthModalPage(page);
    const profilePage = new ProfilePage(page);
    const testUser = buildQaUser();
    const candidateData = buildCandidateProfile();

    await test.step("Krok 1: Rejestracja nowego konta testowego", async () => {
      await landing.open();
      await landing.clickRegister();
      await authModal.registerUser(testUser.email, testUser.password, testUser.fullName);
      await expect(page.locator("#appDashboard")).toBeVisible({ timeout: 10_000 });
    });

    await test.step("Krok 2: Otwarcie edytora profilu i uzupełnienie danych", async () => {
      await profilePage.open();
      await profilePage.fillBaseProfile(candidateData);
    });

    await test.step("Krok 3: Zapisanie profilu za pomocą przycisku Zapisz", async () => {
      await profilePage.save();
    });

    await test.step("Krok 4: Weryfikacja zachowania wprowadzonych danych po odświeżeniu widoku", async () => {
      await profilePage.open();
      await expect(profilePage.fullNameInput).toHaveValue(candidateData.personal_info.full_name);
      await expect(profilePage.titleInput).toHaveValue(candidateData.personal_info.title);
      await expect(profilePage.emailInput).toHaveValue(candidateData.personal_info.email);
      await expect(profilePage.phoneInput).toHaveValue(candidateData.personal_info.phone);
    });
  });
});
