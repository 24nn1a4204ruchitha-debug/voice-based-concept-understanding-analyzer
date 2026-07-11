"""
report_generator.py
--------------------
Generates a downloadable, structured PDF report summarizing the analysis
results for a given session, using the fpdf2 library.
"""

import os
import re
import datetime
from typing import Dict


def _clean_text(text: str) -> str:
    """Strip characters that the default PDF font (Latin-1) can't encode."""
    if not text:
        return ""
    return re.sub(r"[^\x00-\xFF]", "", text)


def generate_pdf_report(report_data: Dict, output_dir: str = "reports") -> str:
    from fpdf import FPDF

    os.makedirs(output_dir, exist_ok=True)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ---- Title ----
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 12, "VBCUA Analysis Report", ln=True, align="C")

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(90, 90, 90)
    pdf.cell(0, 8, _clean_text(report_data.get("type", "")), ln=True, align="C")
    pdf.ln(4)

    # ---- Meta info ----
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 7, f"Name: {_clean_text(report_data.get('student_name', 'Anonymous'))}", ln=True)
    pdf.cell(0, 7, f"Date: {report_data.get('timestamp', datetime.datetime.now())}", ln=True)
    if "concept" in report_data:
        pdf.cell(0, 7, f"Concept: {_clean_text(report_data.get('concept', ''))}", ln=True)
    pdf.ln(4)

    # ---- Overall score ----
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, f"Overall Score: {report_data.get('overall_score', 0):.1f} / 100", ln=True)
    pdf.ln(2)

    # ---- Score breakdown ----
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Score Breakdown", ln=True)
    pdf.set_font("Helvetica", "", 10)
    for key, value in report_data.get("breakdown", {}).items():
        if isinstance(value, dict):
            pdf.cell(0, 6, f"  {key}:", ln=True)
            for sub_k, sub_v in value.items():
                pdf.cell(0, 6, f"    - {sub_k}: {sub_v}", ln=True)
        else:
            pdf.cell(0, 6, f"  {key}: {value}", ln=True)
    pdf.ln(3)

    # ---- Audio features ----
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Audio & Fluency Metrics", ln=True)
    pdf.set_font("Helvetica", "", 10)
    for key, value in report_data.get("audio_features", {}).items():
        pdf.cell(0, 6, f"  {key}: {value}", ln=True)
    pdf.ln(3)

    # ---- Feedback ----
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Feedback", ln=True)
    pdf.set_font("Helvetica", "", 10)
    for line in report_data.get("feedback", []):
        pdf.multi_cell(0, 6, _clean_text(f"- {line}"))
    pdf.ln(3)

    # ---- Transcript ----
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Transcript", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, _clean_text(report_data.get("transcript", "") or "No speech detected."))

    if "reference_text" in report_data:
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Reference Concept Definition", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 6, _clean_text(report_data.get("reference_text", "")))

    safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", report_data.get("student_name", "user"))
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"VBCUA_Report_{safe_name}_{timestamp}.pdf"
    output_path = os.path.join(output_dir, filename)
    pdf.output(output_path)

    return output_path
