from fpdf import FPDF
from typing import Dict


def generate_pdf_report(report: Dict, out_path: str = "interview_report.pdf") -> str:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=f"Interview Report - Role: {report.get('role')}", ln=True)
    pdf.cell(0, 8, txt=f"Decision: {report.get('decision')}   Score: {report.get('total_score'):.1f}", ln=True)
    pdf.ln(4)
    pdf.multi_cell(0, 6, txt="Detailed breakdown:")
    for k, v in report.get("breakdown_avg", {}).items():
        pdf.cell(0, 6, txt=f" - {k}: {v:.1f}", ln=True)
    pdf.ln(4)
    pdf.multi_cell(0, 6, txt="Questions & answers:")
    for item in report.get("items", []):
        pdf.multi_cell(0, 6, txt=f"Q: {item.get('question')}\nA: {item.get('answer')}\nEval: {item.get('evaluation', {})}\n")
        pdf.ln(2)
    pdf.output(out_path)
    return out_path
