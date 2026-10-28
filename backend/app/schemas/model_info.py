from typing import List, Dict
from pydantic import BaseModel

class ModelThresholds(BaseModel):
    inconclusive_lower: float
    inconclusive_upper: float

class ModelInfoResponse(BaseModel):
    model_name: str
    architecture: str
    framework: str
    intended_use: str
    training_dataset: str
    license: str
    cpu_compatible: bool
    supported_languages: List[str]
    decision_thresholds: ModelThresholds
    known_limitations: List[str]
    disclaimer: str
