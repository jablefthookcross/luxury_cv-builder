"""
VitaeCraft AI - AI Engine Module
Handles CV tailoring using Google Gemini API, Ollama (Local LLM), or a Keyword Fallback Engine.
Enforces 3 Buckets Selection, Smart Content Budgeting, Bucket C Noise Removal, and State Synchronization.
"""

import os
import re
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List, Set

ANTI_AI_PROMPT_DIRECTIVE = """
GŁÓWNA LOGIKA SELEKCJI DANYCH I BUDŻETOWANIA TREŚCI (CORE RULES):

1. ZASADA 3 KOSZYKÓW DLA UMIEJĘTNOŚCI I NARZĘDZI (3 BUCKETS SELECTION):
   - KOSZYK A (MUST HAVE): Technologie i umiejętności wprost wymienione w ofercie (np. SQL, SoapUI, Postman, Jira Xray, REST/SOAP API). Te elementy MUSZĄ znaleźć się na samej górze sekcji Skills, Summary oraz w doświadczeniu.
   - KOSZYK B (NICE TO HAVE & VALUE ADD): Twarde umiejętności kandydata z profilu wspierające rolę (np. automatyzacja w Playwright, SQL, DBeaver, ISTQB Standards).
   - KOSZYK C (IRRELEVANT / NOISE - KATEGORYCZNY ZAKAZ): Narzędzia i domeny całkowicie niezwiązane z analizowaną ofertą (np. Android Studio / Xcode / Mobile Device Logs przy ofercie backendowej/integracyjnej/webowej; specyficzna terminologia finansowa przy ofercie rejestrów publicznych). BEZWZGLĘDNIE USUŃ JE Z CV.

2. ŚCISŁY LIMIT DŁUGOŚCI (CONTENT BUDGETING):
   - Sekcja Skills: Maksymalnie 6-8 najważniejszych tagów na kategorię (tagi 1–3 słowa, np. SoapUI, Postman, REST API, Jira (Xray)).
   - Professional Summary: Dokładnie 3-4 zwarte, techniczne zdania:
     * Zdanie 1: Rola, lata doświadczenia i główne obszary testów pasujące do oferty.
     * Zdanie 2: Główne technologie z KOSZYKA A (SQL, SoapUI, Postman, SOAP/REST API).
     * Zdanie 3: Narzędzia śledzenia błędów (Jira Xray), dokumentacja testowa oraz metodologia Agile/Scrum.
     * Zdanie 4: Dodatkowy atut z KOSZYKA B (automatyzacja w Playwright, DBeaver/SQL).

3. DYNAMICZNA ADAPTACJA DOŚWIADCZENIA (WORK EXPERIENCE):
   - Punkty (bullet points) zawierające technologie z KOSZYKA A (SQL, SoapUI, API, Xray) przesuwaj na 1. i 2. miejsce na liście w poszczególnych firmach.

4. DOPASOWANIE JĘZYKA (LANGUAGE SYNC):
   - Jeśli oferta jest po angielsku -> wygeneruj całą treść CV w 100% po angielsku.
   - Jeśli po polsku -> opisy po polsku z angielskimi pojęciami technicznymi.
"""

class AIEngine:
    def __init__(self, provider: str = "auto", gemini_key: Optional[str] = None, ollama_url: str = "http://localhost:11434"):
        self.provider = provider
        self.gemini_key = gemini_key or os.environ.get("GEMINI_API_KEY", "")
        self.ollama_url = ollama_url
        self.ollama_model = os.environ.get("OLLAMA_MODEL", "llama3.2")

    def tailor_cv(self, master_profile: Dict[str, Any], job_description: str, target_role: str = "") -> Dict[str, Any]:
        """
        Tailors the candidate's master profile for a specific job offer.
        Returns a customized profile dictionary.
        """
        provider_to_use = self._determine_provider()
        print(f"[AIEngine] Tailoring CV using provider: {provider_to_use}")

        if provider_to_use == "gemini":
            try:
                return self._tailor_with_gemini(master_profile, job_description, target_role)
            except Exception as e:
                print(f"[AIEngine Warning] Gemini call failed ({e}). Falling back to Rule Engine.")
                return self._tailor_with_fallback(master_profile, job_description, target_role)

        elif provider_to_use == "ollama":
            try:
                return self._tailor_with_ollama(master_profile, job_description, target_role)
            except Exception as e:
                print(f"[AIEngine Warning] Ollama call failed ({e}). Falling back to Rule Engine.")
                return self._tailor_with_fallback(master_profile, job_description, target_role)

        else:
            return self._tailor_with_fallback(master_profile, job_description, target_role)

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
        return f"""Jesteś doświadczonym Rekruterem IT i Ekspertem Tworzenia Technicznych CV dla dowolnych ról IT.
Twoim zadaniem jest dopasowanie Głównego Profilu Kandydata do podanej Oferty Pracy z zastosowaniem uniwersalnych zasad Relevance Filtering & Smart Content Budgeting.

{ANTI_AI_PROMPT_DIRECTIVE}

Stanowisko / Rola: {target_role if target_role else 'Opisane w ofercie'}

Oferta Pracy:
\"\"\"
{job_description}
\"\"\"

Główny Profil Kandydata (JSON):
\"\"\"
{json.dumps(master_profile, ensure_ascii=False, indent=2)}
\"\"\"

INSTRUKCJA SELEKCJI I BUDŻETOWANIA:
1. Zastosuj ZASADĘ 3 KOSZYKÓW:
   - Koszyk A (MUST HAVE): SQL, SoapUI, Postman, Jira Xray, REST/SOAP API, Test Documentation -> góra sekcji Skills, Summary i początek punktów doświadczenia.
   - Koszyk B (VALUE ADD): Pokrewne twarde umiejętności kandydata (Playwright, TypeScript, DBeaver, ISTQB Standards).
   - Koszyk C (NOISE): Narzędzia/domeny NIEZWIĄZANE z tą ofertą (np. Android Studio / Xcode / Mobile Logs, jeśli oferta dotyczy integracji/backendu/webu) -> CAŁKOWICIE USUŃ z CV.
2. LIMIT CONTENT BUDGETING: Max 6-8 tagów na kategorię skills (tagi max 1-3 słowa). Summary dokładnie 3-4 zwarte, techniczne zdania.
3. DYNAMIC EXPERIENCE: Zmień kolejność bullet points w firmach, tak by te z technologiami z Koszyka A były na 1. i 2. miejscu.
4. LANGUAGE SYNC: Jeśli oferta jest po angielsku -> wygeneruj CV w 100% po angielsku. Jeśli po polsku -> opisy po polsku z angielskimi pojęciami technicznymi.
5. NIE zmieniaj imienia (Michał Kosowski), danych kontaktowych ani nazw firm kandydata.

Zwróć TYLKO czysty obiekt JSON. Nie używaj znaczników markdown ```json.
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

    def _tailor_with_fallback(self, master_profile: Dict[str, Any], job_description: str, target_role: str = "") -> Dict[str, Any]:
        """Universal Rule Engine implementing 3-Buckets Selection & Content Budgeting."""
        tailored = json.loads(json.dumps(master_profile))
        job_lower = job_description.lower()

        # Language Detection
        english_indicators = ["requirements", "responsibilities", "experience", "skills", "must have", "nice to have", "proficient", "knowledge of"]
        is_english_offer = sum(1 for kw in english_indicators if kw in job_lower) >= 2

        # Role & Technology Detection
        is_mobile = any(k in job_lower for k in ["mobile", "android", "xcode", "ios", "mobil"])
        has_soap = "soap" in job_lower or "soapui" in job_lower
        has_sql = "sql" in job_lower
        has_xray = "xray" in job_lower
        has_postman = "postman" in job_lower
        has_testrail = "testrail" in job_lower
        has_finance = any(k in job_lower for k in ["finan", "broker", "invest", "giełd"])
        has_istqb = "istqb" in job_lower

        if target_role:
            tailored["personal_info"]["title"] = target_role

        # 1. BUCKETS SELECTION & SKILL BUDGETING
        new_skills = []

        # Category 1: Testing & API
        testing_items = []
        if has_soap:
            testing_items.extend(["SOAP & REST API Testing", "SoapUI", "Postman"])
        elif has_postman:
            testing_items.extend(["REST API Testing", "Postman", "Swagger"])
        else:
            testing_items.extend(["REST API Testing", "Postman"])

        if has_sql:
            testing_items.append("SQL Database Verification")

        testing_items.extend(["Integration Testing", "Functional Testing", "Regression Testing", "ISTQB Standards"])
        if is_mobile:
            testing_items.insert(0, "Mobile Testing")

        new_skills.append({
            "category": "Testing & API",
            "items": testing_items[:8]
        })

        # Category 2: Tools & Test Management
        tools_items = []
        if has_xray:
            tools_items.append("Jira (Xray)")
        else:
            tools_items.append("Jira")

        tools_items.extend(["Confluence", "Git"])
        if has_sql:
            tools_items.append("SQL Developer / DBeaver")

        tools_items.append("Test Documentation & Reporting")

        if is_mobile:
            tools_items.extend(["Android Studio", "Xcode", "Mobile Device Logs"])

        if has_testrail:
            tools_items.append("TestRail")

        tools_items.append("Docker")

        # STRIP BUCKET C: If not mobile, remove Android Studio / Xcode / Mobile Logs!
        if not is_mobile:
            tools_items = [t for t in tools_items if t not in ["Android Studio", "Xcode", "Mobile Device Logs"]]

        new_skills.append({
            "category": "Tools & Test Management",
            "items": tools_items[:8]
        })

        # Category 3: Automation & Languages (Secondary / Value Add)
        auto_items = ["SQL", "Playwright", "TypeScript", "JavaScript", "GitLab CI/CD", "GitHub Actions"]
        new_skills.append({
            "category": "Automation & Languages",
            "items": auto_items[:8]
        })

        tailored["skills"] = new_skills

        # 2. DYNAMIC WORK EXPERIENCE RE-ORDERING (Bucket A bullets moved to 1st & 2nd place)
        for job in tailored.get("experience", []):
            highlights = job.get("highlights", [])

            # Inject SoapUI / SQL / Xray context into highlights if matching offer
            if has_soap and not any("SoapUI" in h or "SOAP" in h for h in highlights):
                highlights.insert(0, "Wykonywanie testów integracyjnych i walidacji usług API (REST & SOAP) przy użyciu narzędzi Postman oraz SoapUI.")
            if has_sql and not any("SQL" in h for h in highlights):
                highlights.insert(1, "Przeprowadzanie weryfikacji bazy danych za pomocą zapytań SQL w celu weryfikacji poprawności przesyłania danych backendowych.")

            scored_highlights = sorted(
                highlights,
                key=lambda h: sum(1 for word in ["sql", "soapui", "soap", "postman", "xray", "api", "integration", "mobile"] if word in h.lower()),
                reverse=True
            )
            job["highlights"] = scored_highlights

        # 3. PROFESSIONAL SUMMARY: Exactly 3-4 tight technical sentences
        if is_english_offer or (has_soap and has_sql):
            s1 = "QA Engineer with 5+ years of experience in manual, integration, and API testing (REST & SOAP)."
            s2 = "Proficient in backend verification and database testing using SQL, test scenario design, and end-to-end defect tracking in Jira and Xray within Agile/Scrum methodologies."
            s3 = "Experienced in preparing comprehensive test documentation, plans, and summary reports for enterprise systems."
            s4 = "Complemented by test automation experience using Playwright in TypeScript."
            tailored["summary"] = f"{s1} {s2} {s3} {s4}"
        elif is_mobile:
            s1 = "Software QA Engineer with 5+ years of experience in manual, exploratory, and mobile application testing."
            s2 = "Specialized in Acceptance Criteria verification, GUI usability testing, and mobile log analysis using Android Studio and Xcode."
            s3 = "Proficient in defect tracking via Jira, Xray, and TestRail within Agile/Scrum delivery teams."
            s4 = "Backed by hands-on experience in REST API validation (Postman/Swagger) and Playwright automation in TypeScript."
            tailored["summary"] = f"{s1} {s2} {s3} {s4}"
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
