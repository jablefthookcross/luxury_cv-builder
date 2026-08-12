"""
VitaeCraft AI - AI Engine Module
Handles CV tailoring using Google Gemini API, Ollama (Local LLM), or a Keyword Fallback Engine.
Enforces realistic, candidate-authentic domain mapping, dynamic domain cleaning, and concise skill tags.
"""

import os
import re
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

ANTI_AI_PROMPT_DIRECTIVE = """
Rygorystyczne Zasady Pisania (Język Polski / Angielski):
1. Piszesz naturalnym, profesjonalnym, bezpośrednim i autentycznym głosem doświadczonego inżyniera QA.
2. ZAKAZ UŻYWANIA sztucznych zwrotów AI i korpo-jargonu, takich jak: "zagłębił się w", "jest świadectwem", "tkanina sukcesu", "transformacyjna podróż", "synergiczne rozwiązania", "przełomowy projekt", "pasjonat kodu".
3. DYNAMIC DOMAIN CLEANING: Nie przenoś nazw konkretnych branż (np. "sektor finansowy", "biura maklerskie", "e-commerce") do sekcji Summary ani Skills, CHYBA ŻE branża ta jest wprost wymagana w wklejonej ofercie pracy. W przeciwnym razie używaj ogólnych sformułowań (np. "aplikacje o wysokim stopniu złożoności", "rozwój cyfrowych platform web i mobile").
4. MOBILE TESTING & DEBUGGING FOCUS: Jeśli oferta dotyczy stanowiska "Manual Tester" lub "Mobile Tester" i wymaga narzędzi do debugowania (np. Android Studio, Xcode, logi urządzeń), WYEKSPONUJ te narzędzia na samym początku sekcji Narzędzia & Systemy oraz w spisie umiejętności.
5. FORMATOWANIE TAGÓW (SKILLS): Skracaj nazwy umiejętności w tagach/pigułkach do maksymalnie 2-3 wyrazów (np. zamień "Techniki testowania wg standardu ISTQB" na "ISTQB Standards", a "Testowanie Aplikacji Mobilnych (Web & Mobile)" na "Mobile Testing"), aby uniknąć rozbijania layoutu w lewej kolumnie.
6. STRICT ROLE ALIGNMENT: Jeśli oferta dotyczy głównie testów manualnych, w sekcji Summary stawiaj na pierwszym miejscu testy eksploracyjne, weryfikację kryteriów akceptacji (Acceptance Criteria), analizę logów i zgłaszanie błędów, a automatyzację (Playwright) traktuj jako dodatek/uzupełnienie.
7. NIE zmyślaj stopni naukowych, uczelni ani oficjalnych certyfikatów (np. nie wpisuj certyfikatu ISTQB, jeśli kandydat go nie posiada; używaj tagu "ISTQB Standards").
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
        return f"""Jesteś doświadczonym Rekruterem IT i Ekspertem Tworzenia Technicznych CV dla Inżynierów QA.
Twoim zadaniem jest dopasowanie Głównego Profilu Kandydata do podanej Oferty Pracy.

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

INSTRUKCJA:
1. Zastosuj DYNAMIC DOMAIN CLEANING: Usunięcie starych branż (np. finanse, e-commerce), jeśli oferta ich nie wymaga.
2. MOBILE & MANUAL FOCUS: Jeśli oferta to Manual Tester / Mobile, postaw na pierwszym miejscu testy eksploracyjne, weryfikację kryteriów akceptacji i logi urządzeń (Android Studio, Xcode).
3. TAG FORMATTING: Wszystkie tagi umiejętności muszą mieć max 2-3 wyrazy (np. "Mobile Testing", "ISTQB Standards", "Android Studio").
4. NIE zmieniaj imienia (Michał Kosowski), danych kontaktowych ani nazw firm kandydata.

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
        """Domain-aware rule engine for precise QA job tailoring with dynamic cleaning."""
        tailored = json.loads(json.dumps(master_profile))
        job_lower = job_description.lower()

        # Update candidate title if target role specified
        if target_role:
            tailored["personal_info"]["title"] = target_role

        # Detect offer characteristics
        is_manual = "manual" in job_lower or "manualny" in job_lower
        is_mobile = "mobile" in job_lower or "mobil" in job_lower or "android" in job_lower or "xcode" in job_lower
        has_testrail = "testrail" in job_lower
        has_finance = any(k in job_lower for k in ["finan", "broker", "invest", "giełd"])
        has_istqb = "istqb" in job_lower

        # Dynamic Domain Cleaning & Skill Formatting
        for skill_cat in tailored.get("skills", []):
            cat_name = skill_cat.get("category", "")
            items = skill_cat.get("items", [])

            # Format item tags to max 2-3 words
            formatted_items = []
            for item in items:
                if item == "Testowanie Aplikacji Mobilnych (Web & Mobile)" or item == "Testowanie Aplikacji Mobilnych":
                    formatted_items.append("Mobile Testing")
                elif "ISTQB" in item:
                    formatted_items.append("ISTQB Standards")
                elif item == "Sektor Finansowy & Brokerage Systems":
                    if has_finance:
                        formatted_items.append("Financial Systems")
                else:
                    formatted_items.append(item)

            if is_mobile:
                if "Android Studio" not in formatted_items:
                    formatted_items.insert(0, "Android Studio")
                if "Xcode" not in formatted_items:
                    formatted_items.insert(1, "Xcode")
                if "Mobile Logs" not in formatted_items and "Mobile Device Logs" not in formatted_items:
                    formatted_items.insert(2, "Mobile Device Logs")

            if has_testrail and "TestRail" not in formatted_items:
                formatted_items.insert(0, "TestRail")

            if has_istqb and "ISTQB Standards" not in formatted_items:
                formatted_items.append("ISTQB Standards")

            skill_cat["items"] = formatted_items

        # Re-sort skills by relevance
        for skill_cat in tailored.get("skills", []):
            items = skill_cat.get("items", [])
            scored_items = sorted(items, key=lambda item: 1 if item.lower() in job_lower else 0, reverse=True)
            skill_cat["items"] = scored_items

        # Dynamic Summary Construction
        if is_manual and is_mobile:
            summary = "Inżynier QA z ponad 5-letnim doświadczeniem w testowaniu manualnym oraz eksploracyjnym aplikacji mobilnych i webowych. Specjalizuje się w weryfikacji kryteriów akceptacji (Acceptance Criteria), analizie logów urządzeń (Android Studio / Xcode), weryfikacji integracji REST API (Postman/Swagger) oraz zgłaszaniu i śledzeniu defektów w narzędziach Jira, Xray i TestRail w środowisku Agile/Scrum. Posiada praktyczne doświadczenie w automatyzacji testów w Playwright (TypeScript)."
        elif is_manual:
            summary = "Inżynier QA z ponad 5-letnim doświadczeniem w testach manualnych, eksploracyjnych oraz walidacji kryteriów akceptacji dla aplikacji webowych i mobilnych. Ekspert w zgłaszaniu defektów, analizie logów i dokumentowaniu przypadków testowych w narzędziach Jira, Xray i TestRail w zespole Agile/Scrum, wspierany znajomością testów REST API oraz automatyzacji w Playwright."
        else:
            summary = master_profile.get("summary", "")

        # Apply domain cleaning: only include finance/brokerage if in job description
        if not has_finance:
            summary = summary.replace("ze szczególnym uwzględnieniem rozwiązań dla sektora finansowego i biur maklerskich (Brokerage). ", "")
            summary = summary.replace("sektora finansowego i biur maklerskich", "rozwijania cyfrowych platform o wysokiej złożoności")

        tailored["summary"] = summary
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
