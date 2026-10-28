import datetime
from fastapi import APIRouter, Response, status
from app.core.config import settings
from app.schemas.model_info import ModelInfoResponse, ModelThresholds
from ml.inference import AIModelInferenceService

router = APIRouter(tags=["Model Transparency & Health"])

@router.get("/model/info", response_model=ModelInfoResponse)
def get_model_info():
    service = AIModelInferenceService.get_instance()
    return ModelInfoResponse(
        model_name=service.model_name,
        architecture="RoBERTa Sequence Classification (125 Million Parameters)",
        framework=getattr(service, "framework", "ONNX Runtime Dynamic INT8 CPU (Zero-PyTorch)"),
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
    """Liveness probe: verifies that the web service process is active and responsive."""
    service = AIModelInferenceService.get_instance()
    is_ready = getattr(service, "is_ready", lambda: service.is_loaded)()
    is_loading = getattr(service, "is_loading", False)
    
    status_str = "healthy" if is_ready else ("initializing" if is_loading else "degraded")
    
    return {
        "status": status_str,
        "service": "CodeWithAnil API",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "model_loaded": is_ready,
        "model_name": service.model_name,
        "framework": getattr(service, "framework", "ONNX Runtime Dynamic INT8"),
    }

@router.get("/ready")
def get_ready(response: Response):
    """
    Readiness probe: indicates whether the model is actually loaded in memory
    and ready to process user inference requests. Returns 503 if still initializing.
    """
    service = AIModelInferenceService.get_instance()
    is_ready = getattr(service, "is_ready", lambda: service.is_loaded)()
    is_loading = getattr(service, "is_loading", False)
    load_error = getattr(service, "load_error", None)

    if is_ready:
        return {
            "status": "ready",
            "ready": True,
            "service": "CodeWithAnil API",
            "model_name": service.model_name,
            "model_version": getattr(service, "model_version", "roberta-base-hc3-int8-v1"),
            "load_time_sec": getattr(service, "load_time_sec", None),
        }

    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    response.headers["Retry-After"] = "5"

    if is_loading:
        return {
            "status": "initializing",
            "ready": False,
            "detail": "AI model is currently loading into memory. Please retry shortly.",
            "retry_after_seconds": 5,
        }

    return {
        "status": "error",
        "ready": False,
        "detail": f"AI model failed to load: {load_error or 'Model not initialized'}",
        "error": load_error,
    }
