export interface JobOfferDataset {
  roleId: string;
  roleName: string;
  language: "pl" | "en";
  company: string;
  expectedKeywords: string[];
  jobText: string;
}

export const PARAMETERIZED_JOB_OFFERS: JobOfferDataset[] = [
  {
    roleId: "qa-automation-ts",
    roleName: "Senior QA Automation Engineer (Playwright & TypeScript)",
    language: "pl",
    company: "FinTech Cloud Solutions",
    expectedKeywords: ["Playwright", "TypeScript", "CI/CD", "SQL", "API", "Jira"],
    jobText: `
Poszukujemy doświadczonego Senior QA Automation Engineera do zespołu rozwoju nowoczesnej platformy bankowej.
Wymagania:
- Minimum 4 lata doświadczenia w automatyzacji testów aplikacji webowych i API.
- Biegła znajomość frameworka Playwright z językiem TypeScript lub JavaScript.
- Doświadczenie w integracji testów z pipeline'ami CI/CD (GitHub Actions / GitLab CI).
- Praktyczna znajomość testowania API (REST) przy użyciu Postman lub Playwright APIRequestContext.
- Dobra znajomość relacyjnych baz danych i zapytań SQL (PostgreSQL / MySQL).
- Znajomość narzędzi Jira (Xray) oraz metodyk Agile/Scrum.
- Płynna znajomość języka polskiego oraz komunikatywny język angielski.
    `.trim(),
  },
  {
    roleId: "qa-engineer-en",
    roleName: "QA Engineer (API & Performance Testing)",
    language: "en",
    company: "Apex Global Cloud Systems",
    expectedKeywords: ["API", "Postman", "SQL", "CI/CD", "Docker", "JMeter"],
    jobText: `
Apex Systems is looking for a QA Engineer to strengthen our quality assurance team in Europe.
Requirements:
- 3+ years of experience in software testing and quality engineering.
- Solid experience in RESTful and SOAP API testing using Postman, SoapUI or REST Assured.
- Strong SQL querying skills for data verification and backend validation.
- Knowledge of automated testing tools like Selenium WebDriver or Playwright.
- Familiarity with CI/CD tools (Jenkins, GitHub Actions) and Docker containerization.
- Experience with test documentation, test design techniques (ISTQB standard).
- Full professional proficiency in English (B2/C1).
    `.trim(),
  },
  {
    roleId: "qa-manual-process",
    roleName: "Specjalista ds. Zapewnienia Jakości Oprogramowania (QA Manual & Process)",
    language: "pl",
    company: "Healthcare Digital Lab",
    expectedKeywords: ["Jira", "Xray", "ISTQB", "SQL", "Scenariusze testowe", "Postman"],
    jobText: `
Dla naszego klienta z sektora medycznego poszukujemy Specjalisty ds. QA.
Zakres obowiązków:
- Projektowanie przypadków i scenariuszy testowych w oparciu o dokumentację biznesową i wymagania HL7/FHIR.
- Prowadzenie testów funkcjonalnych, regresyjnych, smoke i eksploracyjnych.
- Weryfikacja poprawności komunikacji API z użyciem Postman oraz weryfikacja bazy danych SQL.
- Ścisła współpraca z programistami i analitykami biznesowymi w Jira (Xray).
- Posiadanie certyfikatu ISTQB Foundation Level będzie dużym atutem.
    `.trim(),
  },
];
