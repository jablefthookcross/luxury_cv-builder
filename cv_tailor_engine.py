"""
VitaeCraft AI - CV Synthesis & Tailoring Engine (Etap 2)
Synthesizes a tailored, ATS-optimized CV using the immutable Master Profile baseline
and the structured Job Specification produced by JobExtractor (Etap 1).
"""

import os
import re
import json
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from pathlib import Path

PROMPT_CV_TAILORING = """
Jesteś elitarnym architektem CV dla inżynierów QA i automatyzacji testów.
Twoim zadaniem jest wygenerowanie spójnego merytorycznie, autentycznego profilu CV w formacie JSON, ściśle dopasowanego do przesłanej specyfikacji oferty pracy.

WEJŚCIE:
1. Master Profile (stałe dane kandydata: dane kontaktowe, historia firm, wykształcenie, języki).
2. Job Specification (ustrukturyzowane wymagania oferty: target_role, primary_tech, secondary_tech, testing_types, tools, responsibilities).

WYMAGANIA DOTYCZĄCE WYNIKU:
- target_title: Użyj dokładnie nazwy z job_spec.target_role.
- professional_summary: 45-60 słów. Płynne, eleganckie podsumowanie inżynierskie. 
  • ZAKAZ stosowania szablonowych zwrotów: "w obszarze: [Lista]", "przy użyciu technologii [Lista]", "oraz Metodyka Agile".
  • Podsumowanie musi tworzyć spójną, naturalną narrację o kompetencjach kandydata.
- skills: Zwróć DOKŁADNIE 3 kategorie, każda zawierająca od 4 do 6 precyzyjnych tagów.
  • Kategoria 1 (Automatyzacja & Testy Web / Test Automation & Web Quality): Frameworki testowe i automatyzacja (Selenium, Playwright, TestNG, Appium, Cypress, Testy Webowe).
  • Kategoria 2 (CI/CD, Narzędzia & Zarządzanie / CI/CD, Tools & Management): Jira, Confluence, Git, CI/CD Pipelines, Docker, Agile/Scrum.
  • Kategoria 3 (Testy API & Bazy Danych / API Testing & Databases): Narzędzia i protokoły API (Postman, REST & SOAP API, Swagger, SoapUI, HL7 FHIR) oraz bazy danych (SQL, PostgreSQL).
- work_experience: Zachowaj realne firmy (Benefit Systems S.A., Sii Polska, Euroloan Group) i daty z profilu bazowego. Zredaguj 4-5 mocnych bullet pointów w najnowszej roli (Benefit Systems), według wzorca: Czynność inżynierska ➡️ Narzędzie/Metoda ➡️ Rezultat techniczny/biznesowy.

Zwróć WYŁĄCZNIE obiekt JSON w języku {LANG}:
{
  "target_title": "...",
  "professional_summary": "...",
  "skills": [
    {"category": "Nazwa Kategorii 1", "items": ["tag1", "tag2", "tag3", "tag4", "tag5"]},
    {"category": "Nazwa Kategorii 2", "items": ["tag1", "tag2", "tag3", "tag4", "tag5"]},
    {"category": "Nazwa Kategorii 3", "items": ["tag1", "tag2", "tag3", "tag4", "tag5"]}
  ],
  "work_experience": [
    {
      "company": "Benefit Systems S.A.",
      "role": "Software tester / QA Automation",
      "period": "2022 – Obecnie",
      "location": "Warszawa",
      "highlights": ["punkt 1", "punkt 2", "punkt 3", "punkt 4", "punkt 5"]
    }
  ]
}
"""

POLISH_BASELINE_EXPERIENCE = [
    {
        "company": "Benefit Systems S.A.",
        "role": "Software tester / QA Automation",
        "period": "2022 – Obecnie",
        "location": "Warszawa",
        "highlights": [
            "Projektowanie, rozwój i utrzymanie automatycznych zestawów testów E2E dla modułów webowych w Playwright (TypeScript/JavaScript).",
            "Integracja i uruchamianie testów automatycznych w ramach pipeline'ów CI/CD (GitLab CI / GitHub Actions / Jenkins).",
            "Walidacja interfejsów API (REST & SOAP) przy użyciu Postman i weryfikacja spójności danych za pomocą zapytań SQL.",
            "Projektowanie ustrukturyzowanych scenariuszy testowych w Jira (Xray) oraz raportowanie metryk jakości w zespole Agile."
        ]
    },
    {
        "company": "Sii Polska Sp. z o.o. (Freelance)",
        "role": "Test And Analysis Engineer",
        "period": "2021-09 – 2022-04",
        "location": "Warszawa",
        "highlights": [
            "Przeprowadzanie testów manualnych i funkcjonalnych modułów aplikacji webowych w oparciu o wymagania z backlogu.",
            "Dokumentowanie defektów z jasnymi krokami reprodukcji i zarządzanie błędami w narzędziach Jira (Xray) oraz HP QC / ALM.",
            "Weryfikacja danych w bazach danych z użyciem narzędzia SQL Developer."
        ]
    },
    {
        "company": "Euroloan Group (Freelance)",
        "role": "Software tester",
        "period": "2019-07 – 2021-01",
        "location": "Warszawa",
        "highlights": [
            "Przeprowadzanie kompleksowych testów funkcjonalnych, eksploatacyjnych, UI oraz regresyjnych dla platform cyfrowych.",
            "Projektowanie, wykonywanie i optymalizacja przypadków testowych zgodnych z kryteriami akceptacji.",
            "Dokumentowanie defektów i weryfikacja poprawek błędów."
        ]
    }
]

ENGLISH_BASELINE_EXPERIENCE = [
    {
        "company": "Benefit Systems S.A.",
        "role": "Software tester / QA Automation",
        "period": "2022 – Present",
        "location": "Warsaw, Poland",
        "highlights": [
            "Designing, developing, and maintaining automated E2E test suites for web applications using Playwright (TypeScript/JavaScript).",
            "Integrating and executing automated test suites within CI/CD pipelines (GitLab CI / GitHub Actions / Jenkins).",
            "Validating REST & SOAP APIs using Postman and ensuring data consistency via SQL queries.",
            "Designing structured test scenarios in Jira (Xray) and reporting test metrics across Agile teams."
        ]
    },
    {
        "company": "Sii Polska Sp. z o.o. (Freelance)",
        "role": "Test And Analysis Engineer",
        "period": "2021-09 – 2022-04",
        "location": "Warsaw, Poland",
        "highlights": [
            "Conducted manual and functional testing of web application modules and customer portals based on backlog user stories.",
            "Documented defects with clear reproduction steps and managed issue tracking in Jira (Xray) and HP QC / ALM following Scrum methodology.",
            "Executed backend API validation via Postman and performed data integrity verification using SQL Developer."
        ]
    },
    {
        "company": "Euroloan Group (Freelance)",
        "role": "Software tester",
        "period": "2019-07 – 2021-01",
        "location": "Warsaw, Poland",
        "highlights": [
            "Executed comprehensive UI, functional, exploratory, and regression testing for web and digital platforms.",
            "Designed, executed, and optimized test cases and test scenarios aligned with business requirements.",
            "Documented software defects and verified bug fixes."
        ]
    }
]


EN_TERM_TRANSLATIONS = {
    # Testing Scope & Methodologies
    "Testy Wydajnościowe (Load & Stress)": "Performance Testing (Load & Stress)",
    "Testy Wydajnościowe (Performance)": "Performance Testing",
    "Testy Obciążeniowe (Load Testing)": "Load Testing",
    "Testy Przeciążeniowe (Stress Testing)": "Stress Testing",
    "Testy Obciążeniowe": "Load Testing",
    "Automatyzacja UI & API": "UI & API Test Automation",
    "Automatyzacja & Testy Web": "Test Automation & Web Testing",
    "Automatyzacja & Jakość": "Test Automation & Quality",
    "Testy Manualne & Eksploracyjne": "Manual & Exploratory Testing",
    "Testy Manualne": "Manual Testing",
    "Testy Eksploracyjne": "Exploratory Testing",
    "Testy Funkcjonalne": "Functional Testing",
    "Testy Regresyjne": "Regression Testing",
    "Testy Akceptacyjne (UAT)": "User Acceptance Testing (UAT)",
    "Testy Akceptacyjne UAT": "User Acceptance Testing (UAT)",
    "Testy Integracyjne": "Integration Testing",
    "Testy Integracyjne SIT": "System Integration Testing (SIT)",
    "Testy Aplikacji Webowych": "Web Application Testing",
    "Testy Aplikacji Mobilnych (iOS/Android)": "Mobile Testing (iOS & Android)",
    "Testowanie iOS": "iOS Testing",
    "Testowanie Android": "Android Testing",
    "Testy Użyteczności (Usability)": "Usability Testing",
    "Testy Bezpieczeństwa (Security)": "Security Testing",
    "Testy Dostępności (WCAG / a11y)": "Accessibility Testing (WCAG)",
    "Testy Dostępności (WCAG)": "Accessibility Testing (WCAG)",
    "Scenariusze & Przypadki Testowe": "Test Scenarios & Test Cases",
    "Plany Testów": "Test Planning & Strategies",
    "Raporty z Testów": "Test Reporting & Quality Metrics",
    "Dokumentacja Testowa (Plany i Raporty)": "Test Documentation & Reports",
    "Dokumentacja Testowa & Plany": "Test Plans & Documentation",
    "Zgłaszanie i Śledzenie Błędów": "Defect Tracking & Reporting",
    "Certyfikat ISTQB": "ISTQB Certification",
    "Metodyka Agile / Scrum": "Agile / Scrum Methodology",
    "Architektura Mikroserwisowa": "Microservices Architecture",
    
    # Tools, CI/CD & Databases
    "SQL (Weryfikacja Danych)": "SQL (Database Verification)",
    "RabbitMQ (Kolejki Wiadomości)": "RabbitMQ (Message Queuing)",
    "Elastic Stack (ELK)": "Elastic Stack (ELK Logs)",
    "Kibana (Analiza Logów)": "Kibana (Log Analysis)",
    "Środowiska Linux / Windows OS": "Linux & Windows OS Environments",
    "Linux OS": "Linux OS",
    "Windows OS": "Windows OS",
    "Postman (API Testing)": "Postman (API Testing)",
    "Postman (Testowanie API)": "Postman (API Testing)",
    "CI/CD Pipelines": "CI/CD Pipelines",
    "Sentry (Error Monitoring)": "Sentry (Error Monitoring)",
    "Appium (Mobile Automation)": "Appium (Mobile Automation)",
    "Selenoid / Selenium Grid": "Selenoid / Selenium Grid",
    "Testy API (REST & SOAP)": "REST & SOAP API Testing",
    "Testy API": "API Testing",
    "Testy Aplikacji Mobilnych": "Mobile Application Testing",
    "Usługi SOAP": "SOAP Web Services",
    "Swagger / OpenAPI": "Swagger / OpenAPI"
}

ROLE_EN_TRANSLATIONS = {
    "Tester Aplikacji Webowych": "Web Application QA Engineer",
    "Tester Oprogramowania": "Software QA Engineer",
    "Starszy Tester Oprogramowania": "Senior Software QA Engineer",
    "Inżynier Testów": "QA Test Engineer",
    "Inżynier Automatyzacji Testów": "QA Automation Engineer",
    "Specjalista ds. Zapewnienia Jakości": "QA Specialist",
    "Tester Manualny": "Manual QA Tester",
    "Specjalista QA": "QA Specialist"
}

def translate_term(term: str, is_en: bool) -> str:
    if not is_en:
        return term
    if term in EN_TERM_TRANSLATIONS:
        return EN_TERM_TRANSLATIONS[term]
    
    t = term
    t = re.sub(r'^Testy\s+Aplikacji\s+Webowych', 'Web Application Testing', t, flags=re.IGNORECASE)
    t = re.sub(r'^Testy\s+Aplikacji\s+Mobilnych', 'Mobile Application Testing', t, flags=re.IGNORECASE)
    t = re.sub(r'^Testy\s+API', 'API Testing', t, flags=re.IGNORECASE)
    t = re.sub(r'^Testy\s+', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\(Weryfikacja Danych\)', '(Database Verification)', t, flags=re.IGNORECASE)
    t = re.sub(r'\(Standard Medyczny\)', '(Healthcare Standard)', t, flags=re.IGNORECASE)
    t = re.sub(r'\(Kolejki Wiadomości\)', '(Message Queuing)', t, flags=re.IGNORECASE)
    t = re.sub(r'\(Analiza Logów\)', '(Log Analysis)', t, flags=re.IGNORECASE)
    t = re.sub(r'\(Zarządzanie Testami\)', '(Test Management)', t, flags=re.IGNORECASE)
    t = re.sub(r'\(Monitorowanie Błędów\)', '(Error Monitoring)', t, flags=re.IGNORECASE)
    t = re.sub(r'\(Automatyzacja Mobilna\)', '(Mobile Automation)', t, flags=re.IGNORECASE)
    t = re.sub(r'^Metodyka\s+', '', t, flags=re.IGNORECASE)
    return t.strip()


def is_skill_redundant(item: str, already_selected: List[str]) -> bool:
    item_norm = re.sub(r'[^a-zA-Z0-9]', '', item.lower())
    item_lower = item.lower()
    
    CLUSTERS = [
        {"rest & soap api", "rest api", "soap api", "testy api (rest & soap)", "testy api", "api testing", "rest & soap api testing"},
        {"mobile testing (ios & android)", "testy aplikacji mobilnych (ios/android)", "testowanie ios", "testowanie android", "ios testing", "android testing", "mobile testing", "mobile application testing"},
        {"ci/cd pipelines", "ci/cd", "ci / cd", "continuous integration"},
        {"selenium webdriver", "selenium"},
        {"sql (weryfikacja danych)", "sql (database verification)", "sql", "bazy danych sql", "sql databases"},
        {"postgresql", "postgresql / oracle db", "postgres", "oracle db"},
        {"postman", "postman (api testing)", "postman (testowanie api)"},
        {"scenariusze & przypadki testowe", "przypadki testowe", "scenariusze testowe", "test scenarios & test cases", "test scenarios", "test cases"},
        {"metodyka agile / scrum", "agile / scrum methodology", "agile", "scrum"}
    ]
    
    for existing in already_selected:
        ex_norm = re.sub(r'[^a-zA-Z0-9]', '', existing.lower())
        if item_norm == ex_norm:
            return True
            
        ex_lower = existing.lower()
        for cluster in CLUSTERS:
            if (item_lower in cluster or any(item_norm == re.sub(r'[^a-zA-Z0-9]', '', c) for c in cluster)) and \
               (ex_lower in cluster or any(ex_norm == re.sub(r'[^a-zA-Z0-9]', '', c) for c in cluster)):
                return True
                
    return False


class CVTailorEngine:
    @staticmethod
    def tailor(master_profile: Dict[str, Any], job_spec: Dict[str, Any], lang: str = "pl", gemini_key: str = "", provider: str = "auto") -> Dict[str, Any]:
        """
        Main tailoring entry point.
        Combines Master Profile + Job Spec to generate tailored CV data in memory.
        """
        clean_master = json.loads(json.dumps(master_profile))
        api_key = gemini_key or os.environ.get("GEMINI_API_KEY", "")

        if provider in ["gemini", "auto"] and api_key.strip():
            try:
                gemini_tailored = CVTailorEngine._tailor_with_gemini(clean_master, job_spec, lang=lang, api_key=api_key.strip())
                if gemini_tailored and gemini_tailored.get("skills"):
                    return CVTailorEngine._merge_and_sanitize(clean_master, gemini_tailored, job_spec, lang=lang)
            except Exception as e:
                print(f"[CVTailorEngine] Gemini tailoring failed: {e}. Falling back to Rule-Based Synthesis.")

        return CVTailorEngine._tailor_with_nlp(clean_master, job_spec, lang=lang)

    @staticmethod
    def _tailor_with_gemini(master_profile: Dict[str, Any], job_spec: Dict[str, Any], lang: str, api_key: str) -> Dict[str, Any]:
        """Calls Gemini Flash API for synthesis."""
        models_to_try = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
        prompt = PROMPT_CV_TAILORING.replace("{LANG}", "English" if lang == "en" else "Polski")
        input_data = {
            "master_profile": {
                "personal_info": master_profile.get("personal_info", {}),
                "experience": master_profile.get("experience", []),
                "education": master_profile.get("education", []),
                "languages": master_profile.get("languages", [])
            },
            "job_spec": job_spec
        }

        last_error = None
        for model in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {"text": f"{prompt}\n\nDANE WEJŚCIOWE:\n{json.dumps(input_data, ensure_ascii=False, indent=2)}"}
                        ]
                    }
                ],
                "generationConfig": {
                    "response_mime_type": "application/json",
                    "temperature": 0.1,
                    "max_output_tokens": 2048
                }
            }

            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            try:
                with urllib.request.urlopen(req, timeout=14) as response:
                    raw_resp = response.read().decode("utf-8")
                    data = json.loads(raw_resp)
                    text_content = data["candidates"][0]["content"]["parts"][0]["text"]
                    return json.loads(text_content)
            except Exception as e:
                last_error = e
                continue

        raise RuntimeError(f"All Gemini models failed in tailoring: {last_error}")

    @staticmethod
    def _tailor_with_nlp(master_profile: Dict[str, Any], job_spec: Dict[str, Any], lang: str = "pl") -> Dict[str, Any]:
        """
        Deterministic, high-accuracy QA synthesis engine.
        Translates Job Spec into coherent 3-category skills, summary, and tailored highlights.
        """
        is_en = (lang == "en")
        tailored = json.loads(json.dumps(master_profile))

        # 1. Target Role Title
        raw_title = job_spec.get("target_role") or ("Senior QA Engineer" if is_en else "Senior Software QA Specialist")
        if is_en:
            target_title = ROLE_EN_TRANSLATIONS.get(raw_title, raw_title)
        else:
            target_title = raw_title

        if "personal_info" not in tailored:
            tailored["personal_info"] = {}
        tailored["personal_info"]["title"] = target_title

        # Languages section lock
        if is_en:
            tailored["languages"] = [
                {"language": "Polish", "level": "Native"},
                {"language": "English", "level": "Full Professional (C2)"}
            ]
        else:
            tailored["languages"] = [
                {"language": "Polski", "level": "Ojczysty (Native)"},
                {"language": "Angielski", "level": "Biegły (Professional)"}
            ]

        # 2. Extract tools and categories
        primary_tech = [translate_term(t, is_en) for t in job_spec.get("primary_technologies", [])]
        secondary_tech = [translate_term(t, is_en) for t in job_spec.get("secondary_technologies", [])]
        testing_types = [translate_term(t, is_en) for t in job_spec.get("testing_types", [])]
        tools = [translate_term(t, is_en) for t in job_spec.get("tools", [])]

        # Categorize into 3 distinct logical groups
        has_automation = any(k in str(primary_tech + testing_types).lower() for k in ["playwright", "selenium", "jmeter", "cypress", "testng", "appium", "allure", "c#", "automatyzacja", "automation", "skrypty"])
        has_performance = any("jmeter" in str(primary_tech).lower() or "k6" in str(primary_tech).lower() or "performance" in str(testing_types).lower() or "wydajno" in str(testing_types).lower() for _ in [1])
        has_cicd = any(k in str(secondary_tech + tools).lower() for k in ["docker", "jenkins", "gitlab", "github", "ci/cd", "continuous integration"])
        is_pure_api_role = not has_automation and any(k in str(primary_tech + testing_types).lower() for k in ["soapui", "postman", "hl7", "rest & soap"])

        selected_skills: List[str] = []
        API_KW = ["postman", "soapui", "rest & soap", "soap api", "rest api", "swagger", "openapi", "graphql", "grpc", "hl7", "fhir", "api testing"]

        # Category 1: Testing Scope & Core Automation / Web / API
        if has_performance:
            cat1_name = "Test Automation & Performance" if is_en else "Automatyzacja & Performance"
        elif is_pure_api_role:
            cat1_name = "API Testing & Integration" if is_en else "Testy API & Integracyjne"
        elif has_automation:
            cat1_name = "Test Automation & Web Quality" if is_en else "Automatyzacja & Testy Web"
        else:
            cat1_name = "Manual & Functional Testing" if is_en else "Testowanie Manualne & Jakość"

        DB_KW = ["sql", "oracle", "postgre", "dbeaver", "database"]

        cat1_items = []
        for item in (primary_tech + testing_types):
            is_api = any(kw in item.lower() for kw in API_KW)
            is_db = any(kw in item.lower() for kw in DB_KW)
            if not is_pure_api_role and (is_api or is_db):
                continue  # Route API and Database items to Category 3
            if "istqb" not in item.lower() and not is_skill_redundant(item, selected_skills) and len(cat1_items) < 6:
                cat1_items.append(item)
                selected_skills.append(item)
        if len(cat1_items) < 4:
            fallback_c1 = ["Selenium WebDriver", "Web Application Testing", "Functional Testing", "Test Scenarios & Test Cases"] if is_en else ["Selenium WebDriver", "Testy Aplikacji Webowych", "Testy Funkcjonalne", "Scenariusze & Przypadki Testowe"]
            for fb in fallback_c1:
                if not is_skill_redundant(fb, selected_skills) and len(cat1_items) < 5:
                    cat1_items.append(fb)
                    selected_skills.append(fb)

        # Category 2: Management, CI/CD, Tools & Methodologies
        if has_cicd:
            cat2_name = "CI/CD, Tools & Management" if is_en else "CI/CD, Narzędzia & Zarządzanie"
            fallback_c2 = ["Jira (Xray)", "Git", "Confluence", "CI/CD Pipelines", "Docker", "Agile / Scrum Methodology"] if is_en else ["Jira (Xray)", "Git", "Confluence", "CI/CD Pipelines", "Docker", "Metodyka Agile / Scrum"]
        else:
            cat2_name = "Test Management & Tools" if is_en else "Zarządzanie Testami & Narzędzia"
            fallback_c2 = ["Jira (Xray)", "Confluence", "Test Documentation & Reports", "ISTQB Certification", "Agile / Scrum Methodology"] if is_en else ["Jira (Xray)", "Confluence", "Dokumentacja Testowa (Plany i Raporty)", "Certyfikat ISTQB", "Metodyka Agile / Scrum"]

        cat2_items = []
        for item in (secondary_tech + tools):
            is_api = any(kw in item.lower() for kw in API_KW)
            if is_api:
                continue  # Route API items to Category 3
            if not is_skill_redundant(item, selected_skills) and len(cat2_items) < 6:
                cat2_items.append(item)
                selected_skills.append(item)
        for fb in fallback_c2:
            if not is_skill_redundant(fb, selected_skills) and len(cat2_items) < 5:
                cat2_items.append(fb)
                selected_skills.append(fb)

        # Category 3: API, Diagnostics, Databases & Secondary Tools
        cat3_name = "API Testing & Databases" if is_en else "Testy API & Bazy Danych"
        cat3_items = []
        
        # Priority 1: Extracted API and Database tools
        for item in (primary_tech + secondary_tech + tools):
            is_api_or_db = any(kw in item.lower() for kw in API_KW + ["sql", "oracle", "postgre", "dbeaver", "sentry", "devtools"])
            if is_api_or_db and not is_skill_redundant(item, selected_skills) and len(cat3_items) < 6:
                cat3_items.append(item)
                selected_skills.append(item)

        cat3_candidates = [
            "SQL (Database Verification)" if is_en else "SQL (Weryfikacja Danych)",
            "REST & SOAP API Testing" if is_en else "REST & SOAP API",
            "Postman (API Testing)" if is_en else "Postman",
            "Swagger / OpenAPI",
            "PostgreSQL / Oracle DB",
            "DBeaver"
        ]
        for cand in cat3_candidates:
            if not is_skill_redundant(cand, selected_skills) and len(cat3_items) < 6:
                cat3_items.append(cand)
                selected_skills.append(cand)

        tailored["skills"] = [
            {"category": cat1_name, "items": cat1_items[:6]},
            {"category": cat2_name, "items": cat2_items[:6]},
            {"category": cat3_name, "items": cat3_items[:6]}
        ]

        # 3. Dynamic Summary Synthesis (No AI slop or bracket lists)
        exp_phrase = "5+ years of" if is_en else "ponad 5-letnim"
        
        # 3a. Automation Frameworks & Languages
        AUTO_FRAMEWORKS_KW = ["playwright", "selenium", "appium", "cypress", "testng", "junit", "pytest", "robot framework", "c#", "typescript", "python", "javascript", "java"]
        auto_tech_list = []
        for t in (primary_tech + secondary_tech + tools):
            if any(kw in t.lower() for kw in AUTO_FRAMEWORKS_KW) and "istqb" not in t.lower():
                clean_t = re.sub(r'\s*\([^)]*\)', '', t).strip()
                if clean_t and clean_t not in auto_tech_list:
                    auto_tech_list.append(clean_t)
        if not auto_tech_list:
            auto_tech_list = ["Selenium WebDriver", "Playwright"] if is_en else ["Selenium WebDriver", "Playwright"]
        auto_tech_str = ", ".join(auto_tech_list[:3])

        # 3b. CI/CD & Cloud Infrastructure (Docker, Kubernetes, AWS, Azure, Jenkins, GitLab CI)
        CI_CLOUD_KW = ["docker", "kubernetes", "k8s", "aws", "azure", "jenkins", "gitlab", "github", "ci/cd", "continuous integration", "cloud"]
        ci_cloud_list = []
        for t in (secondary_tech + tools + primary_tech):
            if any(kw in t.lower() for kw in CI_CLOUD_KW) and "istqb" not in t.lower():
                clean_t = re.sub(r'\s*\([^)]*\)', '', t).strip()
                if clean_t and clean_t not in ci_cloud_list:
                    ci_cloud_list.append(clean_t)
        
        if ci_cloud_list:
            ci_str_en = f"integrating test execution across CI/CD and cloud environments ({', '.join(ci_cloud_list[:2])}), "
            ci_str_pl = f"integracji procesów testowych ze środowiskami CI/CD i chmurowymi ({', '.join(ci_cloud_list[:2])}), "
        else:
            ci_str_en = "integrating automated workflows into CI/CD pipelines, " if has_cicd else ""
            ci_str_pl = "integracji procesów testowych z pipeline'ami CI/CD, " if has_cicd else ""

        # 3c. Defect Management Tools (Strictly Jira, Confluence, Xray, Azure DevOps Test Plans - NEVER cloud/Docker)
        DEFECT_KW = ["jira", "confluence", "xray", "azure devops test plans", "azure devops", "bugzilla", "hp qc", "alm", "zephyr", "qase"]
        defect_list = []
        for t in tools:
            # Explicitly exclude pure clouds or containers from defect management
            if any(kw in t.lower() for kw in ["aws", "docker", "kubernetes", "k8s", "linux", "windows"]):
                continue
            if any(kw in t.lower() for kw in DEFECT_KW):
                clean_t = re.sub(r'\s*\([^)]*\)', '', t).strip()
                if clean_t and clean_t not in defect_list:
                    defect_list.append(clean_t)
        defect_tools_str = ", ".join(defect_list[:2]) or ("Jira (Xray) and Confluence" if is_en else "Jira (Xray) i Confluence")

        has_istqb = any("istqb" in str(x).lower() for x in (primary_tech + testing_types + tools))
        istqb_str_pl = " Posiada certyfikat ISTQB." if has_istqb else ""
        istqb_str_en = " Certified in ISTQB standards." if has_istqb else ""

        # Summary synthesis with role focus
        all_spec_text = " ".join([target_title, str(primary_tech), str(secondary_tech), str(testing_types), str(tools), str(job_spec.get("key_responsibilities", []))]).lower()
        is_mobile = any(k in all_spec_text for k in ["mobile", "ios", "android", "appium", "aosp", "mobiln"])
        is_backend_manual_api = (
            any(k in all_spec_text for k in ["manual", "backend", "api", "soap", "rest", "postman", "swagger", "sql", "database", "baza danych", "kibana", "grafana", "dahlia", "logs", "logi"])
            and not any(k in target_title.lower() for k in ["automation", "automatyzujący", "sdet", "developer in test"])
        )

        if is_en:
            if is_backend_manual_api:
                summary = (
                    f"{target_title} with {exp_phrase} experience specializing in functional, integration, REST & SOAP API testing, and SQL database validation. "
                    f"Proficient in designing structured test scenarios in {defect_tools_str}, system log analysis (Kibana, Grafana), and defect lifecycle management. "
                    f"Possesses working knowledge of test automation frameworks ({auto_tech_str}).{istqb_str_en}"
                )
            else:
                summary = (
                    f"{target_title} with {exp_phrase} experience specializing in web application quality assurance and test automation. "
                    f"Proficient in designing structured verification strategies, developing automated test suites utilizing {auto_tech_str}, "
                    f"{ci_str_en}and defect management in {defect_tools_str}. "
                    f"Skilled in backend data validation using SQL queries.{istqb_str_en}"
                )
        else:
            if is_backend_manual_api:
                summary = (
                    f"{target_title} z {exp_phrase} doświadczeniem w testowaniu funkcjonalnym, integracyjnym, API (REST & SOAP) oraz weryfikacji baz danych SQL. "
                    f"Specjalizuje się w projektowaniu ustrukturyzowanych scenariuszy testowych w {defect_tools_str}, analizie logów aplikacyjnych (Kibana, Grafana) oraz sprawnym raportowaniu defektów. "
                    f"Posiada praktyczną znajomość automatyzacji testów ({auto_tech_str}).{istqb_str_pl}"
                )
            else:
                summary = (
                    f"{target_title} z {exp_phrase} doświadczeniem w testowaniu i zapewnianiu jakości oprogramowania. "
                    f"Specjalizuje się w projektowaniu ustrukturyzowanych strategii weryfikacji, automatyzacji testów w oparciu o {auto_tech_str} "
                    f"{ci_str_pl}oraz sprawnym raportowaniu defektów w {defect_tools_str}. "
                    f"Biegle waliduje spójność danych z wykorzystaniem relacyjnych baz danych SQL.{istqb_str_pl}"
                )

        tailored["summary"] = summary

        # 4. Dynamic Work Experience Synthesis (Benefit Systems role with Smart Prioritization)
        raw_exp = ENGLISH_BASELINE_EXPERIENCE if is_en else POLISH_BASELINE_EXPERIENCE
        tailored_exp = []

        AUTO_FRAMEWORKS_KW = ["playwright", "selenium", "appium", "cypress", "testng", "junit", "pytest", "robot framework", "c#", "typescript", "python"]
        auto_frameworks = []
        for t in (primary_tech + secondary_tech + tools):
            if any(kw in t.lower() for kw in AUTO_FRAMEWORKS_KW) and "istqb" not in t.lower():
                clean_t = re.sub(r'\s*\([^)]*\)', '', t).strip()
                if clean_t and clean_t not in auto_frameworks:
                    auto_frameworks.append(clean_t)
        if not auto_frameworks:
            auto_frameworks = ["Playwright", "Selenium WebDriver", "Appium"] if is_en else ["Playwright", "Selenium WebDriver", "Appium"]

        for job in raw_exp:
            job_copy = json.loads(json.dumps(job))
            if "Benefit" in job_copy.get("company", ""):
                bullets = []
                if is_backend_manual_api:
                    # Priority 1: API, SQL & Logs
                    bullets.append(
                        "Validating REST & SOAP web APIs using Postman and Swagger, verifying data integrity across SQL databases, and analyzing application logs in Kibana and Grafana."
                        if is_en else
                        "Walidacja usług sieciowych REST & SOAP API przy użyciu narzędzi Postman oraz Swagger, weryfikacja spójności danych na relacyjnych bazach SQL oraz analiza logów aplikacyjnych w Kibana i Grafana."
                    )
                    # Priority 2: Functional & Backend Integration
                    bullets.append(
                        "Conducting thorough functional, integration, and exploratory testing across backend services and web platforms."
                        if is_en else
                        "Przeprowadzanie testów integracyjnych, funkcjonalnych oraz eksploracyjnych systemów backendowych i platform webowych."
                    )
                    # Priority 3: Test Planning & Documentation
                    bullets.append(
                        "Designing structured test plans, comprehensive test scenarios, and project documentation in Jira (Xray) and Confluence in Agile/Scrum teams."
                        if is_en else
                        "Projektowanie planów testów, scenariuszy testowych oraz kompleksowej dokumentacji w Jira (Xray) i Confluence w zespole Agile/Scrum."
                    )
                    # Priority 4: Defect Tracking & Root Cause Analysis
                    bullets.append(
                        "Managing defect triage lifecycles, performing root cause analysis (RCA), and verifying developer bug fixes."
                        if is_en else
                        "Prowadzenie procesu obsługi defektów, analiza przyczyn źródłowych błędów (RCA) oraz retesty zgłoszeń deweloperskich."
                    )
                    # Priority 5: Test Automation Support
                    bullets.append(
                        f"Maintaining and supporting automated regression test suites utilizing {', '.join(auto_frameworks[:2])}."
                        if is_en else
                        f"Utrzymanie i rozbudowa automatycznych skryptów testowych w oparciu o {', '.join(auto_frameworks[:2])} na potrzeby testów regresyjnych."
                    )
                elif is_mobile:
                    # Priority 1: Mobile Testing
                    bullets.append(
                        "Conducting comprehensive mobile application testing across iOS and Android platforms utilizing diagnostic tools and device emulators."
                        if is_en else
                        "Przeprowadzanie kompleksowych testów aplikacji mobilnych na platformach iOS i Android z wykorzystaniem narzędzi diagnostycznych i emulatorów."
                    )
                    # Priority 2: Automation E2E
                    bullets.append(
                        f"Designing and developing automated E2E test suites utilizing {', '.join(auto_frameworks[:3])}."
                        if is_en else
                        f"Projektowanie i wdrażanie automatycznych zestawów testowych E2E z wykorzystaniem {', '.join(auto_frameworks[:3])}."
                    )
                    # Priority 3: CI/CD
                    bullets.append(
                        "Integrating mobile and web test suites into continuous delivery pipelines (GitLab CI / CI/CD Pipelines)."
                        if is_en else
                        "Integracja testów mobilnych i webowych w procesach ciągłego dostarczania oprogramowania (CI/CD Pipelines)."
                    )
                    # Priority 4: API & SQL
                    bullets.append(
                        "Validating mobile backend REST/SOAP APIs in Postman and ensuring data consistency via SQL database queries."
                        if is_en else
                        "Walidacja usług backendowych REST/SOAP API w Postmanie oraz weryfikacja spójności danych za pomocą zapytań SQL."
                    )
                    # Priority 5: Defect Tracking
                    bullets.append(
                        "Managing mobile defect triage workflows, conducting root cause analysis, and collaborating within Agile Scrum teams in Jira."
                        if is_en else
                        "Prowadzenie procesu obsługi defektów aplikacji mobilnych, analiza błędów oraz współpraca w zespole Scrum z wykorzystaniem narzędzi Jira i Confluence."
                    )
                else:
                    # Priority 1: Pure Test Automation (Web)
                    bullets.append(
                        f"Designing and implementing scalable automated E2E test suites and verification workflows utilizing {', '.join(auto_frameworks[:3])}."
                        if is_en else
                        f"Projektowanie i wdrażanie automatycznych zestawów testowych E2E oraz strategii weryfikacji z wykorzystaniem {', '.join(auto_frameworks[:3])}."
                    )
                    # Priority 2: Functional / Exploratory
                    bullets.append(
                        "Conducting thorough functional, integration, and exploratory testing across enterprise web platforms."
                        if is_en else
                        "Wykonywanie testów funkcjonalnych, integracyjnych i eksploracyjnych na platformach webowych i systemach cyfrowych."
                    )
                    # Priority 3: CI/CD
                    if secondary_tech or "docker" in str(tools).lower() or "jenkins" in str(tools).lower() or has_cicd:
                        ci_tools = [t for t in (secondary_tech + tools) if any(k in t.lower() for k in ["docker", "jenkins", "gitlab", "github", "ci"])]
                        ci_str = ", ".join(ci_tools[:2]) or ("CI/CD Pipelines" if is_en else "procesów CI/CD")
                        bullets.append(
                            f"Embedding automated test execution into continuous delivery pipelines utilizing {ci_str}."
                            if is_en else
                            f"Integracja testów w procesach ciągłego dostarczania oprogramowania (CI/CD) w oparciu o {ci_str}."
                        )
                    # Priority 4: API & Database
                    bullets.append(
                        "Validating REST/SOAP web APIs using Postman and ensuring backend data consistency across SQL relational databases."
                        if is_en else
                        "Walidacja usług sieciowych REST/SOAP API przy użyciu narzędzia Postman oraz weryfikacja spójności danych na relacyjnych bazach danych SQL."
                    )
                    # Priority 5: Defect Tracking & Agile
                    bullets.append(
                        "Managing defect triage workflows, conducting root cause analysis, and collaborating within Agile Scrum teams using Jira and Confluence."
                        if is_en else
                        "Prowadzenie procesu obsługi defektów, analiza przyczyn źródłowych błędów oraz współpraca w zespole Scrum z wykorzystaniem narzędzi Jira i Confluence."
                    )

                job_copy["highlights"] = bullets[:5]

            tailored_exp.append(job_copy)

        tailored["experience"] = tailored_exp
        return tailored

    @staticmethod
    def _merge_and_sanitize(master: Dict[str, Any], gemini_output: Dict[str, Any], job_spec: Dict[str, Any], lang: str) -> Dict[str, Any]:
        """Merges Gemini output with master profile guarantees."""
        result = json.loads(json.dumps(master))

        # Title
        title = gemini_output.get("target_title") or job_spec.get("target_role") or result.get("personal_info", {}).get("title")
        if "personal_info" not in result:
            result["personal_info"] = {}
        result["personal_info"]["title"] = title

        # Summary
        if gemini_output.get("professional_summary"):
            result["summary"] = gemini_output["professional_summary"]

        # Skills
        if gemini_output.get("skills") and isinstance(gemini_output["skills"], list):
            sanitized_skills = []
            used = set()
            for cat in gemini_output["skills"]:
                c_name = cat.get("category", "").strip()
                c_items = []
                for it in cat.get("items", []):
                    it_clean = it.strip()
                    it_key = re.sub(r'[^a-zA-Z0-9]', '', it_clean.lower())
                    if it_key and it_key not in used and it_clean.lower() != c_name.lower() and len(c_items) < 6:
                        c_items.append(it_clean)
                        used.add(it_key)
                if c_items:
                    sanitized_skills.append({"category": c_name, "items": c_items})
            if len(sanitized_skills) == 3:
                result["skills"] = sanitized_skills

        # Experience
        if gemini_output.get("work_experience") and isinstance(gemini_output["work_experience"], list):
            for g_job in gemini_output["work_experience"]:
                g_comp = g_job.get("company", "")
                for m_job in result.get("experience", []):
                    if g_comp.lower() in m_job.get("company", "").lower() and g_job.get("highlights"):
                        m_job["highlights"] = g_job["highlights"][:5]

        return result
