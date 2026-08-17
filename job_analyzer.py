"""
VitaeCraft AI - Job Analyzer & Dynamic Archetype Engine
Analyzes job descriptions using a universal Archetype Weighting Matrix and it_terms_catalog.json.
Eliminates hardcoded company rules in favor of dynamic mathematical archetype classification.
"""

import re
import json
from typing import Dict, Any, List, Set, Tuple
from pathlib import Path

APP_DIR = Path(__file__).parent
CATALOG_PATH = APP_DIR / "it_terms_catalog.json"

# Universal Archetype Definitions
ARCHETYPES = {
    "mobile": {
        "id": "mobile",
        "name_pl": "Testowanie Mobilne & Proxy",
        "name_en": "Mobile & Proxy Testing",
        "primary_category_pl": "Testy Mobilne & API",
        "primary_category_en": "Mobile & API Testing",
        "default_title_pl": "Senior QA Specialist (Mobile & Web)",
        "default_title_en": "Senior QA Specialist (Mobile & Web)",
        "keywords": [
            "mobile", "mobilne", "mobilnych", "android", "ios", "xcode", "android studio",
            "proxyman", "charles", "burp", "burp suite", "appium", "logcat", "usability",
            "testy użyteczności", "aosp", "mobile testing"
        ],
        "core_skills_pl": [
            "Testy Aplikacji Mobilnych (iOS/Android)", "Proxyman / Burp Suite", "Testowanie API (Postman)",
            "Testy Manualne & Eksploracyjne", "Testy Użyteczności (Usability)", "Plany Testów & Scenariusze"
        ],
        "core_skills_en": [
            "Mobile Testing (iOS/Android)", "Proxyman / Burp Suite", "API Testing (Postman)",
            "Manual & Exploratory Testing", "Usability Testing", "Test Plans & Scenarios"
        ]
    },
    "backend_api": {
        "id": "backend_api",
        "name_pl": "Backend, API & Bazy Danych",
        "name_en": "Backend, API & Databases",
        "primary_category_pl": "REST & SOAP API",
        "primary_category_en": "REST & SOAP API",
        "default_title_pl": "Senior QA Engineer (Backend & API)",
        "default_title_en": "Senior QA Engineer (Backend & API)",
        "keywords": [
            "soapui", "postman", "rest api", "soap api", "microservices", "architektura mikroserwisowa",
            "elasticsearch", "kibana", "postgresql", "oracle", "mysql", "dbeaver",
            "sql developer", "bpm", "tia", "integration", "integracyjne", "backend", "api testing"
        ],
        "core_skills_pl": [
            "REST & SOAP API", "SoapUI / Postman", "Architektura Mikroserwisowa",
            "SQL (Złożone Zapytania, JOIN)", "PostgreSQL / Oracle", "Elasticsearch (Analiza Logów)"
        ],
        "core_skills_en": [
            "REST & SOAP API", "SoapUI / Postman", "Microservices Architecture",
            "SQL (Advanced Queries, JOINs)", "PostgreSQL / Oracle", "Elasticsearch (Log Analysis)"
        ]
    },
    "automation": {
        "id": "automation",
        "name_pl": "Automatyzacja & Performance",
        "name_en": "Automation & Performance",
        "primary_category_pl": "Automatyzacja Testów & Performance",
        "primary_category_en": "Test Automation & Performance",
        "default_title_pl": "QA Automation & Performance Engineer",
        "default_title_en": "QA Automation & Performance Engineer",
        "keywords": [
            "playwright", "selenium", "selenoid", "cypress", "c#", "jmeter", "jenkins", "docker",
            "typescript", "javascript", "python", "ci/cd", "gitlab ci", "github actions", "pom",
            "page object model", "automation", "automatyzacja", "skrypty testowe", "e2e",
            "performance testing", "load testing", "stress testing", "testy wydajnościowe",
            "rabbitmq", "elastic stack", "ui & api", "ui and api"
        ],
        "core_skills_pl": [
            "Playwright (TypeScript/C#)", "Selenium / Selenoid", "Apache JMeter (Performance)",
            "Automatyzacja UI & API", "Page Object Model (POM)", "Docker & Jenkins CI/CD"
        ],
        "core_skills_en": [
            "Playwright (TypeScript/C#)", "Selenium / Selenoid", "Apache JMeter (Performance)",
            "UI & API Test Automation", "Page Object Model (POM)", "Docker & Jenkins CI/CD"
        ]
    },
    "management_process": {
        "id": "management_process",
        "name_pl": "Zarządzanie Testami & SDLC",
        "name_en": "Test Management & SDLC",
        "primary_category_pl": "Zarządzanie Testami & SDLC",
        "primary_category_en": "Test Management & SDLC",
        "default_title_pl": "Senior Software QA Specialist",
        "default_title_en": "Senior Software QA Specialist",
        "keywords": [
            "azure devops", "azure devops test plans", "test plans", "xray", "qase",
            "sdlc", "test management", "dokumentacja testowa", "sharepoint",
            "proces testowy", "zarządzanie jakością"
        ],
        "core_skills_pl": [
            "Zarządzanie Testami & SDLC", "Azure DevOps Test Plans", "Jira (Xray) & Confluence",
            "Standardy ISTQB", "Testy Akceptacyjne (UAT)", "Dokumentacja Testowa & Plany"
        ],
        "core_skills_en": [
            "Test Management & SDLC", "Azure DevOps Test Plans", "Jira (Xray) & Confluence",
            "ISTQB Standards", "Acceptance Testing (UAT)", "Test Plans & Documentation"
        ]
    },
    "manual_qa": {
        "id": "manual_qa",
        "name_pl": "Testy Manualne & QA",
        "name_en": "Manual & Functional QA",
        "primary_category_pl": "Testowanie & Jakość",
        "primary_category_en": "Testing & Quality",
        "default_title_pl": "Tester Oprogramowania / Specjalista QA",
        "default_title_en": "Software QA Tester",
        "keywords": [
            "tester oprogramowania", "testy oprogramowania", "testowanie oprogramowania", "tester",
            "manual software tester", "manual tester", "tester manualny", "testy manualne",
            "testy funkcjonalne", "testów funkcjonalnych", "testy regresyjne", "testów regresyjnych",
            "przypadki testowe", "przypadków testowych", "scenariusze testowe", "scenariuszy",
            "zgłaszanie błędów", "analiza błędów", "istqb", "certyfikat istqb", "jira", "sql",
            "hp qc", "alm", "katalon", "utp", "zephyr", "devtools", "bankowość", "bank",
            "logistyczne", "aplikacje biznesowe", "kpi", "retail banking", "bankowość detaliczna"
        ],
        "core_skills_pl": [
            "Testy Manualne", "Testy Funkcjonalne & Regresyjne", "Scenariusze & Przypadki Testowe",
            "Certyfikat ISTQB", "Zgłaszanie i Śledzenie Błędów"
        ],
        "core_skills_en": [
            "Manual Testing", "Functional & Regression Testing", "Test Plans & Scenarios",
            "ISTQB Standards", "Defect Tracking & Reporting"
        ]
    }
}

def load_catalog_terms() -> Dict[str, str]:
    terms = {}
    if CATALOG_PATH.exists():
        try:
            with open(CATALOG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                for domain, items in data.items():
                    if isinstance(items, dict):
                        for kw, label in items.items():
                            terms[kw.lower()] = label
            return terms
        except Exception:
            pass
    return {
        "manual testing": "Testy Manualne", "postman": "Postman", "soapui": "SoapUI",
        "rest": "REST API", "soap": "SOAP API", "sql": "SQL", "postgresql": "PostgreSQL",
        "elasticsearch": "Elasticsearch", "jira": "Jira", "agile": "Agile / Scrum"
    }

class JobAnalyzer:
    @staticmethod
    def classify_archetypes(job_description: str) -> Dict[str, Any]:
        """
        Evaluates job description across all archetypes and calculates weighted scores.
        Returns sorted archetype scores, primary archetype, and secondary archetype.
        """
        if not job_description.strip():
            return {
                "primary": "management_process",
                "secondary": "automation",
                "scores": {"management_process": 1, "automation": 0, "backend_api": 0, "mobile": 0}
            }

        job_lower = job_description.lower()
        scores: Dict[str, int] = {k: 0 for k in ARCHETYPES.keys()}

        for arch_id, arch_data in ARCHETYPES.items():
            for kw in arch_data["keywords"]:
                pattern = r'\b' + re.escape(kw) + r'\b'
                matches = len(re.findall(pattern, job_lower))
                if matches > 0:
                    # Give higher weight to unique distinctive keywords
                    weight = 3 if kw in ["proxyman", "burp", "soapui", "playwright", "test plans", "sdlc", "aosp", "xcode"] else 1
                    scores[arch_id] += matches * weight

        sorted_archs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_archs[0][0] if sorted_archs[0][1] > 0 else "management_process"
        secondary = sorted_archs[1][0] if len(sorted_archs) > 1 and sorted_archs[1][1] > 0 else ("automation" if primary != "automation" else "backend_api")

        return {
            "primary": primary,
            "secondary": secondary,
            "scores": scores,
            "primary_data": ARCHETYPES[primary],
            "secondary_data": ARCHETYPES[secondary]
        }

    @staticmethod
    def generate_dynamic_skills(job_description: str, lang: str = "pl") -> List[Dict[str, Any]]:
        """
        Generates 3 skill categories of 4-6 clean, non-duplicated tags based on archetype scoring.
        Prioritizes matched catalog keywords directly into categories.
        """
        arch_info = JobAnalyzer.classify_archetypes(job_description)
        primary_id = arch_info["primary"]
        is_en = (lang == "en")
        job_lower = (job_description or "").lower()

        if primary_id == "mobile":
            cat1_name = "Mobile & API Testing" if is_en else "Testy Mobilne & API"
            cat1_pool = [
                "Mobile Testing (iOS/Android)" if is_en else "Testy Aplikacji Mobilnych (iOS/Android)",
                "Proxyman / Burp Suite",
                "API Testing (Postman)" if is_en else "Testowanie API (Postman)",
                "Usability Testing" if is_en else "Testy Użyteczności (Usability)",
                "Manual & Exploratory Testing" if is_en else "Testy Manualne & Eksploracyjne",
                "Test Plans & Test Cases" if is_en else "Plany Testów & Scenariusze"
            ]
            cat2_name = "Tools & Workflow" if is_en else "Narzędzia & Workflow"
            cat2_pool = [
                "Azure DevOps", "Jira (Xray)", "Git", "Qase", "Confluence",
                "Android Studio / Xcode"
            ]
            cat3_name = "Automation & Databases" if is_en else "Automatyzacja & Bazy Danych"
            cat3_pool = [
                "Playwright (TypeScript/JS)",
                "SQL (Database Verification)" if is_en else "SQL (Weryfikacja Danych)",
                "TypeScript / JavaScript",
                "CI/CD Pipelines" if is_en else "Pipelines CI/CD",
                "Windows OS Environments" if is_en else "Środowiska Windows OS"
            ]
        elif primary_id == "backend_api":
            cat1_name = "REST & SOAP API" if is_en else "REST & SOAP API"
            cat1_pool = [
                "SoapUI / Postman",
                "Swagger",
                "Microservices Architecture" if is_en else "Architektura Mikroserwisowa",
                "Integration Testing" if is_en else "Testy Integracyjne",
                "REST API Services" if is_en else "Usługi REST API",
                "SOAP WebServices" if is_en else "WebServices SOAP"
            ]
            cat2_name = "Databases & Diagnostics" if is_en else "Bazy Danych & Diagnostyka"
            cat2_pool = [
                "SQL (Advanced Queries, JOINs)" if is_en else "SQL (Złożone Zapytania, JOIN)",
                "PostgreSQL / Oracle",
                "Elasticsearch (Log Analysis)" if is_en else "Elasticsearch (Analiza Logów)",
                "Kibana (Logs)" if is_en else "Kibana (Logi)",
                "DBeaver / SQL Developer"
            ]
            cat3_name = "Tools & Environments" if is_en else "Narzędzia & Środowiska"
            cat3_pool = [
                "Jira (Xray)", "Confluence", "Git / GitLab CI",
                "Playwright (TypeScript/JS)",
                "Windows OS Environments" if is_en else "Środowiska Windows OS"
            ]
        elif primary_id == "automation":
            cat1_name = "Test Automation & Performance" if is_en else "Automatyzacja & Performance"
            cat1_pool = [
                "Playwright (TypeScript/C#)",
                "C# (.NET)",
                "Selenium / Selenoid",
                "Apache JMeter" if is_en else "Apache JMeter (Performance)",
                "UI & API Test Automation" if is_en else "Automatyzacja UI & API",
                "Page Object Model (POM)",
                "TypeScript / JavaScript",
                "E2E Test Automation" if is_en else "Automatyzacja E2E"
            ]
            cat2_name = "CI/CD & Environments" if is_en else "CI/CD & Środowiska"
            cat2_pool = [
                "Docker",
                "Jenkins CI/CD",
                "Git",
                "Linux & Windows OS" if is_en else "Środowiska Linux / Windows OS",
                "GitLab CI / GitHub Actions",
                "Azure DevOps"
            ]
            cat3_name = "API, Messaging & Databases" if is_en else "API, Komunikacja & Bazy Danych"
            cat3_pool = [
                "REST & SOAP API",
                "RabbitMQ" if is_en else "RabbitMQ (Kolejki Wiadomości)",
                "Elastic Stack (ELK)" if is_en else "Elastic Stack (Analiza Logów)",
                "Postman (API Testing)" if is_en else "Postman (Testowanie API)",
                "SQL (Database Verification)" if is_en else "SQL (Weryfikacja Danych)",
                "Jira (Xray)", "Confluence"
            ]
        elif primary_id in ["manual_qa", "manual_banking"]:
            cat1_name = "Testing & Quality" if is_en else "Testowanie & Jakość"
            cat1_pool = [
                "Manual Testing" if is_en else "Testy Manualne",
                "Functional & Regression Testing" if is_en else "Testy Funkcjonalne & Regresyjne",
                "Test Plans & Scenarios" if is_en else "Scenariusze & Przypadki Testowe",
                "ISTQB Standards" if is_en else "Certyfikat ISTQB",
                "Acceptance Testing (UAT)" if is_en else "Testy Akceptacyjne (UAT)"
            ]
            cat2_name = "QA Tools & Defect Tracking" if is_en else "Narzędzia & Zgłaszanie Błędów"
            cat2_pool = [
                "Jira (Xray)",
                "Confluence",
                "Defect Tracking & Reporting" if is_en else "Zgłaszanie i Śledzenie Błędów",
                "HP QC / ALM",
                "UTP Platform",
                "Zephyr",
                "Katalon Studio",
                "Chrome DevTools"
            ]
            cat3_name = "Databases & Automation" if is_en else "Bazy Danych & Środowiska"
            cat3_pool = [
                "SQL (Database Verification)" if is_en else "SQL (Weryfikacja Danych)",
                "Playwright (TypeScript/JS)",
                "Postman (API Testing)" if is_en else "Postman (Testowanie API)",
                "Katalon Studio",
                "Chrome DevTools",
                "Windows OS Environments" if is_en else "Środowiska Windows OS"
            ]
        else: # management_process
            cat1_name = "Test Management & SDLC" if is_en else "Zarządzanie Testami & SDLC"
            cat1_pool = [
                "Azure DevOps Test Plans",
                "Test Plans & Documentation" if is_en else "Dokumentacja Testowa & Plany",
                "ISTQB Standards" if is_en else "Standardy ISTQB",
                "QA Strategy & Planning" if is_en else "Strategia Testów & Plany",
                "SDLC Quality Assurance" if is_en else "Zapewnianie Jakości SDLC"
            ]
            cat2_name = "Testing & Quality" if is_en else "Testowanie & Jakość"
            cat2_pool = [
                "Manual Testing" if is_en else "Testy Manualne",
                "Integration Testing" if is_en else "Testy Integracyjne",
                "Regression Testing" if is_en else "Testy Regresyjne",
                "Acceptance Testing (UAT)" if is_en else "Testy Akceptacyjne (UAT)",
                "Functional Testing" if is_en else "Testy Funkcjonalne",
                "SharePoint Applications"
            ]
            cat3_name = "Tools & Databases" if is_en else "Narzędzia & Bazy Danych"
            cat3_pool = [
                "SQL (Queries & Verification)" if is_en else "SQL (Zapytania & Weryfikacja)",
                "Azure DevOps", "Jira (Xray)", "Confluence",
                "Windows OS Environments" if is_en else "Środowiska Windows OS"
            ]

        # Prioritize pool items that are actually mentioned in the job description
        def sort_pool_by_mention(pool: List[str]) -> List[str]:
            mentioned = []
            unmentioned = []
            for item in pool:
                parts = [p.strip().lower() for p in re.split(r'[/(),&]', item) if len(p.strip()) > 2]
                if any(p in job_lower for p in parts):
                    mentioned.append(item)
                else:
                    unmentioned.append(item)
            return mentioned + unmentioned

        cat1_pool = sort_pool_by_mention(cat1_pool)
        cat2_pool = sort_pool_by_mention(cat2_pool)
        cat3_pool = sort_pool_by_mention(cat3_pool)

        # Assemble and deduplicate across all 3 categories (4-6 items each)
        used_skills: Set[str] = set()

        def select_unique(pool: List[str], count: int = 5) -> List[str]:
            selected = []
            for item in pool:
                item_clean = item.strip()
                item_key = re.sub(r'[^a-zA-Z0-9]', '', item_clean.lower())
                if item_key and item_key not in used_skills and len(selected) < count:
                    selected.append(item_clean)
                    used_skills.add(item_key)
            return selected

        cat1_items = select_unique(cat1_pool, count=5)
        cat2_items = select_unique(cat2_pool, count=6)
        cat3_items = select_unique(cat3_pool, count=5)

        return [
            {"category": cat1_name, "items": cat1_items},
            {"category": cat2_name, "items": cat2_items},
            {"category": cat3_name, "items": cat3_items}
        ]

    @staticmethod
    def analyze(job_description: str, tailored_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes job description and evaluates candidate fit against tailored profile.
        Returns exact ATS match percentage, found keywords, missing keywords, and archetype breakdown.
        """
        if not job_description.strip():
            return {
                "match_score": 0,
                "job_keywords": [],
                "matched_keywords": [],
                "missing_keywords": [],
                "summary": "Brak treści oferty pracy.",
                "archetype": "management_process"
            }

        job_lower = job_description.lower()
        catalog = load_catalog_terms()

        extracted_terms = {}
        for kw, display_label in catalog.items():
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, job_lower):
                if display_label not in extracted_terms.values():
                    extracted_terms[kw] = display_label

        full_profile_text = json.dumps(tailored_profile, ensure_ascii=False).lower()

        matched = []
        missing = []

        for kw, label in extracted_terms.items():
            if kw in full_profile_text or label.lower() in full_profile_text:
                if label not in matched:
                    matched.append(label)
            else:
                if label not in missing:
                    missing.append(label)

        total = len(extracted_terms)
        score = int((len(matched) / total) * 100) if total > 0 else 90

        arch_info = JobAnalyzer.classify_archetypes(job_description)

        return {
            "match_score": min(score, 100),
            "job_keywords": list(extracted_terms.values()),
            "matched_keywords": matched,
            "missing_keywords": missing,
            "total_keywords_found": total,
            "matched_count": len(matched),
            "archetype": arch_info["primary"],
            "archetype_scores": arch_info["scores"]
        }

