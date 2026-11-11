import * as allure from "allure-js-commons";
import { test, expect } from "../fixtures/test-fixtures";
import { buildCandidateProfile } from "../data/builders";

test.describe("API - Generowanie i Eksport CV do Formatu PDF", () => {
  test.beforeEach(async () => {
    await allure.parentSuite("Testy API");
    await allure.suite("Eksport i Dystrybucja");
    await allure.subSuite("Silnik Generowania PDF");
    await allure.epic("Wektorowy Eksport Dokumentów PDF");
    await allure.feature("Generowanie Pliku PDF A4");
  });

  test("Pomyślne wygenerowanie pliku PDF ze statusem 200, nagłówkiem application/pdf i sygnaturą %PDF @smoke @regression", async ({
    apiClient,
    authSession,
    cleanup,
  }) => {
    void cleanup;
    await allure.story("Weryfikacja binarnego strumienia PDF i magicznych bajtów");

    const profile = buildCandidateProfile();

    const res = await apiClient.tailor.exportPdf(
      {
        profile_data: profile,
        template: "pro_qa_sidebar",
        lang: "pl",
      },
      authSession.token
    );

    expect(res.status()).toBe(200);

    // Sprawdzenie typu MIME
    const contentType = res.headers()["content-type"] || "";
    expect(contentType).toContain("application/pdf");

    // Sprawdzenie nazwy pliku w Content-Disposition
    const disposition = res.headers()["content-disposition"] || "";
    expect(disposition).toContain("attachment");
    expect(disposition).toMatch(/\.pdf"?$/i);

    // Sprawdzenie nagłówków anty-cache
    const cacheControl = res.headers()["cache-control"] || "";
    expect(cacheControl).toContain("no-store");

    // Sprawdzenie zawartości binarnej - magiczne bajty %PDF
    const buffer = await res.body();
    expect(buffer.length).toBeGreaterThan(1000);
    const magicHeader = buffer.subarray(0, 5).toString("ascii");
    expect(magicHeader.startsWith("%PDF-")).toBe(true);
  });
});
