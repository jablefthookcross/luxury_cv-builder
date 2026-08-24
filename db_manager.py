"""
VitaeCraft AI - Database & Authentication Manager
Author: MagicMike Development Team
Version: 2.2.0

Lightweight, robust, zero-rate-limit Auth and User Isolation engine.
Supports standalone HMAC-signed session tokens and persistent profile storage
with seamless Supabase cloud synchronization.
"""

import os
import sys
import json
import time
import uuid
import hmac
import base64
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional
from werkzeug.security import generate_password_hash, check_password_hash

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

APP_DIR = Path(__file__).parent
DEFAULT_PROFILE_PATH = APP_DIR / "profile_data.json"
USERS_FILE = APP_DIR / "users_db.json"
USER_PROFILES_FILE = APP_DIR / "user_profiles_db.json"

AUTH_SECRET = os.environ.get("SUPABASE_ANON_KEY", "vitaecraft-secret-token-key-2026-qa-engine")

# Supabase Cloud Client (Optional / Secondary Vault)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY", "") or os.environ.get("SUPABASE_KEY", "")

supabase_client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client, Client
        supabase_client: Optional[Client] = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("[DBManager] Connected to Supabase Cloud Database.")
    except Exception as e:
        print(f"[DBManager Warning] Supabase client initialization failed: {e}")

def _load_json(path: Path, default_val: Any) -> Any:
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default_val
    return default_val

def _save_json(path: Path, data: Any) -> bool:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[DBManager Error] Failed saving {path}: {e}")
        return False


class DBManager:
    @staticmethod
    def is_supabase_enabled() -> bool:
        return supabase_client is not None

    @classmethod
    def create_token(cls, user_id: str, username: str) -> str:
        """Creates a tamper-proof HMAC-SHA256 signed session token."""
        payload = {
            "uid": user_id,
            "usr": username,
            "exp": int(time.time()) + (60 * 86400)  # 60 days validity
        }
        raw_bytes = json.dumps(payload).encode("utf-8")
        b64_payload = base64.urlsafe_b64encode(raw_bytes).decode("utf-8").rstrip("=")
        sig = hmac.new(AUTH_SECRET.encode("utf-8"), b64_payload.encode("utf-8"), hashlib.sha256).hexdigest()
        return f"{b64_payload}.{sig}"

    @classmethod
    def get_user_from_token(cls, token: str) -> Optional[Dict[str, Any]]:
        """Verifies session token signature and returns authenticated user metadata."""
        if not token or "." not in token:
            return None
        try:
            b64_payload, sig = token.rsplit(".", 1)
            expected_sig = hmac.new(AUTH_SECRET.encode("utf-8"), b64_payload.encode("utf-8"), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(sig, expected_sig):
                return None
            
            # Decode base64 padding
            padding = "=" * ((4 - len(b64_payload) % 4) % 4)
            raw_json = base64.urlsafe_b64decode((b64_payload + padding).encode("utf-8")).decode("utf-8")
            payload = json.loads(raw_json)
            
            if payload.get("exp", 0) < time.time():
                return None
            
            return {
                "id": payload.get("uid"),
                "email": payload.get("usr"),
                "username": payload.get("usr")
            }
        except Exception as e:
            return None

    @classmethod
    def register_user(cls, email_or_username: str, password: str, full_name: str = "") -> Dict[str, Any]:
        """Registers a user without external email dependencies or SMTP rate limits."""
        username = email_or_username.strip().lower()
        full_name_clean = full_name.strip()
        
        if not username or not password:
            return {"status": "error", "message": "Wprowadź login/e-mail oraz hasło."}
            
        if len(password) < 4:
            return {"status": "error", "message": "Hasło musi mieć co najmniej 4 znaki."}

        users_db = _load_json(USERS_FILE, {})
        if username in users_db:
            return {"status": "error", "message": "Użytkownik o takim loginie już istnieje. Zaloguj się."}

        user_id = str(uuid.uuid4())
        pwd_hash = generate_password_hash(password)
        
        # Save user to store
        users_db[username] = {
            "id": user_id,
            "username": username,
            "full_name": full_name_clean,
            "password_hash": pwd_hash,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        _save_json(USERS_FILE, users_db)

        # Initialize baseline profile for this user from profile_data.json
        base_tmpl = _load_json(DEFAULT_PROFILE_PATH, {})
        init_profile = json.loads(json.dumps(base_tmpl)) if base_tmpl else {
            "personal_info": {
                "full_name": full_name_clean or "Michał Kosowski",
                "title": "Software QA Engineer",
                "email": username if "@" in username else "mmkosowski94@gmail.com",
                "phone": "518075716",
                "location": "Warszawa",
                "linkedin": "",
                "github": "https://github.com/jablefthookcross"
            },
            "summary": "",
            "skills": [],
            "experience": [],
            "languages": [
                {"language": "Polski", "level": "Ojczysty (Native)"},
                {"language": "Angielski", "level": "Biegły (Professional)"}
            ],
            "education": [],
            "certifications": []
        }
        
        cls.save_profile(init_profile, user_id=user_id)
        token = cls.create_token(user_id, username)

        return {
            "status": "success",
            "message": "Konto utworzone pomyślnie! Zalogowano automatycznie.",
            "user": {"id": user_id, "email": username, "username": username, "full_name": full_name_clean},
            "access_token": token
        }

    @classmethod
    def login_user(cls, email_or_username: str, password: str) -> Dict[str, Any]:
        """Authenticates user with username/password instantly."""
        username = email_or_username.strip().lower()
        if not username or not password:
            return {"status": "error", "message": "Wprowadź login/e-mail oraz hasło."}

        users_db = _load_json(USERS_FILE, {})
        user_record = users_db.get(username)

        if not user_record or not check_password_hash(user_record.get("password_hash", ""), password):
            return {"status": "error", "message": "Błędny login lub hasło."}

        token = cls.create_token(user_record["id"], username)
        return {
            "status": "success",
            "message": "Zalogowano pomyślnie!",
            "user": {
                "id": user_record["id"],
                "email": username,
                "username": username,
                "full_name": user_record.get("full_name", "")
            },
            "access_token": token
        }

    @classmethod
    def get_profile(cls, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetches master profile:
        - If user_id is provided, returns that user's profile from local DB or Supabase.
        - If not found or empty, ALWAYS falls back to DEFAULT_PROFILE_PATH (never an empty shell).
        """
        if user_id:
            profiles_db = _load_json(USER_PROFILES_FILE, {})
            if user_id in profiles_db and profiles_db[user_id].get("experience"):
                return profiles_db[user_id]
            
            # Sync check with Supabase if enabled
            if cls.is_supabase_enabled():
                try:
                    res = supabase_client.table("profiles").select("*").eq("id", user_id).execute()
                    if res.data and len(res.data) > 0:
                        row = res.data[0]
                        prof = {
                            "personal_info": {
                                "full_name": row.get("full_name", "Michał Kosowski"),
                                "title": row.get("title", "Software QA Engineer"),
                                "email": row.get("email", "mmkosowski94@gmail.com"),
                                "phone": row.get("phone", "518075716"),
                                "location": row.get("location", "Warszawa"),
                                "linkedin": row.get("linkedin", ""),
                                "github": row.get("github", "https://github.com/jablefthookcross")
                            },
                            "summary": row.get("summary", ""),
                            "skills": row.get("skills", []),
                            "experience": row.get("experience", []),
                            "languages": row.get("languages", [
                                {"language": "Polski", "level": "Ojczysty (Native)"},
                                {"language": "Angielski", "level": "Biegły (Professional)"}
                            ]),
                            "education": [],
                            "certifications": []
                        }
                        if prof.get("experience"):
                            profiles_db[user_id] = prof
                            _save_json(USER_PROFILES_FILE, profiles_db)
                            return prof
                except Exception as e:
                    print(f"[DBManager Warning] Supabase profile read: {e}")

        # Fallback to pristine baseline profile_data.json
        return _load_json(DEFAULT_PROFILE_PATH, {})

    @classmethod
    def save_profile(cls, profile_data: Dict[str, Any], user_id: Optional[str] = None) -> bool:
        """
        Saves master base profile data persistently:
        - Updates user-specific record in user_profiles_db.json and Supabase when user_id is provided.
        - Updates default profile_data.json only for guest mode (user_id is None).
        """
        if user_id:
            profiles_db = _load_json(USER_PROFILES_FILE, {})
            profiles_db[user_id] = profile_data
            _save_json(USER_PROFILES_FILE, profiles_db)

            if cls.is_supabase_enabled():
                try:
                    pinfo = profile_data.get("personal_info", {})
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
                except Exception as e:
                    print(f"[DBManager Warning] Supabase save: {e}")
            return True

        # Guest mode save (only when user_id is None)
        return _save_json(DEFAULT_PROFILE_PATH, profile_data)
