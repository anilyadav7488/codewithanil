from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class TextAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Raw text to evaluate")
    include_sentences: bool = Field(default=True, description="Whether to include sentence-level breakdown")
    save_history: bool = Field(default=False, description="Whether to store this record for authenticated user")

class SentenceScore(BaseModel):
    sentence_index: int
    text: str
    ai_score: float
    human_score: float
    prediction: str
    is_highlighted: bool
    confidence_rating: str

class TextAnalysisResponse(BaseModel):
    id: Optional[int] = None
    input_text: str
    word_count: int
    character_count: int
    prediction: str # 'Human', 'AI-Generated', 'Inconclusive'
    ai_score: float # 0.0 - 1.0 calibrated
    human_score: float # 0.0 - 1.0 calibrated
    raw_logits: Optional[Dict[str, float]] = None
    is_inconclusive: bool
    confidence_level: str # 'Low', 'Medium', 'High'
    model_name: str
    model_version: str
    processing_time_ms: int
    limitations: List[str]
    sentence_analyses: Optional[List[SentenceScore]] = None
    created_at: Optional[datetime] = None

class AnalysisHistoryItem(BaseModel):
    id: int
    user_id: Optional[int]
    analysis_type: str
    prediction: str
    model_score: float
    model_version: str
    word_count: int
    snippet: str
    created_at: datetime
    has_report: bool = True

class UserStatsResponse(BaseModel):
    total_analyses: int
    ai_count: int
    human_count: int
    inconclusive_count: int
    average_ai_score: float
    total_words_analyzed: int
