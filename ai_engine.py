"""
VitaeCraft AI - Universal 10/10 QA Tailoring Engine
Analyses job postings, compares against candidate's master profile,
and dynamically computes:
1. WHAT TO KEEP (Core QA achievements & candidate credentials)
2. WHAT TO STRIP / EXCLUDE (Bucket C irrelevant noise)
3. WHAT TO MODIFY & HIGHLIGHT (Bucket A & B skills, summary, and experience)
4. 100% LANGUAGE SYNC (EN / PL) with ZERO state pollution between runs.
"""

import os
import re
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List, Set

PROMPT_10_OUT_OF_10_DIRECTIVE = """
Jesteś Eksperckim Rekruterem IT i Test Architektem. Twój cel to stworzenie perfekcyjnego CV (10/10) dla Inżyniera QA na podstawie podanej oferty pracy i profilu kandydata (Michał Kosowski).

ZASADY ANALIZY I DOSTOSOWANIA (10/10 TAILORING):
1. ZEROWE ZANIECZYSZCZENIE KONTEKSTEM (NO STATE POLLUTION):
   - Analizujesz WYŁĄCZNIE obecną ofertę pracy. Nie dodawaj starych technologii z poprzednich ofert.

2. SELEKCJA ZASADĄ 3 KOSZYKÓW (RELEVANCE FILTERING):
   - KOSZYK A (MUST HAVE): Technologie z wymagań oferty (np. SQL, SoapUI, Postman, Jira Xray, Playwright, Python, Mobile, Cypress) -> umieść na samej górze sekcji Skills, w Podsumowaniu i w pierwszych punktach doświadczenia.
   - KOSZYK B (VALUE ADD): Pokrewne twarde umiejętności kandydata z profilu (np. testy eksploracyjne, walidacja kryteriów akceptacji, SQL, normy ISTQB) -> umieść jako uzupełnienie.
   - KOSZYK C (IRRELEVANT / NOISE - KATEGORYCZNY ZAKAZ): Narzędzia i domeny NIEZWIĄZANE z tą ofertą (np. Android Studio/Xcode przy ofercie backendowej/webowej; SoapUI przy ofercie czysto mobilnej/frontendowej; finanse/brokerage gdy oferta dotyczy e-commerce/automotive). BEZWZGLĘDNIE USUŃ JE Z CV.

3. SPÓJNOŚĆ JĘZYKOWA 100% (LANGUAGE SYNC):
   - Oferta po angielsku -> Wygeneruj 100% treści CV po angielsku (Summary, Skills, Nazwy stanowisk, Języki obce, RODO/GDPR i WSZYSTKIE punkty obowiązków).
   - Oferta po polsku -> Wygeneruj opisy po polsku z angielskimi terminami technicznymi.

4. UNIKALNOŚĆ I SENS OBOWIĄZKÓW (WORK EXPERIENCE):
   - Każda firma w sekcji experience MUSI zachować swoje własne, unikalne zadania. NIE powielaj tych samych zdań pomiędzy firmami.
   - Dopasuj język i akcenty obowiązków w każdej firmie pod technologie z Koszyka A.

5. CONTENT BUDGETING:
   - Sekcja Skills: Max 6-8 tagów na kategorię (tagi zwięzłe: 1-3 słowa).
   - Professional Summary: Dokładnie 3-4 zwarte, bardzo techniczne zdania (bez korpo-żargonu AI).
"""

class AIEngine:
    def __init__(self, provider: str = "auto", gemini_key: Optional[str] = None, ollama_url: str = "http://localhost:11434"):
        self.provider = provider
        self.gemini_key = gemini_key or os.environ.get("GEMINI_API_KEY", "")
        self.ollama_url = ollama_url
        self.ollama_model = os.environ.get("OLLAMA_MODEL", "llama3.2")

    def tailor_cv(self, master_profile: Dict[str, Any], job_description: str, target_role: str = "") -> Dict[str, Any]:
        """
        Tailors the candidate's master profile cleanly starting from fresh master_profile.
        """
        # Always operate on a clean clone of master_profile
        clean_master = json.loads(json.dumps(master_profile))
        provider_to_use = self._determine_provider()
        print(f"[AIEngine] Tailoring CV using provider: {provider_to_use}")

        if provider_to_use == "gemini":
            try:
                result = self._tailor_with_gemini(clean_master, job_description, target_role)
                return self._post_process_tailored(result, job_description, clean_master)
            except Exception as e:
                print(f"[AIEngine Warning] Gemini call failed ({e}). Falling back to Rule Engine.")
                return self._tailor_with_fallback(clean_master, job_description, target_role)

        elif provider_to_use == "ollama":
            try:
                result = self._tailor_with_ollama(clean_master, job_description, target_role)
                return self._post_process_tailored(result, job_description, clean_master)
            except Exception as e:
                print(f"[AIEngine Warning] Ollama call failed ({e}). Falling back to Rule Engine.")
                return self._tailor_with_fallback(clean_master, job_description, target_role)

        else:
            return self._tailor_with_fallback(clean_master, job_description, target_role)

    def _determine_provider(self) -> str:
        if self.provider == "gemini" and self.gemini_key:
            return "gemini"
        elif self.provider == "ollama":
            return "ollama"
        elif self.provider == "auto":
            if self.gemini_key:
                return "gemini"
            elif self._check_ollama_alive():
                return "ollama"
        return "fallback"

    def _check_ollama_alive(self) -> bool:
        try:
            req = urllib.request.Request(f"{self.ollama_url}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=2) as response:
                return response.status == 200
        except Exception:
            return False

    def _build_prompt(self, master_profile: Dict[str, Any], job_description: str, target_role: str) -> str:
        return f"""{PROMPT_10_OUT_OF_10_DIRECTIVE}

Stanowisko / Rola: {target_role if target_role else 'Opisane w ofercie'}

Oferta Pracy (DO ANALIZY):
\"\"\"
{job_description}
\"\"\"

Czysty Profil Kandydata (JSON do przekształcenia):
\"\"\"
{json.dumps(master_profile, ensure_ascii=False, indent=2)}
\"\"\"

Zwróć TYLKO czysty obiekt JSON dopasowanego CV. Nie używaj znaczników markdown ```json.
"""

    def _tailor_with_gemini(self, master_profile: Dict[str, Any], job_description: str, target_role: str) -> Dict[str, Any]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
        prompt = self._build_prompt(master_profile, job_description, target_role)
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            text_response = res_data["candidates"][0]["content"]["parts"][0]["text"]
            return self._clean_and_parse_json(text_response, master_profile)

    def _tailor_with_ollama(self, master_profile: Dict[str, Any], job_description: str, target_role: str) -> Dict[str, Any]:
        url = f"{self.ollama_url}/api/generate"
        prompt = self._build_prompt(master_profile, job_description, target_role)
        
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        
        with urllib.request.urlopen(req, timeout=60) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            text_response = res_data.get("response", "")
            return self._clean_and_parse_json(text_response, master_profile)

    def _post_process_tailored(self, tailored: Dict[str, Any], job_description: str, master_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Post-processing to enforce candidate identity, clean certifications, and language sync."""
        res = json.loads(json.dumps(tailored))
        
        # Candidate Credentials Safeguard
        pinfo = res.get("personal_info", {})
        master_info = master_profile.get("personal_info", {})
        pinfo["full_name"] = master_info.get("full_name", "Michał Kosowski")
        pinfo["email"] = master_info.get("email", "mmkosowski94@gmail.com")
        pinfo["phone"] = master_info.get("phone", "518075716")
        pinfo["linkedin"] = master_info.get("linkedin", "https://linkedin.com/in/michal-kosowski")
        pinfo["github"] = master_info.get("github", "https://github.com")
        res["personal_info"] = pinfo
        
        res["certifications"] = []
        return res

    def _tailor_with_fallback(self, master_profile: Dict[str, Any], job_description: str, target_role: str = "") -> Dict[str, Any]:
        """Smart Rule Engine implementing 10/10 Relevance Filtering & Language Sync."""
        tailored = json.loads(json.dumps(master_profile))
        job_lower = job_description.lower()

        # Language Detection
        english_indicators = ["requirements", "responsibilities", "experience", "skills", "must have", "nice to have", "proficient", "knowledge of", "minimum"]
        is_english_offer = sum(1 for kw in english_indicators if kw in job_lower) >= 2

        # Role & Tech Keyword Extraction with Exact Regex Word Boundaries
        is_mobile = bool(re.search(r'\b(mobile|android|xcode|logcat|mobilne|mobilnych)\b', job_lower))
        has_soap = bool(re.search(r'\b(soap|soapui)\b', job_lower))
        has_sql = bool(re.search(r'\b(sql)\b', job_lower))
        has_xray = bool(re.search(r'\b(xray)\b', job_lower))
        has_postman = bool(re.search(r'\b(postman)\b', job_lower))
        has_testrail = bool(re.search(r'\b(testrail)\b', job_lower))
        has_playwright = bool(re.search(r'\b(playwright)\b', job_lower))

        if target_role:
            tailored["personal_info"]["title"] = target_role
        else:
            tailored["personal_info"]["title"] = "Manual Mobile Tester" if is_mobile else "Software QA Engineer"

        # 1. DYNAMIC SKILLS BUCKETING
        new_skills = []

        # Category 1: Testing & API
        testing_items = []
        if is_mobile:
            testing_items.extend(["Mobile Testing", "Exploratory Testing", "User Stories Analysis", "Acceptance Criteria", "Regression Testing", "ISTQB Standards"])
        else:
            if has_soap:
                testing_items.extend(["SOAP & REST API Testing", "SoapUI", "Postman", "SQL Database Verification", "Integration Testing", "Functional Testing", "Regression Testing", "ISTQB Standards"])
            elif has_postman:
                testing_items.extend(["REST API Testing", "Postman", "Swagger", "SQL Database Verification", "Integration Testing", "Functional Testing", "Regression Testing", "ISTQB Standards"])
            else:
                testing_items.extend(["REST API Testing", "Postman", "Integration Testing", "Functional Testing", "Regression Testing", "ISTQB Standards"])

        cat1_title = "Testing & API" if is_english_offer else "Testowanie & API"
        new_skills.append({"category": cat1_title, "items": testing_items[:8]})

        # Category 2: Tools & Test Management
        tools_items = []
        if is_mobile:
            tools_items.extend(["Android Studio", "Xcode", "Mobile Device Logs", "Jira", "TestRail", "Confluence", "Git", "Docker"])
        else:
            if has_xray:
                tools_items.append("Jira (Xray)")
            else:
                tools_items.append("Jira")
            tools_items.extend(["Confluence", "Git"])
            if has_sql:
                tools_items.append("SQL Developer / DBeaver")
            tools_items.append("Test Documentation & Reporting")
            if has_testrail:
                tools_items.append("TestRail")
            tools_items.append("Docker")

        cat2_title = "Tools & Test Management" if is_english_offer else "Narzędzia & Zarządzanie Testami"
        new_skills.append({"category": cat2_title, "items": tools_items[:8]})

        # Category 3: Automation & Languages
        auto_items = ["SQL", "Playwright", "TypeScript", "JavaScript", "GitLab CI/CD", "GitHub Actions"]
        cat3_title = "Automation & Languages" if is_english_offer else "Automatyzacja & Języki"
        new_skills.append({"category": cat3_title, "items": auto_items[:8]})

        tailored["skills"] = new_skills

        # 2. WORK EXPERIENCE: 100% OFFER ALIGNED & 100% LANGUAGE SYNC
        if is_english_offer:
            if is_mobile:
                tailored["experience"] = [
                    {
                        "position": "Software tester / QA Automation",
                        "company": "Benefit Systems S.A.",
                        "location": "Warsaw, Poland",
                        "start_date": "2022",
                        "end_date": "Present",
                        "highlights": [
                            "Performed manual, exploratory, and regression testing for mobile (iOS & Android) and web applications.",
                            "Analyzed mobile device logs using Android Studio and Xcode logcat to isolate client-side defects.",
                            "Verified user stories and acceptance criteria across multiple mobile test builds.",
                            "Documented bugs and test scenarios in Jira and TestRail within Agile/Scrum ceremonies."
                        ]
                    },
                    {
                        "position": "Test And Analysis Engineer",
                        "company": "Sii Polska Sp. z o.o. (Freelance)",
                        "location": "Warsaw, Poland",
                        "start_date": "2021-09",
                        "end_date": "2022-04",
                        "highlights": [
                            "Conducted manual, functional, and exploratory testing of web and mobile application modules.",
                            "Executed regression testing cycles and documented bug reproduction steps in Jira.",
                            "Validated User Stories and acceptance criteria prior to release deployments."
                        ]
                    },
                    {
                        "position": "Software tester",
                        "company": "Euroloan Group (Freelance)",
                        "location": "Warsaw, Poland",
                        "start_date": "2019-07",
                        "end_date": "2021-01",
                        "highlights": [
                            "Executed comprehensive functional and usability testing across mobile and web platforms.",
                            "Designed and maintained test suites for mobile application builds."
                        ]
                    }
                ]
            else:
                tailored["experience"] = [
                    {
                        "position": "Software tester / QA Automation",
                        "company": "Benefit Systems S.A.",
                        "location": "Warsaw, Poland",
                        "start_date": "2022",
                        "end_date": "Present",
                        "highlights": [
                            "Executed manual, integration, and API testing (REST & SOAP) using Postman and SoapUI to validate complex backend services.",
                            "Conducted database verification and data integrity checks using SQL queries.",
                            "Designed, executed, and maintained automated E2E web test scripts using Playwright in TypeScript/JavaScript.",
                            "Prepared test plans, test scenarios, and execution summary reports in Jira (Xray) and Confluence within Agile/Scrum delivery teams."
                        ]
                    },
                    {
                        "position": "Test And Analysis Engineer",
                        "company": "Sii Polska Sp. z o.o. (Freelance)",
                        "location": "Warsaw, Poland",
                        "start_date": "2021-09",
                        "end_date": "2022-04",
                        "highlights": [
                            "Conducted manual and functional testing of HR web applications based on backlog requirements.",
                            "Executed backend API validation via Postman and performed data integrity verification using SQL Developer.",
                            "Documented defects with clear reproduction steps and managed issue tracking in Jira (Xray) following Scrum methodology."
                        ]
                    },
                    {
                        "position": "Software tester",
                        "company": "Euroloan Group (Freelance)",
                        "location": "Warsaw, Poland",
                        "start_date": "2019-07",
                        "end_date": "2021-01",
                        "highlights": [
                            "Executed comprehensive UI, functional, and regression testing for enterprise web applications.",
                            "Designed, executed, and optimized test cases and test scenarios aligned with business acceptance criteria."
                        ]
                    }
                ]
        else:
            if is_mobile:
                tailored["experience"] = [
                    {
                        "position": "Software tester / QA Automation",
                        "company": "Benefit Systems S.A.",
                        "location": "Warszawa",
                        "start_date": "2022",
                        "end_date": "Obecnie",
                        "highlights": [
                            "Wykonywanie testów manualnych, eksploracyjnych i regresyjnych aplikacji mobilnych (iOS & Android) oraz webowych.",
                            "Analiza logów urządzeń mobilnych przy użyciu Android Studio oraz Xcode logcat w celu izolacji błędów klienta.",
                            "Weryfikacja User Stories oraz kryteriów akceptacji na poszczególnych buildach aplikacji mobilnych.",
                            "Zgłaszanie defektów i zarządzanie przypadkami testowymi w narzędziach Jira oraz TestRail w zespole Agile/Scrum."
                        ]
                    },
                    {
                        "position": "Test And Analysis Engineer",
                        "company": "Sii Polska Sp. z o.o. (Freelance)",
                        "location": "Warszawa",
                        "start_date": "2021-09",
                        "end_date": "2022-04",
                        "highlights": [
                            "Przeprowadzanie testów manualnych, funkcjonalnych i eksploracyjnych modułów aplikacji webowych i mobilnych.",
                            "Wykonywanie cykli testów regresyjnych oraz dokumentowanie kroków reprodukcji błędów w Jira.",
                            "Walidacja kryteriów akceptacji przed wdrożeniami produkcyjnymi."
                        ]
                    },
                    {
                        "position": "Software tester",
                        "company": "Euroloan Group (Freelance)",
                        "location": "Warszawa",
                        "start_date": "2019-07",
                        "end_date": "2021-01",
                        "highlights": [
                            "Przeprowadzanie kompleksowych testów funkcjonalnych i użytecznościowych aplikacji mobilnych i webowych.",
                            "Projektowanie i utrzymanie zestawów testowych dla wydań mobilnych."
                        ]
                    }
                ]
            else:
                tailored["experience"] = [
                    {
                        "position": "Software tester / QA Automation",
                        "company": "Benefit Systems S.A.",
                        "location": "Warszawa",
                        "start_date": "2022",
                        "end_date": "Obecnie",
                        "highlights": [
                            "Wykonywanie testów integracyjnych i walidacji usług API (REST & SOAP) przy użyciu narzędzi Postman oraz SoapUI.",
                            "Przeprowadzanie weryfikacji bazy danych za pomocą zapytań SQL w celu weryfikacji poprawności przesyłania danych backendowych.",
                            "Projektowanie, wykonywanie i utrzymywanie automatycznych skryptów testowych E2E dla aplikacji webowych w Playwright (TypeScript/JavaScript).",
                            "Tworzenie planów testów, scenariuszy testowych oraz raportów z wykonania w Jira (Xray) i Confluence w zespole Agile/Scrum."
                        ]
                    },
                    {
                        "position": "Test And Analysis Engineer",
                        "company": "Sii Polska Sp. z o.o. (Freelance)",
                        "location": "Warszawa",
                        "start_date": "2021-09",
                        "end_date": "2022-04",
                        "highlights": [
                            "Przeprowadzanie testów manualnych i funkcjonalnych aplikacji webowych HR w oparciu o wymagania z backlogu.",
                            "Wykonywanie testów backendowych i API w Postmanie oraz walidacja danych z użyciem SQL Developer.",
                            "Zgłaszanie błędów z jasnymi krokami reprodukcji i śledzenie defektów w Jira (Xray) w metodologii Scrum."
                        ]
                    },
                    {
                        "position": "Software tester",
                        "company": "Euroloan Group (Freelance)",
                        "location": "Warszawa",
                        "start_date": "2019-07",
                        "end_date": "2021-01",
                        "highlights": [
                            "Przeprowadzanie kompleksowych testów UI, funkcjonalnych i regresyjnych systemów cyfrowych na platformach webowych.",
                            "Projektowanie, wykonywanie i optymalizacja przypadków i scenariuszy testowych zgodnych z wymaganiami biznesowymi."
                        ]
                    }
                ]

        # 3. LANGUAGES SECTION
        if is_english_offer:
            tailored["languages"] = [
                {"language": "Polish", "level": "Native"},
                {"language": "English", "level": "Full Professional (C2)"}
            ]
        else:
            tailored["languages"] = [
                {"language": "Polski", "level": "Ojczysty (Native)"},
                {"language": "Angielski", "level": "Biegły (Professional)"}
            ]

        # 4. PROFESSIONAL SUMMARY
        if is_mobile:
            if is_english_offer:
                s1 = "Software QA Engineer with 5+ years of experience in manual, exploratory, and mobile application testing."
                s2 = "Specialized in Acceptance Criteria verification, GUI usability testing, and mobile log analysis using Android Studio and Xcode."
                s3 = "Proficient in defect tracking via Jira, Xray, and TestRail within Agile/Scrum delivery teams."
                s4 = "Backed by hands-on experience in REST API validation (Postman/Swagger) and Playwright automation in TypeScript."
            else:
                s1 = "Inżynier QA z ponad 5-letnim doświadczeniem w testowaniu manualnym oraz eksploracyjnym aplikacji mobilnych i webowych."
                s2 = "Specjalizuje się w weryfikacji kryteriów akceptacji (Acceptance Criteria), testach GUI & Usability oraz analizie logów urządzeń mobilnych (Android Studio, Xcode)."
                s3 = "Sprawnie zarządza błędami i dokumentacją testową w narzędziach Jira, Xray oraz TestRail w zespole Agile/Scrum."
                s4 = "Posiada dodatkowe doświadczenie w walidacji REST API (Postman/Swagger) oraz automatyzacji w Playwright (TypeScript)."
        else:
            if is_english_offer:
                s1 = "QA Engineer with 5+ years of experience in manual, integration, and API testing (REST & SOAP)."
                s2 = "Proficient in backend verification and database testing using SQL, test scenario design, and end-to-end defect tracking in Jira and Xray within Agile/Scrum methodologies."
                s3 = "Experienced in preparing comprehensive test documentation, plans, and summary reports for enterprise systems."
                s4 = "Complemented by test automation experience using Playwright in TypeScript."
            else:
                s1 = "Inżynier QA z ponad 5-letnim doświadczeniem w testach manualnych, integracyjnych oraz testowaniu API (REST & SOAP)."
                s2 = "Specjalizuje się w weryfikacji baz danych za pomocą SQL, projektowaniu scenariuszy testowych oraz śledzeniu błędów w Jira (Xray) w zespole Agile/Scrum."
                s3 = "Doświadczony w tworzeniu kompleksowej dokumentacji testowej, planów testów oraz raportów dla systemów rejestrów i platform cyfrowych."
                s4 = "Wspierany praktyczną znajomością automatyzacji testów w Playwright (TypeScript)."
        
        tailored["summary"] = f"{s1} {s2} {s3} {s4}"
        tailored["certifications"] = []
        return tailored

    def _clean_and_parse_json(self, text: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        try:
            return json.loads(text)
        except Exception as e:
            print(f"[AIEngine Error] JSON parsing failed: {e}")
            return fallback
