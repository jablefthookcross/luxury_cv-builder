import * as allure from "allure-js-commons";
import { test, expect } from "../fixtures/test-fixtures";
import { buildQaUser, buildCandidateProfile } from "../data/builders";

test.describe("API - Izolacja Danych Użytkowników i Ochrona Danych Osobowych", () => {
  test.beforeEach(async () => {
    await allure.parentSuite("Testy API");
    await allure.suite("Bezpieczeństwo i Dostęp");
    await allure.subSuite("Izolacja Danych i Wielodostęp");
    await allure.epic("Ochrona Danych i Prywatności Kandydata");
    await allure.feature("Polityki Izolacji Profilu (RLS)");
  });

  test("Gość (niezalogowany) otrzymuje profil DEMO z anonimowymi danymi kontaktowymi @regression @security", async ({
    apiClient,
  }) => {
    await allure.story("Zabezpieczenie profilu gościa przed wyciekiem danych innych użytkowników");

    await test.step("Pobranie profilu bez nagłówka Authorization Bearer", async () => {
      const res = await apiClient.profile.getProfile();
      expect(res.status()).toBe(200);

      const profile = await res.json();
      expect(profile).toBeDefined();

      const pinfo = profile.personal_info || {};
      // Sprawdzenie, że gość otrzymuje Jan Kowalski (Profil Demo) lub bezpieczny szablon demonstracyjny
      expect(pinfo.full_name).toContain("Jan Kowalski");
      expect(pinfo.email).toMatch(/demo|przyklad/i);
      expect(pinfo.phone).toMatch(/\+48\s*000/);

      // Kluczowa weryfikacja bezpieczeństwa: gość nie ma dostępu do realnych danych właściciela
      expect(pinfo.full_name).not.toBe("Michał Kosowski");
      expect(pinfo.email).not.toBe("mmkosowski94@gmail.com");
    });
  });

  test("Nowo zarejestrowany użytkownik otrzymuje w 100% czysty profil bazowy bez zaśmiecenia @regression", async ({
    apiClient,
    testUser,
    cleanup,
  }) => {
    void cleanup;
    await allure.story("Czysty stan profilu dla nowego kandydata");

    const session = await apiClient.auth.registerAndLogin(testUser);

    await test.step("Weryfikacja zawartości profilu nowo utworzonego konta", async () => {
      const res = await apiClient.profile.getProfile(session.token);
      expect(res.status()).toBe(200);

      const profile = await res.json();
      const pinfo = profile.personal_info || {};

      // Profil musi być pusty lub zawierać wyłącznie przekazane imię przy rejestracji
      expect(pinfo.title || "").toBe("");
      expect(pinfo.location || "").toBe("");
      expect(pinfo.phone || "").toBe("");
      expect(profile.summary || "").toBe("");

      // Sekcje złożone muszą być pustymi tablicami
      expect(Array.isArray(profile.experience)).toBe(true);
      expect(profile.experience.length).toBe(0);
      expect(Array.isArray(profile.skills)).toBe(true);
      expect(profile.skills.length).toBe(0);
      expect(Array.isArray(profile.languages)).toBe(true);
      expect(profile.languages.length).toBe(0);
    });
  });

  test("Ustawienia AI (/api/settings) nie ujawniają surowego klucza GEMINI_API_KEY @regression @security", async ({
    apiClient,
  }) => {
    await allure.story("Ochrona sekretów AI i kluczy API przed wyciekiem na frontend");

    const res = await apiClient.profile.getSettings();
    expect(res.status()).toBe(200);

    const body = await res.json();
    expect(body.status).toBe("success");
    expect(body.settings).toBeDefined();

    // Klucz API nie może być zwrócony jako jawny string
    expect(body.settings.gemini_key).toBeUndefined();
    expect(typeof body.settings.has_gemini_key).toBe("boolean");
  });

  test("Użytkownik A nie nadpisuje profilu Użytkownika B (pełna separacja danych) @regression @security", async ({
    apiClient,
    cleanup,
  }) => {
    void cleanup;
    await allure.story("Izolacja zapisów w bazie danych pomiędzy różnymi kontami");

    const userA = buildQaUser({ fullName: "Inżynier QA Alfa" });
    const userB = buildQaUser({ fullName: "Inżynier QA Beta" });

    const sessionA = await apiClient.auth.registerAndLogin(userA);
    const sessionB = await apiClient.auth.registerAndLogin(userB);

    await test.step("Użytkownik A zapisuje własny, unikalny profil bazowy", async () => {
      const customProfileA = buildCandidateProfile({
        personal_info: {
          full_name: "Inżynier QA Alfa",
          title: "Senior SDET Architect",
          email: userA.email,
          phone: "+48 111 222 333",
          location: "Kraków",
          linkedin: "",
          github: "",
        },
      });

      const saveResA = await apiClient.profile.saveProfile(customProfileA, sessionA.token);
      expect(saveResA.status()).toBe(200);
    });

    await test.step("Weryfikacja, że Użytkownik B widzi wyłącznie swój profil, a nie profil Użytkownika A", async () => {
      const resB = await apiClient.profile.getProfile(sessionB.token);
      const profileB = await resB.json();

      expect(profileB.personal_info?.full_name).not.toBe("Inżynier QA Alfa");
      expect(profileB.personal_info?.title).not.toBe("Senior SDET Architect");
    });
  });
});
