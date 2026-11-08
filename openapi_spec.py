"""
VitaeCraft AI - OpenAPI 3.0 Specification
Defines all endpoints, parameters, request bodies, and responses for Swagger UI and Postman.
"""

def get_openapi_spec() -> dict:
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "VitaeCraft AI - Intelligent CV Generator & QA Tailoring Engine API",
            "version": "2.1.0",
            "description": (
                "Kompletna dokumentacja REST API dla aplikacji **VitaeCraft AI**.\n\n"
                "Umożliwia pełną automatyzację generowania CV dopasowanego do ofert pracy dla inżynierów QA / SDET, "
                "zarządzanie profilami kandydatów, archiwum aplikacji oraz **nuklearne czyszczenie środowiska testowego**.\n\n"
                "### Autoryzacja:\n"
                "- **Użytkownicy**: nagłówek `Authorization: Bearer <access_token>` (uzyskany z `/api/auth/login` lub `/api/auth/register`).\n"
                "- **Administrator / Test Operator**: nagłówek `x-admin-secret: <ADMIN_CLEANUP_SECRET>` dla endpointu `/admin/cleanup`."
            ),
            "contact": {
                "name": "VitaeCraft Development & QA Architecture",
                "url": "https://github.com/jablefthookcross"
            }
        },
        "servers": [
            {"url": "https://vitaecraft-ai.onrender.com", "description": "Środowisko chmurowe / produkcyjne (zawsze online)"},
            {"url": "http://127.0.0.1:5000", "description": "Lokalny serwer deweloperski / testowy"}
        ],
        "tags": [
            {"name": "Admin & Technical", "description": "Nuklearne czyszczenie danych testowych i reset stanu aplikacji"},
            {"name": "Authentication", "description": "Rejestracja, logowanie i weryfikacja tokenów sesji"},
            {"name": "Profile", "description": "Zarządzanie profilem bazowym kandydata oraz import z pliku PDF"},
            {"name": "AI Tailoring & Intelligence", "description": "Silnik AI: analiza ogłoszeń, ekstrakcja wymagań, dopasowywanie CV i szlifowanie promptem"},
            {"name": "Preview & Export", "description": "Renderowanie podglądu HTML oraz eksport do pliku PDF (Playwright 1:1)"},
            {"name": "Saved CVs Archive", "description": "Archiwum wygenerowanych i zapisanych aplikacji CV"},
            {"name": "Settings", "description": "Konfiguracja silnika LLM (Gemini API / Ollama)"}
        ],
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "Podaj token dostępu wygenerowany podczas logowania lub rejestracji."
                },
                "AdminSecret": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "x-admin-secret",
                    "description": "Tajny klucz administracyjny do wywołania nuklearnego czyszczenia (np. w Postmanie lub testach)."
                }
            },
            "schemas": {
                "PersonalInfo": {
                    "type": "object",
                    "properties": {
                        "full_name": {"type": "string", "example": "Michał Kosowski"},
                        "title": {"type": "string", "example": "Software QA Engineer / Test Automation"},
                        "email": {"type": "string", "format": "email", "example": "tester@example.com"},
                        "phone": {"type": "string", "example": "+48 518 075 716"},
                        "location": {"type": "string", "example": "Warszawa, Polska"},
                        "linkedin": {"type": "string", "example": ""},
                        "github": {"type": "string", "example": "https://github.com/jablefthookcross"},
                        "website": {"type": "string", "example": ""}
                    }
                },
                "SkillCategory": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string", "example": "Programowanie & Automatyzacja"},
                        "items": {
                            "type": "array",
                            "items": {"type": "string"},
                            "example": ["Playwright", "TypeScript", "JavaScript", "SQL", "Git"]
                        }
                    }
                },
                "ExperienceItem": {
                    "type": "object",
                    "properties": {
                        "company": {"type": "string", "example": "Benefit Systems S.A."},
                        "position": {"type": "string", "example": "Software tester / QA Automation"},
                        "location": {"type": "string", "example": "Warszawa"},
                        "start_date": {"type": "string", "example": "2022"},
                        "end_date": {"type": "string", "example": "Obecnie"},
                        "highlights": {
                            "type": "array",
                            "items": {"type": "string"},
                            "example": [
                                "Projektowanie i automatyzacja testów E2E w Playwright.",
                                "Testy manualne i walidacja REST API w Postmanie."
                            ]
                        }
                    }
                },
                "LanguageItem": {
                    "type": "object",
                    "properties": {
                        "language": {"type": "string", "example": "Angielski"},
                        "level": {"type": "string", "example": "Biegły (B2+)"}
                    }
                },
                "ProfileSchema": {
                    "type": "object",
                    "properties": {
                        "personal_info": {"$ref": "#/components/schemas/PersonalInfo"},
                        "summary": {"type": "string", "example": "QA Automation Engineer z ponad 5-letnim doświadczeniem..."},
                        "skills": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/SkillCategory"}
                        },
                        "experience": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/ExperienceItem"}
                        },
                        "languages": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/LanguageItem"}
                        },
                        "projects": {"type": "array", "items": {"type": "object"}},
                        "education": {"type": "array", "items": {"type": "object"}},
                        "certifications": {"type": "array", "items": {"type": "object"}}
                    }
                },
                "JobSpec": {
                    "type": "object",
                    "properties": {
                        "target_role": {"type": "string", "example": "Senior QA Automation Engineer"},
                        "seniority": {"type": "string", "example": "Senior"},
                        "domain": {"type": "string", "example": "E-Commerce / FinTech"},
                        "primary_technologies": {"type": "array", "items": {"type": "string"}, "example": ["Playwright", "TypeScript", "REST API"]},
                        "secondary_technologies": {"type": "array", "items": {"type": "string"}, "example": ["SQL", "Docker", "GitLab CI"]},
                        "tools": {"type": "array", "items": {"type": "string"}, "example": ["Jira", "Postman", "Swagger"]},
                        "testing_types": {"type": "array", "items": {"type": "string"}, "example": ["E2E", "API Testing", "Regression"]},
                        "detected_language": {"type": "string", "example": "pl"}
                    }
                }
            }
        },
        "paths": {
            "/admin/cleanup": {
                "post": {
                    "tags": ["Admin & Technical"],
                    "summary": "💥 Nuklearne czyszczenie wszystkich danych testowych",
                    "description": (
                        "Destrukcyjny techniczny endpoint czyszczący środowisko ze śmieci testowych.\n\n"
                        "Usuwa:\n"
                        "- Utworzone konta testowe z bazy użytkowników\n"
                        "- Profile testowe\n"
                        "- Zapisane aplikacje z archiwum Moje CV-ki (katalog lokalny oraz Supabase)\n"
                        "- Pliki tymczasowe PDF z katalogu wyjściowego\n\n"
                        "**Wymaga podania sekretu** w nagłówku `x-admin-secret`.\n"
                        "Domyślnie zachowuje profil właściciela (`Michał Kosowski` / `tester_qa_2026`)."
                    ),
                    "security": [
                        {"AdminSecret": []}
                    ],
                    "parameters": [
                        {
                            "name": "x-admin-secret",
                            "in": "header",
                            "required": True,
                            "schema": {"type": "string", "example": "vitaecraft-nuclear-secret-2026"},
                            "description": "Klucz zabezpieczający endpoint czyszczenia"
                        }
                    ],
                    "requestBody": {
                        "required": False,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "preserve_owner": {
                                            "type": "boolean",
                                            "default": True,
                                            "description": "Czy zachować konto i profil właściciela (Michał Kosowski)"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Czyszczenie zakończone pomyślnie",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "status": "success",
                                        "message": "Nuklearne czyszczenie wykonane pomyślnie. Śmieci usunięte, stan zresetowany.",
                                        "details": {
                                            "users_deleted": 3,
                                            "profiles_deleted": 3,
                                            "saved_cvs_deleted": 5,
                                            "temp_files_deleted": 2,
                                            "preserve_owner": True
                                        }
                                    }
                                }
                            }
                        },
                        "403": {
                            "description": "Brak dostępu – błędny lub brakujący nagłówek x-admin-secret"
                        }
                    }
                }
            },
            "/api/admin/cleanup": {
                "post": {
                    "tags": ["Admin & Technical"],
                    "summary": "💥 Nuklearne czyszczenie (Alias /api/admin/cleanup)",
                    "description": "Alias dla `/admin/cleanup`. Działa identycznie.",
                    "security": [{"AdminSecret": []}],
                    "parameters": [
                        {
                            "name": "x-admin-secret",
                            "in": "header",
                            "required": True,
                            "schema": {"type": "string", "example": "vitaecraft-nuclear-secret-2026"}
                        }
                    ],
                    "responses": {
                        "200": {"description": "Sukces"},
                        "403": {"description": "Błąd autoryzacji"}
                    }
                }
            },
            "/api/auth/register": {
                "post": {
                    "tags": ["Authentication"],
                    "summary": "Rejestracja nowego użytkownika",
                    "description": "Tworzy nowe konto z czystym, wyizolowanym profilem startowym.",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["email", "password"],
                                    "properties": {
                                        "email": {"type": "string", "example": "nowy_tester@example.com"},
                                        "password": {"type": "string", "example": "tajnehaslo123"},
                                        "full_name": {"type": "string", "example": "Jan Nowy"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Konto utworzone, zwraca token dostępu",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "status": "success",
                                        "message": "Konto utworzone pomyślnie! Zalogowano automatycznie.",
                                        "access_token": "eyJ1aWQiOi...",
                                        "user": {"id": "uuid-...", "email": "nowy_tester@example.com", "full_name": "Jan Nowy"}
                                    }
                                }
                            }
                        },
                        "400": {"description": "Nieprawidłowe dane rejestracji"}
                    }
                }
            },
            "/api/auth/login": {
                "post": {
                    "tags": ["Authentication"],
                    "summary": "Logowanie użytkownika",
                    "description": "Uwierzytelnia użytkownika i generuje token JWT.",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["email", "password"],
                                    "properties": {
                                        "email": {"type": "string", "example": "mmkosowski94@gmail.com"},
                                        "password": {"type": "string", "example": "tester_qa_2026"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Zalogowano pomyślnie",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "status": "success",
                                        "message": "Zalogowano pomyślnie!",
                                        "access_token": "eyJ1aWQiOi...",
                                        "user": {"id": "uuid-...", "email": "mmkosowski94@gmail.com", "full_name": "Michał Kosowski"}
                                    }
                                }
                            }
                        },
                        "400": {"description": "Błędny login lub hasło"}
                    }
                }
            },
            "/api/auth/status": {
                "get": {
                    "tags": ["Authentication"],
                    "summary": "Sprawdzenie statusu sesji",
                    "description": "Zwraca status zalogowanego użytkownika na podstawie nagłówka Bearer.",
                    "security": [{"BearerAuth": []}],
                    "responses": {
                        "200": {
                            "description": "Informacje o zalogowanym użytkowniku lub trybie gościa",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "authenticated": True,
                                        "user": {"id": "uuid-...", "email": "mmkosowski94@gmail.com"}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/profile": {
                "get": {
                    "tags": ["Profile"],
                    "summary": "Pobranie Głównego Profilu Bazowego",
                    "description": "Zwraca profil przypisany do zalogowanego użytkownika (lub anonimowy profil demo dla gościa).",
                    "security": [{"BearerAuth": []}],
                    "responses": {
                        "200": {
                            "description": "Obiekt profilu kandydata",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ProfileSchema"}
                                }
                            }
                        }
                    }
                },
                "post": {
                    "tags": ["Profile"],
                    "summary": "Zapisanie / Aktualizacja Profilu Bazowego",
                    "description": "Zapisuje dane profilu dla aktualnie uwierzytelnionego użytkownika.",
                    "security": [{"BearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ProfileSchema"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Profil zapisany pomyślnie",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "status": "success",
                                        "message": "Główny Profil Bazowy został pomyślnie zapisany w chmurze!"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/profile/reset": {
                "post": {
                    "tags": ["Profile"],
                    "summary": "Reset DRAFT-u do Profilu Bazowego",
                    "description": "Resetuje obecną edycję draftu i przywraca czysty profil bazowy.",
                    "security": [{"BearerAuth": []}],
                    "responses": {
                        "200": {
                            "description": "Draft zresetowany",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "status": "success",
                                        "message": "DRAFT został zresetowany do Twojego Głównego Profilu Bazowego!"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/profile/delete": {
                "post": {
                    "tags": ["Profile"],
                    "summary": "Wyczyszczenie profilu bazowego",
                    "description": "Czyści profil bazowy użytkownika do pustego formularza.",
                    "security": [{"BearerAuth": []}],
                    "responses": {
                        "200": {
                            "description": "Profil wyczyszczony"
                        }
                    }
                }
            },
            "/api/upload-pdf": {
                "post": {
                    "tags": ["Profile"],
                    "summary": "Import CV z pliku PDF",
                    "description": "Ekstrahuje tekst z pliku PDF z CV i konwertuje go w pamięci na ustrukturyzowany Profil Bazowy.",
                    "security": [{"BearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "required": ["file"],
                                    "properties": {
                                        "file": {
                                            "type": "string",
                                            "format": "binary",
                                            "description": "Plik PDF z CV kandydata"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Plik PDF pomyślnie sparsowany",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "status": "success",
                                        "message": "Plik Michal_Kosowski_CV.pdf został pomyślnie zaimportowany!",
                                        "profile": {"$ref": "#/components/schemas/ProfileSchema"}
                                    }
                                }
                            }
                        },
                        "400": {"description": "Niepoprawny plik PDF lub brak tekstu"}
                    }
                }
            },
            "/api/clean-text": {
                "post": {
                    "tags": ["AI Tailoring & Intelligence"],
                    "summary": "Oczyszczenie treści oferty pracy",
                    "description": "Usuwa szum ze stron z ogłoszeniami (benefity, ciasteczka, nawigacja).",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["text"],
                                    "properties": {
                                        "text": {"type": "string", "example": "Szukamy QA Automation... Pakiet multisport, owocowe czwartki..."}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Oczyszczony tekst oferty",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "status": "success",
                                        "cleaned_text": "Szukamy QA Automation..."
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/analyze-job": {
                "post": {
                    "tags": ["AI Tailoring & Intelligence"],
                    "summary": "KROK 1: Inteligentna analiza wymagań oferty (Job Spec)",
                    "description": "Analizuje treść ogłoszenia i zwraca obiekt JobSpecification z technologiami, narzędziami i poziomem seniority.",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["job_text"],
                                    "properties": {
                                        "job_text": {"type": "string", "example": "Poszukujemy Senior QA Automation z biegłą znajomością Playwright i TypeScript..."},
                                        "provider": {"type": "string", "default": "auto", "enum": ["auto", "gemini", "ollama"]}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Ustrukturyzowana specyfikacja oferty",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "status": "success",
                                        "spec": {"$ref": "#/components/schemas/JobSpec"}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/tailor": {
                "post": {
                    "tags": ["AI Tailoring & Intelligence"],
                    "summary": "KROK 2: Generowanie dopasowanego CV w pamięci",
                    "description": "Kompiluje dedykowane CV na podstawie profilu bazowego i oferty pracy. Zwraca dopasowany profil, wynik ATS i audyt autentyczności.",
                    "security": [{"BearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["job_description"],
                                    "properties": {
                                        "job_description": {"type": "string", "example": "Wymagania: Playwright, TypeScript, SQL..."},
                                        "target_role": {"type": "string", "example": "QA Automation Engineer"},
                                        "provider": {"type": "string", "default": "auto", "enum": ["auto", "gemini", "ollama"]},
                                        "template": {"type": "string", "default": "pro_qa_sidebar"},
                                        "lang": {"type": "string", "default": "auto", "enum": ["auto", "pl", "en"]}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Wygenerowane CV oraz wyniki audytu",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "status": "success",
                                        "message": "Dedykowane CV zostało wygenerowane bezstanowo w pamięci!",
                                        "profile": {"$ref": "#/components/schemas/ProfileSchema"},
                                        "rendered_html": "<html>...</html>",
                                        "ats_analysis": {
                                            "match_score": 95,
                                            "matched_keywords": ["Playwright", "TypeScript", "SQL"],
                                            "missing_keywords": []
                                        },
                                        "audit_results": {
                                            "anti_ai_score": 100,
                                            "is_ats_safe": True
                                        },
                                        "buckets_breakdown": {
                                            "bucket_a": ["Playwright", "TypeScript"],
                                            "bucket_b": ["SQL", "Git"],
                                            "bucket_c": ["Android Studio"]
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/tailor-from-spec": {
                "post": {
                    "tags": ["AI Tailoring & Intelligence"],
                    "summary": "Dopasowanie CV bezpośrednio ze specyfikacji JobSpec",
                    "description": "Kompiluje CV na podstawie wcześniej wygenerowanego obiektu JobSpecification.",
                    "security": [{"BearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["job_spec"],
                                    "properties": {
                                        "job_spec": {"$ref": "#/components/schemas/JobSpec"},
                                        "template": {"type": "string", "default": "pro_qa_sidebar"},
                                        "lang": {"type": "string", "default": "auto"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Wygenerowane CV"}
                    }
                }
            },
            "/api/refine-cv": {
                "post": {
                    "tags": ["AI Tailoring & Intelligence"],
                    "summary": "KROK 3: Szlifowanie CV promptem języka naturalnego",
                    "description": "Wprowadza precyzyjne modyfikacje do aktualnego CV zgodnie z poleceniem użytkownika.",
                    "security": [{"BearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["user_instruction"],
                                    "properties": {
                                        "current_cv_data": {"$ref": "#/components/schemas/ProfileSchema"},
                                        "user_instruction": {"type": "string", "example": "Skróć podsumowanie do 2 zdań i umieść Playwright na pierwszym miejscu w umiejętnościach."},
                                        "template": {"type": "string", "default": "pro_qa_sidebar"},
                                        "lang": {"type": "string", "default": "pl"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Zaktualizowany profil i podgląd HTML",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "status": "success",
                                        "message": "Poprawki AI zostały pomyślnie zastosowane!",
                                        "profile": {"$ref": "#/components/schemas/ProfileSchema"},
                                        "rendered_html": "<html>...</html>"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/preview/render": {
                "post": {
                    "tags": ["Preview & Export"],
                    "summary": "Renderowanie podglądu HTML z danych profilu",
                    "description": "Generuje kod HTML szablonu CV na podstawie przekazanego obiektu JSON.",
                    "security": [{"BearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "profile": {"$ref": "#/components/schemas/ProfileSchema"},
                                        "template": {"type": "string", "default": "pro_qa_sidebar"},
                                        "lang": {"type": "string", "default": "pl"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Wygenerowany kod HTML",
                            "content": {
                                "application/json": {
                                    "example": {"status": "success", "html": "<html>...</html>"}
                                }
                            }
                        }
                    }
                }
            },
            "/preview/current": {
                "get": {
                    "tags": ["Preview & Export"],
                    "summary": "Pobranie aktualnego podglądu HTML (dla iFrame)",
                    "description": "Zwraca bezpośredni dokument HTML dla podglądu w przeglądarce.",
                    "parameters": [
                        {"name": "template", "in": "query", "schema": {"type": "string", "default": "pro_qa_sidebar"}},
                        {"name": "lang", "in": "query", "schema": {"type": "string", "default": "pl"}},
                        {"name": "token", "in": "query", "schema": {"type": "string"}, "description": "Token JWT użytkownika"}
                    ],
                    "responses": {
                        "200": {
                            "description": "Dokument HTML szablonu",
                            "content": {"text/html": {}}
                        }
                    }
                }
            },
            "/api/export/pdf": {
                "post": {
                    "tags": ["Preview & Export"],
                    "summary": "Pobranie pliku PDF (Playwright 1:1 Pixel-Perfect)",
                    "description": "Kompiluje i zwraca binarny plik PDF z polskimi znakami i brakiem cache'owania.",
                    "security": [{"BearerAuth": []}],
                    "requestBody": {
                        "required": False,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "profile_data": {"$ref": "#/components/schemas/ProfileSchema"},
                                        "template": {"type": "string", "default": "pro_qa_sidebar"},
                                        "lang": {"type": "string", "default": "pl"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Plik PDF z CV",
                            "content": {"application/pdf": {}}
                        }
                    }
                }
            },
            "/api/saved-cvs": {
                "get": {
                    "tags": ["Saved CVs Archive"],
                    "summary": "Pobranie listy zapisanych CV",
                    "description": "Zwraca listę wszystkich zapisanych aplikacji CV dla zalogowanego użytkownika.",
                    "security": [{"BearerAuth": []}],
                    "responses": {
                        "200": {
                            "description": "Lista zapisanych aplikacji",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "status": "success",
                                        "cvs": [
                                            {
                                                "id": "uuid-...",
                                                "company_name": "Google",
                                                "target_title": "Senior QA Engineer",
                                                "match_score": 96,
                                                "lang": "pl",
                                                "created_at": "2026-11-08 19:00:00"
                                            }
                                        ]
                                    }
                                }
                            }
                        }
                    }
                },
                "post": {
                    "tags": ["Saved CVs Archive"],
                    "summary": "Zapisanie CV do archiwum Moje CV-ki",
                    "description": "Zapisuje skompilowaną aplikację CV w bazie Supabase / lokalnym repozytorium.",
                    "security": [{"BearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["company_name"],
                                    "properties": {
                                        "company_name": {"type": "string", "example": "Google Poland"},
                                        "target_title": {"type": "string", "example": "Staff QA Automation Engineer"},
                                        "lang": {"type": "string", "default": "pl"},
                                        "match_score": {"type": "integer", "example": 98},
                                        "profile_data": {"$ref": "#/components/schemas/ProfileSchema"},
                                        "job_text": {"type": "string", "example": "Treść ogłoszenia..."}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "CV pomyślnie zapisane",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "status": "success",
                                        "message": "CV dla Google Poland zostało pomyślnie zapisane w Moich CV!"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/saved-cvs/{cv_id}": {
                "get": {
                    "tags": ["Saved CVs Archive"],
                    "summary": "Pobranie szczegółów zapisanego CV",
                    "security": [{"BearerAuth": []}],
                    "parameters": [
                        {"name": "cv_id", "in": "path", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {
                        "200": {"description": "Rekord CV wraz z pełnym profilem"},
                        "404": {"description": "Nie znaleziono pliku"}
                    }
                },
                "delete": {
                    "tags": ["Saved CVs Archive"],
                    "summary": "Usunięcie zapisanego CV z archiwum",
                    "security": [{"BearerAuth": []}],
                    "parameters": [
                        {"name": "cv_id", "in": "path", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {
                        "200": {"description": "Zapisane CV zostało usunięte"},
                        "404": {"description": "Nie znaleziono"}
                    }
                }
            },
            "/api/saved-cvs/{cv_id}/export/pdf": {
                "get": {
                    "tags": ["Saved CVs Archive"],
                    "summary": "Pobranie pliku PDF zapisanego CV z archiwum",
                    "security": [{"BearerAuth": []}],
                    "parameters": [
                        {"name": "cv_id", "in": "path", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {
                        "200": {
                            "description": "Plik PDF",
                            "content": {"application/pdf": {}}
                        }
                    }
                }
            },
            "/api/settings": {
                "get": {
                    "tags": ["Settings"],
                    "summary": "Pobranie statusu konfiguracji AI",
                    "description": "Zwraca status podłączonego klucza Gemini i konfigurację Ollama (bez wycieku kluczy).",
                    "responses": {
                        "200": {
                            "description": "Status konfiguracji",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "status": "success",
                                        "settings": {
                                            "has_gemini_key": True,
                                            "ollama_url": "http://localhost:11434",
                                            "ollama_model": "llama3.2"
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "post": {
                    "tags": ["Settings"],
                    "summary": "Zapisanie konfiguracji silników AI",
                    "description": "Pozwala zaktualizować klucz Gemini lub parametry lokalnego serwera Ollama.",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "gemini_key": {"type": "string", "example": "AQ..."},
                                        "ollama_url": {"type": "string", "example": "http://localhost:11434"},
                                        "ollama_model": {"type": "string", "example": "llama3.2"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Ustawienia zapisane"}
                    }
                }
            }
        }
    }
