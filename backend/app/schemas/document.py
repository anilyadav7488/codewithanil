from typing import Optional
from pydantic import BaseModel
from app.schemas.analysis import TextAnalysisResponse

class DocumentAnalysisResponse(BaseModel):
    document_id: int
    filename: str
    file_type: str
    extracted_word_count: int
    text_preview: str
    requires_ocr_warning: bool
    analysis: TextAnalysisResponse
