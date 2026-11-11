export interface QaUser {
  email: string;
  password: string;
  fullName: string;
}

export interface CandidateProfile {
  personal_info: {
    full_name: string;
    title: string;
    email: string;
    phone: string;
    location: string;
    linkedin: string;
    github: string;
  };
  summary: string;
  experience: Array<{
    position: string;
    company: string;
    location: string;
    start_date: string;
    end_date: string;
    highlights: string[];
  }>;
  skills: Array<{
    category: string;
    items: string[];
  }>;
  languages: Array<{
    language: string;
    level: string;
  }>;
}

export function buildQaUser(overrides: Partial<QaUser> = {}): QaUser {
  const timestamp = Date.now();
  const rand = Math.floor(Math.random() * 10000);
  return {
    email: `qa_test_${timestamp}_${rand}@vitaecraft.test`,
    password: `TestSecurePass2026!`,
    fullName: `Michał QA Tester ${rand}`,
    ...overrides,
  };
}

export function buildCandidateProfile(overrides: Partial<CandidateProfile> = {}): CandidateProfile {
  return {
    personal_info: {
      full_name: "Jan Kowalski",
      title: "Senior QA Automation Engineer",
      email: "jan.kowalski@example.com",
      phone: "+48 500 100 200",
      location: "Warszawa",
      linkedin: "https://linkedin.com/in/jankowalski-qa",
      github: "https://github.com/jankowalski-qa",
    },
    summary:
      "Doświadczony Senior QA Automation Engineer z ponad 5-letnią praktyką w projektowaniu niezależnych frameworków testowych E2E i API. Specjalizuję się w Playwright (TypeScript), wdrażaniu rygorystycznych pipeline'ów CI/CD oraz weryfikacji architektury bazodanowej SQL w środowiskach chmurowych.",
    experience: [
      {
        position: "Senior QA Automation Engineer",
        company: "TechFin Solutions Sp. z o.o.",
        location: "Warszawa",
        start_date: "2022-01",
        end_date: "Obecnie",
        highlights: [
          "Zbudowałem od zera framework testów E2E w Playwright i TypeScript, skracając czas weryfikacji regresji o 65%.",
          "Zintegrowałem testy automatyczne z GitHub Actions, blokując wadliwe commity przed wdrożeniem na produkcję.",
          "Zautomatyzowałem weryfikację krytycznych endpointów REST API za pomocą Playwright APIRequestContext i Postman.",
          "Wdrożyłem raportowanie Allure z czytelnymi krokami biznesowymi, eliminując flakiness testów do poziomu poniżej 1%."
        ]
      },
      {
        position: "QA Engineer / Tester Oprogramowania",
        company: "Global Softworks",
        location: "Warszawa",
        start_date: "2020-03",
        end_date: "2021-12",
        highlights: [
          "Przeprowadzałem kompleksowe testy funkcjonalne, regresyjne oraz eksploracyjne platformy transakcyjnej.",
          "Weryfikowałem integralność i spójność danych finansowych w relacyjnych bazach danych PostgreSQL za pomocą zapytań SQL.",
          "Tworzyłem ustrukturyzowane scenariusze i plany testowe w Jira Xray zgodne ze standardami ISTQB."
        ]
      }
    ],
    skills: [
      {
        category: "Test Automation & Core Stack",
        items: ["Playwright", "TypeScript", "JavaScript", "Selenium WebDriver", "Allure Report"]
      },
      {
        category: "API Testing & Databases",
        items: ["REST API", "Postman", "SQL", "PostgreSQL", "JSON Schema"]
      },
      {
        category: "CI/CD & QA Process",
        items: ["GitHub Actions", "Docker", "Git", "Jira (Xray)", "Agile / Scrum"]
      }
    ],
    languages: [
      { language: "Polski", level: "Ojczysty (Native)" },
      { language: "Angielski", level: "Biegły (B2+)" }
    ],
    ...overrides,
  };
}
