from typing import List, Dict
from pydantic import BaseModel, Field

class PromptAnalysisRequest(BaseModel):
    prompt: str = Field(..., min_length=2, max_length=10000, description="The prompt instruction to audit")

class PromptMetrics(BaseModel):
    clarity: int
    specificity: int
    context: int
    constraints: int
    output_formatting: int
    completeness: int
    ambiguity_reduction: int

class PromptAnalysisResponse(BaseModel):
    original_prompt: str
    overall_score: int
    metrics: PromptMetrics
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    improved_prompt: str
    analysis_summary: str
    disclaimer: str
