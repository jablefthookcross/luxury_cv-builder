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
    def get_user_from_token(cls, token: str) -> Optional[Dict[str, Any]]:
        """Verifies JWT token with Supabase Auth and returns user info."""
        if not cls.is_supabase_enabled() or not token:
            return None
        try:
            res = supabase_client.auth.get_user(token)
            if res and res.user:
                return {"id": res.user.id, "email": res.user.email}
        except Exception as e:
            print(f"[DBManager Warning] Token verification failed: {e}")
        return None

    @classmethod
    def register_user(cls, email: str, password: str, full_name: str = "") -> Dict[str, Any]:
        """Registers a new user in Supabase and initializes a clean, isolated profile."""
        if not cls.is_supabase_enabled():
            return {"status": "error", "message": "Supabase nie jest połączone. Użyj trybu lokalnego."}
            
        try:
            display_name = full_name.strip() or email.split("@")[0].capitalize()
            res = supabase_client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {"full_name": display_name}
                }
            })
            if res.user:
                # Initialize clean profile row in Supabase profiles table
                try:
                    init_profile = {
                        "id": res.user.id,
                        "full_name": display_name,
                        "email": email,
                        "phone": "",
                        "location": "Warszawa",
                        "linkedin": "",
                        "github": "",
                        "summary": "",
                        "skills": [],
                        "experience": [],
                        "languages": [
                            {"language": "Polish", "level": "Native"},
                            {"language": "English", "level": "Full Professional (C2)"}
                        ],
                        "education": [],
                        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    supabase_client.table("profiles").upsert(init_profile).execute()
                except Exception as db_err:
                    print(f"[DBManager Warning] Initial profile creation failed: {db_err}")

                return {
                    "status": "success",
                    "message": "Konto utworzone pomyślnie! Zaloguj się.",
                    "user": {"id": res.user.id, "email": res.user.email, "full_name": display_name},
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
        """
        Fetches user master profile from Supabase profiles table for authenticated users.
        Falls back to local profile_data.json ONLY when user_id is None (guest mode).
        """
        if cls.is_supabase_enabled() and user_id:
            try:
                res = supabase_client.table("profiles").select("*").eq("id", user_id).execute()
                if res.data and len(res.data) > 0:
                    row = res.data[0]
                    return {
                        "personal_info": {
                            "full_name": row.get("full_name", ""),
                            "title": row.get("title", "Software QA Engineer"),
                            "email": row.get("email", ""),
                            "phone": row.get("phone", ""),
                            "location": row.get("location", "Warszawa"),
                            "linkedin": row.get("linkedin", ""),
                            "github": row.get("github", "")
                        },
                        "summary": row.get("summary", ""),
                        "skills": row.get("skills", []),
                        "experience": row.get("experience", []),
                        "languages": row.get("languages", [
                            {"language": "Polish", "level": "Native"},
                            {"language": "English", "level": "Full Professional (C2)"}
                        ]),
                        "education": [],
                        "certifications": []
                    }
                else:
                    # Clean isolated template for new authenticated user
                    return {
                        "personal_info": {
                            "full_name": "",
                            "title": "Software QA Engineer",
                            "email": "",
                            "phone": "",
                            "location": "Warszawa",
                            "linkedin": "",
                            "github": ""
                        },
                        "summary": "",
                        "skills": [],
                        "experience": [],
                        "languages": [
                            {"language": "Polish", "level": "Native"},
                            {"language": "English", "level": "Full Professional (C2)"}
                        ],
                        "education": [],
                        "certifications": []
                    }
            except Exception as e:
                print(f"[DBManager Error] Reading profile from Supabase failed: {e}")
                return {
                    "personal_info": {
                        "full_name": "",
                        "title": "Software QA Engineer",
                        "email": "",
                        "phone": "",
                        "location": "Warszawa",
                        "linkedin": "",
                        "github": ""
                    },
                    "summary": "",
                    "skills": [],
                    "experience": [],
                    "languages": [
                        {"language": "Polish", "level": "Native"},
                        {"language": "English", "level": "Full Professional (C2)"}
                    ],
                    "education": [],
                    "certifications": []
                }

        # Local JSON Fallback (ONLY for guest / offline mode where user_id is None)
        if DEFAULT_PROFILE_PATH.exists():
            try:
                with open(DEFAULT_PROFILE_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    @classmethod
    def save_profile(cls, profile_data: Dict[str, Any], user_id: Optional[str] = None) -> bool:
        """
        Saves profile data:
        - If user_id is provided, saves ONLY to Supabase profiles table for that user_id.
        - If user_id is None, saves to local profile_data.json.
        """
        pinfo = profile_data.get("personal_info", {})
        
        if cls.is_supabase_enabled() and user_id:
            try:
                payload = {
                    "id": user_id,
                    "full_name": pinfo.get("full_name", ""),
                    "title": pinfo.get("title", "Software QA Engineer"),
                    "email": pinfo.get("email", ""),
                    "phone": pinfo.get("phone", ""),
                    "location": pinfo.get("location", "Warszawa"),
                    "linkedin": pinfo.get("linkedin", ""),
                    "github": pinfo.get("github", ""),
                    "summary": profile_data.get("summary", ""),
                    "skills": profile_data.get("skills", []),
                    "experience": profile_data.get("experience", []),
                    "languages": profile_data.get("languages", []),
                    "education": [],
                    "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                supabase_client.table("profiles").upsert(payload).execute()
                print(f"[DBManager] Profile saved to Supabase for user {user_id}")
                return True
            except Exception as e:
                print(f"[DBManager Error] Saving profile to Supabase failed: {e}")
                return False

        # Only save locally in guest mode
        try:
            with open(DEFAULT_PROFILE_PATH, "w", encoding="utf-8") as f:
                json.dump(profile_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"[DBManager Error] Saving profile locally failed: {e}")
            return False
