"""
VitaeCraft AI - Job Intelligence & Requirement Extractor (Etap 1)
Extracts clean, structured Job Specifications from any raw job offer text.
Supports Google Gemini Structured Outputs and a deterministic QA Domain NLP Extractor.
"""

import os
import re
import json
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from pathlib import Path

APP_DIR = Path(__file__).parent
CATALOG_PATH = APP_DIR / "it_terms_catalog.json"

PROMPT_JOB_EXTRACTION = """
Jesteś starszym architektem rekrutacji technicznej w obszarze QA / Software Engineering.
Twoim zadaniem jest precyzyjna analiza surowego tekstu ogłoszenia o pracę i wyekstrahowanie kluczowych wymagań technicznych.

Zwróć WYŁĄCZNIE poprawny obiekt JSON o następującej strukturze:
{
  "target_role": "Dokładna nazwa stanowiska z ogłoszenia (np. Senior Test Engineer-QA (UI & API), Tester Oprogramowania)",
  "seniority": "Junior / Mid / Senior / Lead",
  "domain": "Branża/obszar (np. E-commerce, Banking, Cloud SaaS, Telecom, General QA)",
  "primary_technologies": ["Główne technologie i języki programowania wymagane w ofercie, np. C#, Playwright, JMeter, SQL"],
  "secondary_technologies": ["Narzędzia wspierające i technologie mile widziane, np. Docker, Jenkins, RabbitMQ, Selenoid"],
  "testing_types": ["Rodzaje testów z ogłoszenia, np. Automatyzacja UI & API, Testy Wydajnościowe (Load & Stress), Testy Regresyjne, UAT"],
  "tools": ["Narzędzia do zarządzania testami i środowiska, np. Jira (Xray), Git, Linux / Windows OS, Postman"],
  "key_responsibilities": [
    "3 do 5 kluczowych odpowiedzialności inżynierskich z ogłoszenia"
  ]
}
"""

def clean_raw_job_text(text: str) -> str:
    """Removes standard recruitment noise (GDPR/RODO clauses, footer links, benefit pills)."""
    if not text:
        return ""
    lines = text.splitlines()
    cleaned = []
    noise_patterns = [
        r"(wyrażam zgodę na przetwarzanie|rodo|gdpr|klauzula informacyjna)",
        r"(o firmie|nasz klient to|przewiń do profilu firmy|aplikuj|benefity:)",
        r"(kawa / herbata|parking|paczki świąteczne|dofinansowanie|karta sportowa|multisport|medicover)",
        r"(etapy rekrutacji|sprawdź, jak dobrze ta oferta|zobacz podsumowanie oferty)"
    ]
    for line in lines:
        l_str = line.strip()
        if not l_str:
            continue
        if any(re.search(p, l_str, re.IGNORECASE) for p in noise_patterns):
            continue
        cleaned.append(l_str)
    return "\n".join(cleaned)


def clean_target_role(role: str) -> str:
    """Sanitizes job role title, removing gender tags, brackets and redundant noise."""
    if not role:
        return "Senior QA Engineer"
    clean = str(role).strip()
    
    # 1. Remove gender indicators in brackets: (f/m), (m/f), (k/m), (m/k), (f/m/d), (m/w/d), (d/f/m), (k/m/inny), (f/m/x), etc.
    clean = re.sub(r'\s*\([fmkdwdxy\s/,\-–—]+\)', '', clean, flags=re.IGNORECASE)
    
    # 2. Normalize dual gender slashes
    clean = re.sub(r'\bTester\s*/\s*Testerka\b', 'Tester', clean, flags=re.IGNORECASE)
    clean = re.sub(r'\bTesterka\s*/\s*Tester\b', 'Tester', clean, flags=re.IGNORECASE)
    clean = re.sub(r'\bSpecjalista\s*/\s*Specjalistka\b', 'Specjalista', clean, flags=re.IGNORECASE)
    clean = re.sub(r'\bSpecjalistka\s*/\s*Specjalista\b', 'Specjalista', clean, flags=re.IGNORECASE)
    clean = re.sub(r'\bInżynier\s*/\s*Inżynierka\b', 'Inżynier', clean, flags=re.IGNORECASE)
    clean = re.sub(r'\bInżynierka\s*/\s*Inżynier\b', 'Inżynier', clean, flags=re.IGNORECASE)
    clean = re.sub(r'\bDeveloper\s*/\s*Developerka\b', 'Developer', clean, flags=re.IGNORECASE)
    clean = re.sub(r'\bDeveloperka\s*/\s*Developer\b', 'Developer', clean, flags=re.IGNORECASE)
    
    # 3. Phrasing fixes
    clean = re.sub(r'aplikacji webowej', 'Aplikacji Webowych', clean, flags=re.IGNORECASE)
    clean = re.sub(r'aplikacji mobilnej', 'Aplikacji Mobilnych', clean, flags=re.IGNORECASE)
    
    # 4. Clean trailing / leading punctuation
    clean = re.sub(r'[\s\-–—/|:]+$', '', clean).strip()
    clean = re.sub(r'^[\s\-–—/|:]+', '', clean).strip()
    
    # Deduplicate repeated words like "Oprogramowania Oprogramowania"
    clean = re.sub(r'\b(\w+)\s+\1\b', r'\1', clean, flags=re.IGNORECASE)
    
    if clean.lower() in ["tester", "testerka", "qa", "qa tester"]:
        clean = "Tester Oprogramowania"
    return clean or "Senior QA Engineer"


class JobExtractor:
    @staticmethod
    def detect_language(text: str) -> str:
        """Accurately determines whether the job offer is in Polish or English."""
        text_lower = text.lower()
        pl_markers = ["w", "z", "oraz", "doświadczenie", "wymagania", "zakres", "obowiązków", "praca", "umowa", "mile", "widziane", "zespół", "znajomość", "będziesz", "oferujemy", "posiadasz", "twój", "nasze"]
        en_markers = ["and", "with", "experience", "requirements", "responsibilities", "skills", "knowledge", "team", "working", "looking", "candidate", "about", "offer", "we are", "you will", "role", "years"]
        
        pl_score = sum(len(re.findall(r'\b' + m + r'\b', text_lower)) for m in pl_markers)
        en_score = sum(len(re.findall(r'\b' + m + r'\b', text_lower)) for m in en_markers)
        
        return "en" if en_score > pl_score else "pl"

    @staticmethod
    def extract(job_text: str, gemini_key: str = "", provider: str = "auto") -> Dict[str, Any]:
        """
        Main extraction entry point.
        Uses Gemini Flash API when key is available; otherwise falls back to the deterministic NLP parser.
        """
        cleaned_text = clean_raw_job_text(job_text)
        detected_lang = JobExtractor.detect_language(cleaned_text or job_text)
        if not cleaned_text.strip():
            empty = JobExtractor._empty_spec()
            empty["detected_language"] = detected_lang
            return empty

        api_key = gemini_key or os.environ.get("GEMINI_API_KEY", "")

        if provider in ["gemini", "auto"] and api_key.strip():
            try:
                spec = JobExtractor._extract_with_gemini(cleaned_text, api_key.strip())
                if spec and spec.get("target_role"):
                    spec["detected_language"] = detected_lang
                    return spec
            except Exception as e:
                print(f"[JobExtractor] Gemini extraction failed: {e}. Falling back to Rule-Based NLP.")

        spec = JobExtractor._extract_with_nlp(cleaned_text)
        spec["detected_language"] = detected_lang
        return spec

    @staticmethod
    def _extract_with_gemini(cleaned_text: str, api_key: str) -> Dict[str, Any]:
        """Calls Gemini Flash API with Structured JSON Outputs."""
        models_to_try = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
        last_error = None

        for model in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {"text": f"{PROMPT_JOB_EXTRACTION}\n\nOFERTA PRACY:\n{cleaned_text}"}
                        ]
                    }
                ],
                "generationConfig": {
                    "response_mime_type": "application/json",
                    "temperature": 0.1,
                    "max_output_tokens": 1200
                }
            }

            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            try:
                with urllib.request.urlopen(req, timeout=12) as response:
                    raw_resp = response.read().decode("utf-8")
                    data = json.loads(raw_resp)
                    text_content = data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(text_content)
                    return JobExtractor._sanitize_spec(parsed)
            except Exception as e:
                last_error = e
                continue

        raise RuntimeError(f"All Gemini models failed: {last_error}")

    @staticmethod
    def _extract_with_nlp(cleaned_text: str) -> Dict[str, Any]:
        """
        Deterministic, high-accuracy QA domain extractor.
        Dynamically scans text against the full it_terms_catalog.json.
        """
        lines = [l.strip() for l in cleaned_text.splitlines() if l.strip()]
        text_lower = cleaned_text.lower()

        # 1. Target Role Detection & Normalization
        target_role = ""
        role_candidates = [
            "senior test engineer-qa (ui & api)", "senior test engineer", "qa automation engineer",
            "senior qa engineer", "senior qa specialist", "tester / testerka", "testerka / tester",
            "tester oprogramowania", "manual software tester", "tester aplikacji webowej", "tester aplikacji webowych",
            "test and analysis engineer", "software qa engineer", "qa engineer", "tester"
        ]
        for line in lines[:6]:
            l_low = line.lower()
            for cand in role_candidates:
                if cand in l_low and len(line) < 70:
                    target_role = line
                    break
            if target_role:
                break
        if not target_role:
            target_role = lines[0] if lines and len(lines[0]) < 50 else "Tester Oprogramowania"

        # Clean & Normalize target role
        target_role = clean_target_role(target_role)

        # 2. Seniority Detection
        seniority = "Mid / Regular"
        if any(w in text_lower for w in ["senior", "starszy", "lead", "principal", "3+ years", "5+ lat", "5+ years", "minimum 3 lata", "min. 3 lata"]):
            seniority = "Senior / Mid"
        elif any(w in text_lower for w in ["junior", "młodszy", "stażysta", "intern"]):
            seniority = "Junior"

        # 3. Domain Detection (iGaming / Healthcare / MedTech / Banking / E-commerce / Cloud)
        domain = "Quality Assurance & IT"
        if any(w in text_lower for w in ["igaming", "gaming", "gry", "rozrywka online", "wazdan"]):
            domain = "iGaming & Rozrywka Cyfrowa (Aplikacje Webowe)"
        elif any(w in text_lower for w in ["zdrowi", "medyczn", "ochron[ay] zdrowia", "szpital", "hl7", "fhir", "rejestrów medycznych", "rejestr publiczn"]):
            domain = "Ochrona Zdrowia & MedTech (Rejestry Publiczne)"
        elif any(w in text_lower for w in ["bank", "bankow", "finans", "fintech", "maklersk"]):
            domain = "Bankowość & Finanse"
        elif any(w in text_lower for w in ["e-commerce", "sklep", "logistyk", "magazyn", "retail"]):
            domain = "E-Commerce & Logistyka"
        elif any(w in text_lower for w in ["mobile", "ios", "android", "aosp"]):
            domain = "Aplikacje Mobilne"
        elif any(w in text_lower for w in ["cloud", "saas", "microservices", "mikroserwis"]):
            domain = "Cloud & Systemy Rozproszone"

        # 4. Dynamic Catalog Scanning from it_terms_catalog.json
        catalog_path = Path(__file__).parent / "it_terms_catalog.json"
        catalog = {}
        if catalog_path.exists():
            try:
                with open(catalog_path, "r", encoding="utf-8") as f:
                    catalog = json.load(f)
            except Exception:
                pass

        primary_tech = []
        secondary_tech = []
        testing_types = []
        tools = []

        # Helper for strict regex boundary
        def has_kw(kw: str) -> bool:
            kw_clean = kw.strip().lower()
            if not kw_clean:
                return False
            # Escape regex special characters, except handle c#, c++, .net specially
            if kw_clean == "c#":
                return bool(re.search(r'(\bc#|\.net\b)', text_lower))
            if kw_clean in [".net", "c++"]:
                return bool(re.search(r'(?:\b|\s)' + re.escape(kw_clean) + r'(?:\b|\s)', text_lower))
            if len(kw_clean) <= 3:
                return bool(re.search(r'\b' + re.escape(kw_clean) + r'\b', text_lower))
            return kw_clean in text_lower

        # Scan testing types & API
        for kw, label in catalog.get("testing_and_api", {}).items():
            if has_kw(kw):
                if any(k in label.lower() for k in ["api", "soap", "rest", "hl7", "postman", "swagger"]):
                    if label not in primary_tech:
                        primary_tech.append(label)
                else:
                    if label not in testing_types:
                        testing_types.append(label)

        # Scan automation frameworks
        for kw, label in catalog.get("automation_frameworks", {}).items():
            if has_kw(kw):
                if label not in primary_tech:
                    primary_tech.append(label)

        # Scan programming languages
        for kw, label in catalog.get("programming_languages", {}).items():
            if has_kw(kw):
                if label not in primary_tech:
                    primary_tech.append(label)

        # Scan tools and management
        for kw, label in catalog.get("tools_and_management", {}).items():
            if has_kw(kw):
                if any(ci in label.lower() for ci in ["ci/cd", "docker", "jenkins", "gitlab", "github", "kubernetes"]):
                    if label not in secondary_tech:
                        secondary_tech.append(label)
                else:
                    if label not in tools:
                        tools.append(label)

        # Scan databases and diagnostics
        for kw, label in catalog.get("databases_and_diagnostics", {}).items():
            if has_kw(kw):
                if "sql" in label.lower() or "oracle" in label.lower() or "postgre" in label.lower():
                    if label not in primary_tech:
                        primary_tech.append(label)
                else:
                    if label not in secondary_tech:
                        secondary_tech.append(label)

        # Responsibilities synthesis
        responsibilities = []
        for l in lines:
            if any(act in l.lower() for act in ["projektowanie", "realizacja", "tworzenie", "building", "designing", "executing", "maintaining", "przeprowadzanie", "automatyzacja", "raportowanie", "weryfikacja", "testowanie"]):
                if 15 < len(l) < 120 and l not in responsibilities:
                    responsibilities.append(l)
                    if len(responsibilities) >= 4:
                        break
        if not responsibilities:
            responsibilities = [
                f"Projektowanie i realizacja testów dla platformy {domain}",
                "Weryfikacja jakości oprogramowania i dokumentowanie defektów",
                "Współpraca z zespołem technicznym w metodyce Agile"
            ]

        # Clean duplicates and canonical clusters
        def deduplicate_canonical_terms(terms_list: List[str]) -> List[str]:
            clean_res = []
            seen_clusters = set()
            clusters = [
                {"rest & soap api", "rest api", "soap api", "testy api (rest & soap)", "testy api", "api testing"},
                {"testy aplikacji mobilnych (ios/android)", "testowanie ios", "testowanie android", "ios testing", "android testing", "mobile testing"},
                {"ci/cd pipelines", "ci/cd", "ci / cd"},
                {"selenium webdriver", "selenium"},
                {"sql (weryfikacja danych)", "sql (database verification)", "sql"},
                {"scenariusze & przypadki testowe", "przypadki testowe", "scenariusze testowe", "test scenarios & test cases", "test scenarios", "test cases"}
            ]
            for t in terms_list:
                t_clean = t.strip()
                t_lower = t_clean.lower()
                matched_cluster = -1
                for idx, cluster in enumerate(clusters):
                    if t_lower in cluster:
                        matched_cluster = idx
                        break
                if matched_cluster != -1:
                    if matched_cluster in seen_clusters:
                        continue
                    seen_clusters.add(matched_cluster)
                if t_clean not in clean_res:
                    clean_res.append(t_clean)
            return clean_res

        primary_clean = deduplicate_canonical_terms(primary_tech)
        secondary_clean = deduplicate_canonical_terms(secondary_tech)
        testing_clean = deduplicate_canonical_terms(testing_types) or ["Testy Aplikacji Webowych", "Testy Funkcjonalne", "Testy Manualne"]
        tools_clean = deduplicate_canonical_terms(tools) or ["Jira (Xray)", "Confluence", "Git"]

        return {
            "target_role": target_role,
            "seniority": seniority,
            "domain": domain,
            "primary_technologies": primary_clean or ["Selenium WebDriver", "SQL (Weryfikacja Danych)"],
            "secondary_technologies": secondary_clean,
            "testing_types": testing_clean,
            "tools": tools_clean,
            "key_responsibilities": responsibilities
        }

    @staticmethod
    def _sanitize_spec(raw: Dict[str, Any]) -> Dict[str, Any]:
        """Ensures all spec fields are clean lists or strings."""
        return {
            "target_role": clean_target_role(raw.get("target_role", "Software QA Specialist")),
            "seniority": str(raw.get("seniority", "Senior")).strip(),
            "domain": str(raw.get("domain", "Quality Assurance")).strip(),
            "primary_technologies": list(dict.fromkeys(raw.get("primary_technologies", []))),
            "secondary_technologies": list(dict.fromkeys(raw.get("secondary_technologies", []))),
            "testing_types": list(dict.fromkeys(raw.get("testing_types", []))),
            "tools": list(dict.fromkeys(raw.get("tools", []))),
            "key_responsibilities": list(raw.get("key_responsibilities", []))
        }

    @staticmethod
    def _empty_spec() -> Dict[str, Any]:
        return {
            "target_role": "Software QA Engineer",
            "seniority": "Senior",
            "domain": "IT / Quality Assurance",
            "primary_technologies": [],
            "secondary_technologies": [],
            "testing_types": [],
            "tools": [],
            "key_responsibilities": []
        }
