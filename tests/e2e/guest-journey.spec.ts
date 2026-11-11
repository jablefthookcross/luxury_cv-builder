import * as allure from "allure-js-commons";
import { test, expect } from "../fixtures/test-fixtures";
import { LandingPage } from "../pages/LandingPage";
import { AuthModalPage } from "../pages/AuthModalPage";

test.describe("E2E UI - Ścieżka Niezalogowanego Gościa (Guest Experience)", () => {
  test.beforeEach(async () => {
    await allure.parentSuite("Testy E2E UI");
    await allure.suite("Ścieżka Użytkownika");
    await allure.subSuite("Gość i Landing Screen");
    await allure.epic("Doświadczenie Pierwszego Kontaktu (Landing Screen)");
    await allure.feature("Ekran Powitalny i Ochrona Kokpitu");
  });

  test("Niezalogowany gość widzi luksusowy ekran powitalny, a kokpit aplikacji jest ukryty @smoke @ui", async ({
    page,
  }) => {
    await allure.story("Widok kandydata niezalogowanego (Guest Mode)");

    const landing = new LandingPage(page);

    await test.step("Krok 1: Wejście na stronę główną aplikacji", async () => {
      await landing.open();
      await landing.expectLandingVisible();
    });

    await test.step("Krok 2: Weryfikacja ukrycia wewnętrznego kokpitu przed logowaniem", async () => {
      const appDashboard = page.locator("#appDashboard");
      const navTabs = page.locator("#authenticatedNavTabs");

      await expect(appDashboard).toBeHidden();
      await expect(navTabs).toBeHidden();
    });

    await test.step("Krok 3: Weryfikacja dostępności bezpośredniego linku do Swagger API", async () => {
      await expect(landing.swaggerApiLink).toBeVisible();
      await expect(landing.swaggerApiLink).toHaveAttribute("href", "/docs");
    });
  });

  test("Gość może otworzyć modal rejestracji lub logowania bezpośrednio z przycisków CTA @ui", async ({
    page,
  }) => {
    await allure.story("Interakcja z przyciskami CTA i otwieranie modalu auth");

    const landing = new LandingPage(page);
    const authModal = new AuthModalPage(page);

    await test.step("Krok 1: Otwarcie modalu rejestracji z głównego przycisku CTA", async () => {
      await landing.open();
      await landing.clickRegister();
      await authModal.expectModalOpen();
      await expect(authModal.modalTitle).toContainText("Rejestracja");
      await expect(authModal.fullNameGroup).toBeVisible();
    });

    await test.step("Krok 2: Przełączenie trybu na logowanie w modalu", async () => {
      await authModal.switchToLogin();
      await expect(authModal.modalTitle).toContainText("Logowanie");
      await expect(authModal.fullNameGroup).toBeHidden();
    });
  });
});
