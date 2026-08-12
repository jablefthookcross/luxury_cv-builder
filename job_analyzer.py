"""
VitaeCraft AI - Job Analyzer & ATS Optimizer Module
Analyzes job descriptions, extracts key skills, and calculates ATS Match Score (0-100%).
"""

import re
import json
from typing import Dict, Any, List, Set

# Comprehensive QA & Tech keywords for extraction
TECH_KEYWORDS = {
    "python", "javascript", "typescript", "react", "node.js", "docker", "git", "github",
    "ci/cd", "rest api", "graphql", "sql", "linux", "windows", "playwright", "cypress", "selenium",
    "agile", "scrum", "jira", "xray", "testrail", "manual testing", "regression", "e2e", "istqb",
    "mobile", "web", "gui", "postman", "swagger", "financial", "brokerage", "usability", "api"
}

class JobAnalyzer:
    @staticmethod
    def analyze(job_description: str, master_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes job description and evaluates candidate fit.
        Returns match percentage, found keywords, and missing keywords.
        """
        if not job_description.strip():
            return {
                "match_score": 0,
                "job_keywords": [],
                "matched_keywords": [],
                "missing_keywords": [],
                "summary": "Brak treści oferty pracy."
            }

        job_lower = job_description.lower()

        # Extract keywords present in job description
        extracted_job_keywords = set()
        for kw in TECH_KEYWORDS:
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, job_lower):
                extracted_job_keywords.add(kw)

        # Full profile text search (case insensitive)
        full_profile_text = json.dumps(master_profile, ensure_ascii=False).lower()

        # Check matched vs missing keywords
        matched = []
        missing = []

        for kw in sorted(extracted_job_keywords):
            if kw in full_profile_text or any(part in full_profile_text for part in kw.split()):
                matched.append(kw.title())
            else:
                missing.append(kw.title())

        total = len(extracted_job_keywords)
        if total > 0:
            score = int((len(matched) / total) * 100)
        else:
            score = 85

        return {
            "match_score": min(score, 100),
            "job_keywords": [k.title() for k in sorted(extracted_job_keywords)],
            "matched_keywords": matched,
            "missing_keywords": missing,
            "total_keywords_found": total,
            "matched_count": len(matched)
        }
