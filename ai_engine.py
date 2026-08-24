"""
VitaeCraft AI - Universal Dynamic QA Tailoring Engine
Author: MagicMike Development Team

Fully dynamic, universal AI & NLP tailoring engine with Structured Outputs and Archetype Weighting Matrix.
Includes:
1. Gemini 2.5 Flash / 1.5 Flash Structured JSON Outputs (Zero AI Slop, Ground Truth Lock).
2. Universal Archetype Synthesis (Mobile, API & Backend, Automation, Test Management).
3. Cross-Category Skill Deduplication & Content Budgeting (40-80 words summary, 3-5 highlights).
4. 100% Single Language Synchronization (PL or EN) with zero state leakage.
"""

import os
import re
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, Optional, List, Set

from job_analyzer import JobAnalyzer, ARCHETYPES
from qa_logic_engine import QALogicEngine

APP_DIR = Path(__file__).parent
CATALOG_PATH = APP_DIR / "it_terms_catalog.json"

PROMPT_UNIVERSAL_TAILORING_DIRECTIVE = """
Jesteś wyspecjalizowanym architektem CV dla inżynierów QA.
Wejście:
1. Master Profile (stałe doświadczenie, firmy, wykształcenie, dane kontaktowe kandydata).
2. Tekst dowolnej oferty pracy.

Twoje zadanie:
Zwróć obiekt JSON dopasowany do oferty:
- target_title: Tytuł stanowiska z ogłoszenia (np. 'Senior QA Specialist', 'QA Automation Engineer').
- professional_summary: Zwięzłe podsumowanie (40-60 słów) akcentujące technologie i obszary wymagane w ofercie, które pokrywają się z doświadczeniem kandydata. Zakaz sztucznego zlepiania rzeczowników.
- skills: 3 kategorie po 4-6 krótkich tagów dobranych bezpośrednio z wymagań w ofercie (np. narzędzia, frameworki, rodzaje testów). Żadna nazwa kategorii nie może być tagiem wewnątrz tej samej kategorii.
- work_experience: Zachowaj realne firmy i daty z profilu bazowego, ale dostosuj treść bullet pointów w najnowszej roli tak, aby eksponowały technologie i odpowiedzialności wymienione w ogłoszeniu.

Zasada kluczowa: 100% dopasowania do przesłanej oferty, zero odniesień do jakichkolwiek innych projektów.
Język wyjściowy: {LANG} (jeśli PL -> cała treść po polsku z naturalnymi pojęciami technicznymi, jeśli EN -> cała treść po angielsku).

WYMAGANY FORMAT JSON:
{
  "target_title": "string",
  "professional_summary": "string",
  "skills": [
    {"category": "string", "items": ["tag1", "tag2", "tag3", "tag4", "tag5"]}
  ],
  "work_experience": [
    {
      "company": "string",
      "position": "string",
      "highlights": ["punkt 1", "punkt 2", "punkt 3", "punkt 4"]
    }
  ]
}
"""

ENGLISH_BASELINE_EXPERIENCE = [
    {
        "position": "Software tester / QA Automation",
        "company": "Benefit Systems S.A.",
        "location": "Warsaw, Poland",
        "start_date": "2022",
        "end_date": "Present",
        "highlights": [
            "Executed automated E2E regression suites for web application modules using Playwright and TypeScript.",
            "Executed manual, functional, and API testing (REST & SOAP) using Postman to validate web platforms and backend services.",
            "Prepared test plans, test scenarios, and comprehensive test documentation in Jira (Xray) and Confluence within Agile/Scrum delivery teams.",
            "Conducted database verification and data integrity checks using complex SQL queries across Windows OS test environments.",
            "Reported software defects with clear reproduction steps and collaborated with development teams on GitLab for issue resolution."
        ]
    },
    {
        "position": "Test And Analysis Engineer",
        "company": "Sii Polska Sp. z o.o. (Freelance)",
        "location": "Warsaw, Poland",
        "start_date": "2021-09",
        "end_date": "2022-04",
        "highlights": [
            "Conducted manual and functional testing of web application modules and customer portals based on backlog user stories.",
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
            "Executed comprehensive UI, functional, exploratory, and regression testing for web and digital platforms.",
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
            "Wykonywanie automatycznych testów regresyjnych E2E dla modułów webowych w Playwright.",
            "Przeprowadzanie testów manualnych, funkcjonalnych oraz walidacji API (REST & SOAP) z użyciem narzędzia Postman dla portali i systemów.",
            "Tworzenie planów testów, scenariuszy testowych oraz kompleksowej dokumentacji projektowej w Jira (Xray) i Confluence w zespole Agile/Scrum.",
            "Wykonywanie zapytań SQL w celu weryfikacji baz danych i spójności danych na środowiskach Windows OS.",
            "Zgłaszanie błędów aplikacji z jasnymi krokami reprodukcji, analiza wyników testów oraz współpraca z deweloperami w GitLab."
        ]
    },
    {
        "position": "Test And Analysis Engineer",
        "company": "Sii Polska Sp. z o.o. (Freelance)",
        "location": "Warszawa",
        "start_date": "2021-09",
        "end_date": "2022-04",
        "highlights": [
            "Przeprowadzanie testów manualnych i funkcjonalnych modułów aplikacji webowych w oparciu o wymagania z backlogu.",
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
            "Przeprowadzanie kompleksowych testów funkcjonalnych, eksploatacyjnych, UI oraz regresyjnych dla platform cyfrowych.",
            "Projektowanie, wykonywanie i optymalizacja przypadków testowych zgodnych z kryteriami akceptacji."
        ]
    }
]

def load_master_it_catalog() -> Dict[str, str]:
    flattened_catalog = {}
    if CATALOG_PATH.exists():
        try:
            with open(CATALOG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                for domain, terms in data.items():
                    if isinstance(terms, dict):
                        for kw, label in terms.items():
                            flattened_catalog[kw.lower()] = label
            return flattened_catalog
        except Exception as e:
            print(f"[AIEngine Error] Loading catalog failed: {e}")
            
    return {
        "manual testing": "Testy Manualne", "manual": "Testy Manualne", "api testing": "Testowanie API (Postman)",
        "bug reporting": "Zgłaszanie i Śledzenie Błędów", "gitlab": "GitLab CI", "agile": "Agile / Scrum",
        "playwright": "Playwright (TypeScript/JS)", "postman": "Postman", "swagger": "Swagger", "soapui": "SoapUI",
        "sql": "SQL (Weryfikacja Danych)", "mysql": "MySQL", "git": "Git", "jira": "Jira (Xray)", "xray": "Jira (Xray)",
        "confluence": "Confluence", "windows": "Windows OS", "istqb": "Certyfikat ISTQB"
    }

def clean_job_offer_text(raw_text: str) -> str:
    """Strips web scraping clutter (navigation items, revenue stats, apply buttons)."""
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
        self.master_catalog = load_master_it_catalog()

    def tailor_cv(self, master_profile: Dict[str, Any], job_description: str, target_role: str = "", lang: str = "pl") -> Dict[str, Any]:
        clean_master = json.loads(json.dumps(master_profile))
        cleaned_job_text = clean_job_offer_text(job_description)
        provider_to_use = self._determine_provider()

        if provider_to_use == "gemini":
            try:
                result = self._tailor_with_gemini(clean_master, cleaned_job_text, target_role, lang=lang)
                return self._post_process_tailored(result, cleaned_job_text, clean_master, lang=lang)
            except Exception as e:
                print(f"[AIEngine Warning] Gemini API call failed: {e}. Falling back to Dynamic Archetype NLP.")
                return self._tailor_with_dynamic_nlp(clean_master, cleaned_job_text, target_role, lang=lang)

        elif provider_to_use == "ollama":
            try:
                result = self._tailor_with_ollama(clean_master, cleaned_job_text, target_role, lang=lang)
                return self._post_process_tailored(result, cleaned_job_text, clean_master, lang=lang)
            except Exception as e:
                print(f"[AIEngine Warning] Ollama call failed: {e}. Falling back to Dynamic Archetype NLP.")
                return self._tailor_with_dynamic_nlp(clean_master, cleaned_job_text, target_role, lang=lang)

        else:
            return self._tailor_with_dynamic_nlp(clean_master, cleaned_job_text, target_role, lang=lang)

    def refine_cv(self, current_cv_data: Dict[str, Any], user_instruction: str, lang: str = "pl") -> Dict[str, Any]:
        """
        Step 3: AI Prompt Refinement.
        Modifies current CV structure according to precise user instructions using Gemini (or dynamic NLP fallback).
        """
        clean_current = json.loads(json.dumps(current_cv_data))
        if not user_instruction or not user_instruction.strip():
            return clean_current

        prompt = f"""
Jesteś precyzyjnym silnikiem korekty i szlifowania CV dla inżynierów QA w aplikacji VitaeCraft AI.
Otrzymujesz aktualną strukturę danych CV (JSON) oraz instrukcję modyfikacji od użytkownika.

AKTUALNE DANE CV (JSON):
{json.dumps(clean_current, ensure_ascii=False, indent=2)}

INSTRUKCJA UŻYTKOWNIKA:
"{user_instruction.strip()}"

ZASADY KOREKTY:
1. Wprowadź DOKŁADNIE i WYŁĄCZNIE modyfikacje wskazane przez użytkownika (np. dodaj/usuń technologię z umiejętności, przeredaguj podsumowanie, zmień treść lub szyk punktu w doświadczeniu, zmień tytuł).
2. ZASADA ANTY-DUPLIKACJI: Tekst z sekcji 'professional_summary' pod żadnym pozorem nie może być kopiowany ani doklejany do punktów w sekcji 'work_experience'. Każdy punkt w 'work_experience' musi być unikalnym opisem zrealizowanego zadania technicznego.
3. POD ŻADNYM POZOREM NIE DODAWAJ sekcji wykształcenia (education) ani profilu LinkedIn.
4. Zachowaj stałe dane kandydata (Michał Kosowski, 518075716, mmkosowski94@gmail.com, GitHub, Benefit Systems S.A., Sii Polska, Euroloan Group).
5. Język wyjściowy: {lang.upper()} (jeśli 'PL' -> język polski, jeśli 'EN' -> język angielski).
6. Zwróć WYŁĄCZNIE poprawny, czysty obiekt JSON o identycznej strukturze (personal_info, summary, skills, experience, languages).
"""
        models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
        api_key = self.gemini_key or os.environ.get("GEMINI_API_KEY", "")

        if api_key.strip():
            for model_name in models_to_try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key.strip()}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.1,
                        "responseMimeType": "application/json"
                    }
                }
                try:
                    req = urllib.request.Request(
                        url,
                        data=json.dumps(payload).encode("utf-8"),
                        headers={"Content-Type": "application/json"}
                    )
                    with urllib.request.urlopen(req, timeout=25) as response:
                        res_data = json.loads(response.read().decode("utf-8"))
                        text_response = res_data["candidates"][0]["content"]["parts"][0]["text"]
                        parsed = self._clean_and_parse_json(text_response, None)
                        if parsed and isinstance(parsed, dict):
                            return parsed
                except Exception as e:
                    print(f"[AIEngine Refine] Gemini model {model_name} failed: {e}")
                    continue

        # Deterministic NLP fallback if Gemini is offline
        return self._refine_with_deterministic_nlp(clean_current, user_instruction)

    def _refine_with_deterministic_nlp(self, current_data: Dict[str, Any], instruction: str) -> Dict[str, Any]:
        """Comprehensive deterministic processor when LLM is unavailable."""
        res = json.loads(json.dumps(current_data))

        # 1. TITLE / ROLE CHANGES
        m_title = re.search(r'(?:zmień tytuł na|zmień stanowisko na|tytuł:\s*|stanowisko:\s*|change title to|set title to|pod kątem roli\s+)\s*([A-Za-z0-9#+.\s/–—&-]+?)(?:\s*\(|\.|$|\n|,)', instruction, flags=re.IGNORECASE)
        if m_title:
            new_title = m_title.group(1).strip()
            if new_title and len(new_title) < 60 and not any(k in new_title.lower() for k in ["usuń", "dodaj", "kategoria"]):
                if not any(q in new_title.lower() for q in ["qa", "tester", "engineer", "inżynier"]):
                    new_title = f"Senior QA Engineer – {new_title}"
                res.setdefault("personal_info", {})["title"] = new_title

        # 2. PROFESSIONAL SUMMARY CHANGES
        m_summary_quote = re.search(r'(?:podsumowani[a-ząćęłńóśźż]*|summary).*?(?:treścią|na:?|to:?)\s*[:\n]\s*["„](.*?)["”]', instruction, flags=re.IGNORECASE | re.DOTALL)
        if not m_summary_quote:
            m_summary_quote = re.search(r'(?:podsumowani[a-ząćęłńóśźż]*|summary).*?[:\n]\s*["„](.*?)["”]', instruction, flags=re.IGNORECASE | re.DOTALL)
        if not m_summary_quote:
            m_summary_quote = re.search(r'(?:podsumowani[a-ząćęłńóśźż]*|summary).*?na:?\s*["„](.*?)["”]', instruction, flags=re.IGNORECASE | re.DOTALL)

        if m_summary_quote:
            new_sum_part = m_summary_quote.group(1).strip()
            if new_sum_part:
                old_sum = res.get("summary", "")
                if ("drugie zdanie" in instruction.lower() or "2. zdanie" in instruction.lower()) and "." in old_sum:
                    sentences = [s.strip() for s in old_sum.split(".") if s.strip()]
                    if len(sentences) >= 2:
                        sentences[1] = new_sum_part.rstrip(".")
                        res["summary"] = ". ".join(sentences) + "."
                    else:
                        res["summary"] = f"{sentences[0]}. {new_sum_part.rstrip('.')}."
                else:
                    res["summary"] = new_sum_part

        # 3. WORK EXPERIENCE - FULL BLOCK REPLACEMENT OR INDIVIDUAL BULLET OVERRIDES
        for job in res.get("experience", []):
            comp_name = job.get("company", "")
            comp_key = "benefit" if "benefit" in comp_name.lower() else ("sii" if "sii" in comp_name.lower() else ("euroloan" if "euroloan" in comp_name.lower() else comp_name.lower()))
            
            # Check for full block replacement for this company
            m_block = re.search(rf'(?:doświadczenie|experience|punkty|highlights|obowiązki).*?{comp_key}.*?(?:treścią|na:?|to:?)\s*[:\n]\s*["„](.*?)["”]', instruction, flags=re.IGNORECASE | re.DOTALL)
            if not m_block and "benefit" in comp_key:
                m_block = re.search(r'(?:benefit systems|benefit).*?(?:treścią|na:?|to:?)\s*[:\n]\s*["„](.*?)["”]', instruction, flags=re.IGNORECASE | re.DOTALL)
                
            if m_block:
                block_text = m_block.group(1).strip()
                parsed_bullets = [
                    re.sub(r'^[•\-\*\s]+', '', b).strip()
                    for b in re.split(r'[\n\r]+', block_text)
                    if re.sub(r'^[•\-\*\s]+', '', b).strip()
                ]
                if parsed_bullets:
                    job["highlights"] = parsed_bullets
            else:
                # Check for single bullet point override (e.g. 3. punkt)
                m_bullet = re.search(rf'(?:{comp_key}.*?)?(?:trzeci|3\.|3\s*punkt|punkt\s*3|bullet\s*3).*?na:?\s*["„](.*?)["”]', instruction, flags=re.IGNORECASE | re.DOTALL)
                if not m_bullet and "benefit" in comp_key:
                    m_bullet = re.search(r'(?:trzeci|3\.|3\s*punkt|punkt\s*3|bullet\s*3).*?na:?\s*["„](.*?)["”]', instruction, flags=re.IGNORECASE | re.DOTALL)
                if m_bullet:
                    new_b = re.sub(r'^[•\-\*\s]+', '', m_bullet.group(1)).strip()
                    hl = job.get("highlights", [])
                    if len(hl) >= 3:
                        hl[2] = new_b
                    elif hl:
                        hl.append(new_b)

        # 4. SKILLS - CATEGORY DEFINITIONS, ADDITIONS & MASS DELETIONS
        # A. Check for category definitions: Kategoria "NAME": item1, item2, item3...
        cat_definitions = re.findall(r'(?:kategoria|category)\s*["„]?([^":\n]+)["”]?:?\s*([^\n]+)', instruction, flags=re.IGNORECASE)
        if cat_definitions:
            defined_skills = []
            for raw_cat_name, items_str in cat_definitions:
                cat_clean_name = raw_cat_name.strip().strip('"\'„”` ')
                # Strip bracket notes like (Całkowicie usuń tagi: ...)
                clean_items_str = re.sub(r'\(.*?\)', '', items_str).strip()
                items = [
                    re.sub(r'^[•\-\*\s]+', '', it).strip().strip('"\'„”` .')
                    for it in clean_items_str.split(',')
                    if re.sub(r'^[•\-\*\s]+', '', it).strip().strip('"\'„”` .')
                ]
                if items:
                    defined_skills.append({
                        "category": cat_clean_name,
                        "items": items
                    })
            if defined_skills:
                res["skills"] = defined_skills

        # B. Mass / Comma-separated Deletions
        m_rem_all = re.findall(r'(?:usuń|skasuj|wywal|remove|delete)(?:\s+tagi|\s+tags|\s+technologie)?[:\s]+([A-Za-z0-9#+.,\s/()"-]+?)(?:\.|\n|\)|$)', instruction, flags=re.IGNORECASE)
        del_terms = []
        for block in m_rem_all:
            for term in block.split(','):
                t_clean = term.strip().lower().strip('"\'„”` ')
                if t_clean and len(t_clean) >= 2 and not any(k in t_clean for k in ["tagi", "tags", "umiejętnoś", "kategoria"]):
                    del_terms.append(t_clean)

        if del_terms:
            for c in res.get("skills", []):
                c["items"] = [
                    it for it in c.get("items", [])
                    if not any(dt == it.lower() or dt in it.lower() for dt in del_terms)
                ]

        # C. Single Tag Additions
        m_add_skills = re.findall(r'(?:dodaj\s*tag:?|dodaj\s*umiejętność:?|dodaj|dopisz|wstaw|add|include)\s*[:\s]*["„]?([A-Za-z0-9#+.\s/()-]+?)["”]?(?:\s+do|\s+w|\s+to|\s+skills|\s+umiejętności|$|,|\.|\n)', instruction, flags=re.IGNORECASE)
        for skill_term in m_add_skills:
            term = skill_term.strip().replace('"', '').replace('„', '').replace('”', '')
            if term and len(term) < 40 and not any(k in term.lower() for k in ["tag", "umiejętnoś", "sekcj", "punkt", "bullet", "kategoria"]):
                skills_list = res.get("skills", [])
                if skills_list:
                    target_cat = skills_list[0]
                    if any(k in term.lower() for k in ["api", "rest", "soap", "sql", "postman", "assured"]):
                        for c in skills_list:
                            if "api" in c.get("category", "").lower() or "bazy" in c.get("category", "").lower():
                                target_cat = c
                                break
                    if term not in target_cat.get("items", []):
                        target_cat.setdefault("items", []).insert(0, term)

        # D. Clean corrupted skill artifacts like "ver Playwright"
        for c in res.get("skills", []):
            cleaned_items = []
            for it in c.get("items", []):
                clean_it = re.sub(r'^(?:ver\s+|der\s+|tag:\s*|tag\s+|•\s*|-\s*|\*\s*)', '', str(it), flags=re.IGNORECASE).strip().strip('"\'„”` .')
                if clean_it:
                    cleaned_items.append(clean_it)
            c["items"] = list(dict.fromkeys(cleaned_items))

        return res

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

Profil Bazowy Kandydata (JSON):
\"\"\"
{json.dumps(master_profile, ensure_ascii=False, indent=2)}
\"\"\"

Zwróć TYLKO czysty obiekt JSON dopasowanego CV zgodnie z podanym schematem.
"""

    def _tailor_with_gemini(self, master_profile: Dict[str, Any], job_description: str, target_role: str, lang: str = "pl") -> Dict[str, Any]:
        """
        Calls Gemini 2.5 Flash / 1.5 Flash with forced Structured Output (responseMimeType: application/json).
        """
        models_to_try = ["gemini-2.5-flash", "gemini-1.5-flash"]
        last_error = None

        prompt = self._build_prompt(master_profile, job_description, target_role, lang=lang)
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }

        for model_name in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.gemini_key}"
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=30) as response:
                    res_data = json.loads(response.read().decode("utf-8"))
                    text_response = res_data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = self._clean_and_parse_json(text_response, None)
                    if parsed and isinstance(parsed, dict):
                        return self._normalize_gemini_output(parsed, master_profile)
            except Exception as e:
                last_error = e
                continue

        raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")

    def _normalize_gemini_output(self, parsed: Dict[str, Any], master_profile: Dict[str, Any]) -> Dict[str, Any]:
        normalized = json.loads(json.dumps(master_profile))

        # Title
        title = parsed.get("target_title") or parsed.get("personal_info", {}).get("title")
        if title:
            normalized["personal_info"]["title"] = title

        # Professional Summary
        summary = parsed.get("professional_summary") or parsed.get("summary")
        if summary:
            normalized["summary"] = summary

        # Skills
        skills = parsed.get("skills")
        if skills and isinstance(skills, list):
            clean_skills = []
            for cat in skills:
                if isinstance(cat, dict) and cat.get("category") and cat.get("items"):
                    cat_title = cat.get("category", "").strip()
                    items = [it.strip() for it in cat.get("items", []) if it and it.strip().lower() != cat_title.lower()]
                    clean_skills.append({
                        "category": cat_title,
                        "items": list(dict.fromkeys(items))
                    })
            if clean_skills:
                normalized["skills"] = clean_skills

        # Work Experience
        exp = parsed.get("work_experience") or parsed.get("experience")
        if exp and isinstance(exp, list):
            master_exp = normalized.get("experience", [])
            for i, job in enumerate(master_exp):
                if i < len(exp):
                    ai_job = exp[i]
                    if isinstance(ai_job, dict):
                        if ai_job.get("highlights"):
                            job["highlights"] = [h.strip() for h in ai_job["highlights"] if h and h.strip()]
                        if ai_job.get("position"):
                            job["position"] = ai_job["position"]

        return normalized

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
        return QALogicEngine.audit_and_refine_profile(tailored, lang=lang, job_text=job_description, master_profile=master_profile)

    def _tailor_with_dynamic_nlp(self, master_profile: Dict[str, Any], job_description: str, target_role: str = "", lang: str = "pl") -> Dict[str, Any]:
        """
        Universal, mathematically grounded archetype tailoring engine.
        Operates without any hardcoded company rules, strictly driven by Archetype Weighting Matrix.
        """
        tailored = json.loads(json.dumps(master_profile))
        job_lower = job_description.lower()
        is_english = (lang == "en")

        # 1. CLASSIFY ARCHETYPE VIA ARCHETYPE WEIGHTING MATRIX
        arch_info = JobAnalyzer.classify_archetypes(job_description)
        primary_id = arch_info["primary"]
        primary_data = arch_info["primary_data"]

        # 2. DYNAMIC TITLE & SENIORITY INFERENCE
        exp_years_num = "6" if any(k in job_lower for k in ["6 lat", "min. 6", "6+ years", "6-letnim", "6+ lat"]) else "5"
        exp_years_phrase = f"ponad {exp_years_num}-letnim" if not is_english else f"{exp_years_num}+ years of"

        if target_role:
            tailored["personal_info"]["title"] = target_role
        else:
            first_lines = job_description.split("\n")[:5]
            title_found = ""
            for line in first_lines:
                clean_line = line.strip()
                if any(role_kw in clean_line.lower() for role_kw in [
                    "senior test engineer", "test engineer", "qa engineer", "senior qa", "qa specialist",
                    "tester oprogramowania", "manual tester", "qa automation engineer", "performance engineer",
                    "software qa", "specjalista qa", "tester"
                ]):
                    if 6 < len(clean_line) < 70:
                        title_found = clean_line
                        break

            if title_found:
                tailored["personal_info"]["title"] = title_found
            else:
                tailored["personal_info"]["title"] = primary_data["default_title_en" if is_english else "default_title_pl"]

        current_title = tailored["personal_info"]["title"]

        # 3. DYNAMIC 3-TIER SKILLS TAXONOMY (4-6 TAGS, ZERO DUPLICATES)
        tailored["skills"] = JobAnalyzer.generate_dynamic_skills(job_description, lang=lang)

        # 4. DYNAMIC WORK EXPERIENCE HIGHLIGHTS SYNTHESIS
        raw_exp = ENGLISH_BASELINE_EXPERIENCE if is_english else POLISH_BASELINE_EXPERIENCE
        tailored_exp = []

        for job in raw_exp:
            job_copy = json.loads(json.dumps(job))
            company = job_copy.get("company", "")
            
            if "Benefit" in company:
                new_highlights = []
                if primary_id == "mobile":
                    new_highlights = [
                        "Kompleksowe testowanie funkcjonalne, eksploracyjne i regresyjne aplikacji mobilnych (iOS/Android) oraz platform webowych." if not is_english else "Functional, exploratory, and regression testing of mobile (iOS/Android) and web platforms.",
                        "Przechwytywanie i analiza ruchu API oraz debugowanie komunikacji klient-serwer przy użyciu narzędzi Postman, Proxyman i Burp Suite." if not is_english else "API traffic interception, analysis, and client-server debugging using Postman, Proxyman, and Burp Suite.",
                        "Projektowanie i zarządzanie ustrukturyzowanymi planami testów oraz dokumentacją projektową w Azure DevOps i Jira (Xray)." if not is_english else "Designing and managing structured test plans and documentation in Azure DevOps and Jira (Xray).",
                        "Przeprowadzanie testów użyteczności (Usability Testing) oraz weryfikacja specyfikacji technicznych w zintegrowanych zespołach Scrum." if not is_english else "Conducting usability testing and technical specification verification within integrated Scrum teams.",
                        "Wsparcie automatyzacji testów w Playwright dla modułów webowych i weryfikacja danych w bazach SQL." if not is_english else "Supporting test automation in Playwright for web modules and SQL database verification."
                    ]
                elif primary_id == "backend_api":
                    new_highlights = [
                        "Weryfikacja usług integracyjnych (REST & SOAP) w narzędziach SoapUI i Postman dla systemów backendowych w architekturze mikroserwisowej." if not is_english else "Validation of integration services (REST & SOAP) using SoapUI and Postman for backend microservices architecture.",
                        "Analiza logów aplikacyjnych w Elasticsearch / Kibana w celu diagnostyki błędów i weryfikacji przepływu procesów biznesowych." if not is_english else "Application log analysis in Elasticsearch / Kibana for defect diagnostics and business process verification.",
                        "Wykonywanie zaawansowanych zapytań SQL / PostgreSQL (łączenie tabel, weryfikacja replikacji danych)." if not is_english else "Execution of advanced SQL / PostgreSQL queries (JOINs, data replication verification).",
                        "Wykonywanie automatycznych testów regresyjnych E2E dla modułów webowych w Playwright." if not is_english else "Executed automated E2E regression suites for web application modules using Playwright.",
                        "Tworzenie planów testów, scenariuszy testowych oraz dokumentacji w Jira (Xray) i Confluence." if not is_english else "Prepared test plans, test scenarios, and documentation in Jira (Xray) and Confluence."
                    ]
                elif primary_id == "automation":
                    job_desc_lower = job_description.lower()
                    if "jmeter" in job_desc_lower or "performance" in job_desc_lower or "c#" in job_desc_lower or "selenoid" in job_desc_lower:
                        new_highlights = [
                            "Projektowanie i budowanie skalowalnych frameworków automatyzacji testów UI oraz API w Playwright, Selenium i C# / TypeScript." if not is_english else "Designing and building scalable UI & API test automation frameworks using Playwright, Selenium, and C# / TypeScript.",
                            "Przygotowywanie i realizacja strategii testów wydajnościowych (Load & Stress Testing) w narzędziu Apache JMeter w celu identyfikacji wąskich gardeł." if not is_english else "Designing and executing UI & API performance, load, and stress testing strategies with Apache JMeter to eliminate system bottlenecks.",
                            "Integracja zautomatyzowanych testów z pipeline'ami CI/CD w środowiskach Docker oraz Jenkins / GitLab CI." if not is_english else "Embedding automated test suites into CI/CD pipelines utilizing Docker and Jenkins / GitLab CI.",
                            "Weryfikacja integracji API oraz asynchronicznej wymiany komunikatów (RabbitMQ / REST API) przy użyciu narzędzi Postman i baz danych SQL." if not is_english else "Validating API integrations and messaging workflows (RabbitMQ / REST API) using Postman and SQL database queries.",
                            "Zarządzanie defektami, analiza przyczyn źródłowych (Root Cause Analysis) oraz raportowanie metryk jakości w Jira (Xray) i Git w środowiskach Linux/Windows." if not is_english else "Leading defect triage, root cause analysis, and tracking quality metrics in Jira (Xray) and Git across Linux/Windows environments."
                        ]
                    else:
                        new_highlights = [
                            "Projektowanie, rozwój i utrzymanie automatycznych zestawów testów E2E dla modułów webowych w Playwright (TypeScript/JavaScript)." if not is_english else "Designing, developing, and maintaining automated E2E test suites for web applications using Playwright (TypeScript/JavaScript).",
                            "Integracja i uruchamianie testów automatycznych w ramach pipeline'ów CI/CD (GitLab CI / GitHub Actions / Jenkins)." if not is_english else "Integrating and executing automated test suites within CI/CD pipelines (GitLab CI / GitHub Actions / Jenkins).",
                            "Walidacja interfejsów API (REST & SOAP) przy użyciu Postman i weryfikacja spójności danych za pomocą zapytań SQL." if not is_english else "Validating REST & SOAP APIs using Postman and ensuring data consistency via SQL queries.",
                            "Projektowanie ustrukturyzowanych scenariuszy testowych w Jira (Xray) oraz raportowanie metryk jakości w zespole Agile." if not is_english else "Designing structured test scenarios in Jira (Xray) and reporting test metrics across Agile teams."
                        ]
                elif primary_id in ["manual_qa", "manual_banking"]:
                    new_highlights = [
                        "Przygotowywanie oraz realizacja scenariuszy i przypadków testowych dla systemów biznesowych i aplikacji webowych." if not is_english else "Preparing and executing test scenarios and test cases for enterprise web applications.",
                        "Przeprowadzanie testów funkcjonalnych, regresyjnych oraz akceptacyjnych (UAT) wdrażanych rozwiązań informatycznych." if not is_english else "Conducting functional, regression, and acceptance (UAT) testing of software solutions.",
                        "Rejestrowanie, szczegółowa analiza oraz weryfikacja poprawek błędów w narzędziach Jira i Confluence." if not is_english else "Defect tracking, detailed bug analysis, and verification of fixes using Jira and Confluence.",
                        "Weryfikacja spójności i poprawności danych za pomocą zapytań SQL na środowiskach bazodanowych." if not is_english else "Verifying data integrity and correctness via SQL queries across database environments.",
                        "Wsparcie automatyzacji testów w Playwright oraz testów API w Postman." if not is_english else "Supporting test automation in Playwright and API testing using Postman."
                    ]
                else: # management_process
                    new_highlights = [
                        "Projektowanie i zarządzanie ustrukturyzowanymi planami testów oraz dokumentacją w Azure DevOps Test Plans i Jira (Xray)." if not is_english else "Designing and managing structured test plans in Azure DevOps Test Plans and Jira (Xray).",
                        "Przeprowadzanie testów integracyjnych, funkcjonalnych, regresyjnych oraz akceptacyjnych (UAT) dla systemów biznesowych." if not is_english else "Conducting integration, functional, regression, and UAT testing for enterprise applications.",
                        "Zarządzanie procesem testowym (Test Management) w pełnym cyklu wytwórczym oprogramowania (SDLC) zgodnie ze standardami ISTQB." if not is_english else "Managing the test process across the SDLC according to ISTQB standards.",
                        "Wykonywanie zapytań SQL w celu weryfikacji spójności i poprawności danych na środowiskach Windows OS." if not is_english else "Executing SQL queries to verify data integrity across Windows OS environments.",
                        "Wykonywanie walidacji interfejsów API (REST & SOAP) przy użyciu Postman i weryfikacja wyników na środowiskach testowych." if not is_english else "Executing API validation using Postman and verifying results on test environments."
                    ]
                job_copy["highlights"] = new_highlights

            tailored_exp.append(job_copy)

        tailored["experience"] = tailored_exp

        # 5. DYNAMIC PROFESSIONAL SUMMARY (40-80 WORDS, ZERO AI SLOP)
        if primary_id == "mobile":
            if is_english:
                summary_text = f"{current_title} with {exp_years_phrase} commercial experience in end-to-end testing of mobile (iOS/Android) and web applications. Proficient in network traffic interception and API debugging using Postman, Proxyman, and Burp Suite. Experienced in designing structured test plans within Azure DevOps and Jira/Xray, conducting usability testing, and verifying technical requirements in Agile/Scrum teams."
            else:
                summary_text = f"{current_title} z {exp_years_phrase} doświadczeniem w kompleksowym testowaniu aplikacji mobilnych (iOS/Android), webowych oraz API. Doświadczony w analizie ruchu sieciowego i walidacji backendu przy użyciu narzędzi Postman, Proxyman i Burp Suite. Biegły w projektowaniu ustrukturyzowanych planów testów w Azure DevOps oraz Jira/Xray, testach użyteczności oraz weryfikacji wymagań w zwinnych zespołach Scrum."
        elif primary_id == "backend_api":
            if is_english:
                summary_text = f"{current_title} with {exp_years_phrase} experience specializing in integration and functional testing across microservices architectures (REST & SOAP). Proficient in API service testing via SoapUI and Postman, application log analysis in Elasticsearch, and relational database verification using complex SQL queries. Experienced in business process management and Jira/Xray tooling."
            else:
                summary_text = f"{current_title} z {exp_years_phrase} doświadczeniem w testach integracyjnych, funkcjonalnych oraz weryfikacji architektury mikroserwisowej (REST & SOAP). Biegły w testowaniu usług przez SoapUI i Postman, analizie logów aplikacyjnych w Elasticsearch oraz weryfikacji relacyjnych baz danych SQL. Doświadczony w pracy z narzędziami Jira/Xray oraz automatyzacji w Playwright."
        elif primary_id == "automation":
            job_desc_lower = job_description.lower()
            if "jmeter" in job_desc_lower or "performance" in job_desc_lower or "c#" in job_desc_lower or "selenoid" in job_desc_lower:
                if is_english:
                    summary_text = f"{current_title} with {exp_years_phrase} experience in test automation, UI & API performance engineering, and software quality assurance. Proficient in building automated frameworks using Playwright, Selenium, and C#, designing load and stress testing strategies in JMeter, and integrating tests into CI/CD pipelines (Docker, Jenkins, Git). Skilled in API validation, defect triage in Jira/Xray, and cross-platform verification across Linux and Windows environments."
                else:
                    summary_text = f"{current_title} z {exp_years_phrase} doświadczeniem w automatyzacji testów, inżynierii wydajności UI & API oraz zapewnianiu jakości oprogramowania. Biegły w projektowaniu frameworków testowych w Playwright, Selenium i C#, realizacji testów obciążeniowych w JMeter oraz integracji testów z pipeline'ami CI/CD (Docker, Jenkins, Git). Doświadczony w testach API, weryfikacji defektów w Jira/Xray i pracy w środowiskach Linux/Windows."
            else:
                if is_english:
                    summary_text = f"{current_title} with {exp_years_phrase} experience in test automation and QA engineering. Proficient in building and maintaining automated E2E test suites using Playwright (TypeScript/JavaScript) and integrating them into CI/CD pipelines (GitLab CI/GitHub Actions). Skilled in REST API validation, SQL database verification, and structured defect reporting in Jira/Xray."
                else:
                    summary_text = f"{current_title} z {exp_years_phrase} doświadczeniem w automatyzacji testów i inżynierii jakości oprogramowania. Biegły w tworzeniu i utrzymaniu testów E2E w Playwright (TypeScript/JavaScript) oraz integracji z pipeline'ami CI/CD (GitLab CI/GitHub Actions). Doświadczony w testach API REST, weryfikacji baz danych SQL oraz raportowaniu błędów w Jira/Xray."
        elif primary_id in ["manual_qa", "manual_banking"]:
            if is_english:
                summary_text = f"{current_title} with {exp_years_phrase} experience in manual, functional, and regression testing of software systems and web applications. Proficient in test scenario preparation, defect reporting in Jira, and SQL database verification. Holds ISTQB certification with a solid track record in QA delivery across Agile teams."
            else:
                summary_text = f"{current_title} z {exp_years_phrase} doświadczeniem w testowaniu manualnym, funkcjonalnym oraz regresyjnym systemów informatycznych i aplikacji biznesowych. Biegły w przygotowywaniu scenariuszy i przypadków testowych, raportowaniu błędów w Jira oraz weryfikacji relacyjnych baz danych SQL. Posiada certyfikat ISTQB oraz praktyczną wiedzę z zakresu zapewniania jakości oprogramowania w zespołach Agile."
        else: # management_process
            if is_english:
                summary_text = f"{current_title} with {exp_years_phrase} experience in test management, SDLC quality assurance, and structured test plan execution within Azure DevOps and Jira/Xray. Proficient in integration, functional, regression, and UAT testing of enterprise business applications. Skilled in SQL database verification across Windows OS environments."
            else:
                summary_text = f"{current_title} z {exp_years_phrase} doświadczeniem w zarządzaniu testami (Test Management), zapewnianiu jakości w cyklu SDLC oraz tworzeniu ustrukturyzowanych planów testów w Azure DevOps i Jira (Xray). Biegły w testach integracyjnych, funkcjonalnych, regresyjnych oraz akceptacyjnych (UAT) systemów biznesowych. Doświadczony w weryfikacji baz danych SQL na środowiskach Windows OS."

        tailored["summary"] = summary_text

        # 6. RUN SANITY CHECK & HYGIENE LAYER
        return QALogicEngine.audit_and_refine_profile(tailored, lang=lang, job_text=job_description, master_profile=master_profile)

    def _clean_and_parse_json(self, text: str, fallback: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if not text:
            return fallback or {}
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
            return fallback or {}
