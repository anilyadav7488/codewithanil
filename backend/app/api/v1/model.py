import datetime
from fastapi import APIRouter
from app.core.config import settings
from app.schemas.model_info import ModelInfoResponse, ModelThresholds
from ml.inference import AIModelInferenceService

router = APIRouter(tags=["Model Transparency"])

@router.get("/model/info", response_model=ModelInfoResponse)
def get_model_info():
    service = AIModelInferenceService.get_instance()
    return ModelInfoResponse(
        model_name=service.model_name,
        architecture="RoBERTa Sequence Classification (125 Million Parameters)",
        framework="PyTorch CPU & Hugging Face Transformers",
        intended_use="Estimation of linguistic and token distribution markers characteristic of LLMs vs human writing.",
        training_dataset="HC3 (Human ChatGPT Comparison Corpus, open benchmark dataset)",
        license="Apache 2.0 / MIT Open Access",
        cpu_compatible=True,
        supported_languages=["English"],
        decision_thresholds=ModelThresholds(
            inconclusive_lower=settings.INCONCLUSIVE_LOWER_THRESHOLD,
            inconclusive_upper=settings.INCONCLUSIVE_UPPER_THRESHOLD,
        ),
        known_limitations=[
            "Short texts (< 50 words) provide reduced signal density and carry higher variance.",
            "ESL / Non-native English writing often features uniform syntactic patterns that can increase false-positive likelihood.",
            "Adversarial rewrites or paraphrasing tools intentionally distort token perplexity markers.",
            "Does not prove authorship or identify specific human or AI individuals."
        ],
        disclaimer="Statistical indicators only. Never use as sole grounds for academic or employment disciplinary action.",
    )

@router.get("/health")
def get_health():
    service = AIModelInferenceService.get_instance()
    return {
        "status": "healthy",
        "service": "CodeWithAnil API",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "model_loaded": service.is_loaded,
        "model_name": service.model_name,
    }
