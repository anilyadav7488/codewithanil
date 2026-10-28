import io
import os
from typing import Tuple
from fastapi import UploadFile, HTTPException, status
from pypdf import PdfReader
import docx

from app.core.config import settings

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}

def validate_uploaded_file(file: UploadFile, max_size_mb: int = settings.MAX_UPLOAD_SIZE_MB) -> str:
    """
    Validates file extension and filename safety.
    """
    filename = file.filename or ""
    _, ext = os.path.splitext(filename.lower())
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Only PDF, DOCX, and TXT files are accepted.",
        )
    return ext

def extract_text_from_file_bytes(content: bytes, ext: str) -> Tuple[str, bool]:
    """
    Extracts text from file contents without macro execution.
    Returns (extracted_text, requires_ocr_warning).
    """
    extracted_text = ""
    requires_ocr = False

    if ext == ".txt":
        try:
            extracted_text = content.decode("utf-8")
        except UnicodeDecodeError:
            extracted_text = content.decode("latin-1", errors="replace")

    elif ext == ".pdf":
        try:
            reader = PdfReader(io.BytesIO(content))
            pages_text = []
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    pages_text.append(t)
            extracted_text = "\n\n".join(pages_text).strip()

            # If PDF has pages but extracted text is tiny, it is likely an image scan
            if len(reader.pages) > 0 and len(extracted_text.split()) < 15:
                requires_ocr = True
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Corrupted or password-protected PDF document: {str(e)}",
            )

    elif ext == ".docx":
        try:
            doc = docx.Document(io.BytesIO(content))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            # Also extract from tables
            for table in doc.tables:
                for row in table.rows:
                    row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_text:
                        paragraphs.append(" | ".join(row_text))
            extracted_text = "\n\n".join(paragraphs).strip()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unable to parse DOCX document: {str(e)}",
            )

    if not extracted_text.strip():
        if requires_ocr:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Scanned document detected. This document contains images rather than selectable text. Optical Character Recognition (OCR) is required before analysis.",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded document contains no extractable text.",
        )

    return extracted_text.strip(), requires_ocr
