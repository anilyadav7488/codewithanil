"""
Automated Unit Tests for ONNX Runtime INT8 Inference Engine.
"""

import pytest
from ml.onnx_inference import ONNXModelInferenceService

@pytest.fixture(scope="module")
def onnx_service():
    service = ONNXModelInferenceService.get_instance()
    loaded = service.load_model()
    assert loaded is True, f"Failed to load ONNX model: {service.load_error}"
    return service

def test_onnx_model_loaded(onnx_service):
    assert onnx_service.is_loaded is True
    assert onnx_service.session is not None
    assert onnx_service.tokenizer is not None
    assert onnx_service.model_version == "roberta-base-hc3-int8-v1"

def test_onnx_predict_valid_text(onnx_service):
    text = (
        "Photosynthesis is the fundamental biological process through which green plants convert light energy into "
        "chemical energy to synthesize organic compounds. Sunlight, water, and atmospheric carbon dioxide are converted "
        "into glucose and molecular oxygen as a vital byproduct."
    )
    result = onnx_service.predict_text(text, include_sentences=True)
    assert "prediction" in result
    assert result["prediction"] in ["Human", "AI-Generated", "Inconclusive"]
    assert 0.0 <= result["ai_score"] <= 1.0
    assert 0.0 <= result["human_score"] <= 1.0
    assert abs((result["ai_score"] + result["human_score"]) - 1.0) < 0.001
    assert result["word_count"] > 15
    assert len(result["sentence_analyses"]) > 0

def test_onnx_empty_and_short_input_validation(onnx_service):
    with pytest.raises(ValueError, match="Input text is empty"):
        onnx_service.predict_text("   ")

    with pytest.raises(ValueError, match="Minimum 15 words required"):
        onnx_service.predict_text("This text is far too short to analyze.")
