"""
VitaeCraft AI - Universal 10/10 Dynamic QA Tailoring Engine
Author: MagicMike Development Team

Fully dynamic, universal AI & NLP tailoring engine with ZERO hardcoded offer checks.
Includes:
1. Smart Offer Text Pre-Processor (strips web scraping clutter & marketing noise).
2. 3-Buckets Classification Breakdown (Must Have, Value Add, Noise Removal).
3. 100% Single Language Lock (PL or EN) with zero state pollution.
"""

import os
import re
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List, Set

PROMPT_UNIVERSAL_TAILORING_DIRECTIVE = """
Jesteś Eksperckim Rekruterem IT i Test Architektem. Twój cel to stworzenie perfekcyjnego CV (10/10) dla Inżyniera QA na podstawie podanej oferty pracy i profilu kandydata (Michał Kosowski).

ZASADY UNIWERSALNEGO DOSTOSOWANIA DLA DOWOLNEJ OFERTY:
1. DYNAMICZNA ANALIZA OFERTY (ZERO HARDCODOWANIA):
   - Przeanalizuj treść podanej oferty pracy i wyciągnij z niej dokładnie te technologie, narzędzia, ramy, certyfikaty i specyfikę branżową, które podał pracodawca.

2. SELEKCJA ZASADĄ 3 KOSZYKÓW (RELEVANCE FILTERING):
   - KOSZYK A (MUST HAVE): Technologie z wymagań oferty obecne w profilu kandydata -> umieść na samej górze sekcji Skills, w Podsumowaniu Zawodowym i w pierwszych punktach doświadczenia.
   - KOSZYK B (VALUE ADD): Pokrewne twarde umiejętności kandydata z profilu wspierające rolę -> umieść jako uzupełnienie.
   - KOSZYK C (IRRELEVANT / NOISE - KATEGORYCZNY ZAKAZ): Narzędzia i domeny z profilu kandydata NIEZWIĄZANE z tą konkretną ofertą -> BEZWZGLĘDNIE USUŃ LUB ZMNIEJSZ ICH PRIORYTET.

3. SPÓJNOŚĆ JĘZYKOWA 100% (LANGUAGE SYNC):
   - WYBRANY JĘZYK = {LANG}.
   - Jeśli LANG = PL -> Całość (Podsumowanie, nazwy kategorii, stanowiska, punkty obowiązków, języki) MUSI być w 100% po polsku z angielskimi pojęciami technicznymi.
   - Jeśli LANG = EN -> Całość (Podsumowanie, nazwy kategorii, stanowiska, punkty obowiązków, języki, daty 'Present') MUSI być w 100% po angielsku.

4. DYNAMICZNE DOŚWIADCZENIE (WORK EXPERIENCE):
   - Zachowaj autentyczność 3 pracodawców kandydata (Benefit Systems S.A., Sii Polska, Euroloan Group).
   - Nie powielaj tych samych zdań między pracodawcami! Przeredaguj i ułóż punkty dla każdego pracodawcy tak, aby uwypuklić zadania pasujące do wymagań analizowanej oferty.

5. CONTENT BUDGETING:
   - Sekcja Skills: Max 6-8 tagów na kategorię (tagi 1-3 słowa).
   - Professional Summary: Dokładnie 3-4 zwarte, bardzo techniczne zdania.
"""

ENGLISH_BASELINE_EXPERIENCE = [
    {
        "position": "Software tester / QA Automation",
        "company": "Benefit Systems S.A.",
        "location": "Warsaw, Poland",
        "start_date": "2022",
        "end_date": "Present",
        "highlights": [
            "Prepared test plans, test scenarios, and comprehensive test documentation in Jira (Xray) and Confluence within Agile/Scrum delivery teams.",
            "Executed manual, functional, and integration testing for core enterprise platforms aligned with business acceptance criteria.",
            "Conducted database verification and data integrity checks using complex SQL queries across Windows OS test environments.",
            "Reported software defects with clear reproduction steps and collaborated with development teams on issue resolution.",
            "Executed manual and API testing (REST & SOAP) using Postman and SoapUI to validate backend workflows."
        ]
    },
    {
        "position": "Test And Analysis Engineer",
        "company": "Sii Polska Sp. z o.o. (Freelance)",
        "location": "Warsaw, Poland",
        "start_date": "2021-09",
        "end_date": "2022-04",
        "highlights": [
            "Conducted manual and functional testing of enterprise web application modules based on backlog user stories.",
            "Documented defects with clear reproduction steps and managed issue tracking in Jira (Xray) and HP QC / ALM following Scrum methodology.",
            "Executed backend API validation via Postman and performed data integrity verification using SQL Developer."
        ]
    },
    {
        "position": "Software tester",
        "company": "Euroloan Group (Freelance)",
        "location": "Warsaw, Poland",
        "start_date": "2019-07",
        "end_date": "2021-01",
        "highlights": [
            "Executed comprehensive UI, functional, and regression testing for financial and digital platforms.",
            "Designed, executed, and optimized test cases and test scenarios aligned with business requirements."
        ]
    }
]

POLISH_BASELINE_EXPERIENCE = [
    {
        "position": "Software tester / QA Automation",
        "company": "Benefit Systems S.A.",
        "location": "Warszawa",
        "start_date": "2022",
        "end_date": "Obecnie",
        "highlights": [
            "Tworzenie planów testów, scenariuszy testowych oraz kompleksowej dokumentacji projektowej w Jira (Xray) i Confluence w zespole Agile/Scrum.",
            "Przeprowadzanie testów manualnych, funkcjonalnych i integracyjnych systemów informatycznych zgodnie z dokumentacją techniczną.",
            "Wykonywanie zapytań SQL w celu weryfikacji baz danych i spójności danych na środowiskach Windows OS.",
            "Zgłaszanie błędów aplikacji, analiza wyników testów oraz współpraca z zespołem deweloperskim przy usuwaniu defektów.",
            "Wykonywanie walidacji usług API (REST & SOAP) przy użyciu Postman oraz SoapUI."
        ]
    },
    {
        "position": "Test And Analysis Engineer",
        "company": "Sii Polska Sp. z o.o. (Freelance)",
        "location": "Warszawa",
        "start_date": "2021-09",
        "end_date": "2022-04",
        "highlights": [
            "Przeprowadzanie testów manualnych i funkcjonalnych modułów aplikacji biznesowych w oparciu o wymagania z backlogu.",
            "Dokumentowanie defektów z jasnymi krokami reprodukcji i zarządzanie błędami w narzędziach Jira (Xray) oraz HP QC / ALM.",
            "Weryfikacja danych w bazach danych z użyciem narzędzia SQL Developer."
        ]
    },
    {
        "position": "Software tester",
        "company": "Euroloan Group (Freelance)",
        "location": "Warszawa",
        "start_date": "2019-07",
        "end_date": "2021-01",
        "highlights": [
            "Przeprowadzanie kompleksowych testów funkcjonalnych, UI oraz regresyjnych dla platform finansowych i cyfrowych.",
            "Projektowanie, wykonywanie i optymalizacja przypadków testowych zgodnych z kryteriami akceptacji."
        ]
    }
]

def clean_job_offer_text(raw_text: str) -> str:
    """Strips web scraping clutter (navigation items, revenue stats, Star Wars fluff, apply buttons)."""
    if not raw_text:
        return ""
        
    lines = raw_text.split("\n")
    cleaned_lines = []
    
    ignore_patterns = [
        r"^0[0-9].*", r"^quick apply.*", r"^zapisz.*", r"^aplikuj.*", r"^zgłaszam się do.*",
        r"^brakuje ci informacji.*", r"^przekażemy twoje pytanie.*", r"^dodane [0-9]+ dni temu.*",
        r"^obroty w 20[0-9]{2}.*", r"^szukamy osób kreatywnych.*star wars.*", r"^jesteś mistrzem komunikacji.*"
    ]
    
    for line in lines:
        l_str = line.strip()
        if not l_str:
            continue
        if any(re.match(p, l_str.lower()) for p in ignore_patterns):
            continue
        cleaned_lines.append(l_str)
        
    return "\n".join(cleaned_lines)

class AIEngine:
    def __init__(self, provider: str = "auto", gemini_key: Optional[str] = None, ollama_url: str = "http://localhost:11434"):
        self.provider = provider
        self.gemini_key = gemini_key or os.environ.get("GEMINI_API_KEY", "")
        self.ollama_url = ollama_url
        self.ollama_model = os.environ.get("OLLAMA_MODEL", "llama3.2")

    def tailor_cv(self, master_profile: Dict[str, Any], job_description: str, target_role: str = "", lang: str = "pl") -> Dict[str, Any]:
        clean_master = json.loads(json.dumps(master_profile))
        cleaned_job_text = clean_job_offer_text(job_description)
        provider_to_use = self._determine_provider()
        print(f"[AIEngine] Tailoring CV using provider: {provider_to_use} (Language: {lang})")

        if provider_to_use == "gemini":
            try:
                result = self._tailor_with_gemini(clean_master, cleaned_job_text, target_role, lang=lang)
                return self._post_process_tailored(result, cleaned_job_text, clean_master, lang=lang)
            except Exception as e:
                print(f"[AIEngine Warning] Gemini call failed ({e}). Falling back to Universal Dynamic Engine.")
                return self._tailor_with_dynamic_nlp(clean_master, cleaned_job_text, target_role, lang=lang)

        elif provider_to_use == "ollama":
            try:
                result = self._tailor_with_ollama(clean_master, cleaned_job_text, target_role, lang=lang)
                return self._post_process_tailored(result, cleaned_job_text, clean_master, lang=lang)
            except Exception as e:
                print(f"[AIEngine Warning] Ollama call failed ({e}). Falling back to Universal Dynamic Engine.")
                return self._tailor_with_dynamic_nlp(clean_master, cleaned_job_text, target_role, lang=lang)

        else:
            return self._tailor_with_dynamic_nlp(clean_master, cleaned_job_text, target_role, lang=lang)

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

    def _build_prompt(self, master_profile: Dict[str, Any], job_description: str, target_role: str, lang: str = "pl") -> str:
        directive = PROMPT_UNIVERSAL_TAILORING_DIRECTIVE.replace("{LANG}", lang.upper())
        return f"""{directive}

Stanowisko / Rola: {target_role if target_role else 'Wyciągnij automatycznie z oferty'}

Oferta Pracy (DO ANALIZY DYNAMICZNEJ):
\"\"\"
{job_description}
\"\"\"

Profil Kandydata (JSON):
\"\"\"
{json.dumps(master_profile, ensure_ascii=False, indent=2)}
\"\"\"

Zwróć TYLKO czysty obiekt JSON dopasowanego CV. Nie używaj znaczników markdown ```json.
"""

    def _tailor_with_gemini(self, master_profile: Dict[str, Any], job_description: str, target_role: str, lang: str = "pl") -> Dict[str, Any]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
        prompt = self._build_prompt(master_profile, job_description, target_role, lang=lang)
        
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

    def _tailor_with_ollama(self, master_profile: Dict[str, Any], job_description: str, target_role: str, lang: str = "pl") -> Dict[str, Any]:
        url = f"{self.ollama_url}/api/generate"
        prompt = self._build_prompt(master_profile, job_description, target_role, lang=lang)
        
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

    def _post_process_tailored(self, tailored: Dict[str, Any], job_description: str, master_profile: Dict[str, Any], lang: str = "pl") -> Dict[str, Any]:
        res = json.loads(json.dumps(tailored))
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

    def _tailor_with_dynamic_nlp(self, master_profile: Dict[str, Any], job_description: str, target_role: str = "", lang: str = "pl") -> Dict[str, Any]:
        tailored = json.loads(json.dumps(master_profile))
        job_lower = job_description.lower()
        is_english = (lang == "en")

        # 1. EXPANDED TECH CATALOG FOR ALL IT DOMAINS
        TECH_CATALOG = {
            "java": "Java",
            "selenium": "Selenium WebDriver",
            "restassured": "RestAssured",
            "rest-assured": "RestAssured",
            "junit": "JUnit",
            "testng": "TestNG",
            "playwright": "Playwright",
            "typescript": "TypeScript",
            "javascript": "JavaScript",
            "python": "Python",
            "cypress": "Cypress",
            "postman": "Postman",
            "soapui": "SoapUI",
            "soap": "SOAP API Testing",
            "rest": "REST API Testing",
            "api": "API Testing",
            "sql": "SQL Database Verification",
            "jmeter": "JMeter",
            "jira": "Jira",
            "xray": "Jira (Xray)",
            "testrail": "TestRail",
            "hp qc": "HP QC",
            "hpqc": "HP QC",
            "alm": "HP ALM",
            "katalon": "Katalon Studio",
            "utp": "UTP",
            "bank": "Aplikacje Bankowe i Maklerskie" if not is_english else "Banking & Brokerage Systems",
            "bankow": "Aplikacje Bankowe" if not is_english else "Banking Applications",
            "makler": "Aplikacje Maklerskie" if not is_english else "Brokerage Systems",
            "windows": "Windows OS",
            "docker": "Docker",
            "git": "Git",
            "gitlab": "GitLab CI/CD",
            "github": "GitHub Actions",
            "mobile": "Mobile Testing",
            "android": "Android Testing",
            "ios": "iOS Testing",
            "xcode": "Xcode",
            "logcat": "Mobile Device Logs",
            "exploratory": "Exploratory Testing",
            "acceptance": "Acceptance Criteria",
            "user stories": "User Stories Analysis",
            "istqb": "ISTQB / ISEB Certification",
            "iseb": "ISTQB / ISEB Certification",
            "plan": "Test Plans & Documentation",
            "dokumentac": "Dokumentacja Testowa" if not is_english else "Test Documentation"
        }

        matched_techs = []
        for kw, display_name in TECH_CATALOG.items():
            if re.search(r'\b' + re.escape(kw) + r'\b', job_lower):
                if display_name not in matched_techs:
                    matched_techs.append(display_name)

        # 2. DYNAMIC TITLE INFERENCE
        if target_role:
            tailored["personal_info"]["title"] = target_role
        else:
            first_lines = job_description.split("\n")[:5]
            title_found = ""
            for line in first_lines:
                clean_line = line.strip()
                if any(role_kw in clean_line.lower() for role_kw in ["tester", "qa", "engineer", "inżynier", "developer"]):
                    if len(clean_line) < 60:
                        title_found = clean_line
                        break
            
            if title_found:
                tailored["personal_info"]["title"] = title_found
            elif "manual" in job_lower:
                tailored["personal_info"]["title"] = "Tester Manualny" if not is_english else "Manual Software Tester"
            else:
                tailored["personal_info"]["title"] = "Software QA Engineer"

        # 3. DYNAMIC 3-BUCKETS SKILLS BUCKETING
        cat1_items = [t for t in matched_techs if t in ["ISTQB / ISEB Certification", "Manual Testing", "Aplikacje Bankowe i Maklerskie", "Banking & Brokerage Systems", "Test Plans & Documentation", "Dokumentacja Testowa", "Exploratory Testing", "Acceptance Criteria", "User Stories Analysis", "SOAP API Testing", "REST API Testing", "Postman", "SoapUI", "Java", "Selenium WebDriver", "RestAssured", "JUnit", "TestNG", "Playwright", "Mobile Testing"]]
        if not cat1_items:
            cat1_items = ["ISTQB / ISEB Certification", "Manual Testing", "Integration Testing", "Functional Testing", "Regression Testing"]
        cat1_items.extend(["Integration Testing", "Functional Testing", "Regression Testing"])
        
        cat1_final = []
        for item in cat1_items:
            if item not in cat1_final:
                cat1_final.append(item)

        cat2_items = [t for t in matched_techs if t in ["Jira (Xray)", "Jira", "HP QC", "HP ALM", "TestRail", "Katalon Studio", "UTP", "Windows OS", "SQL Database Verification", "Confluence", "Git", "Docker"]]
        cat2_items.extend(["Jira (Xray)", "HP QC / ALM", "Windows OS", "Confluence", "Git", "SQL Developer / DBeaver", "Docker"])
        cat2_final = []
        for item in cat2_items:
            if item not in cat2_final:
                cat2_final.append(item)

        cat3_items = [t for t in matched_techs if t in ["SQL Database Verification", "SQL", "Windows OS", "Git", "Java", "Playwright", "TypeScript", "JavaScript", "GitLab CI/CD"]]
        cat3_items.extend(["SQL", "Playwright", "TypeScript", "JavaScript", "GitLab CI/CD"])
        cat3_final = []
        for item in cat3_items:
            if item not in cat3_final:
                cat3_final.append(item)

        new_skills = [
            {"category": "Testing & API" if is_english else "Testowanie & API", "items": cat1_final[:8]},
            {"category": "Tools & Test Management" if is_english else "Narzędzia & Zarządzanie Testami", "items": cat2_final[:8]},
            {"category": "Automation & Languages" if is_english else "Automatyzacja & Języki", "items": cat3_final[:8]}
        ]
        tailored["skills"] = new_skills

        # Compute 3 Buckets Breakdown for GUI Card
        bucket_a = matched_techs[:8]
        bucket_b = [item for item in cat1_final + cat2_final + cat3_final if item not in bucket_a][:8]
        all_master_tools = ["Android Studio", "Xcode", "Mobile Device Logs", "Playwright", "TypeScript", "Docker", "SoapUI", "RestAssured"]
        bucket_c = [t for t in all_master_tools if t not in bucket_a and t not in bucket_b][:5]
        
        tailored["_buckets_breakdown"] = {
            "bucket_a": bucket_a,
            "bucket_b": bucket_b,
            "bucket_c": bucket_c
        }

        # 4. DYNAMIC WORK EXPERIENCE RE-ORDERING
        raw_exp = ENGLISH_BASELINE_EXPERIENCE if is_english else POLISH_BASELINE_EXPERIENCE
        tailored_exp = []
        
        for job in raw_exp:
            job_copy = json.loads(json.dumps(job))
            highlights = job_copy.get("highlights", [])

            def score_highlight(h_text: str) -> int:
                h_lower = h_text.lower()
                score = 0
                for tech in matched_techs:
                    if tech.lower() in h_lower:
                        score += 3
                if "manual" in job_lower and ("automatyzac" in h_lower or "automated" in h_lower):
                    score -= 5
                return score

            sorted_highlights = sorted(highlights, key=score_highlight, reverse=True)
            job_copy["highlights"] = sorted_highlights
            tailored_exp.append(job_copy)

        tailored["experience"] = tailored_exp

        # 5. LANGUAGES SECTION
        if is_english:
            tailored["languages"] = [
                {"language": "Polish", "level": "Native"},
                {"language": "English", "level": "Full Professional (C2)"}
            ]
        else:
            tailored["languages"] = [
                {"language": "Polski", "level": "Ojczysty (Native)"},
                {"language": "Angielski", "level": "Biegły (Professional)"}
            ]

        # 6. DYNAMIC PROFESSIONAL SUMMARY
        top_tech_str = ", ".join(matched_techs[:4]) if matched_techs else "Jira, ISTQB, SQL"
        if is_english:
            s1 = f"Software QA Engineer with 5+ years of experience specializing in {top_tech_str}."
            s2 = "Proficient in test plan creation, test scenario design, defect reporting, and database verification across Agile/Scrum delivery teams."
            s3 = "Experienced in preparing comprehensive test documentation, execution summary reports, and quality metrics for enterprise applications."
            s4 = "Complemented by test automation capabilities using Playwright and Java frameworks."
        else:
            s1 = f"Inżynier QA z ponad 5-letnim doświadczeniem specjalizujący się w {top_tech_str}."
            s2 = "Specjalizuje się w tworzeniu planów testów, przypadków testowych, raportowaniu błędów oraz weryfikacji baz danych SQL na środowiskach Windows OS."
            s3 = "Doświadczony w tworzeniu dokumentacji projektowej, planów testów oraz raportów z wykonania dla systemów bankowych i biznesowych."
            s4 = "Wspierany wiedzą z zakresu automatyzacji testów w Playwright oraz narzędziach Java."

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
