"""
VitaeCraft AI - CV Archive Manager
Handles persistent storage, retrieval, editing, and deletion of saved tailored CV applications.
Stores saved CVs as JSON files in APP_DIR / "saved_cvs".
"""

import os
import json
import time
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional

APP_DIR = Path(__file__).parent
SAVED_CVS_DIR = APP_DIR / "saved_cvs"

class CVArchiveManager:
    @staticmethod
    def _ensure_dir():
        SAVED_CVS_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def list_saved_cvs(cls) -> List[Dict[str, Any]]:
        cls._ensure_dir()
        cvs = []
        for file in SAVED_CVS_DIR.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    cvs.append({
                        "id": data.get("id", file.stem),
                        "company_name": data.get("company_name", "Nieokreślona firma"),
                        "target_title": data.get("target_title", "Software QA Engineer"),
                        "lang": data.get("lang", "pl"),
                        "match_score": data.get("match_score", 0),
                        "created_at": data.get("created_at", ""),
                        "filename": file.name
                    })
            except Exception as e:
                print(f"[CVArchiveManager Error] Failed reading {file}: {e}")
        
        # Sort by creation date descending
        return sorted(cvs, key=lambda x: x.get("created_at", ""), reverse=True)

    @classmethod
    def save_cv(cls, company_name: str, target_title: str, lang: str, match_score: int, profile_data: Dict[str, Any], job_text: str = "") -> Dict[str, Any]:
        cls._ensure_dir()
        cv_id = f"cv_{int(time.time())}_{uuid.uuid4().hex[:6]}"
        created_at = time.strftime("%Y-%m-%d %H:%M:%S")
        
        cv_record = {
            "id": cv_id,
            "company_name": company_name.strip() or "Moja Aplikacja",
            "target_title": target_title.strip() or "Software QA Engineer",
            "lang": lang or "pl",
            "match_score": match_score or 0,
            "created_at": created_at,
            "job_text": job_text,
            "profile_data": profile_data
        }
        
        file_path = SAVED_CVS_DIR / f"{cv_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(cv_record, f, ensure_ascii=False, indent=2)
            
        print(f"[CVArchiveManager] Saved tailored CV to {file_path}")
        return cv_record

    @classmethod
    def get_cv(cls, cv_id: str) -> Optional[Dict[str, Any]]:
        cls._ensure_dir()
        file_path = SAVED_CVS_DIR / f"{cv_id}.json"
        if not file_path.exists():
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[CVArchiveManager Error] Failed reading {cv_id}: {e}")
            return None

    @classmethod
    def update_cv(cls, cv_id: str, new_profile_data: Dict[str, Any], company_name: Optional[str] = None, target_title: Optional[str] = None) -> Optional[Dict[str, Any]]:
        record = cls.get_cv(cv_id)
        if not record:
            return None
            
        record["profile_data"] = new_profile_data
        if company_name is not None:
            record["company_name"] = company_name
        if target_title is not None:
            record["target_title"] = target_title
        record["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        file_path = SAVED_CVS_DIR / f"{cv_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
            
        return record

    @classmethod
    def delete_cv(cls, cv_id: str) -> bool:
        cls._ensure_dir()
        file_path = SAVED_CVS_DIR / f"{cv_id}.json"
        if file_path.exists():
            try:
                os.remove(file_path)
                return True
            except Exception as e:
                print(f"[CVArchiveManager Error] Failed deleting {cv_id}: {e}")
                return False
        return False
