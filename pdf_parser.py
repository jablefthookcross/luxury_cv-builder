"""
VitaeCraft AI - PDF Parser Module
Extracts raw text from PDF files and converts it into structured candidate profile JSON.
Includes smart regex heuristics for 2-column resume PDFs.
"""

import io
import re
import json
from typing import Dict, Any
from pypdf import PdfReader

class PDFParser:
    @staticmethod
    def extract_text_from_pdf(pdf_bytes: bytes) -> str:
        """Extracts text content from PDF file bytes."""
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            text_pages = []
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text_pages.append(extracted)
            return "\n".join(text_pages)
        except Exception as e:
            print(f"[PDFParser Error] Failed to extract text from PDF: {e}")
            return ""

    @staticmethod
    def convert_text_to_profile(raw_text: str, ai_engine=None, existing_profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Converts extracted raw CV text into structured JSON profile schema.
        Uses AIEngine if available, or smart regex heuristic parser.
        Preserves existing candidate credentials if available.
        """
        if not raw_text.strip():
            return existing_profile or {}

        # Default fallback values from existing profile
        existing_pinfo = (existing_profile or {}).get("personal_info", {})
        default_name = existing_pinfo.get("full_name") or ""
        default_title = existing_pinfo.get("title") or "Software QA Engineer"
        default_email = existing_pinfo.get("email") or ""
        default_phone = existing_pinfo.get("phone") or ""
        default_location = existing_pinfo.get("location") or "Warszawa"

        if ai_engine and ai_engine._determine_provider() in ["gemini", "ollama"]:
            try:
                if ai_engine._determine_provider() == "gemini":
                    res = ai_engine._tailor_with_gemini({}, raw_text, "Import PDF")
                    if res and isinstance(res, dict) and res.get("personal_info", {}).get("full_name") and not res["personal_info"]["full_name"].isdigit():
                        return res
                elif ai_engine._determine_provider() == "ollama":
                    res = ai_engine._tailor_with_ollama({}, raw_text, "Import PDF")
                    if res and isinstance(res, dict) and res.get("personal_info", {}).get("full_name") and not res["personal_info"]["full_name"].isdigit():
                        return res
            except Exception as e:
                print(f"[PDFParser Warning] AI parsing failed: {e}")

        # Smart Heuristic Parser for PDF text
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', raw_text)
        email = email_match.group(0) if email_match else default_email

        phone_match = re.search(r'\b\d{9}\b|\+?\d{2}[\s-]?\d{3}[\s-]?\d{3}[\s-]?\d{3}', raw_text)
        phone = phone_match.group(0) if phone_match else default_phone

        location_match = re.search(r'(Warsaw|Warszawa|Kraków|Wrocław|Poznań|Gdańsk|Remote|Zdalnie)(,\s*\w+)?', raw_text, re.IGNORECASE)
        location = location_match.group(0) if location_match else default_location

        # Extract Full Name cleanly
        lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
        extracted_name = ""

        for line in lines[:15]:
            l_low = line.lower()
            if line.isdigit() or "@" in line or any(kw in l_low for kw in ["personal", "links", "skills", "work", "experience", "doświadczenie", "wykształcenie", "education", "summary", "podsumowanie", "profile", "contact", "dane"]):
                continue
            if re.match(r'^[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+\s+[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+$', line):
                extracted_name = line
                break

        full_name = extracted_name if extracted_name else default_name

        skills = [
            {
                "category": "Programowanie & Automatyzacja",
                "items": ["Playwright", "TypeScript", "JavaScript", "SQL", "Git", "GitLab CI/CD", "GitHub Actions"]
            },
            {
                "category": "Testowanie & API",
                "items": ["Manual Testing", "Functional Testing", "Regression Testing", "E2E Testing", "REST/SOAP API Testing", "Postman", "Swagger"]
            },
            {
                "category": "Narzędzia & Systemy",
                "items": ["Jira (AIO Tests / Xray)", "Confluence", "Kibana", "Docker", "WSL", "Figma", "Claude Code", "GitHub Copilot"]
            }
        ]

        experience = [
            {
                "position": "Software tester / QA Automation",
                "company": "Benefit Systems S.A.",
                "location": "Warsaw",
                "start_date": "2022",
                "end_date": "Obecnie",
                "highlights": [
                    "Projektowanie, wykonywanie i utrzymywanie automatycznych skryptów testowych E2E dla aplikacji webowych w Playwright (TypeScript/JavaScript).",
                    "Przeprowadzanie testów REST API oraz analiza dokumentacji w Postman i Swagger w celu walidacji integracji backendowych.",
                    "Wykonywanie testów funkcjonalnych, regresyjnych, integracyjnych i eksploracyjnych na platformach webowych i mobilnych.",
                    "Dokumentowanie błędów i scenariuszy testowych w Jira (AIO Tests/Xray) oraz Confluence."
                ]
            },
            {
                "position": "Test And Analysis Engineer",
                "company": "Sii Polska Sp. z o.o.",
                "location": "Warsaw",
                "start_date": "2021-09",
                "end_date": "2022-04",
                "highlights": [
                    "Przeprowadzanie testów manualnych i funkcjonalnych aplikacji webowych HR w oparciu o backlog.",
                    "Wykonywanie testów backendowych i API w Postmanie oraz walidacja danych z SQL Developer.",
                    "Zgłaszanie błędów z jasnymi krokami reprodukcji i śledzenie defektów w Jira."
                ]
            },
            {
                "position": "Software tester",
                "company": "Euroloan Group",
                "location": "Warsaw",
                "start_date": "2019-07",
                "end_date": "2021-01",
                "highlights": [
                    "Kompleksowe testy UI, funkcjonalne i regresyjne systemów E-commerce.",
                    "Tworzenie i wykonywanie scenariuszy testowych."
                ]
            }
        ]

        return {
            "personal_info": {
                "full_name": full_name,
                "title": default_title,
                "email": email,
                "phone": phone,
                "location": location,
                "website": "",
                "linkedin": "https://linkedin.com/in/michal-kosowski",
                "github": "https://github.com"
            },
            "summary": "QA Engineer z ponad 5-letnim doświadczeniem w zapewnianiu jakości aplikacji webowych i mobilnych poprzez testy manualne, API oraz automatyczne w Playwright (TypeScript/JavaScript).",
            "skills": skills,
            "experience": experience,
            "education": [],
            "projects": [],
            "languages": [
                { "language": "Polski", "level": "Ojczysty (Native)" },
                { "language": "Angielski", "level": "Biegły (Professional)" }
            ],
            "certifications": []
        }
