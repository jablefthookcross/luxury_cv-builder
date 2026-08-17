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
from job_extractor import JobExtractor
from cv_tailor_engine import CVTailorEngine
from job_analyzer import JobAnalyzer
from pdf_parser import PDFParser
from pdf_exporter import PDFExporter
from qa_logic_engine import QALogicEngine
from cv_archive_manager import CVArchiveManager
from db_manager import DBManager

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

@app.route("/api/auth/register", methods=["POST"])
def auth_register():
    payload = request.get_json() or {}
    email = payload.get("email", "").strip()
    password = payload.get("password", "").strip()
    full_name = payload.get("full_name", "Michał Kosowski").strip()
    
    if not email or not password:
        return jsonify({"status": "error", "message": "Wprowadź adres e-mail i hasło."}), 400
        
    res = DBManager.register_user(email, password, full_name)
    return jsonify(res)

@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    payload = request.get_json() or {}
    email = payload.get("email", "").strip()
    password = payload.get("password", "").strip()
    
    if not email or not password:
        return jsonify({"status": "error", "message": "Wprowadź adres e-mail i hasło."}), 400
        
    res = DBManager.login_user(email, password)
    return jsonify(res)

@app.route("/api/auth/status")
def auth_status():
    return jsonify({
        "status": "success",
        "supabase_enabled": DBManager.is_supabase_enabled()
    })

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

@app.route("/api/profile/reset", methods=["POST"])
def reset_profile_api():
    global ACTIVE_TAILORED_PROFILE, ACTIVE_JOB_TEXT
    ACTIVE_TAILORED_PROFILE = None
    ACTIVE_JOB_TEXT = ""
    if TAILORED_PROFILE_PATH.exists():
        try:
            TAILORED_PROFILE_PATH.unlink()
        except Exception:
            pass
    master_profile = load_json_file(DEFAULT_PROFILE_PATH, {})
    return jsonify({"status": "success", "message": "Aktywny DRAFT został zresetowany. Przywrócono czysty profil bazowy!", "profile": master_profile})

@app.route("/api/profile/delete", methods=["POST", "DELETE"])
def delete_master_profile_api():
    global ACTIVE_TAILORED_PROFILE, ACTIVE_JOB_TEXT
    empty_profile = {
        "personal_info": {
            "full_name": "Michał Kosowski",
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
        "languages": [],
        "education": [],
        "certifications": []
    }
    save_json_file(DEFAULT_PROFILE_PATH, empty_profile)
    ACTIVE_TAILORED_PROFILE = None
    ACTIVE_JOB_TEXT = ""
    if TAILORED_PROFILE_PATH.exists():
        try:
            TAILORED_PROFILE_PATH.unlink()
        except Exception:
            pass
    return jsonify({"status": "success", "message": "Profil bazowy został pomyślnie wyczyszczony! Możesz teraz wgrać nowy plik PDF ze swoim CV.", "profile": empty_profile})

@app.route("/api/upload-pdf", methods=["POST"])
def upload_pdf_api():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "Nie przesłano pliku."}), 400
        
    file = request.files['file']
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        return jsonify({"status": "error", "message": "Proszę wybrać plik w formacie PDF."}), 400
        
    try:
        pdf_bytes = file.read()
        raw_text = PDFParser.extract_text_from_pdf(pdf_bytes)
        
        if not raw_text.strip():
            return jsonify({"status": "error", "message": "Nie udało się odczytać tekstu z pliku PDF."}), 400
            
        settings = get_settings()
        gemini_key = settings.get("gemini_key") or os.environ.get("GEMINI_API_KEY", "")
        ollama_url = settings.get("ollama_url", "http://localhost:11434")
        ai = AIEngine(provider="auto", gemini_key=gemini_key, ollama_url=ollama_url)
        
        new_profile = PDFParser.convert_text_to_profile(raw_text, ai_engine=ai)
        
        save_json_file(DEFAULT_PROFILE_PATH, new_profile)
        
        global ACTIVE_TAILORED_PROFILE, ACTIVE_JOB_TEXT
        ACTIVE_TAILORED_PROFILE = new_profile
        ACTIVE_JOB_TEXT = ""
        save_json_file(TAILORED_PROFILE_PATH, new_profile)
        
        return jsonify({
            "status": "success",
            "message": f"Plik {file.filename} został pomyślnie zaimportowany i zapisany jako Główny Profil Bazowy!",
            "profile": new_profile
        })
    except Exception as e:
        print(f"[Error] PDF upload failed: {e}")
        return jsonify({"status": "error", "message": f"Błąd przetwarzania pliku PDF: {str(e)}"}), 500

@app.route("/api/clean-text", methods=["POST"])
def clean_text_api():
    payload = request.get_json() or {}
    raw_text = payload.get("text", "")
    cleaned = clean_job_offer_text(raw_text)
    return jsonify({"status": "success", "cleaned_text": cleaned})

@app.route("/api/settings", methods=["GET", "POST"])
def settings_api():
    if request.method == "POST":
        payload = request.get_json() or {}
        gemini_key = payload.get("gemini_key", "").strip()
        ollama_url = payload.get("ollama_url", "http://localhost:11434").strip()
        ollama_model = payload.get("ollama_model", "llama3.2").strip()

        data = {
            "gemini_key": gemini_key,
            "ollama_url": ollama_url,
            "ollama_model": ollama_model
        }
        if save_json_file(SETTINGS_PATH, data):
            return jsonify({"status": "success", "message": "Ustawienia AI zostały pomyślnie zapisane!"})
        return jsonify({"status": "error", "message": "Błąd zapisu ustawień."}), 500

    settings = get_settings()
    return jsonify({
        "status": "success",
        "settings": {
            "gemini_key": settings.get("gemini_key", ""),
            "ollama_url": settings.get("ollama_url", "http://localhost:11434"),
            "ollama_model": settings.get("ollama_model", "llama3.2")
        }
    })

@app.route("/api/analyze-job", methods=["POST"])
def analyze_job_api():
    """
    ETAP 1: Moduł Inteligencji Oferty.
    Parsuje surowy tekst oferty i zwraca ustrukturyzowany JobSpecification JSON.
    """
    payload = request.get_json() or {}
    raw_job_text = payload.get("job_text") or payload.get("job_description") or ""
    provider = payload.get("provider", "auto")

    if not raw_job_text.strip():
        return jsonify({"status": "error", "message": "Wklej treść oferty pracy do analizy."}), 400

    settings = get_settings()
    gemini_key = settings.get("gemini_key") or os.environ.get("GEMINI_API_KEY", "")

    spec = JobExtractor.extract(raw_job_text, gemini_key=gemini_key, provider=provider)
    return jsonify({
        "status": "success",
        "message": "Oferta pomyślnie przeanalizowana!",
        "spec": spec
    })

@app.route("/api/tailor", methods=["POST"])
@app.route("/api/tailor-from-spec", methods=["POST"])
def tailor_api():
    """
    ETAP 2: Moduł Dopasowania i Syntezy CV.
    Łączy nienaruszalny profil bazowy z JobSpecification JSON i zwraca dedykowany profil CV.
    """
    global ACTIVE_TAILORED_PROFILE, ACTIVE_LANGUAGE, ACTIVE_JOB_TEXT
    payload = request.get_json() or {}
    
    job_description = payload.get("job_description") or payload.get("job_text") or ""
    job_spec = payload.get("job_spec")
    target_role = payload.get("target_role", "")
    provider = payload.get("provider", "auto")
    
    settings = get_settings()
    gemini_key = settings.get("gemini_key") or os.environ.get("GEMINI_API_KEY", "")

    if not job_spec:
        if job_description.strip():
            job_spec = JobExtractor.extract(job_description, gemini_key=gemini_key, provider=provider)
        else:
            job_spec = JobExtractor._empty_spec()

    detected_lang = job_spec.get("detected_language") or JobExtractor.detect_language(job_description)
    req_lang = payload.get("lang") or payload.get("language")
    ACTIVE_LANGUAGE = req_lang if (req_lang and req_lang != "auto") else detected_lang
    ACTIVE_JOB_TEXT = job_description
    
    # ALWAYS load pristine master_profile baseline from disk (READ-ONLY)
    master_profile = load_json_file(DEFAULT_PROFILE_PATH, {})

    if target_role:
        job_spec["target_role"] = target_role

    # Synthesize tailored profile in memory
    tailored_profile = CVTailorEngine.tailor(master_profile, job_spec, lang=ACTIVE_LANGUAGE, gemini_key=gemini_key, provider=provider)
    tailored_profile = QALogicEngine.audit_and_refine_profile(tailored_profile, lang=ACTIVE_LANGUAGE, job_text=job_description or json.dumps(job_spec), master_profile=master_profile)
    
    ats_analysis = JobAnalyzer.analyze(job_description or json.dumps(job_spec), tailored_profile)
    audit_results = QALogicEngine.audit_anti_ai_and_ats(tailored_profile)

    ACTIVE_TAILORED_PROFILE = tailored_profile
    save_json_file(TAILORED_PROFILE_PATH, tailored_profile)
    
    template_name = payload.get("template", "pro_qa_sidebar")
    try:
        rendered_html = render_template(f"cv_templates/{template_name}.html", data=tailored_profile, lang=ACTIVE_LANGUAGE)
    except Exception:
        rendered_html = render_template("cv_templates/pro_qa_sidebar.html", data=tailored_profile, lang=ACTIVE_LANGUAGE)

    return jsonify({
        "status": "success",
        "message": "CV DRAFT pomyślnie wygenerowane!",
        "profile": tailored_profile,
        "job_spec": job_spec,
        "ats_analysis": ats_analysis,
        "audit_results": audit_results,
        "buckets_breakdown": tailored_profile.get("_buckets_breakdown", {}),
        "rendered_html": rendered_html
    })

@app.route("/preview/render", methods=["POST"])
def preview_render():
    payload = request.get_json() or {}
    data = payload.get("profile") or get_active_profile()
    template_name = payload.get("template", "pro_qa_sidebar")
    lang = payload.get("lang") or payload.get("language") or ACTIVE_LANGUAGE
    
    master_profile = load_json_file(DEFAULT_PROFILE_PATH, {})
    refined_data = QALogicEngine.audit_and_refine_profile(data, lang=lang, job_text=ACTIVE_JOB_TEXT, master_profile=master_profile)
    
    try:
        html = render_template(f"cv_templates/{template_name}.html", data=refined_data, lang=lang)
    except Exception:
        html = render_template("cv_templates/pro_qa_sidebar.html", data=refined_data, lang=lang)
        
    return jsonify({"status": "success", "html": html})

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
    req_lang = request.args.get("lang", ACTIVE_LANGUAGE)
    if not req_lang or req_lang == "auto":
        lang = JobExtractor.detect_language(ACTIVE_JOB_TEXT) if ACTIVE_JOB_TEXT else "pl"
    else:
        lang = req_lang
    ACTIVE_LANGUAGE = lang
    
    data = get_active_profile()
    master_profile = load_json_file(DEFAULT_PROFILE_PATH, {})
    data = QALogicEngine.audit_and_refine_profile(data, lang=lang, job_text=ACTIVE_JOB_TEXT, master_profile=master_profile)
    
    template_file = f"cv_templates/{template_name}.html"
    try:
        html = render_template(template_file, data=data, lang=lang)
    except Exception:
        html = render_template("cv_templates/pro_qa_sidebar.html", data=data, lang=lang)
        
    resp = Response(html, mimetype="text/html")
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

@app.route("/api/generate-pdf", methods=["POST", "GET"])
@app.route("/api/export/pdf", methods=["GET", "POST"])
@app.route("/export/pdf", methods=["GET", "POST"])
def export_pdf():
    """
    Stateless In-Memory PDF generation pipeline:
    1. Extracts raw job description from request (POST payload or GET query).
    2. Runs AIEngine with pristine baseline (profile_data.json) + fresh job text.
    3. Validates and sanitizes data via QALogicEngine.
    4. Passes JSON directly to Jinja2 template and compiles PDF via PDFExporter (Playwright).
    5. Returns fresh PDF with strict anti-caching headers.
    """
    global ACTIVE_LANGUAGE, ACTIVE_JOB_TEXT, ACTIVE_TAILORED_PROFILE

    if request.method == "POST":
        payload = request.get_json() or {}
        profile_data = payload.get("profile_data")
        job_spec = payload.get("job_spec")
        job_description = payload.get("job_text") or payload.get("job_description") or ACTIVE_JOB_TEXT or ""
        target_role = payload.get("target_role", "")
        template_name = payload.get("template", "pro_qa_sidebar")
        req_lang = payload.get("language") or payload.get("lang")
        provider = payload.get("provider", "auto")
    else:
        profile_data = None
        job_spec = None
        job_description = request.args.get("job_text") or request.args.get("job_description") or ACTIVE_JOB_TEXT or ""
        target_role = request.args.get("target_role", "")
        template_name = request.args.get("template", "pro_qa_sidebar")
        req_lang = request.args.get("language") or request.args.get("lang")
        provider = request.args.get("provider", "auto")

    # Determine language with priority on auto-detection when lang == 'auto' or unspecified
    if not req_lang or req_lang == "auto":
        if job_spec and job_spec.get("detected_language"):
            lang = job_spec.get("detected_language")
        elif job_description.strip():
            lang = JobExtractor.detect_language(job_description)
        else:
            lang = ACTIVE_LANGUAGE or "pl"
    else:
        lang = req_lang

    # Step 1: Load pristine master profile ground truth from disk (READ-ONLY)
    master_profile = load_json_file(DEFAULT_PROFILE_PATH, {})

    if profile_data:
        tailored_data = profile_data
    elif job_spec:
        settings = get_settings()
        gemini_key = settings.get("gemini_key") or os.environ.get("GEMINI_API_KEY", "")
        tailored_data = CVTailorEngine.tailor(master_profile, job_spec, lang=lang, gemini_key=gemini_key, provider=provider)
    elif job_description.strip():
        settings = get_settings()
        gemini_key = settings.get("gemini_key") or os.environ.get("GEMINI_API_KEY", "")
        job_spec = JobExtractor.extract(job_description, gemini_key=gemini_key, provider=provider)
        if target_role:
            job_spec["target_role"] = target_role
        tailored_data = CVTailorEngine.tailor(master_profile, job_spec, lang=lang, gemini_key=gemini_key, provider=provider)
    else:
        tailored_data = get_active_profile()

    # Step 3: Validate and refine through QALogicEngine
    final_data = QALogicEngine.audit_and_refine_profile(tailored_data, lang=lang, job_text=job_description or json.dumps(job_spec or {}), master_profile=master_profile)

    # Step 4: Render directly to Jinja2 and generate PDF
    rendered_html = render_template(f"cv_templates/{template_name}.html", data=final_data, lang=lang)
    pdf_bytes = PDFExporter.generate_pdf_from_html(rendered_html)
    if not pdf_bytes:
        pdf_bytes = PDFExporter.generate_pdf(final_data)

    filename = "Michal_Kosowski_CV.pdf" if lang == "pl" else "Michal_Kosowski_Resume.pdf"

    # Step 5: Return PDF with zero-cache headers
    response = Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )
    return response

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
