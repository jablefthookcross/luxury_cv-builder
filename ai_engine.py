"""
VitaeCraft AI - AI Engine Module
Handles CV tailoring using Google Gemini API, Ollama (Local LLM), or a Keyword Fallback Engine.
Enforces Universal Relevance Filtering, 3 Buckets Selection, Smart Content Budgeting, and Language Sync.
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
   - KOSZYK A (MUST HAVE): Technologie i umiejętności wprost wymienione w ofercie (w sekcjach wymagania / technologie / zakres zadań). Te elementy MUSZĄ znaleźć się na samej górze sekcji Skills, Summary oraz w doświadczeniu.
   - KOSZYK B (NICE TO HAVE & VALUE ADD): Twarde umiejętności kandydata z profilu, które wspierają profil oferty (np. znajomość automatyzacji w Playwright przy ofercie manualnej, testy API, SQL, weryfikacja logów, standaryzacja ISTQB). Umieść je jako uzupełnienie.
   - KOSZYK C (IRRELEVANT / NOISE - KATEGORYCZNY ZAKAZ): Narzędzia i domeny całkowicie niezwiązane z analizowaną ofertą (np. Android Studio / Xcode przy ofercie czysto webowej; specyficzna terminologia domenowa typu Brokerage / Finanse / E-commerce, gdy oferta tego nie wymaga). BEZWZGLĘDNIE USUŃ JE Z DANEGO CV.

2. ŚCISŁY LIMIT DŁUGOŚCI (CONTENT BUDGETING):
   - Sekcja Skills: Maksymalnie 6-8 najważniejszych tagów na kategorię. Liczy się trafność, a nie objętość. Tagi muszą być krótkie (1–3 słowa, np. Postman, REST API, Mobile Testing, ISTQB Standards).
   - Professional Summary: Dokładnie 3-4 zwarte, techniczne zdania:
     * Zdanie 1: Rola, lata doświadczenia i główne domeny pasujące do oferty (bez korpo-żargonu i AI-slopu typu "delivering quality assurance").
     * Zdanie 2: Główne technologie z KOSZYKA A i typy testów pasujące do projektu.
     * Zdanie 3: Narzędzia do zgłaszania błędów, CI/CD oraz metodologia (Agile/Scrum).
     * Zdanie 4 (opcjonalnie): Dodatkowy atut z KOSZYKA B (np. automatyzacja w Playwright, bazy danych SQL, znajomość norm testowania).

3. DYNAMICZNA ADAPTACJA DOŚWIADCZENIA (WORK EXPERIENCE):
   - W punktach (bullet points) przy poszczególnych firmach zachowaj realne projekty kandydata, ale zmień kolejność: punkty zawierające technologie z KOSZYKA A przesuwaj na 1. i 2. miejsce na liście dla danego stanowiska.

4. DOPASOWANIE JĘZYKA (LANGUAGE SYNC):
   - Jeśli oferta jest po angielsku -> wygeneruj całą treść CV w 100% po angielsku.
   - Jeśli oferta jest po polsku -> zachowaj angielskie nazewnictwo techniczne (np. Exploratory Testing, Acceptance Criteria, E2E Tests), ale opisy wygeneruj w języku polskim.
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
        return f"""Jesteś doświadczonym Rekruterem IT i Ekspertem Tworzenia Technicznych CV dla dowolnych ról IT (QA, Automation, Manual, Mobile, Pentest, Fullstack).
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
   - Koszyk A (MUST HAVE): Słowa z oferty -> góra sekcji Skills, Summary i początek punktów doświadczenia.
   - Koszyk B (VALUE ADD): Pokrewne twarde umiejętności kandydata -> uzupełnienie.
   - Koszyk C (NOISE): Narzędzia/domeny NIEZWIĄZANE z tą ofertą -> CAŁKOWICIE USUŃ z CV.
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
        english_indicators = ["requirements", "responsibilities", "experience", "skills", "must have", "nice to have"]
        is_english_offer = sum(1 for kw in english_indicators if kw in job_lower) >= 2

        # Role & Domain Detection
        is_mobile = any(k in job_lower for k in ["mobile", "android", "xcode", "ios", "mobil"])
        is_manual = "manual" in job_lower or "manualny" in job_lower
        has_testrail = "testrail" in job_lower
        has_finance = any(k in job_lower for k in ["finan", "broker", "invest", "giełd"])
        has_istqb = "istqb" in job_lower

        if target_role:
            tailored["personal_info"]["title"] = target_role

        # 1. BUCKETS SELECTION & SKILL BUDGETING
        for skill_cat in tailored.get("skills", []):
            cat_name = skill_cat.get("category", "")
            items = skill_cat.get("items", [])

            bucket_a = []
            bucket_b = []

            for item in items:
                item_lower = item.lower()
                # Bucket C Removal: If Android Studio / Xcode but job is not mobile, strip it!
                if ("android studio" in item_lower or "xcode" in item_lower or "mobile logs" in item_lower) and not is_mobile:
                    continue
                # Bucket C Removal: If financial/brokerage but job is not finance, strip it!
                if ("finan" in item_lower or "broker" in item_lower) and not has_finance:
                    continue

                # Shorten tag formatting to 1-3 words
                tag_name = item
                if "ISTQB" in item:
                    tag_name = "ISTQB Standards"
                elif "Mobiln" in item or "Mobile Testing" in item:
                    tag_name = "Mobile Testing"

                if item_lower in job_lower or tag_name.lower() in job_lower:
                    bucket_a.append(tag_name)
                else:
                    bucket_b.append(tag_name)

            # Insert Bucket A items that might be missing from candidate profile if present in offer
            if is_mobile:
                for mob_tool in ["Android Studio", "Xcode", "Mobile Device Logs"]:
                    if mob_tool.lower() in job_lower and mob_tool not in bucket_a:
                        bucket_a.append(mob_tool)
            if has_testrail and "TestRail" not in bucket_a:
                bucket_a.append("TestRail")
            if has_istqb and "ISTQB Standards" not in bucket_a:
                bucket_a.append("ISTQB Standards")

            # Combine Bucket A (Must Have) + Bucket B (Value Add), cap at max 6-8 tags
            combined = bucket_a + [b for b in bucket_b if b not in bucket_a]
            skill_cat["items"] = combined[:8]

        # 2. DYNAMIC WORK EXPERIENCE RE-ORDERING (Bucket A bullets moved to 1st & 2nd place)
        for job in tailored.get("experience", []):
            highlights = job.get("highlights", [])
            scored_highlights = sorted(
                highlights,
                key=lambda h: sum(1 for word in re.findall(r'\b\w+\b', job_lower) if len(word) > 3 and word in h.lower()),
                reverse=True
            )
            job["highlights"] = scored_highlights

        # 3. PROFESSIONAL SUMMARY: Exactly 3-4 tight technical sentences
        if is_english_offer:
            if is_mobile:
                s1 = "Software QA Engineer with 5+ years of experience in manual, exploratory, and mobile application testing."
                s2 = "Specialized in Acceptance Criteria verification, GUI usability testing, and mobile log analysis using Android Studio and Xcode."
                s3 = "Proficient in defect tracking via Jira, Xray, and TestRail within Agile/Scrum delivery teams."
                s4 = "Backed by hands-on experience in REST API validation (Postman/Swagger) and Playwright automation in TypeScript."
            elif is_manual:
                s1 = "Software QA Engineer with 5+ years of experience delivering quality assurance for web and mobile digital platforms."
                s2 = "Expert in test case design, exploratory testing, and acceptance criteria verification."
                s3 = "Experienced in defect management using Jira, Xray, and TestRail in Agile/Scrum environments."
                s4 = "Complemented by REST API validation (Postman/Swagger) and Playwright automation capabilities."
            else:
                s1 = "Software QA Engineer with 5+ years of experience in test automation and quality assurance for web platforms."
                s2 = "Skilled in E2E web automation using Playwright (TypeScript) and REST API validation."
                s3 = "Proficient in CI/CD pipeline integration, Git, and defect tracking in Jira/Xray."
                s4 = "Committed to delivering high-performance, resilient software products in Agile teams."
            tailored["summary"] = f"{s1} {s2} {s3} {s4}"
        else:
            if is_mobile:
                s1 = "Inżynier QA z ponad 5-letnim doświadczeniem w testowaniu manualnym oraz eksploracyjnym aplikacji mobilnych i webowych."
                s2 = "Specjalizuje się w weryfikacji kryteriów akceptacji (Acceptance Criteria), testach GUI & Usability oraz analizie logów urządzeń mobilnych (Android Studio, Xcode)."
                s3 = "Sprawnie zarządza błędami i dokumentacją testową w narzędziach Jira, Xray oraz TestRail w zespole Agile/Scrum."
                s4 = "Posiada dodatkowe doświadczenie w walidacji REST API (Postman/Swagger) oraz automatyzacji w Playwright (TypeScript)."
            elif is_manual:
                s1 = "Inżynier QA z ponad 5-letnim doświadczeniem w testach manualnych, eksploracyjnych oraz walidacji wymagań dla aplikacji cyfrowych."
                s2 = "Ekspert w projektowaniu przypadków testowych, weryfikacji kryteriów akceptacji oraz testach regresyjnych."
                s3 = "Odpowiedzialny za śledzenie błędów i tworzenie dokumentacji w Jira, Xray i TestRail w środowisku Agile/Scrum."
                s4 = "Wspierany praktyczną znajomością testów REST API (Postman/Swagger) oraz automatyzacji w Playwright."
            else:
                s1 = "Inżynier QA z ponad 5-letnim doświadczeniem w zapewnianiu jakości oraz automatyzacji testów aplikacji webowych i mobilnych."
                s2 = "Specjalizuje się w automatyzacji E2E w Playwright (TypeScript) oraz kompleksowych testach REST API."
                s3 = "Pracuje w oparciu o rurociągi CI/CD (GitLab CI/GitHub Actions) i metodologię Agile/Scrum z narzędziami Jira i Xray."
                s4 = "Zorientowany na dostarczanie niezawodnego i wydajnego oprogramowania zgodnego z wymaganiami biznesowymi."
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
