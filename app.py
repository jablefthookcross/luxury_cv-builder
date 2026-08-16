"""
VitaeCraft AI - Intelligent Personal CV Generator & Tailor
Author: MagicMike Development Team
Version: 2.1.0

Web GUI and API server for VitaeCraft AI with Playwright 1:1 PDF exporter,
QA Logic Engine, Anti-AI Auditor, ATS Compliance Safeguard, and Saved CVs Archive Manager.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from flask import Flask, render_template, request, jsonify, Response

from ai_engine import AIEngine, clean_job_offer_text
from job_analyzer import JobAnalyzer
from pdf_parser import PDFParser
from pdf_exporter import PDFExporter
from qa_logic_engine import QALogicEngine
from cv_archive_manager import CVArchiveManager

APP_DIR = Path(__file__).parent
DEFAULT_PROFILE_PATH = APP_DIR / "profile_data.json"
TAILORED_PROFILE_PATH = APP_DIR / "active_tailored_profile.json"
SETTINGS_PATH = APP_DIR / "settings.json"
OUTPUT_DIR = APP_DIR / "output"

app = Flask(__name__, template_folder="templates", static_folder="static")

ACTIVE_TAILORED_PROFILE = None
ACTIVE_LANGUAGE = "pl"
ACTIVE_JOB_TEXT = ""

def load_json_file(path: Path, default_data: dict) -> dict:
    if not path.exists():
        return default_data
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Error] Failed loading {path}: {e}")
        return default_data

def save_json_file(path: Path, data: dict) -> bool:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[Error] Failed saving {path}: {e}")
        return False

def get_settings() -> dict:
    default_settings = {
        "gemini_key": os.environ.get("GEMINI_API_KEY", ""),
        "ollama_url": os.environ.get("OLLAMA_URL", "http://localhost:11434"),
        "ollama_model": os.environ.get("OLLAMA_MODEL", "llama3.2")
    }
    return load_json_file(SETTINGS_PATH, default_settings)

def get_active_profile() -> dict:
    global ACTIVE_TAILORED_PROFILE
    if TAILORED_PROFILE_PATH.exists():
        loaded = load_json_file(TAILORED_PROFILE_PATH, {})
        if loaded:
            return loaded
    if ACTIVE_TAILORED_PROFILE:
        return ACTIVE_TAILORED_PROFILE
    return load_json_file(DEFAULT_PROFILE_PATH, {})

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/profile", methods=["GET", "POST"])
def master_profile_api():
    global ACTIVE_TAILORED_PROFILE, ACTIVE_JOB_TEXT
    if request.method == "POST":
        new_data = request.get_json()
        if save_json_file(DEFAULT_PROFILE_PATH, new_data):
            ACTIVE_TAILORED_PROFILE = new_data
            ACTIVE_JOB_TEXT = ""
            save_json_file(TAILORED_PROFILE_PATH, new_data)
            return jsonify({"status": "success", "message": "Główny profil bazowy pomyślnie zapisany!"})
        return jsonify({"status": "error", "message": "Błąd podczas zapisu profilu."}), 500
    
    data = load_json_file(DEFAULT_PROFILE_PATH, {})
    return jsonify(data)

@app.route("/api/clean-text", methods=["POST"])
def clean_text_api():
    payload = request.get_json() or {}
    raw_text = payload.get("text", "")
    cleaned = clean_job_offer_text(raw_text)
    return jsonify({"status": "success", "cleaned_text": cleaned})

@app.route("/api/tailor", methods=["POST"])
def tailor_api():
    global ACTIVE_TAILORED_PROFILE, ACTIVE_LANGUAGE, ACTIVE_JOB_TEXT
    payload = request.get_json() or {}
    
    job_description = payload.get("job_description", "")
    target_role = payload.get("target_role", "")
    provider = payload.get("provider", "auto")
    ACTIVE_LANGUAGE = payload.get("lang", "pl")
    ACTIVE_JOB_TEXT = job_description
    
    settings = get_settings()
    gemini_key = settings.get("gemini_key") or os.environ.get("GEMINI_API_KEY", "")
    ollama_url = settings.get("ollama_url", "http://localhost:11434")
    
    # ALWAYS load pristine master_profile baseline from disk
    master_profile = load_json_file(DEFAULT_PROFILE_PATH, {})
    
    ai = AIEngine(provider=provider, gemini_key=gemini_key, ollama_url=ollama_url)
    tailored_profile = ai.tailor_cv(master_profile, job_description, target_role, lang=ACTIVE_LANGUAGE)
    tailored_profile = QALogicEngine.audit_and_refine_profile(tailored_profile, lang=ACTIVE_LANGUAGE, job_text=job_description)
    
    ats_analysis = JobAnalyzer.analyze(job_description, tailored_profile)
    audit_results = QALogicEngine.audit_anti_ai_and_ats(tailored_profile)
    
    ACTIVE_TAILORED_PROFILE = tailored_profile
    save_json_file(TAILORED_PROFILE_PATH, tailored_profile)

    return jsonify({
        "status": "success",
        "message": "CV DRAFT pomyślnie wygenerowane! Możesz je teraz przejrzeć, zedytować lub zapisać do Moich CV.",
        "profile": tailored_profile,
        "ats_analysis": ats_analysis,
        "audit_results": audit_results,
        "buckets_breakdown": tailored_profile.get("_buckets_breakdown", {})
    })

# --- SAVED CVS ARCHIVE API ENDPOINTS ---

@app.route("/api/saved-cvs", methods=["GET", "POST"])
def saved_cvs_archive_api():
    if request.method == "POST":
        payload = request.get_json() or {}
        company_name = payload.get("company_name", "Moja Aplikacja")
        target_title = payload.get("target_title", "")
        lang = payload.get("lang", ACTIVE_LANGUAGE)
        match_score = payload.get("match_score", 0)
        profile_data = payload.get("profile_data") or get_active_profile()
        job_text = payload.get("job_text", ACTIVE_JOB_TEXT)
        
        record = CVArchiveManager.save_cv(
            company_name=company_name,
            target_title=target_title,
            lang=lang,
            match_score=match_score,
            profile_data=profile_data,
            job_text=job_text
        )
        return jsonify({"status": "success", "message": f"CV dla {company_name} zostało pomyślnie zapisane w Moich CV!", "record": record})
        
    records = CVArchiveManager.list_saved_cvs()
    return jsonify({"status": "success", "cvs": records})

@app.route("/api/saved-cvs/<cv_id>", methods=["GET", "PUT", "DELETE"])
def saved_cv_detail_api(cv_id):
    if request.method == "DELETE":
        if CVArchiveManager.delete_cv(cv_id):
            return jsonify({"status": "success", "message": "Zapisane CV zostało usunięte."})
        return jsonify({"status": "error", "message": "Nie znaleziono wskazanego pliku CV."}), 404
        
    if request.method == "PUT":
        payload = request.get_json() or {}
        profile_data = payload.get("profile_data")
        company_name = payload.get("company_name")
        target_title = payload.get("target_title")
        
        updated = CVArchiveManager.update_cv(cv_id, profile_data, company_name=company_name, target_title=target_title)
        if updated:
            return jsonify({"status": "success", "message": "Zapisane CV zaktualizowane pomyślnie!", "record": updated})
        return jsonify({"status": "error", "message": "Wystąpił błąd podczas aktualizacji."}), 500
        
    record = CVArchiveManager.get_cv(cv_id)
    if record:
        return jsonify({"status": "success", "record": record})
    return jsonify({"status": "error", "message": "Nie znaleziono wskazanego CV."}), 404

@app.route("/api/saved-cvs/<cv_id>/export/pdf")
def saved_cv_export_pdf(cv_id):
    record = CVArchiveManager.get_cv(cv_id)
    if not record:
        return jsonify({"status": "error", "message": "Nie znaleziono CV."}), 404
        
    template_name = request.args.get("template", "pro_qa_sidebar")
    data = record.get("profile_data", {})
    lang = record.get("lang", "pl")
    job_text = record.get("job_text", "")
    
    data = QALogicEngine.audit_and_refine_profile(data, lang=lang, job_text=job_text)
    rendered_html = render_template(f"cv_templates/{template_name}.html", data=data, lang=lang)
    
    pdf_bytes = PDFExporter.generate_pdf_from_html(rendered_html)
    if not pdf_bytes:
        pdf_bytes = PDFExporter.generate_pdf(data)
        
    company_slug = record.get("company_name", "CV").replace(" ", "_")
    filename = f"Michal_Kosowski_CV_{company_slug}.pdf"
    
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@app.route("/preview/current")
def preview_current():
    global ACTIVE_LANGUAGE, ACTIVE_JOB_TEXT
    template_name = request.args.get("template", "pro_qa_sidebar")
    lang = request.args.get("lang", ACTIVE_LANGUAGE)
    ACTIVE_LANGUAGE = lang
    
    data = get_active_profile()
    data = QALogicEngine.audit_and_refine_profile(data, lang=lang, job_text=ACTIVE_JOB_TEXT)
    
    template_file = f"cv_templates/{template_name}.html"
    try:
        return render_template(template_file, data=data, lang=lang)
    except Exception:
        return render_template("cv_templates/pro_qa_sidebar.html", data=data, lang=lang)

@app.route("/api/export/pdf")
def export_pdf():
    global ACTIVE_LANGUAGE, ACTIVE_JOB_TEXT
    template_name = request.args.get("template", "pro_qa_sidebar")
    lang = request.args.get("lang", ACTIVE_LANGUAGE)
    
    data = get_active_profile()
    data = QALogicEngine.audit_and_refine_profile(data, lang=lang, job_text=ACTIVE_JOB_TEXT)
    
    rendered_html = render_template(f"cv_templates/{template_name}.html", data=data, lang=lang)
    
    pdf_bytes = PDFExporter.generate_pdf_from_html(rendered_html)
    if not pdf_bytes:
        pdf_bytes = PDFExporter.generate_pdf(data)
        
    filename = "Michal_Kosowski_CV.pdf" if lang == "pl" else "Michal_Kosowski_Resume.pdf"
    
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

def main():
    parser = argparse.ArgumentParser(description="VitaeCraft AI - Inteligentny Generator CV")
    parser.add_argument("--export", action="store_true", help="Wyeksportuj aktualne CV jako plik HTML")
    parser.add_argument("--port", type=int, default=5000, help="Port serwera (domyślnie 5000)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Adres hosta (domyślnie 127.0.0.1)")

    args = parser.parse_args()

    if args.export:
        OUTPUT_DIR.mkdir(exist_ok=True)
        data = load_json_file(DEFAULT_PROFILE_PATH, {})
        with app.app_context():
            html = render_template("cv_templates/pro_qa_sidebar.html", data=data, lang="pl")
        out_file = OUTPUT_DIR / "resume.html"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✅ Wyeksportowano CV do: {out_file.resolve()}")
        sys.exit(0)

    print(f"🚀 Uruchamianie VitaeCraft AI v2.1.0 (z Archiwum Moje CV-ki)...")
    print(f"📍 Serwer dostępny pod adresem: http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=True)

if __name__ == "__main__":
    main()
