import * as allure from "allure-js-commons";
import { test, expect } from "../fixtures/test-fixtures";
import { buildQaUser } from "../data/builders";

test.describe("API - Nuklearne Czyszczenie Danych Testowych (POST /admin/cleanup)", () => {
  test.beforeEach(async () => {
    await allure.parentSuite("Testy API");
    await allure.suite("Administracja i Higiena Środowiska");
    await allure.subSuite("Nuklearne Czyszczenie");
    await allure.epic("Utrzymanie i Integralność Środowiska Testowego");
    await allure.feature("Punkt Końcowy /admin/cleanup");
  });

  test("Odrzucenie żądania czyszczenia bez nagłówka x-admin-secret (status 403) @regression @security", async ({
    apiClient,
  }) => {
    await allure.story("Blokada nieautoryzowanego czyszczenia bazy danych");

    const res = await apiClient.admin.cleanupWithoutSecret();
    expect(res.status()).toBe(403);

    const body = await res.json();
    expect(body.status).toBe("error");
    expect(body.message).toContain("x-admin-secret");
  });

  test("Odrzucenie żądania z nieprawidłowym kluczem sekretu (status 403) @regression @security", async ({
    apiClient,
  }) => {
    await allure.story("Weryfikacja poprawności hasła administratora");

    const res = await apiClient.admin.cleanup("niepoprawny-falszywy-klucz-2026");
    expect(res.status()).toBe(403);

    const body = await res.json();
    expect(body.status).toBe("error");
  });

  test("Pomyślne wykonanie czyszczenia bazy z poprawnym kluczem i zachowaniem konta właściciela @smoke @regression", async ({
    apiClient,
  }) => {
    await allure.story("Nuklearne czyszczenie kont testowych z zachowaniem właściciela");

    // 1. Utworzenie tymczasowego użytkownika testowego
    const tempUser = buildQaUser();
    await apiClient.auth.register(tempUser);

    // 2. Wywołanie czyszczenia z poprawnym kluczem
    const cleanRes = await apiClient.admin.cleanup("vitaecraft-nuclear-secret-2026", true);
    expect(cleanRes.status()).toBe(200);

    const body = await cleanRes.json();
    expect(body.status).toBe("success");
    expect(body.details).toBeDefined();
    expect(typeof body.details.users_deleted).toBe("number");
    expect(body.details.preserve_owner).toBe(true);

    // 3. Weryfikacja, że tymczasowy użytkownik został usunięty (nie może się zalogować)
    const loginRes = await apiClient.auth.login(tempUser);
    const loginBody = await loginRes.json();
    expect(loginBody.status).toBe("error");
  });
});
