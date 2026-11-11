import * as allure from "allure-js-commons";
import { test, expect } from "../fixtures/test-fixtures";
import { buildQaUser } from "../data/builders";

test.describe("API - Rejestracja, Logowanie i Bezpieczeństwo Tokenów JWT", () => {
  test.beforeEach(async () => {
    await allure.parentSuite("Testy API");
    await allure.suite("Bezpieczeństwo i Dostęp");
    await allure.subSuite("Autentykacja i Sesje");
    await allure.epic("System Autentykacji i Zarządzania Tożsamością");
    await allure.feature("Rejestracja i Logowanie");
  });

  test("Pomyślna rejestracja nowego kandydata oraz logowanie z tokenem JWT @smoke @regression", async ({
    apiClient,
    cleanup,
  }) => {
    void cleanup;
    await allure.story("Cykl rejestracji i logowania kandydata");

    const user = buildQaUser();

    await test.step("Krok 1: Wysłanie żądania rejestracji nowego użytkownika (POST /api/auth/register)", async () => {
      const regRes = await apiClient.auth.register(user);
      expect(regRes.status()).toBe(200);

      const regBody = await regRes.json();
      expect(regBody.status).toBe("success");
      expect(regBody.user).toBeDefined();
      expect(regBody.user.email).toBe(user.email);
    });

    await test.step("Krok 2: Logowanie za pomocą zarejestrowanych danych (POST /api/auth/login)", async () => {
      const loginRes = await apiClient.auth.login(user);
      expect(loginRes.status()).toBe(200);

      const loginBody = await loginRes.json();
      expect(loginBody.status).toBe("success");
      expect(loginBody.access_token).toBeDefined();
      expect(typeof loginBody.access_token).toBe("string");
      expect(loginBody.access_token.length).toBeGreaterThan(15);
      expect(loginBody.user.email).toBe(user.email);
    });
  });

  test("Odrzucenie rejestracji z brakującymi polami ze statusem 400 @regression @security", async ({
    apiClient,
  }) => {
    await allure.story("Walidacja wymaganych pól rejestracji");

    await test.step("Próba rejestracji bez podania hasła", async () => {
      const res = await apiClient.auth.register({ email: "invalid_no_pass@test.com", password: "", fullName: "Tester" });
      expect(res.status()).toBe(400);

      const body = await res.json();
      expect(body.status).toBe("error");
      expect(body.message).toContain("Wprowadź adres e-mail i hasło");
    });

    await test.step("Próba rejestracji bez podania adresu e-mail", async () => {
      const res = await apiClient.auth.register({ email: "", password: "ValidPassword123!", fullName: "Tester" });
      expect(res.status()).toBe(400);

      const body = await res.json();
      expect(body.status).toBe("error");
    });
  });

  test("Odrzucenie logowania z błędnymi danymi uwierzytelniającymi @regression @security", async ({
    apiClient,
  }) => {
    await allure.story("Blokada nieautoryzowanego dostępu przy złym haśle");

    await test.step("Próba logowania nieistniejącego konta lub ze złym hasłem", async () => {
      const res = await apiClient.auth.login({
        email: "non_existent_account_2026@domain.xyz",
        password: "completely_wrong_pass",
      });
      const body = await res.json();

      expect(body.status).toBe("error");
      expect(body.access_token).toBeUndefined();
    });
  });

  test("Sprawdzenie statusu serwera autoryzacji i połączenia z bazą Supabase @smoke", async ({
    apiClient,
  }) => {
    await allure.story("Weryfikacja kondycji usługi auth (Healthcheck)");

    const res = await apiClient.auth.status();
    expect(res.status()).toBe(200);

    const body = await res.json();
    expect(body.status).toBe("success");
    expect(typeof body.supabase_enabled).toBe("boolean");
  });
});
