"""
VitaeCraft AI - CV Archive Manager
Handles persistent storage, retrieval, editing, and deletion of saved tailored CV applications.
Stores saved CVs in Supabase Cloud PostgreSQL Database with fallback to local JSON files.
"""

import os
import json
import time
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional
from db_manager import DBManager, supabase_client

APP_DIR = Path(__file__).parent
SAVED_CVS_DIR = APP_DIR / "saved_cvs"

class CVArchiveManager:
    @staticmethod
    def _ensure_dir():
        SAVED_CVS_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def list_saved_cvs(cls, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        cvs_map = {}
        
        # 1. Fetch from Supabase Cloud if connected
        if DBManager.is_supabase_enabled():
            try:
                query = supabase_client.table("saved_cvs").select("*")
                if user_id:
                    query = query.eq("user_id", user_id)
                res = query.order("created_at", desc=True).execute()
                if res.data:
                    for row in res.data:
                        cid = str(row.get("id"))
                        cvs_map[cid] = {
                            "id": cid,
                            "company_name": row.get("company_name", "Nieokreślona firma"),
                            "target_title": row.get("target_title", "Software QA Engineer"),
                            "lang": row.get("lang", "pl"),
                            "match_score": row.get("match_score", 0),
                            "created_at": str(row.get("created_at", ""))[:19],
                            "filename": f"{cid}.json"
                        }
            except Exception as e:
                print(f"[CVArchiveManager Warning] Supabase list_saved_cvs: {e}")

        # 2. Merge local files as backup
        cls._ensure_dir()
        for file in SAVED_CVS_DIR.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    cid = str(data.get("id", file.stem))
                    if cid not in cvs_map:
                        cvs_map[cid] = {
                            "id": cid,
                            "company_name": data.get("company_name", "Nieokreślona firma"),
                            "target_title": data.get("target_title", "Software QA Engineer"),
                            "lang": data.get("lang", "pl"),
                            "match_score": data.get("match_score", 0),
                            "created_at": str(data.get("created_at", ""))[:19],
                            "filename": file.name
                        }
            except Exception as e:
                print(f"[CVArchiveManager Error] Failed reading local file {file}: {e}")
        
        # Sort by creation date descending
        return sorted(cvs_map.values(), key=lambda x: x.get("created_at", ""), reverse=True)

    @classmethod
    def save_cv(cls, company_name: str, target_title: str, lang: str, match_score: int, profile_data: Dict[str, Any], job_text: str = "", user_id: Optional[str] = None) -> Dict[str, Any]:
        cls._ensure_dir()
        cv_id = str(uuid.uuid4())
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
        if user_id:
            cv_record["user_id"] = user_id

        # 1. Save to Supabase Cloud
        if DBManager.is_supabase_enabled():
            try:
                payload = {
                    "id": cv_id,
                    "company_name": cv_record["company_name"],
                    "target_title": cv_record["target_title"],
                    "lang": cv_record["lang"],
                    "match_score": cv_record["match_score"],
                    "profile_data": profile_data,
                    "job_text": job_text,
                    "created_at": created_at
                }
                if user_id:
                    payload["user_id"] = user_id
                supabase_client.table("saved_cvs").insert(payload).execute()
                print(f"[CVArchiveManager] Successfully saved CV '{company_name}' to Supabase Cloud.")
            except Exception as e:
                print(f"[CVArchiveManager Warning] Supabase save_cv failed: {e}")

        # 2. Save to local disk backup
        file_path = SAVED_CVS_DIR / f"{cv_id}.json"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(cv_record, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[CVArchiveManager Error] Local disk save: {e}")
            
        return cv_record

    @classmethod
    def get_cv(cls, cv_id: str) -> Optional[Dict[str, Any]]:
        # 1. Try Supabase Cloud
        if DBManager.is_supabase_enabled():
            try:
                res = supabase_client.table("saved_cvs").select("*").eq("id", cv_id).execute()
                if res.data and len(res.data) > 0:
                    row = res.data[0]
                    return {
                        "id": str(row.get("id")),
                        "company_name": row.get("company_name"),
                        "target_title": row.get("target_title"),
                        "lang": row.get("lang", "pl"),
                        "match_score": row.get("match_score", 0),
                        "created_at": str(row.get("created_at", ""))[:19],
                        "job_text": row.get("job_text", ""),
                        "profile_data": row.get("profile_data", {})
                    }
            except Exception as e:
                print(f"[CVArchiveManager Warning] Supabase get_cv: {e}")

        # 2. Try Local File
        cls._ensure_dir()
        file_path = SAVED_CVS_DIR / f"{cv_id}.json"
        if file_path.exists():
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

        # 1. Update in Supabase
        if DBManager.is_supabase_enabled():
            try:
                update_payload = {
                    "profile_data": new_profile_data,
                    "updated_at": record["updated_at"]
                }
                if company_name is not None:
                    update_payload["company_name"] = company_name
                if target_title is not None:
                    update_payload["target_title"] = target_title
                supabase_client.table("saved_cvs").update(update_payload).eq("id", cv_id).execute()
            except Exception as e:
                print(f"[CVArchiveManager Warning] Supabase update_cv: {e}")
        
        # 2. Update local file
        cls._ensure_dir()
        file_path = SAVED_CVS_DIR / f"{cv_id}.json"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(record, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[CVArchiveManager Error] Failed local update {cv_id}: {e}")
            
        return record

    @classmethod
    def delete_cv(cls, cv_id: str) -> bool:
        deleted = False
        # 1. Delete in Supabase
        if DBManager.is_supabase_enabled():
            try:
                supabase_client.table("saved_cvs").delete().eq("id", cv_id).execute()
                deleted = True
            except Exception as e:
                print(f"[CVArchiveManager Warning] Supabase delete_cv: {e}")

        # 2. Delete local file
        cls._ensure_dir()
        file_path = SAVED_CVS_DIR / f"{cv_id}.json"
        if file_path.exists():
            try:
                os.remove(file_path)
                deleted = True
            except Exception as e:
                print(f"[CVArchiveManager Error] Failed deleting local {cv_id}: {e}")
        return deleted
