"""
VitaeCraft AI - Supabase Database & Auth Manager
Author: MagicMike Development Team

Handles authentication, database persistence, and Row Level Security (RLS) via Supabase API.
Includes seamless fallback to local JSON files when operating offline or in standalone local mode.
"""

import os
import json
import time
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

APP_DIR = Path(__file__).parent
DEFAULT_PROFILE_PATH = APP_DIR / "profile_data.json"

# Supabase Environment Config
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY", "") or os.environ.get("SUPABASE_KEY", "")

supabase_client = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client, Client
        supabase_client: Optional[Client] = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("[DBManager] Connected to Supabase Cloud Database.")
    except Exception as e:
        print(f"[DBManager Warning] Supabase client initialization failed: {e}. Using local JSON fallback.")

class DBManager:
    @staticmethod
    def is_supabase_enabled() -> bool:
        return supabase_client is not None

    @classmethod
    def register_user(cls, email: str, password: str, full_name: str = "Michał Kosowski") -> Dict[str, Any]:
        if not cls.is_supabase_enabled():
            return {"status": "error", "message": "Supabase nie jest połączone. Użyj trybu lokalnego."}
            
        try:
            res = supabase_client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {"full_name": full_name}
                }
            })
            if res.user:
                return {
                    "status": "success",
                    "message": "Konto utworzone pomyślnie! Sprawdź skrzynkę e-mail lub zaloguj się.",
                    "user": {"id": res.user.id, "email": res.user.email},
                    "access_token": res.session.access_token if res.session else None
                }
            return {"status": "error", "message": "Rejestracja nie powiodła się."}
        except Exception as e:
            return {"status": "error", "message": f"Błąd rejestracji: {str(e)}"}

    @classmethod
    def login_user(cls, email: str, password: str) -> Dict[str, Any]:
        if not cls.is_supabase_enabled():
            return {"status": "error", "message": "Supabase nie jest połączone. Użyj trybu lokalnego."}
            
        try:
            res = supabase_client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            if res.user and res.session:
                return {
                    "status": "success",
                    "message": "Zalogowano pomyślnie!",
                    "user": {"id": res.user.id, "email": res.user.email},
                    "access_token": res.session.access_token
                }
            return {"status": "error", "message": "Błędny email lub hasło."}
        except Exception as e:
            return {"status": "error", "message": f"Błąd logowania: {str(e)}"}

    @classmethod
    def get_profile(cls, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Fetches user master profile from Supabase or local profile_data.json."""
        if cls.is_supabase_enabled() and user_id:
            try:
                res = supabase_client.table("profiles").select("*").eq("id", user_id).execute()
                if res.data and len(res.data) > 0:
                    row = res.data[0]
                    return {
                        "personal_info": {
                            "full_name": row.get("full_name", "Michał Kosowski"),
                            "title": "Software QA Engineer / Test Automation Engineer",
                            "email": row.get("email", ""),
                            "phone": row.get("phone", ""),
                            "location": row.get("location", "Warszawa"),
                            "linkedin": row.get("linkedin", ""),
                            "github": row.get("github", "https://github.com/jablefthookcross")
                        },
                        "summary": row.get("summary", ""),
                        "skills": row.get("skills", []),
                        "experience": row.get("experience", []),
                        "languages": row.get("languages", []),
                        "education": row.get("education", []),
                        "certifications": []
                    }
            except Exception as e:
                print(f"[DBManager Error] Reading profile from Supabase failed: {e}")

        # Local JSON Fallback
        if DEFAULT_PROFILE_PATH.exists():
            try:
                with open(DEFAULT_PROFILE_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    @classmethod
    def save_profile(cls, profile_data: Dict[str, Any], user_id: Optional[str] = None) -> bool:
        """Saves master profile to Supabase or local profile_data.json."""
        pinfo = profile_data.get("personal_info", {})
        
        if cls.is_supabase_enabled() and user_id:
            try:
                payload = {
                    "id": user_id,
                    "full_name": pinfo.get("full_name", "Michał Kosowski"),
                    "email": pinfo.get("email", ""),
                    "phone": pinfo.get("phone", ""),
                    "location": pinfo.get("location", "Warszawa"),
                    "linkedin": pinfo.get("linkedin", ""),
                    "github": pinfo.get("github", "https://github.com/jablefthookcross"),
                    "summary": profile_data.get("summary", ""),
                    "skills": profile_data.get("skills", []),
                    "experience": profile_data.get("experience", []),
                    "languages": profile_data.get("languages", []),
                    "education": profile_data.get("education", []),
                    "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                supabase_client.table("profiles").upsert(payload).execute()
                print(f"[DBManager] Profile saved to Supabase for user {user_id}")
                return True
            except Exception as e:
                print(f"[DBManager Error] Saving profile to Supabase failed: {e}")

        # Always save locally as well
        try:
            with open(DEFAULT_PROFILE_PATH, "w", encoding="utf-8") as f:
                json.dump(profile_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"[DBManager Error] Saving profile locally failed: {e}")
            return False
