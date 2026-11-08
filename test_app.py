"""
Unit and Integration tests for VitaeCraft AI.
"""

import json
from pathlib import Path
from ai_engine import AIEngine
from job_analyzer import JobAnalyzer

def test_job_analyzer():
    profile = {
        "skills": [
            {"category": "Backend", "items": ["Python", "Flask", "PostgreSQL", "Docker"]}
        ]
    }
    job = "Looking for a Senior Python Developer with Flask and PostgreSQL experience. Docker is a plus."
    
    analysis = JobAnalyzer.analyze(job, profile)
    assert analysis["match_score"] > 50
    assert "Python" in analysis["matched_keywords"]
    assert "Flask" in analysis["matched_keywords"]
    print("✅ JobAnalyzer unit test passed!")

def test_ai_fallback():
    engine = AIEngine(provider="fallback")
    master = {
        "personal_info": {"full_name": "Test User"},
        "skills": [{"category": "Tech", "items": ["React", "Python"]}]
    }
    result = engine.tailor_cv(master, "Python job post")
    assert result["personal_info"]["full_name"] == "Test User"
    print("✅ AIEngine fallback unit test passed (candidate name preserved)!")

def test_flask_endpoints():
    from app import app
    client = app.test_client()
    res = client.get("/api/profile")
    assert res.status_code == 200
    res_saved = client.get("/api/saved-cvs")
    assert res_saved.status_code == 200
    print("✅ Flask API endpoints unit test passed!")

def test_regression_skill_parsing_and_parentheses():
    engine = AIEngine(provider="fallback")
    master = {
        "personal_info": {"full_name": "Michał Kosowski"},
        "summary": "Original summary",
        "skills": [],
        "experience": []
    }
    instruction = """Skills:
- TESTY & METODYKI QA: Testy Manualne, Testy Eksploracyjne, Scenariusze Testowe
- TESTY MOBILE & DIAGNOSTYKA: Testy Mobile (Android, iOS), Android Studio, Xcode, Git
- ZARZĄDZANIE, API & BAZY: Jira (Xray), TestRail, Postman, SQL"""
    
    result = engine.refine_cv(master, instruction, lang="pl")
    cats = {c["category"]: c["items"] for c in result.get("skills", [])}
    
    # 1. Check all 3 categories parsed (including category with comma in name)
    assert "ZARZĄDZANIE, API & BAZY" in cats, f"Category with comma was dropped: {list(cats.keys())}"
    assert "TESTY MOBILE & DIAGNOSTYKA" in cats
    assert "TESTY & METODYKI QA" in cats
    
    # 2. Check tag with parentheses and comma wasn't split
    mobile_items = cats["TESTY MOBILE & DIAGNOSTYKA"]
    assert any("Android, iOS" in itm for itm in mobile_items), f"Parentheses tag was split: {mobile_items}"
    assert not any(itm == "iOS)" for itm in mobile_items), f"Corrupted iOS) tag found: {mobile_items}"
    print("✅ Skill parsing with commas and parentheses unit test passed!")

def test_regression_css_no_justify_rivers():
    template_path = Path(__file__).parent / "templates" / "cv_templates" / "pro_qa_sidebar.html"
    content = template_path.read_text(encoding="utf-8")
    assert "text-align: justify;" not in content.split(".summary-p")[1].split("}")[0], "Summary paragraph still has text-align: justify!"
    print("✅ CSS typography unit test passed (no justify rivers in summary)!")

def test_regression_methodology_fallback_no_jira():
    from qa_logic_engine import QALogicEngine
    profile = {
        "skills": [
            {"category": "Testy & Metodyki QA", "items": ["Testy Manualne"]}
        ],
        "summary": "Test summary",
        "experience": []
    }
    refined = QALogicEngine.audit_and_refine_profile(profile, lang="pl")
    methodology_items = refined["skills"][0]["items"]
    assert "Jira (Xray)" not in methodology_items, f"Jira was incorrectly injected into methodology: {methodology_items}"
    print("✅ Methodology fallback unit test passed (no Jira in methodologies)!")

if __name__ == "__main__":
    test_job_analyzer()
    test_ai_fallback()
    test_flask_endpoints()
    test_regression_skill_parsing_and_parentheses()
    test_regression_css_no_justify_rivers()
    test_regression_methodology_fallback_no_jira()
    print("🎉 All unit and regression tests passed successfully!")
