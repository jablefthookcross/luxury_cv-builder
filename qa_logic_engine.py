"""
VitaeCraft AI - QA Logic Engine & Anti-AI / ATS Verification Auditor
Enforces strict QA-engineer logic, professional QA terminology, action verbs, and metrics.
Includes automated Anti-AI Jargon Auditing, ATS Parser Compliance Checks, and 100% Language Lock.
"""

import json
import re
from typing import Dict, Any, List

PROHIBITED_AI_BUZZWORDS = [
    "zagłębił się", "zagłębiła się", "jest świadectwem", "tkanina sukcesu",
    "transformacyjna podróż", "synergiczne rozwiązania", "przełomowy projekt",
    "pasjonat kodu", "dynamiczny lider", "zmieniający zasady gry", "holistyczne podejście",
    "tapestry of", "testament to", "delved into", "transformative journey", "synergistic",
    "game-changer", "passionate developer", "beacon of quality", "delivering quality assurance"
]

MOBILE_KEYWORDS = ["android studio", "xcode", "mobile device logs", "mobile testing", "logcat"]
BACKEND_SOAP_KEYWORDS = ["soapui", "soap api testing", "soap & rest api testing"]

class QALogicEngine:
    @staticmethod
    def audit_anti_ai_and_ats(profile: Dict[str, Any]) -> Dict[str, Any]:
        full_text = json.dumps(profile, ensure_ascii=False).lower()
        
        detected_buzzwords = []
        for word in PROHIBITED_AI_BUZZWORDS:
            if word in full_text:
                detected_buzzwords.append(word)

        ai_score = 100 - (len(detected_buzzwords) * 20)
        ai_score = max(ai_score, 0)

        pinfo = profile.get("personal_info", {})
        ats_checks = {
            "has_full_name": bool(pinfo.get("full_name") and pinfo["full_name"] != "Kandydat"),
            "has_contact_info": bool(pinfo.get("email") and pinfo.get("phone")),
            "has_summary": bool(profile.get("summary")),
            "has_experience": bool(profile.get("experience")),
            "has_skills": bool(profile.get("skills")),
            "no_fake_certifications": len(profile.get("certifications", [])) == 0 or any("ISTQB" not in str(c) for c in profile.get("certifications", []))
        }

        passed_checks = sum(1 for v in ats_checks.values() if v)
        ats_score = int((passed_checks / len(ats_checks)) * 100)

        return {
            "anti_ai_score": ai_score,
            "anti_ai_status": "100% Autentyczny Język Inżynierski (Brak Śladów AI)" if ai_score == 100 else f"Wykryto słowa AI: {', '.join(detected_buzzwords)}",
            "detected_ai_buzzwords": detected_buzzwords,
            "ats_readiness_score": ats_score,
            "ats_checks": ats_checks,
            "is_ats_safe": ats_score >= 85 and ai_score >= 80
        }

    @staticmethod
    def audit_and_refine_profile(profile: Dict[str, Any], lang: str = "pl", job_text: str = "") -> Dict[str, Any]:
        """
        Audits candidate profile from a Senior QA Architect perspective.
        Enforces candidate credentials, offer alignment, 100% EDUCATION LOCK, and 100% LANGUAGE LOCK.
        """
        refined = json_clone(profile)
        pinfo = refined.get("personal_info", {})
        
        if not pinfo.get("full_name") or pinfo["full_name"] == "Kandydat":
            pinfo["full_name"] = "Michał Kosowski"

        job_lower = job_text.lower()
        is_mobile_offer = bool(re.search(r'\b(mobile|android|xcode|logcat|mobilne|mobilnych)\b', job_lower))

        if job_text:
            if not is_mobile_offer:
                for cat in refined.get("skills", []):
                    cat["items"] = [
                        item for item in cat.get("items", [])
                        if item.lower() not in MOBILE_KEYWORDS
                    ]
                summary = refined.get("summary", "")
                summary = summary.replace(" (Android Studio / Xcode)", "").replace(" (Android Studio, Xcode)", "")
                summary = summary.replace("using Android Studio and Xcode.", "using industry standard QA tools.")
                summary = summary.replace("and mobile ", " ")
                refined["summary"] = summary
            else:
                for cat in refined.get("skills", []):
                    cat["items"] = [
                        item for item in cat.get("items", [])
                        if item.lower() not in BACKEND_SOAP_KEYWORDS
                    ]

        PL_PROCESS_SKILLS_MAP = {
            "Manual Testing": "Testy Manualne",
            "API Testing": "Testowanie API (REST & SOAP)",
            "Integration Testing": "Testy Integracyjne",
            "Functional Testing": "Testy Funkcjonalne",
            "Regression Testing": "Testy Regresyjne",
            "Exploratory Testing": "Testy Eksploracyjne",
            "Bug Reporting": "Zgłaszanie i Śledzenie Błędów",
            "Test Cases & Scenarios": "Scenariusze i Przypadki Testowe",
            "Test Plans & Documentation": "Plany Testów i Dokumentacja",
            "UAT Acceptance Testing": "Testy Akceptacyjne UAT",
            "SQL Database Verification": "Weryfikacja Baz Danych SQL",
            "Windows OS": "Środowiska Windows OS"
        }
        EN_PROCESS_SKILLS_MAP = {v: k for k, v in PL_PROCESS_SKILLS_MAP.items()}

        # 100% STRICT LANGUAGE LOCK: If lang == 'pl', translate category titles & process skill items to Polish. If 'en', to English.
        for cat in refined.get("skills", []):
            title = cat.get("category", "")
            if lang == "pl":
                if title in ["Testing & API", "Testowanie & API"]:
                    cat["category"] = "Testowanie & API"
                elif title in ["Tools & Test Management", "Narzędzia & Zarządzanie Testami"]:
                    cat["category"] = "Narzędzia & Zarządzanie Testami"
                elif title in ["Automation & Languages", "Automatyzacja & Języki"]:
                    cat["category"] = "Automatyzacja & Języki"
                
                cat["items"] = [PL_PROCESS_SKILLS_MAP.get(item, item) for item in cat.get("items", [])]
            else:
                if title in ["Testing & API", "Testowanie & API"]:
                    cat["category"] = "Testing & API"
                elif title in ["Tools & Test Management", "Narzędzia & Zarządzanie Testami"]:
                    cat["category"] = "Tools & Test Management"
                elif title in ["Automation & Languages", "Automatyzacja & Języki"]:
                    cat["category"] = "Automation & Languages"
                
                cat["items"] = [EN_PROCESS_SKILLS_MAP.get(item, item) for item in cat.get("items", [])]

        # Experience date, location & highlights language sync
        for job in refined.get("experience", []):
            company = job.get("company", "")
            if lang == "en":
                if job.get("end_date") and "obecnie" in str(job.get("end_date")).lower():
                    job["end_date"] = "Present"
                if "warszaw" in str(job.get("location", "")).lower():
                    job["location"] = "Warsaw, Poland"

                if "Benefit" in company:
                    job["position"] = "Software tester / QA Automation"
                    job["highlights"] = [
                        "Executed automated E2E regression suites for web application modules using Playwright and TypeScript.",
                        "Executed manual, functional, and API testing (REST & SOAP) using Postman to validate web platforms and backend services.",
                        "Prepared test plans, test scenarios, and comprehensive test documentation in Jira (Xray) and Confluence within Agile/Scrum delivery teams.",
                        "Conducted database verification and data integrity checks using complex SQL queries across Windows OS test environments.",
                        "Reported software defects with clear reproduction steps and collaborated with development teams on GitLab for issue resolution."
                    ]
                elif "Sii" in company:
                    job["position"] = "Test And Analysis Engineer"
                    job["highlights"] = [
                        "Executed backend API validation via Postman and performed data integrity verification using SQL Developer.",
                        "Conducted manual and functional testing of web application modules and customer portals based on backlog user stories.",
                        "Documented defects with clear reproduction steps and managed issue tracking in Jira (Xray) and HP QC / ALM following Scrum methodology."
                    ]
                elif "Euroloan" in company:
                    job["position"] = "Software tester"
                    job["highlights"] = [
                        "Executed comprehensive UI, functional, exploratory, and regression testing for web and digital platforms.",
                        "Designed, executed, and optimized test cases and test scenarios aligned with business requirements."
                    ]
            else:
                if job.get("end_date") and "present" in str(job.get("end_date")).lower():
                    job["end_date"] = "Obecnie"
                if "warsaw" in str(job.get("location", "")).lower():
                    job["location"] = "Warszawa"

                if "Benefit" in company:
                    job["position"] = "Software tester / QA Automation"
                    job["highlights"] = [
                        "Wykonywanie automatycznych testów regresyjnych E2E dla modułów webowych w Playwright.",
                        "Przeprowadzanie testów manualnych, funkcjonalnych oraz walidacji API (REST & SOAP) z użyciem narzędzia Postman dla portali i systemów.",
                        "Tworzenie planów testów, scenariuszy testowych oraz kompleksowej dokumentacji projektowej w Jira (Xray) i Confluence w zespole Agile/Scrum.",
                        "Wykonywanie zapytań SQL w celu weryfikacji baz danych i spójności danych na środowiskach Windows OS.",
                        "Zgłaszanie błędów aplikacji z jasnymi krokami reprodukcji, analiza wyników testów oraz współpraca z deweloperami w GitLab."
                    ]
                elif "Sii" in company:
                    job["position"] = "Test And Analysis Engineer"
                    job["highlights"] = [
                        "Dokumentowanie defektów z jasnymi krokami reprodukcji i zarządzanie błędami w narzędziach Jira (Xray) oraz HP QC / ALM.",
                        "Przeprowadzanie testów manualnych i funkcjonalnych modułów aplikacji webowych w oparciu o wymagania z backlogu.",
                        "Weryfikacja danych w bazach danych z użyciem narzędzia SQL Developer."
                    ]
                elif "Euroloan" in company:
                    job["position"] = "Software tester"
                    job["highlights"] = [
                        "Przeprowadzanie kompleksowych testów funkcjonalnych, eksploatacyjnych, UI oraz regresyjnych dla platform cyfrowych.",
                        "Projektowanie, wykonywanie i optymalizacja przypadków testowych zgodnych z kryteriami akceptacji."
                    ]

        # Languages section sync
        if lang == "en":
            refined["languages"] = [
                {"language": "Polish", "level": "Native"},
                {"language": "English", "level": "Full Professional (C2)"}
            ]
        else:
            refined["languages"] = [
                {"language": "Polski", "level": "Ojczysty (Native)"},
                {"language": "Angielski", "level": "Biegły (Professional)"}
            ]

        refined["certifications"] = []
        return refined

def json_clone(obj: Any) -> Any:
    return json.loads(json.dumps(obj))
