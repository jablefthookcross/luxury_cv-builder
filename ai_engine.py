"""
VitaeCraft AI - AI Engine Module
Handles CV tailoring using Google Gemini API, Ollama (Local LLM), or a Keyword Fallback Engine.
Enforces realistic, candidate-authentic domain mapping without fake certifications or hallucinations.
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
3. Używaj mocnych czasowników wykonawczych (np. "przeprowadziłem", "zbudowałem", "zaprojektowałem", "zoptymalizowałem", "zreprodukowałem", "zautomatyzowałem").
4. NIE zmyślaj stopni naukowych, uczelni ani certyfikatów (np. nie wpisuj certyfikatu ISTQB, jeśli kandydat go nie posiada; zamiast tego wskaż znajomość technik testowania wg standardu ISTQB).
5. Możesz dodawać TYLKO trywialne, bliskie narzędzia będące bezpośrednimi odpowiednikami posiadanych (np. TestRail obok Jira/Xray, Windows OS, Chrome DevTools, Testowanie GUI & Usability, Domena Finansowa/Brokerage).
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

Stanowisko / Rola: {target_role if target_role else 'Manual Tester – Web and Mobile Applications'}

Oferta Pracy:
\"\"\"
{job_description}
\"\"\"

Główny Profil Kandydata (JSON):
\"\"\"
{json.dumps(master_profile, ensure_ascii=False, indent=2)}
\"\"\"

INSTRUKCJA:
1. Przeredaguj podsumowanie zawodowe kandydata, kładąc nacisk na testowanie aplikacji Web i Mobile, GUI/Usability, weryfikację kryteriów akceptacji, współpracę z programistami oraz wsparcie procesów Agile/Scrum.
2. Jeśli oferta wymaga narzędzi pokrewnych (np. TestRail obok Jira/Xray, Windows OS, DevTools), możesz bezpiecznie dopisać je do sekcji umiejętności.
3. NIE dopisuj oficjalnego certyfikatu ISTQB, jeśli kandydat go nie posiada (zamiast tego dopisz w umiejętnościach: "Praktyczna znajomość technik testowania wg standardu ISTQB").
4. Przegrupuj i wyróżnij w doświadczeniu zawodowym testy funkcjonalne, regresyjne, mobilne oraz walidację systemów finansowych, e-commerce i brokerage.
5. Wynik MUSI być poprawnym obiektem JSON zachowującym dokładny schemat (personal_info, summary, skills, experience, education, projects, languages, certifications).
6. NIE zmieniaj imienia (Michał Kosowski), danych kontaktowych ani nazw firm kandydata.

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
        """Domain-aware rule engine for precise QA job tailoring."""
        tailored = json.loads(json.dumps(master_profile))
        job_lower = job_description.lower()

        # Update candidate title if target role specified
        if target_role:
            tailored["personal_info"]["title"] = target_role

        # Detect key offer keywords for smart, legitimate additions
        has_testrail = "testrail" in job_lower
        has_windows = "windows" in job_lower
        has_istqb = "istqb" in job_lower
        has_mobile = "mobile" in job_lower or "mobil" in job_lower
        has_gui = "gui" in job_lower or "usability" in job_lower
        has_finance = any(k in job_lower for k in ["finan", "broker", "invest", "giełd"])

        # Inject adjacent/trivial tools safely into skills
        for skill_cat in tailored.get("skills", []):
            cat_name = skill_cat.get("category", "")
            items = skill_cat.get("items", [])

            if "Narzędzia" in cat_name or "Tools" in cat_name:
                if has_testrail and "TestRail" not in items:
                    items.insert(1, "TestRail")
                if has_windows and "Windows OS" not in items:
                    items.append("Windows OS")
                skill_cat["items"] = items

            elif "Testowanie" in cat_name or "Testing" in cat_name:
                if has_istqb and not any("ISTQB" in i for i in items):
                    items.append("Techniki testowania wg standardu ISTQB")
                if has_mobile and not any("Mobile" in i for i in items):
                    items.insert(0, "Testowanie Aplikacji Mobilnych (Web & Mobile)")
                if has_gui and not any("GUI" in i for i in items):
                    items.insert(1, "Testy GUI & Usability (User Experience)")
                if has_finance and not any("Finan" in i for i in items):
                    items.append("Sektor Finansowy & Brokerage Systems")
                skill_cat["items"] = items

        # Re-sort skills by relevance to offer
        for skill_cat in tailored.get("skills", []):
            items = skill_cat.get("items", [])
            scored_items = sorted(items, key=lambda item: 1 if item.lower() in job_lower else 0, reverse=True)
            skill_cat["items"] = scored_items

        # Tailor summary for Web/Mobile & Financial domain match
        summary_prefix = ""
        if has_mobile and has_finance:
            summary_prefix = "Inżynier QA z ponad 5-letnim doświadczeniem w testowaniu manualnym oraz automatycznym aplikacji webowych i mobilnych (Web & Mobile GUI/Usability), ze szczególnym uwzględnieniem rozwiązań dla sektora finansowego i biur maklerskich (Brokerage). "
        elif has_mobile:
            summary_prefix = "Inżynier QA z ponad 5-letnim doświadczeniem w zapewnianiu jakości cyfrowych kanałów webowych i mobilnych (Web & Mobile) od strony użytkownika końcowego (GUI & Usability). "
        
        if summary_prefix:
            tailored["summary"] = summary_prefix + "Specjalizuje się w weryfikacji kryteriów akceptacji, testach funkcjonalnych, regresyjnych, walidacji API (Postman/Swagger) oraz pracy w zespołach Agile/Scrum przy użyciu narzędzi Jira, Xray oraz TestRail."

        # Keep certifications empty (user doesn't have official certificate)
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
