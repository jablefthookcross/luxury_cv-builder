"""
VitaeCraft AI - Intelligent Personal CV Generator & Tailor
Author: MagicMike Development Team
Version: 1.9.0

Web GUI and API server for VitaeCraft AI with Playwright 1:1 PDF exporter,
QA Logic Engine, Anti-AI Auditor, ATS Compliance Safeguard, and Dynamic PDF State Persistence.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from flask import Flask, render_template, request, jsonify, Response

from ai_engine import AIEngine
from job_analyzer import JobAnalyzer
from pdf_parser import PDFParser
from pdf_exporter import PDFExporter
from qa_logic_engine import QALogicEngine

APP_DIR = Path(__file__).parent
DEFAULT_PROFILE_PATH = APP_DIR / "profile_data.json"
TAILORED_PROFILE_PATH = APP_DIR / "active_tailored_profile.json"
SETTINGS_PATH = APP_DIR / "settings.json"
OUTPUT_DIR = APP_DIR / "output"

app = Flask(__name__, template_folder="templates", static_folder="static")

ACTIVE_TAILORED_PROFILE = None
ACTIVE_LANGUAGE = "pl"

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
    global ACTIVE_TAILORED_PROFILE
    if request.method == "POST":
        new_data = request.get_json()
        if save_json_file(DEFAULT_PROFILE_PATH, new_data):
            ACTIVE_TAILORED_PROFILE = new_data
            save_json_file(TAILORED_PROFILE_PATH, new_data)
            return jsonify({"status": "success", "message": "Główny profil pomyślnie zapisany!"})
        return jsonify({"status": "error", "message": "Błąd podczas zapisu profilu."}), 500
    
    data = load_json_file(DEFAULT_PROFILE_PATH, {})
    return jsonify(data)

@app.route("/api/upload-pdf", methods=["POST"])
def upload_pdf_api():
    global ACTIVE_TAILORED_PROFILE
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "Brak pliku PDF w żądaniu."}), 400

    file = request.files['file']
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"status": "error", "message": "Załączony plik musi być w formacie PDF."}), 400

    pdf_bytes = file.read()
    raw_text = PDFParser.extract_text_from_pdf(pdf_bytes)

    if not raw_text.strip():
        return jsonify({"status": "error", "message": "Nie udało się odczytać tekstu z tego pliku PDF."}), 400

    settings = get_settings()
    gemini_key = settings.get("gemini_key") or os.environ.get("GEMINI_API_KEY", "")
    ollama_url = settings.get("ollama_url", "http://localhost:11434")
    
    ai = AIEngine(provider="auto", gemini_key=gemini_key, ollama_url=ollama_url)
    parsed_profile = PDFParser.convert_text_to_profile(raw_text, ai_engine=ai)
    parsed_profile = QALogicEngine.audit_and_refine_profile(parsed_profile, lang=ACTIVE_LANGUAGE)

    save_json_file(DEFAULT_PROFILE_PATH, parsed_profile)
    ACTIVE_TAILORED_PROFILE = parsed_profile
    save_json_file(TAILORED_PROFILE_PATH, parsed_profile)

    return jsonify({
        "status": "success",
        "message": "CV w formacie PDF zostało pomyślnie zaimportowane i przetworzone!",
        "profile": parsed_profile
    })

@app.route("/api/settings", methods=["GET", "POST"])
def settings_api():
    if request.method == "POST":
        data = request.get_json()
        if save_json_file(SETTINGS_PATH, data):
            if data.get("gemini_key"):
                os.environ["GEMINI_API_KEY"] = data["gemini_key"]
            return jsonify({"status": "success", "message": "Ustawienia zapisane pomyślnie!"})
        return jsonify({"status": "error", "message": "Błąd podczas zapisu ustawień."}), 500

    settings = get_settings()
    masked = dict(settings)
    if masked.get("gemini_key"):
        k = masked["gemini_key"]
        masked["gemini_key_masked"] = k[:4] + "..." + k[-4:] if len(k) > 8 else "***"
    return jsonify(masked)

@app.route("/api/tailor", methods=["POST"])
def tailor_api():
    global ACTIVE_TAILORED_PROFILE, ACTIVE_LANGUAGE
    payload = request.get_json() or {}
    
    job_description = payload.get("job_description", "")
    target_role = payload.get("target_role", "")
    provider = payload.get("provider", "auto")
    ACTIVE_LANGUAGE = payload.get("lang", "pl")
    
    settings = get_settings()
    gemini_key = settings.get("gemini_key") or os.environ.get("GEMINI_API_KEY", "")
    ollama_url = settings.get("ollama_url", "http://localhost:11434")
    
    master_profile = load_json_file(DEFAULT_PROFILE_PATH, {})
    
    ai = AIEngine(provider=provider, gemini_key=gemini_key, ollama_url=ollama_url)
    tailored_profile = ai.tailor_cv(master_profile, job_description, target_role)
    tailored_profile = QALogicEngine.audit_and_refine_profile(tailored_profile, lang=ACTIVE_LANGUAGE)
    
    ats_analysis = JobAnalyzer.analyze(job_description, tailored_profile)
    audit_results = QALogicEngine.audit_anti_ai_and_ats(tailored_profile)
    
    # Save active tailored state to disk and memory for PDF generator sync
    ACTIVE_TAILORED_PROFILE = tailored_profile
    save_json_file(TAILORED_PROFILE_PATH, tailored_profile)

    return jsonify({
        "status": "success",
        "message": "CV pomyślnie dopasowane i zsynchronizowane z plikiem PDF!",
        "ats_analysis": ats_analysis,
        "audit_results": audit_results
    })

@app.route("/preview/current")
def preview_current():
    global ACTIVE_LANGUAGE
    template_name = request.args.get("template", "pro_qa_sidebar")
    lang = request.args.get("lang", ACTIVE_LANGUAGE)
    ACTIVE_LANGUAGE = lang
    
    data = get_active_profile()
    data = QALogicEngine.audit_and_refine_profile(data, lang=lang)
    
    template_file = f"cv_templates/{template_name}.html"
    try:
        return render_template(template_file, data=data, lang=lang)
    except Exception:
        return render_template("cv_templates/pro_qa_sidebar.html", data=data, lang=lang)

@app.route("/api/export/pdf")
def export_pdf():
    global ACTIVE_LANGUAGE
    template_name = request.args.get("template", "pro_qa_sidebar")
    lang = request.args.get("lang", ACTIVE_LANGUAGE)
    
    # Dynamically fetch the current tailored profile
    data = get_active_profile()
    data = QALogicEngine.audit_and_refine_profile(data, lang=lang)
    
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

@app.route("/api/export/html")
def export_html():
    global ACTIVE_LANGUAGE
    template_name = request.args.get("template", "pro_qa_sidebar")
    lang = request.args.get("lang", ACTIVE_LANGUAGE)
    
    data = get_active_profile()
    data = QALogicEngine.audit_and_refine_profile(data, lang=lang)
    
    rendered = render_template(f"cv_templates/{template_name}.html", data=data, lang=lang)
    filename = "Michal_Kosowski_CV.html" if lang == "pl" else "Michal_Kosowski_Resume.html"
    
    return Response(
        rendered,
        mimetype="text/html",
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

    print(f"🚀 Uruchamianie VitaeCraft AI v1.9...")
    print(f"📍 Serwer dostępny pod adresem: http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=True)

if __name__ == "__main__":
    main()
