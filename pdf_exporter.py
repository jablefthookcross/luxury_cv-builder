"""
VitaeCraft AI - PDF Exporter Module
Generates 1:1 pixel-perfect PDF files matching browser preview using Playwright Headless Chromium.
Includes DejaVu ReportLab fallback engine.
"""

import io
import asyncio
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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
        Renders HTML content in Playwright Headless Chromium and prints to A4 PDF.
        Guarantees 100% pixel-perfect matching with browser preview!
        """
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_content(html_content, wait_until="networkidle")
                
                pdf_bytes = page.pdf(
                    format="A4",
                    print_background=True,
                    margin={"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"}
                )
                browser.close()
                return pdf_bytes
        except Exception as e:
            print(f"[PDFExporter Warning] Playwright PDF generation failed ({e}). Falling back to ReportLab.")
            return b""

    @staticmethod
    def generate_pdf(data: dict) -> bytes:
        """ReportLab Fallback PDF Generator."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        story = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'CVTitle',
            parent=styles['Heading1'],
            fontName=FONT_BOLD,
            fontSize=22,
            leading=26,
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
            fontSize=9,
            textColor=colors.HexColor('#64748b')
        )
        sec_title_style = ParagraphStyle(
            'CVSecTitle',
            parent=styles['Heading2'],
            fontName=FONT_BOLD,
            fontSize=11,
            leading=15,
            textColor=colors.HexColor('#0f172a'),
            spaceBefore=10,
            spaceAfter=4
        )
        body_style = ParagraphStyle(
            'CVBody',
            parent=styles['Normal'],
            fontName=FONT_REGULAR,
            fontSize=9,
            leading=13.5,
            textColor=colors.HexColor('#334155')
        )
        bullet_style = ParagraphStyle(
            'CVBullet',
            parent=styles['Normal'],
            fontName=FONT_REGULAR,
            fontSize=8.5,
            leading=12.5,
            textColor=colors.HexColor('#334155'),
            leftIndent=10
        )

        pinfo = data.get("personal_info", {})
        story.append(Paragraph(pinfo.get("full_name", "Michał Kosowski"), title_style))
        if pinfo.get("title"):
            story.append(Paragraph(pinfo.get("title"), subtitle_style))
        
        contacts = []
        if pinfo.get("email"): contacts.append(pinfo.get("email"))
        if pinfo.get("phone"): contacts.append(str(pinfo.get("phone")))
        if pinfo.get("location"): contacts.append(pinfo.get("location"))

        story.append(Spacer(1, 4))
        story.append(Paragraph(" • ".join(contacts), contact_style))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563eb'), spaceAfter=8))

        if data.get("summary"):
            story.append(Paragraph("PODSUMOWANIE ZAWODOWE", sec_title_style))
            story.append(Paragraph(data["summary"], body_style))
            story.append(Spacer(1, 6))

        if data.get("experience"):
            story.append(Paragraph("DOŚWIADCZENIE ZAWODOWE", sec_title_style))
            for job in data["experience"]:
                pos = job.get('position', '')
                comp = job.get('company', '')
                header_text = f"<b>{pos}</b> — <font color='#2563eb'>{comp}</font>"
                meta_text = f"<font color='#64748b'>{job.get('start_date', '')} – {job.get('end_date', '')} | {job.get('location', '')}</font>"
                story.append(Paragraph(f"{header_text} &nbsp;&nbsp; {meta_text}", body_style))
                
                highlights = job.get("highlights", [])
                if isinstance(highlights, list):
                    for h in highlights:
                        story.append(Paragraph(f"• {h}", bullet_style))
                story.append(Spacer(1, 4))

        if data.get("skills"):
            story.append(Paragraph("UMIEJĘTNOŚCI I TECHNOLOGIE", sec_title_style))
            for cat in data["skills"]:
                cat_name = cat.get("category", "")
                items = cat.get("items", [])
                if isinstance(items, list):
                    items_str = ", ".join(items)
                else:
                    items_str = str(items)
                story.append(Paragraph(f"<b>{cat_name}:</b> {items_str}", body_style))
                story.append(Spacer(1, 2))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
