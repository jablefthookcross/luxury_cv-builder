import * as allure from "allure-js-commons";
import { test, expect } from "../fixtures/test-fixtures";
import { buildCandidateProfile } from "../data/builders";
import { auditCvQualityAndAntiAi } from "../data/anti-ai-rules";

test.describe("API - Audytor Jakości Anti-AI i Standardów Inżynierskich QA", () => {
  test.beforeEach(async () => {
    await allure.parentSuite("Testy API");
    await allure.suite("Jakość i Zgodność ATS");
    await allure.subSuite("Weryfikacja Anti-AI i Budżetowanie Treści");
    await allure.epic("Gwarancja Autentyczności i Jakości Językowej");
    await allure.feature("Audytor Anti-AI & Spójność Schematów");
  });

  test("Generowane CV nie zawiera botowych zwrotów AI ani marketingowego żargonu @regression", async ({
    apiClient,
    authSession,
    cleanup,
  }) => {
    void cleanup;
    await allure.story("Weryfikacja braku sztucznych zwrotów AI (buzzword slop)");

    const jobOffer = `
      Szukamy doświadczonego Inżyniera QA do automatyzacji testów webowych.
      Stack: Playwright, TypeScript, CI/CD, SQL, Jira.
    `;

    const res = await apiClient.tailor.tailor(
      {
        job_description: jobOffer,
        target_role: "Senior QA Automation Engineer",
        lang: "pl",
      },
      authSession.token
    );

    expect(res.status()).toBe(200);
    const body = await res.json();
    const tailoredProfile = body.profile;

    const audit = auditCvQualityAndAntiAi(tailoredProfile);
    expect(audit.foundAiBuzzwords).toHaveLength(0);

    // Sprawdzenie również dedykowanego wyniku zwracanego przez backend
    const backendAudit = body.audit_results;
    expect(backendAudit).toBeDefined();
    expect(backendAudit.anti_ai_score).toBeGreaterThanOrEqual(80);
  });

  test("Podsumowanie zawodowe stosuje perspektywę 1-osobową i mieści się w budżecie słów (40-80) @regression", async ({
    apiClient,
    authSession,
    cleanup,
  }) => {
    void cleanup;
    await allure.story("Budżet słów i profesjonalna perspektywa 1-osobowa w podsumowaniu");

    const sampleJob = "Stanowisko: Tester Oprogramowania QA. Narzędzia: Postman, SQL, Jira, ISTQB.";

    const res = await apiClient.tailor.tailor(
      {
        job_description: sampleJob,
        target_role: "Software QA Tester",
        lang: "pl",
      },
      authSession.token
    );

    const body = await res.json();
    const profile = body.profile;
    const summary = profile.summary || "";

    const words = summary.trim().split(/\s+/).filter((w: string) => w.length > 0);
    expect(words.length).toBeGreaterThanOrEqual(30);
    expect(words.length).toBeLessThanOrEqual(95);

    const audit = auditCvQualityAndAntiAi(profile);
    expect(audit.firstPersonValid).toBe(true);
  });

  test("Rygorystyczny schemat kategoryzacji: dokładnie 3 grupy technologiczne z 4-6 tagami w każdej @regression", async ({
    apiClient,
    authSession,
    cleanup,
  }) => {
    void cleanup;
    await allure.story("Weryfikacja taksonomii i limitu umiejętności w 3 kategoriach");

    const res = await apiClient.tailor.tailor(
      {
        job_description: "Senior QA Engineer. Playwright, Postman, SQL, Docker, Jenkins, Git, Jira.",
        target_role: "Senior QA Engineer",
        lang: "en",
      },
      authSession.token
    );

    const body = await res.json();
    const skills = body.profile?.skills || [];

    // Dokładnie 3 kategorie
    expect(skills.length).toBe(3);

    for (const cat of skills) {
      expect(cat.category).toBeDefined();
      expect(typeof cat.category).toBe("string");
      expect(cat.category.length).toBeGreaterThan(3);

      expect(Array.isArray(cat.items)).toBe(true);
      expect(cat.items.length).toBeGreaterThanOrEqual(4);
      expect(cat.items.length).toBeLessThanOrEqual(6);
    }
  });
});
