# ⚡ VitaeCraft AI — Luxury CV & Resume Builder (QA Architecture)

VitaeCraft AI to inteligentny, darmowy, lokalny generator oraz kreator CV przeznaczony dla Inżynierów QA, Testerów Oprogramowania i Specjalistów IT. Aplikacja pozwala na precyzyjne dopasowywanie CV pod oferty pracy z natychmiastową weryfikacją logiki domenowej QA, analizą słów kluczowych ATS oraz 100% zgodnym bezbłędnym eksportem PDF (Playwright Vector Engine).

---

## ✨ Główne Funkcje

- **👁️ Podgląd 1:1 Pixel-Perfect**: Zastosowanie silnika **Playwright Headless Chromium** do generowania pliku PDF 1:1 identycznego z podglądem wizualnym w przeglądarce (pełna obsługa polskich znaków UTF-8 bez czarnych kwadratów).
- **🧠 QA Domain Logic Engine (`qa_logic_engine.py`)**: Silnik weryfikacji logiki QA formułuje doświadczenie za pomocą autentycznych czasowników akcji i narzędzi (Playwright, TypeScript, REST API, Postman, Swagger, Jira, Xray, TestRail, Agile/Scrum).
- **🛡️ 100% ATS-Proof (Skanery Korporacyjne)**: Analizator słów kluczowych obok tradycyjnego szablonu dwukolumnowego oferuje dedykowany szablon jednokolumnowy **`ats_single_column.html`** zgodny ze skanerami Workday, Taleo i Greenhouse.
- **🌐 Wsparcie Dwujęzyczne (PL & EN)**: Przełącznik języka pozwala na automatyczne tłumaczenie i generowanie CV po polsku lub angielsku.
- **🤖 Podwójny Silnik AI**: Wsparcie dla Google Gemini API (darmowy tier), Ollama (lokalne LLM) oraz wbudowanego silnika regułowego z rygorystyczną dyrektywą Anti-AI Jargon.
- **📝 Formularz Wizualny & Edytor JSON**: Wygodne zarządzanie danymi kontaktowymi, podsumowaniem, doświadczeniem, umiejętnościami i językami obcymi.

---

## 🚀 Szybkie Uruchomienie (Quick Start)

### 1. Klonowanie Repozytorium:
```bash
git clone https://github.com/jablefthookcross/luxury_cv_builder.git
cd luxury_cv_builder
```

### 2. Utworzenie Środowiska Wirtualnego & Instalacja Zależności:
```bash
python3 -m venv venv
source venv/bin/activate   # Na systemach Linux/WSL/macOS
# lub dla Windows CMD: venv\Scripts\activate

pip install -r requirements.txt
playwright install chromium
```

### 3. Uruchomienie Aplikacji:
```bash
python app.py --host 0.0.0.0 --port 5000
```
Otwórz przeglądarkę pod adresem: **http://127.0.0.1:5000**

---

## 🛠️ Architektura Projektu

```text
luxury_cv_builder/
├── app.py                     # Główny serwer Flask & REST API
├── ai_engine.py              # Silnik AI (Gemini, Ollama, Rule Fallback)
├── qa_logic_engine.py        # Ekspert logiki inżynierii jakości QA (PL/EN)
├── pdf_exporter.py           # Silnik generowania PDF 1:1 (Playwright Chromium)
├── pdf_parser.py             # Parser tekstu z załączonych plików PDF
├── job_analyzer.py           # Analizator ATS Match Score (%)
├── profile_data.json         # Główny profil bazowy kandydata
├── requirements.txt          # Zależności bibliotek Python
├── templates/                # Szablony HTML i szablony CV
│   ├── index.html            # Interfejs GUI Dashboardu
│   └── cv_templates/
│       ├── pro_qa_sidebar.html
│       └── ats_single_column.html
└── static/                   # Stylizacja CSS & Zasoby
    └── css/style.css
```

---

## 📄 Licencja
Projekt udostępniany na licencji MIT.
