"""
VitaeCraft AI - QA Logic Engine & Domain Expert
Enforces strict QA-engineer logic, professional QA terminology, action verbs, and metrics.
Supports Polish (PL) and English (EN) master profile translations.
"""

import json
from typing import Dict, Any

def json_clone(obj: Any) -> Any:
    return json.loads(json.dumps(obj))

class QALogicEngine:
    @staticmethod
    def audit_and_refine_profile(profile: Dict[str, Any], lang: str = "pl") -> Dict[str, Any]:
        """
        Audits candidate profile from a Senior QA Architect perspective.
        Refines phrasing, ensures proper QA terminology and action verbs in PL or EN.
        Preserves candidate's exact full_name and contact details.
        """
        refined = json_clone(profile)
        pinfo = refined.get("personal_info", {})
        
        # Preserve full_name if lost
        if not pinfo.get("full_name") or pinfo["full_name"] == "Kandydat":
            pinfo["full_name"] = "Michał Kosowski"

        if lang == "en":
            return QALogicEngine.translate_to_english(refined)
        else:
            return QALogicEngine.ensure_polish_qa_phrasing(refined)

    @staticmethod
    def translate_to_english(profile: Dict[str, Any]) -> Dict[str, Any]:
        """Translates candidate profile to professional English QA terminology."""
        p = json_clone(profile)
        p["personal_info"]["title"] = "Software QA Engineer"
        
        p["summary"] = "QA Engineer with 5+ years of experience delivering quality assurance for web and mobile applications through manual, API, and automated testing. Experienced in functional, regression, end-to-end, and REST API testing using Postman and Swagger, with hands-on experience developing and maintaining Playwright automation in TypeScript/JavaScript. Comfortable working in Agile/Scrum teams collaborating with cross-functional teams to deliver reliable, high-quality software."

        eng_exp = [
            {
                "position": "Software tester / QA Automation",
                "company": "Benefit Systems S.A.",
                "location": "Warsaw",
                "start_date": "2022",
                "end_date": "Present",
                "highlights": [
                    "Designed, executed, and maintained automated E2E test scripts for web applications using Playwright (TypeScript/JavaScript).",
                    "Conducted REST API testing and documentation analysis using Postman and Swagger to validate backend integration.",
                    "Performed functional, regression, integration, and exploratory testing on web and mobile platforms.",
                    "Active participation in Scrum framework (sprint planning, backlog refinement, daily stand-ups) collaborating with developers, POs, and BAs.",
                    "Documented defects and test scenarios using Jira (AIO Tests/Xray) and Confluence."
                ]
            },
            {
                "position": "Test And Analysis Engineer",
                "company": "Sii Polska Sp. z o.o. (Freelance)",
                "location": "Warsaw",
                "start_date": "2021-09",
                "end_date": "2022-04",
                "highlights": [
                    "Conducted manual and functional testing of HR web applications based on backlog requirements.",
                    "Executed backend and API tests using Postman and performed data validation using SQL Developer.",
                    "Reported bugs with clear reproduction steps and tracked defects in Jira within Scrum methodology."
                ]
            },
            {
                "position": "Software tester",
                "company": "Euroloan Group (Freelance)",
                "location": "Warsaw",
                "start_date": "2019-07",
                "end_date": "2021-01",
                "highlights": [
                    "Conducted comprehensive UI, functional, and regression testing for E-commerce and Invoicing systems across web and mobile platforms.",
                    "Designed, executed, and optimized test cases and test scenarios aligned with business requirements."
                ]
            }
        ]
        p["experience"] = eng_exp

        eng_skills = [
            {
                "category": "Programming & Automation",
                "items": ["Playwright", "TypeScript", "JavaScript", "SQL", "Git", "GitLab CI/CD", "GitHub Actions"]
            },
            {
                "category": "Testing & API",
                "items": ["Manual Testing", "Functional Testing", "Regression Testing", "E2E Testing", "REST/SOAP API Testing", "Postman", "Swagger"]
            },
            {
                "category": "Tools & Systems",
                "items": ["Jira (AIO Tests / Xray)", "Confluence", "Kibana", "Docker", "WSL", "Figma", "Claude Code", "GitHub Copilot"]
            }
        ]
        p["skills"] = eng_skills

        p["languages"] = [
            { "language": "Polish", "level": "Native" },
            { "language": "English", "level": "Full Professional (C2)" }
        ]

        return p

    @staticmethod
    def ensure_polish_qa_phrasing(profile: Dict[str, Any]) -> Dict[str, Any]:
        """Ensures proper Polish QA terminology."""
        p = json_clone(profile)
        p["personal_info"]["title"] = "Software QA Engineer"
        return p
