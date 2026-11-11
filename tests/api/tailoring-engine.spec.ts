import * as allure from "allure-js-commons";
import { test, expect } from "../fixtures/test-fixtures";
import { PARAMETERIZED_JOB_OFFERS } from "../data/job-offers";
import { buildCandidateProfile } from "../data/builders";

test.describe("API - Silnik Inteligencji Ofert i Bezstanowego Dopasowania CV", () => {
  test.beforeEach(async () => {
    await allure.parentSuite("Testy API");
    await allure.suite("Logika Biznesowa");
    await allure.subSuite("Analiza i Synteza CV");
    await allure.epic("Silnik Inteligencji Dopasowania CV");
    await allure.feature("Ekstrakcja i Dopasowanie Ofert (Etap 1 i 2)");
  });

  test("Ekstrakcja wymagań i technologii z surowego tekstu ogłoszenia (POST /api/analyze-job) @smoke @regression", async ({
    apiClient,
  }) => {
    await allure.story("Parsowanie oferty pracy i generowanie JobSpecification");

    const sampleJobText = `
      Poszukujemy Senior QA Automation Engineera.
      Wymagania kluczowe: Playwright, TypeScript, SQL, Docker, CI/CD oraz znajomość Jira.
      Mile widziane: testy wydajnościowe JMeter.
    `;

    const res = await apiClient.tailor.analyzeJob(sampleJobText);
    expect(res.status()).toBe(200);

    const body = await res.json();
    expect(body.status).toBe("success");
    expect(body.spec).toBeDefined();

    const spec = body.spec;
    expect(spec.seniority).toBeDefined();
    expect(Array.isArray(spec.primary_technologies)).toBe(true);
    expect(Array.isArray(spec.secondary_technologies) || Array.isArray(spec.tools)).toBe(true);

    // Sprawdzenie, czy kluczowe technologie zostały rozpoznane
    const allFound = [
      ...(spec.primary_technologies || []),
      ...(spec.secondary_technologies || []),
      ...(spec.tools || []),
    ].map((t: string) => t.toLowerCase());

    const hasPlaywright = allFound.some((t) => t.includes("playwright"));
    const hasSqlOrTs = allFound.some((t) => t.includes("sql") || t.includes("typescript"));
    expect(hasPlaywright || hasSqlOrTs).toBe(true);
  });

  for (const offer of PARAMETERIZED_JOB_OFFERS) {
    test(`Parametryzowane dopasowanie CV: ${offer.roleName} [${offer.language.toUpperCase()}] @regression`, async ({
      apiClient,
      authSession,
      cleanup,
    }) => {
      void cleanup;
      await allure.story(`Dopasowanie profilu pod rolę ${offer.roleName}`);

      await test.step("Krok 1: Wstępne przygotowanie profilu kandydata", async () => {
        const profile = buildCandidateProfile();
        await apiClient.profile.saveProfile(profile, authSession.token);
      });

      let tailoredResult: any;

      await test.step("Krok 2: Wywołanie bezstanowego endpointu POST /api/tailor", async () => {
        const res = await apiClient.tailor.tailor(
          {
            job_description: offer.jobText,
            target_role: offer.roleName,
            lang: offer.language,
          },
          authSession.token
        );

        expect(res.status()).toBe(200);
        tailoredResult = await res.json();
        expect(tailoredResult.status).toBe("success");
        expect(tailoredResult.profile).toBeDefined();
      });

      await test.step("Krok 3: Weryfikacja 3-koszykowego podziału selekcji umiejętności", async () => {
        const buckets = tailoredResult.buckets_breakdown;
        expect(buckets).toBeDefined();
        expect(Array.isArray(buckets.bucket_a)).toBe(true);
        expect(Array.isArray(buckets.bucket_b)).toBe(true);
        expect(Array.isArray(buckets.bucket_c)).toBe(true);
      });

      await test.step("Krok 4: Weryfikacja kalkulacji ATS Match Score", async () => {
        const ats = tailoredResult.ats_analysis;
        expect(ats).toBeDefined();
        expect(typeof ats.match_score).toBe("number");
        expect(ats.match_score).toBeGreaterThanOrEqual(50);
        expect(ats.match_score).toBeLessThanOrEqual(100);
      });

      await test.step("Krok 5: Weryfikacja zachowania języka wyjściowego", async () => {
        const languages = tailoredResult.profile.languages || [];
        expect(languages.length).toBeGreaterThanOrEqual(2);

        if (offer.language === "en") {
          const hasEnglishNativeOrProf = languages.some(
            (l: any) => l.language === "English" || l.language === "Polish"
          );
          expect(hasEnglishNativeOrProf).toBe(true);
        } else {
          const hasPolski = languages.some((l: any) => l.language === "Polski");
          expect(hasPolski).toBe(true);
        }
      });
    });
  }

  test("Bezstanowe generowanie DRAFT-u nie nadpisuje głównego profilu w bazie danych @regression", async ({
    apiClient,
    authSession,
    cleanup,
  }) => {
    void cleanup;
    await allure.story("Zasada bezstanowości (Stateless) - nienaruszalność bazy danych");

    const originalProfile = buildCandidateProfile({
      personal_info: {
        full_name: "Oryginalny Kandydat",
        title: "Architekt Jakości",
        email: authSession.user.email,
        phone: "+48 999 888 777",
        location: "Gdańsk",
        linkedin: "",
        github: "",
      },
    });

    await apiClient.profile.saveProfile(originalProfile, authSession.token);

    // Wywołanie /api/tailor z nową rolą
    const tailorRes = await apiClient.tailor.tailor(
      {
        job_description: "Szukamy DevSecOps Engineera...",
        target_role: "Lead DevSecOps",
        lang: "pl",
      },
      authSession.token
    );
    expect(tailorRes.status()).toBe(200);

    // Sprawdzenie, że profil bazowy w bazie pozostał nietknięty
    const baseProfileRes = await apiClient.profile.getProfile(authSession.token);
    const baseProfile = await baseProfileRes.json();

    expect(baseProfile.personal_info.full_name).toBe("Oryginalny Kandydat");
    expect(baseProfile.personal_info.title).toBe("Architekt Jakości");
  });

  test("Zastosowanie poprawek użytkownika w prompt refinerze (POST /api/refine-cv) @regression", async ({
    apiClient,
    authSession,
  }) => {
    await allure.story("Interaktywna rafinacja CV za pomocą poleceń promptu");

    const testProfile = buildCandidateProfile();
    const instruction = "Dodaj Playwright APIRequestContext do umiejętności i upewnij się, że podsumowanie ma profesjonalny ton";

    const res = await apiClient.tailor.refine(testProfile, instruction, "pl", authSession.token);
    expect(res.status()).toBe(200);

    const body = await res.json();
    expect(body.status).toBe("success");
    expect(body.profile).toBeDefined();
    expect(body.profile.skills).toBeDefined();
  });
});
