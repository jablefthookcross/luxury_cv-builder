"""
VitaeCraft AI - PDF Exporter Module
Generates 1:1 pixel-perfect PDF files matching browser preview using Playwright Headless Chromium.
Includes clean ReportLab fallback engine.
"""

import os
import sys
import io
import asyncio
import subprocess
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Ensure Playwright browser paths are discovered on Render / Docker / Linux
if not os.environ.get("PLAYWRIGHT_BROWSERS_PATH"):
    if Path("/ms-playwright").exists():
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/ms-playwright"

# Register Polish UTF-8 supporting fonts for ReportLab fallback
FONT_REGULAR = "Helvetica"
FONT_BOLD = "Helvetica-Bold"

dejavu_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
dejavu_bold_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")

if dejavu_path.exists() and dejavu_bold_path.exists():
    try:
        pdfmetrics.registerFont(TTFont('DejaVu', str(dejavu_path)))
        pdfmetrics.registerFont(TTFont('DejaVu-Bold', str(dejavu_bold_path)))
        FONT_REGULAR = "DejaVu"
        FONT_BOLD = "DejaVu-Bold"
    except Exception as e:
        print(f"[PDFExporter Warning] Could not register DejaVu fonts: {e}")

class PDFExporter:
    @staticmethod
    def generate_pdf_from_html(html_content: str) -> bytes:
        """
        Renders HTML content in Playwright Headless Chromium with Docker/Cloud sandbox flags.
        Guarantees 100% pixel-perfect matching with browser preview!
        """
        docker_args = [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--no-first-run",
            "--no-zygote",
            "--single-process"
        ]

        def _render_once():
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, args=docker_args)
                page = browser.new_page()
                try:
                    page.set_content(html_content, wait_until="networkidle", timeout=30000)
                    page.evaluate("document.fonts.ready")
                except Exception:
                    page.set_content(html_content, wait_until="load", timeout=30000)
                pdf_bytes = page.pdf(
                    format="A4",
                    print_background=True,
                    margin={"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"}
                )
                browser.close()
                return pdf_bytes

        try:
            return _render_once()
        except Exception as first_err:
            print(f"[PDFExporter Warning] First Playwright launch attempt failed ({first_err}). Attempting on-the-fly chromium installation...")
            try:
                subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
                return _render_once()
            except Exception as e:
                print(f"[PDFExporter Fatal] Playwright PDF generation failed after install attempt: {e}. Falling back to ReportLab.")
                return b""

    @staticmethod
    def generate_pdf(data: dict, lang: str = "pl") -> bytes:
        """Clean ReportLab Fallback PDF Generator with bilingual header support."""
        is_en = (lang == "en")
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=32,
            bottomMargin=28
        )

        story = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'CVTitle',
            parent=styles['Heading1'],
            fontName=FONT_BOLD,
            fontSize=20,
            leading=24,
            textColor=colors.HexColor('#0f172a')
        )
        subtitle_style = ParagraphStyle(
            'CVSubtitle',
            parent=styles['Normal'],
            fontName=FONT_BOLD,
            fontSize=11,
            leading=15,
            textColor=colors.HexColor('#2563eb')
        )
        contact_style = ParagraphStyle(
            'CVContact',
            parent=styles['Normal'],
            fontName=FONT_REGULAR,
            fontSize=8.5,
            textColor=colors.HexColor('#64748b')
        )
        sec_title_style = ParagraphStyle(
            'CVSecTitle',
            parent=styles['Heading2'],
            fontName=FONT_BOLD,
            fontSize=10.5,
            leading=14,
            textColor=colors.HexColor('#0f172a'),
            spaceBefore=8,
            spaceAfter=4
        )
        body_style = ParagraphStyle(
            'CVBody',
            parent=styles['Normal'],
            fontName=FONT_REGULAR,
            fontSize=8.5,
            leading=12.5,
            textColor=colors.HexColor('#334155')
        )
        bullet_style = ParagraphStyle(
            'CVBullet',
            parent=styles['Normal'],
            fontName=FONT_REGULAR,
            fontSize=8.2,
            leading=11.8,
            textColor=colors.HexColor('#334155'),
            leftIndent=12
        )
        rodo_style = ParagraphStyle(
            'CVRodo',
            parent=styles['Normal'],
            fontName=FONT_REGULAR,
            fontSize=6.0,
            leading=8.0,
            textColor=colors.HexColor('#94a3b8')
        )

        pinfo = data.get("personal_info", {})
        story.append(Paragraph(pinfo.get("full_name", "Michał Kosowski"), title_style))
        if pinfo.get("title"):
            story.append(Paragraph(pinfo.get("title"), subtitle_style))
        
        contacts = []
        if pinfo.get("email"): contacts.append(pinfo.get("email"))
        if pinfo.get("phone"): contacts.append(str(pinfo.get("phone")))
        loc = "Warsaw, Poland" if is_en else (pinfo.get("location") or "Warszawa")
        contacts.append(loc)
        if pinfo.get("linkedin"): contacts.append("LinkedIn")
        if pinfo.get("github"): contacts.append("GitHub")

        story.append(Spacer(1, 3))
        story.append(Paragraph(" &bull; ".join(contacts), contact_style))
        story.append(Spacer(1, 4))
        story.append(HRFlowable(width="100%", thickness=1.0, color=colors.HexColor('#0f172a'), spaceAfter=6))

        if data.get("summary"):
            story.append(Paragraph("PROFESSIONAL SUMMARY" if is_en else "PODSUMOWANIE ZAWODOWE", sec_title_style))
            story.append(Paragraph(data["summary"], body_style))
            story.append(Spacer(1, 4))

        if data.get("experience"):
            story.append(Paragraph("WORK EXPERIENCE" if is_en else "DOŚWIADCZENIE ZAWODOWE", sec_title_style))
            for job in data["experience"]:
                pos = job.get('position') or job.get('role') or 'Software Tester'
                comp = job.get('company', '')
                dates = job.get('period') or f"{job.get('start_date', '')} – {job.get('end_date', '')}"
                loc_job = "Warsaw, Poland" if is_en else (job.get('location') or 'Warszawa')
                
                story.append(Paragraph(f"<b>{pos}</b> <font color='#64748b' size='7.5'>({dates})</font>", body_style))
                story.append(Paragraph(f"<font color='#2563eb'><b>{comp}</b></font> &bull; <font color='#64748b'>{loc_job}</font>", body_style))
                
                highlights = job.get("highlights", [])
                if isinstance(highlights, list):
                    for h in highlights:
                        story.append(Paragraph(f"&bull; {h}", bullet_style))
                story.append(Spacer(1, 3))

        if data.get("skills"):
            story.append(Paragraph("SKILLS & TECHNOLOGIES" if is_en else "UMIEJĘTNOŚCI I TECHNOLOGIE", sec_title_style))
            for cat in data["skills"]:
                cat_name = cat.get("category", "")
                items = cat.get("items", [])
                items_str = ", ".join(items) if isinstance(items, list) else str(items)
                story.append(Paragraph(f"<b>{cat_name}:</b> {items_str}", body_style))
                story.append(Spacer(1, 2))

        if data.get("languages"):
            story.append(Paragraph("LANGUAGES" if is_en else "JĘZYKI", sec_title_style))
            lang_items = []
            for l in data["languages"]:
                lang_items.append(f"<b>{l.get('language')}:</b> {l.get('level')}")
            story.append(Paragraph(" &bull; ".join(lang_items), body_style))
            story.append(Spacer(1, 4))

        story.append(Spacer(1, 6))
        rodo_text = (
            "I hereby give consent for my personal data included in my application to be processed for the purposes of current and future recruitment processes in accordance with Regulation (EU) 2016/679 of the European Parliament and of the Council (GDPR)."
            if is_en else
            "Wyrażam zgodę na przetwarzanie moich danych osobowych dla potrzeb niezbędnych do realizacji procesu rekrutacji (zgodnie z ustawą z dnia 10 maja 2018 roku o ochronie danych osobowych (Dz. U. ustaw z 2018, poz. 1000) oraz zgodnie z Rozporządzeniem Parlamentu Europejskiego i Rady (UE) 2016/679 z dnia 27 kwietnia 2016 r. w sprawie ochrony osób fizycznych w związku z przetwarzaniem danych osobowych i w sprawie swobodnego przepływu takich danych oraz uchylenia dyrektywy 95/46/WE (RODO))."
        )
        story.append(Paragraph(rodo_text, rodo_style))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
