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
    assert result["personal_info"]["full_name"] == "Michał Kosowski"
    print("✅ AIEngine fallback unit test passed!")

def test_flask_endpoints():
    from app import app
    client = app.test_client()
    res = client.get("/api/profile")
    assert res.status_code == 200
    res_saved = client.get("/api/saved-cvs")
    assert res_saved.status_code == 200
    print("✅ Flask API endpoints unit test passed!")

if __name__ == "__main__":
    test_job_analyzer()
    test_ai_fallback()
    test_flask_endpoints()
    print("🎉 All unit tests passed successfully!")
