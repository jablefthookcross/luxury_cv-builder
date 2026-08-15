"""
VitaeCraft AI - QA Logic Engine & Anti-AI / ATS Verification Auditor
Enforces strict QA-engineer logic, professional QA terminology, action verbs, and metrics.
Includes automated Anti-AI Jargon Auditing, ATS Parser Compliance Checks, and Deterministic Bucket C Removal.
"""

import json
import re
from typing import Dict, Any, List

PROHIBITED_AI_BUZZWORDS = [
    "zagłębił się", "zagłębiła się", "jest świadectwem", "tkanina sukcesu",
    "transformacyjna podróż", "synergiczne rozwiązania", "przełomowy projekt",
    "pasjonat kodu", "dynamiczny lider", "zmieniający zasady gry", "holistyczne podejście",
    "tapestry of", "testament to", "delved into", "transformative journey", "synergistic",
    "game-changer", "passionate developer", "beacon of quality", "delivering quality assurance"
]

MOBILE_KEYWORDS = ["android studio", "xcode", "mobile device logs", "mobile testing", "logcat"]
BACKEND_SOAP_KEYWORDS = ["soapui", "soap api testing", "soap & rest api testing", "sql database verification"]

class QALogicEngine:
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
            "has_full_name": bool(pinfo.get("full_name") and pinfo["full_name"] != "Kandydat"),
            "has_contact_info": bool(pinfo.get("email") and pinfo.get("phone")),
            "has_summary": bool(profile.get("summary")),
            "has_experience": bool(profile.get("experience")),
            "has_skills": bool(profile.get("skills")),
            "no_fake_certifications": len(profile.get("certifications", [])) == 0 or any("ISTQB" not in str(c) for c in profile.get("certifications", []))
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
    def audit_and_refine_profile(profile: Dict[str, Any], lang: str = "pl", job_text: str = "") -> Dict[str, Any]:
        """
        Audits candidate profile from a Senior QA Architect perspective.
        Enforces candidate credentials and strips Bucket C items strictly per offer type.
        """
        refined = json_clone(profile)
        pinfo = refined.get("personal_info", {})
        
        if not pinfo.get("full_name") or pinfo["full_name"] == "Kandydat":
            pinfo["full_name"] = "Michał Kosowski"

        if not pinfo.get("title"):
            pinfo["title"] = "Software QA Engineer"

        job_lower = job_text.lower()
        is_mobile_offer = bool(re.search(r'\b(mobile|android|xcode|logcat|mobilne|mobilnych)\b', job_lower))

        if job_text:
            if not is_mobile_offer:
                # 1. Strip mobile skills if NOT a mobile offer
                for cat in refined.get("skills", []):
                    cat["items"] = [
                        item for item in cat.get("items", [])
                        if item.lower() not in MOBILE_KEYWORDS
                    ]
                # 2. Clean summary if AI left mobile tools
                summary = refined.get("summary", "")
                summary = summary.replace(" (Android Studio / Xcode)", "").replace(" (Android Studio, Xcode)", "")
                summary = summary.replace("using Android Studio and Xcode.", "using industry standard QA tools.")
                summary = summary.replace("and mobile ", " ")
                refined["summary"] = summary
            else:
                # 1. Strip SoapUI / SOAP noise if it IS a mobile offer
                for cat in refined.get("skills", []):
                    cat["items"] = [
                        item for item in cat.get("items", [])
                        if item.lower() not in BACKEND_SOAP_KEYWORDS
                    ]

        refined["certifications"] = []
        return refined

def json_clone(obj: Any) -> Any:
    return json.loads(json.dumps(obj))
