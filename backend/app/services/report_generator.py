import io
import hashlib
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from app.models.analysis import Analysis

def generate_analysis_pdf_report(analysis: Analysis) -> io.BytesIO:
    """
    Builds a professional PDF Certificate of Analysis using ReportLab.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    # Custom styles
    header_style = ParagraphStyle(
        'DocHeader',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0b1120')
    )

    tagline_style = ParagraphStyle(
        'DocTagline',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#64748b')
    )

    section_style = ParagraphStyle(
        'DocSection',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#0284c7'),
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1e293b')
    )

    disclaimer_style = ParagraphStyle(
        'DocDisclaimer',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#475569')
    )

    elements = []

    # Brand Title
    elements.append(Paragraph("CodeWithAnil — Text Authenticity Audit Report", header_style))
    elements.append(Paragraph("Detect AI Writing. Analyze Text. Explore Authenticity.", tagline_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=15))

    # Meta Table
    report_time = analysis.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
    text_content = analysis.input_text or analysis.text_snippet
    sha256_hash = hashlib.sha256(text_content.encode('utf-8')).hexdigest()

    meta_data = [
        [Paragraph("<b>Audit ID:</b>", body_style), Paragraph(f"CWA-{analysis.id:06d}", body_style)],
        [Paragraph("<b>Timestamp:</b>", body_style), Paragraph(report_time, body_style)],
        [Paragraph("<b>Input Word Count:</b>", body_style), Paragraph(f"{analysis.word_count} words ({analysis.character_count} chars)", body_style)],
        [Paragraph("<b>SHA-256 Checksum:</b>", body_style), Paragraph(f"<font size=7>{sha256_hash}</font>", body_style)],
    ]

    meta_table = Table(meta_data, colWidths=[120, 400])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 15))

    # Core Findings Section
    elements.append(Paragraph("Classification & Model Probability", section_style))

    ai_pct = f"{round(analysis.model_score * 100)}%"
    human_pct = f"{round(analysis.human_score * 100)}%"

    results_data = [
        [Paragraph("<b>Metric</b>", body_style), Paragraph("<b>Evaluated Score</b>", body_style), Paragraph("<b>Statistical Meaning</b>", body_style)],
        [Paragraph("Classification Result", body_style), Paragraph(f"<b>{analysis.prediction}</b>", body_style), Paragraph("Overall categorical threshold assignment", body_style)],
        [Paragraph("AI-Associated Probability", body_style), Paragraph(f"<b>{ai_pct}</b>", body_style), Paragraph("Calibrated probability of generative model patterns", body_style)],
        [Paragraph("Human-Associated Probability", body_style), Paragraph(f"<b>{human_pct}</b>", body_style), Paragraph("Calibrated probability of human linguistic variation", body_style)],
        [Paragraph("Inconclusive Boundary", body_style), Paragraph("Yes" if analysis.is_inconclusive else "No", body_style), Paragraph("Score lies within the 40%-60% uncertainty range", body_style)],
        [Paragraph("Evaluator Model", body_style), Paragraph(f"{analysis.model_name}", body_style), Paragraph(f"Version: {analysis.model_version}", body_style)],
        [Paragraph("Inference Latency", body_style), Paragraph(f"{analysis.processing_time_ms} ms", body_style), Paragraph("CPU Float32 PyTorch forward pass", body_style)],
    ]

    res_table = Table(results_data, colWidths=[140, 110, 270])
    res_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0f2fe')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(res_table)
    elements.append(Spacer(1, 15))

    # Analyzed Text Excerpt
    elements.append(Paragraph("Evaluated Text Excerpt", section_style))
    sample_excerpt = (analysis.text_snippet[:350] + "...") if len(analysis.text_snippet) > 350 else analysis.text_snippet
    elements.append(Paragraph(f"<i>\"{sample_excerpt}\"</i>", body_style))
    elements.append(Spacer(1, 15))

    # Mandatory Ethical and Scientific Disclaimer
    elements.append(Paragraph("Methodology & Responsible Use Disclaimer", section_style))
    disclaimer_text = (
        "This certificate presents probabilistic model outputs derived from sequence classification transformers. "
        "It does NOT constitute conclusive legal, academic, or disciplinary proof of authorship. "
        "Language models and human writers share overlapping syntactic distributions. In particular, technical prose, "
        "highly formatted documents, and writing by non-native English speakers may yield elevated AI probability scores. "
        "Any decisions regarding text authenticity should combine automated indicators with revision history, interview dialogue, "
        "and contextual human review."
    )
    elements.append(Paragraph(disclaimer_text, disclaimer_style))
    elements.append(Spacer(1, 15))

    # Verification Footer
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#94a3b8'), spaceAfter=8))
    elements.append(Paragraph("CodeWithAnil • Open Architecture AI Verification • https://codewithanil.com", tagline_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer
