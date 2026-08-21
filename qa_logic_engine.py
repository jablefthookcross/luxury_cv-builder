"""
VitaeCraft AI - QA Logic Engine & Anti-AI / ATS Verification Auditor
Enforces strict QA-engineer logic, professional QA terminology, action verbs, and metrics.
Includes automated Anti-AI Jargon Auditing, ATS Parser Compliance Checks, Content Budgeting (40-80 words summary, 3-5 highlights), and Cross-Category Deduplication.
"""

import json
import re
from typing import Dict, Any, List, Set

def sanitize_prose_text(text: str) -> str:
    if not text:
        return ""
    # Strip leading bullets, dots and punctuation
    cleaned = re.sub(r'^[•\-\*\s.]+', '', text)
    # Strip technical bracket annotations in prose text
    cleaned = re.sub(r'\s*\([^)]*(?:Weryfikacja|Standard|Testing|Metodyka|Analiza|Kolejki|Message|Logs|Logi|Grid|Błędów|Logów)[^)]*\)', '', cleaned)
    cleaned = re.sub(r'\s*\(\.NET\)', '', cleaned)
    # Fix repeated periods or punctuation slop (e.g. ".." -> ".")
    cleaned = re.sub(r'\.{2,}', '.', cleaned)
    cleaned = re.sub(r'\s{2,}', ' ', cleaned)
    return cleaned.strip()

PROHIBITED_AI_BUZZWORDS = [
    "zagłębił się", "zagłębiła się", "jest świadectwem", "tkanina sukcesu",
    "transformacyjna podróż", "synergiczne rozwiązania", "przełomowy projekt",
    "pasjonat kodu", "dynamiczny lider", "zmieniający zasady gry", "holistyczne podejście",
    "tapestry of", "testament to", "delved into", "transformative journey", "synergistic",
    "game-changer", "passionate developer", "beacon of quality", "delivering quality assurance"
]

class QALogicEngine:
    # 1. FORBIDDEN AI SLOP & BOT PHRASES (Banned from QA CVs)
    AI_BUZZWORDS = [
        "dynamiczny profesjonalista", "dynamiczny tester", "dynamic professional",
        "results-driven", "zorientowany na wyniki", "pasjonat jakości",
        "synergia", "synergy", "holistyczny", "holistic approach",
        "game changer", "rockstar", "ninja", "ewangelista",
        "ponadprzeciętny", "innowacyjne rozwiązania", "proven track record of success"
    ]

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
            "has_full_name": bool(pinfo.get("full_name") and pinfo["full_name"] not in ["Kandydat", "Work Experience", "WorkExperience"]),
            "has_contact_info": bool(pinfo.get("email") and pinfo.get("phone")),
            "has_summary": bool(profile.get("summary")),
            "has_experience": bool(profile.get("experience")),
            "has_skills": bool(profile.get("skills")),
            "has_languages": bool(profile.get("languages"))
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
    def audit_and_refine_profile(profile: Dict[str, Any], lang: str = "pl", job_text: str = "", master_profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Audits candidate profile from a Senior QA Architect perspective.
        Enforces candidate credentials, offer alignment, 100% EDUCATION LOCK, and 100% LANGUAGE LOCK.
        Applies Content Budgeting (40-80 words summary, 3-5 highlights per employer).
        """
        refined = json.loads(json.dumps(profile))
        master = master_profile or {}
        master_pinfo = master.get("personal_info", {})
        
        # 1. PERSONAL INFO SANITY CHECK & GROUND TRUTH LOCK
        pinfo = refined.get("personal_info", {})
        pinfo["full_name"] = "Michał Kosowski"
        pinfo["email"] = "mmkosowski94@gmail.com"
        pinfo["phone"] = "518075716"
        pinfo["location"] = "Warsaw, Poland" if lang == "en" else "Warszawa"
        pinfo["linkedin"] = ""
        pinfo["github"] = "https://github.com/jablefthookcross"
        refined["personal_info"] = pinfo
        refined["education"] = []

        # Languages section lock
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

        # 2. CANONICAL SYNONYM DEDUPLICATION & CROSS-CATEGORY BUDGETING
        CANONICAL_CLUSTERS = [
            {"rest & soap api", "rest api", "soap api", "testy api", "api testing", "testy api (rest & soap)"},
            {"mobile testing (ios & android)", "testy aplikacji mobilnych (ios/android)", "testowanie ios", "testowanie android", "ios testing", "android testing", "mobile testing"},
            {"ci/cd pipelines", "ci/cd", "ci / cd"},
            {"selenium webdriver", "selenium"},
            {"sql (weryfikacja danych)", "sql (database verification)", "sql", "bazy danych sql", "sql databases"},
            {"scenariusze & przypadki testowe", "przypadki testowe", "scenariusze testowe", "test scenarios & test cases", "test scenarios", "test cases"},
            {"testy manualne & eksploracyjne", "testy manualne", "testy eksploracyjne", "manual & exploratory testing", "manual testing", "exploratory testing"}
        ]

        seen_skills: Set[str] = set()
        seen_cluster_indices: Set[int] = set()
        clean_skills = []
        
        for cat in refined.get("skills", []):
            cat_name = cat.get("category", "").strip()
            cat_name_norm = re.sub(r'[^a-zA-Z0-9ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]', '', cat_name.lower())
            raw_items = list(dict.fromkeys(cat.get("items", [])))
            filtered_items = []
            
            for item in raw_items:
                if not item:
                    continue
                # Clean corrupted prefixes, quotes and bullet characters
                clean_item = str(item).strip().strip('"\'„”` ')
                clean_item = re.sub(r'^[•\-\*\s]+', '', clean_item)
                clean_item = re.sub(r'^(?:ver\s+|der\s+|tag:\s*|tag\s+)', '', clean_item, flags=re.IGNORECASE).strip()
                clean_item = clean_item.strip('"\'„”` ')
                item_lower = clean_item.lower()
                item_norm = re.sub(r'[^a-zA-Z0-9ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]', '', item_lower)
                
                # Block if tag equals category name or is a clone of category name
                if item_norm == cat_name_norm or (len(clean_item) > 8 and (item_norm in cat_name_norm or cat_name_norm in item_norm)):
                    continue
                
                # Check canonical cluster membership
                in_cluster_idx = -1
                for idx, cluster in enumerate(CANONICAL_CLUSTERS):
                    if item_lower in cluster or item_norm in [re.sub(r'[^a-zA-Z0-9]', '', c) for c in cluster]:
                        in_cluster_idx = idx
                        break
                
                if in_cluster_idx != -1:
                    if in_cluster_idx in seen_cluster_indices:
                        continue  # Already represented by a higher-priority or earlier tag in the cluster
                    seen_cluster_indices.add(in_cluster_idx)

                # Check for direct or cross-category duplicates
                if item_norm and item_norm not in seen_skills and len(clean_item) < 45:
                    filtered_items.append(clean_item)
                    seen_skills.add(item_norm)
                    
            filtered_items = list(dict.fromkeys(filtered_items))
            
            if len(filtered_items) < 4:
                fallbacks = ["Jira (Xray)", "Confluence", "Git", "Postman", "Playwright"] if lang != "en" else ["Jira (Xray)", "Confluence", "Git", "Postman", "Playwright"]
                for fb in fallbacks:
                    fb_norm = re.sub(r'[^a-zA-Z0-9]', '', fb.lower())
                    if fb_norm not in seen_skills and fb_norm != cat_name_norm and len(filtered_items) < 5:
                        filtered_items.append(fb)
                        seen_skills.add(fb_norm)
                        
            clean_skills.append({
                "category": cat_name,
                "items": list(dict.fromkeys(filtered_items))[:6]
            })
            
        # Deduplicate and differentiate category titles (e.g. avoid repeating "API Testing" in Category 1 and 3)
        for i, cat in enumerate(clean_skills):
            cname = cat.get("category", "")
            if i > 0 and ("api" in cname.lower() or "testy" in cname.lower()) and any("api" in clean_skills[j].get("category", "").lower() for j in range(i)):
                if "database" in cname.lower() or "bazy" in cname.lower() or any("sql" in str(it).lower() for it in cat.get("items", [])):
                    cat["category"] = "Databases & Backend Tools" if lang == "en" else "Bazy Danych & Narzędzia"
                elif "ci/cd" in cname.lower() or "cloud" in cname.lower():
                    cat["category"] = "CI/CD & Cloud Infrastructure" if lang == "en" else "Infrastruktura CI/CD & Cloud"
                else:
                    cat["category"] = "Testing Tools & Methodologies" if lang == "en" else "Narzędzia & Metodyki Testowe"

        refined["skills"] = clean_skills

        # 3. PROFESSIONAL SUMMARY WORD BUDGETING (40-80 WORDS)
        summary = refined.get("summary", "").strip()
        words = summary.split()
        
        # Clean potential syntax bugs
        summary = summary.replace("5+-letnim", "5-letnim").replace("6+-letnim", "6-letnim")
        summary = re.sub(r'\s+', ' ', summary)
        words = summary.split()
        
        if len(words) > 80:
            # Trim to the closest sentence boundary before 80 words
            sentences = re.split(r'(?<=[.!?])\s+', summary)
            trimmed_sentences = []
            cur_count = 0
            for s in sentences:
                s_words = len(s.split())
                if cur_count + s_words <= 80 or not trimmed_sentences:
                    trimmed_sentences.append(s)
                    cur_count += s_words
                else:
                    break
            summary = " ".join(trimmed_sentences)
            
        elif len(words) < 40 and summary:
            # Expand summary smoothly with QA core competencies
            if lang == "en":
                summary += " Proven expertise in designing structured test documentation, executing regression suites, and ensuring high software quality across fast-paced delivery cycles."
            else:
                summary += " Posiada udokumentowane doświadczenie w tworzeniu ustrukturyzowanej dokumentacji testowej, wykonywaniu testów regresyjnych oraz dbaniu o najwyższą jakość oprogramowania w zwinnych zespołach."
                
        refined["summary"] = sanitize_prose_text(summary)

        # 4. WORK EXPERIENCE BUDGETING & ANTI-DUPLICATION WITH SUMMARY
        summary_sentences = [s.strip().lower() for s in re.split(r'[.!?]', refined["summary"]) if len(s.strip()) > 10]

        for job in refined.get("experience", []):
            company = job.get("company", "")
            raw_hls = job.get("highlights", [])
            clean_hls = []
            
            for h in raw_hls:
                h_clean = sanitize_prose_text(str(h).strip())
                if not h_clean:
                    continue
                
                # Check for high overlap with summary sentences (anti-duplication)
                h_lower = h_clean.lower()
                is_summary_clone = False
                for sent in summary_sentences:
                    if sent in h_lower or h_lower in sent:
                        is_summary_clone = True
                        break
                    h_words = set(re.findall(r'\w{4,}', h_lower))
                    sent_words = set(re.findall(r'\w{4,}', sent))
                    if h_words and len(h_words & sent_words) / max(len(h_words), 1) >= 0.75:
                        is_summary_clone = True
                        break

                if is_summary_clone:
                    continue

                if h_clean not in clean_hls and len(clean_hls) < 5:
                    clean_hls.append(h_clean)
                    
            if len(clean_hls) < 3:
                # Ensure at least 3 bullet points per employer with authentic tasks
                if "Benefit" in company:
                    clean_hls.append("Projektowanie i wdrażanie automatycznych zestawów testowych E2E z wykorzystaniem Playwright oraz Selenium." if lang == "pl" else "Designed and executed automated E2E test suites utilizing Playwright and Selenium WebDriver.")
                    clean_hls.append("Wykonywanie testów integracyjnych oraz weryfikacja danych w relacyjnych bazach danych SQL." if lang == "pl" else "Executed integration testing and database verification using SQL queries.")
                elif "Sii" in company:
                    clean_hls.append("Weryfikacja danych w bazach danych z użyciem narzędzi SQL." if lang == "pl" else "Verified database records and data integrity using SQL tools.")
                elif "Euroloan" in company:
                    clean_hls.append("Dokumentowanie defektów i weryfikacja poprawek błędów." if lang == "pl" else "Documented software defects and verified bug fixes.")
                    
            job["highlights"] = [sanitize_prose_text(h) for h in clean_hls[:5]]

            # Ensure position and role synchronization
            pos = job.get("position") or job.get("role") or "Software Tester"
            job["position"] = pos
            job["role"] = pos

            # Normalize start_date and end_date (split by range separator surrounded by whitespace)
            if not job.get("start_date") and job.get("period"):
                parts = re.split(r'\s+[–—\-]\s+', job["period"].strip())
                if len(parts) >= 1:
                    job["start_date"] = parts[0].strip()
                if len(parts) >= 2:
                    job["end_date"] = parts[1].strip()

            # Language formatting for dates and location
            if lang == "en":
                if job.get("end_date") and "obecnie" in str(job.get("end_date")).lower():
                    job["end_date"] = "Present"
                if "warszaw" in str(job.get("location", "")).lower():
                    job["location"] = "Warsaw, Poland"
                if not job.get("location"):
                    job["location"] = "Warsaw, Poland"
            else:
                if job.get("end_date") and "present" in str(job.get("end_date")).lower():
                    job["end_date"] = "Obecnie"
                if "warsaw" in str(job.get("location", "")).lower():
                    job["location"] = "Warszawa"
                if not job.get("location"):
                    job["location"] = "Warszawa"

            # Rebuild period string for safety
            if job.get("start_date"):
                job["period"] = f"{job['start_date']} – {job.get('end_date', 'Present' if lang == 'en' else 'Obecnie')}"

        # 5. HARD LOCK: NO EDUCATION, CANDIDATE LANGUAGES
        refined["education"] = []

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

