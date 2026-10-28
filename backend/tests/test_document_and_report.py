import os
import sys
import io

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from datetime import datetime, timezone
from app.models.analysis import Analysis
from app.services.report_generator import generate_analysis_pdf_report
from app.services.document_parser import extract_text_from_file_bytes

def test_extract_text_txt():
    sample_text = b"This is a sample document for testing text extraction from uploaded files in CodeWithAnil."
    extracted, ocr = extract_text_from_file_bytes(sample_text, ".txt")
    assert "CodeWithAnil" in extracted
    assert ocr is False
    print("[PASS] TXT Text Extraction")

def test_generate_pdf_report():
    mock_analysis = Analysis(
        id=42,
        user_id=1,
        input_text="Artificial intelligence algorithms detect patterns in large text corpora using attention layers.",
        text_snippet="Artificial intelligence algorithms detect patterns...",
        analysis_type="text",
        word_count=13,
        character_count=98,
        prediction="AI-Generated",
        model_score=0.892,
        human_score=0.108,
        is_inconclusive=False,
        model_name="Hello-SimpleAI/chatgpt-detector-roberta",
        model_version="roberta-base-hc3-v1",
        processing_time_ms=185,
        created_at=datetime.now(timezone.utc)
    )

    pdf_buffer = generate_analysis_pdf_report(mock_analysis)
    pdf_bytes = pdf_buffer.getvalue()
    
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")
    print(f"[PASS] PDF Report Generation: generated {len(pdf_bytes)} bytes with valid PDF header")

if __name__ == "__main__":
    test_extract_text_txt()
    test_generate_pdf_report()
