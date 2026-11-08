# ⚡ VitaeCraft AI — Intelligent ATS Resume Engine for QA Specialists

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white&style=flat-square)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-000000?logo=flask&logoColor=white&style=flat-square)](https://flask.palletsprojects.com/)
[![Playwright](https://img.shields.io/badge/Playwright-Chromium-45BA4B?logo=playwright&logoColor=white&style=flat-square)](https://playwright.dev/)
[![Gemini](https://img.shields.io/badge/Google_Gemini-API-8E75C2?logo=google&logoColor=white&style=flat-square)](https://ai.google.dev/)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-black?style=flat-square)](https://ollama.ai/)
[![ATS](https://img.shields.io/badge/ATS-100%25_Compliant-success?style=flat-square)](https://workday.com)

VitaeCraft AI to inteligentny, lokalny generator oraz optymalizator CV stworzony z myślą o Inżynierach QA, Testerach Oprogramowania i Specjalistach IT. Aplikacja analizuje treść ofert pracy, weryfikuje słownictwo domenowe inżynierii jakości, dopasowuje profil kandydata pod skanery korporacyjne (ATS) i eksportuje wektorowe pliki PDF 1:1 za pomocą bezgłowej przeglądarki Chromium (Playwright Vector Engine).

---

## ✨ Kluczowe Cechy Architektury

- **👁️ Playwright Vector PDF Exporter**: Zamiast niestabilnych generatorów HTML-to-PDF (takich jak wkhtmltopdf czy pdfkit, które gubią polskie znaki UTF-8 i psują kerning), VitaeCraft wykorzystuje bezgłowy silnik **Playwright Headless Chromium**. Zapewnia to wektorowy wydruk PDF 1:1 identyczny z renderem w nowoczesnej przeglądarce.
- **🧠 QA Domain Logic Engine (`qa_logic_engine.py`)**: Dedykowany silnik reguł domenowych dbający o poprawność techniczną i wiarygodność profilu QA. Weryfikuje i formatuje opisy doświadczenia z wykorzystaniem profesjonalnych czasowników akcji i narzędzi (Playwright, TypeScript, REST API, Postman, Swagger, Jira, Xray, TestRail, Agile/Scrum).
- **🛡️ 100% Zgodność z ATS (Workday, Taleo, Greenhouse)**: Obok estetycznego szablonu dwukolumnowego aplikacja zawiera zoptymalizowany szablon jednokolumnowy **`ats_single_column.html`**, który eliminuje tabelaryczne artefakty i jest bezbłędnie parsowany przez korporacyjne parsery CV.
- **🤖 Hybrydowy Silnik AI + Deterministyczny Fallback**:
  - Obsługa chmurowego **Google Gemini API** (szybka analiza i wzbogacanie treści).
  - Wsparcie dla w pełni lokalnych modeli LLM przez **Ollama** (brak wysyłania danych poza maszynę).
  - Deterministyczny silnik regułowy (Rule-based Fallback) – gwarantuje działanie aplikacji nawet bez dostępu do API czy internetu, z rygorystycznym filtrowaniem żargonu "AI buzzwords".
- **🌐 Pełna Dwujęzyczność (PL & EN)**: Dynamiczne przełączanie języka i automatyczna adaptacja terminologii branżowej pod rynek polski i międzynarodowy.

---

## 🚀 Szybkie Uruchomienie (Quick Start)

### 1. Klonowanie Repozytorium
```bash
git clone https://github.com/jablefthookcross/luxury_cv-builder.git
cd luxury_cv-builder
```

### 2. Utworzenie Środowiska Wirtualnego & Instalacja
```bash
python3 -m venv venv
source venv/bin/activate   # Linux / WSL / macOS
# lub dla Windows: venv\Scripts\activate

pip install -r requirements.txt
playwright install chromium
```

### 3. Konfiguracja Środowiska (Opcjonalna)
Skopiuj szablon konfiguracji:
```bash
cp .env.example .env
```
*(W pliku `.env` możesz opcjonalnie podać `GEMINI_API_KEY` lub skonfigurować lokalną `Ollama`. W przypadku braku kluczy aplikacja automatycznie skorzysta z silnika wbudowanego).*

### 4. Uruchomienie Aplikacji
```bash
python app.py --host 127.0.0.1 --port 5000
```
Otwórz w przeglądarce: **http://127.0.0.1:5000**

---

## 🛠️ Struktura i Moduły

```text
luxury_cv-builder/
├── app.py                     # Serwer Flask & REST API
├── ai_engine.py              # Silnik orkiestracji AI (Gemini / Ollama / Fallback)
├── qa_logic_engine.py        # Ekspert reguł inżynierii jakości i słownictwa QA
├── cv_tailor_engine.py       # Silnik dopasowywania doświadczenia do oferty pracy
├── pdf_exporter.py           # Silnik generowania PDF 1:1 (Playwright Chromium)
├── job_analyzer.py           # Analizator zgodności słów kluczowych i ATS Match Score
├── pdf_parser.py             # Ekstraktor tekstu ze źródłowych plików CV
├── profile_data.json         # Bazowe dane profilowe
├── requirements.txt          # Zależności Python
├── templates/                # Szablony Jinja2 (interfejs oraz szablony CV)
│   ├── index.html            # Dashboard aplikacji
│   └── cv_templates/
│       ├── pro_qa_sidebar.html
│       └── ats_single_column.html
└── static/                   # Style CSS i assety interfejsu
```

---

## 📄 Licencja
Projekt udostępniany na licencji MIT.

