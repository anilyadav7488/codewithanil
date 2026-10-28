"""
Production Readiness, Health/Readiness Lifecycle, and Error Handling Tests.
Tests real inference, 503 error handling, CORS headers, and readiness endpoints.
"""

import pytest
from unittest.mock import patch, PropertyMock
from ml.onnx_inference import ONNXModelInferenceService, ModelLifecycleStatus

def test_ready_endpoint_healthy(client):
    """Verifies that /ready and /api/ready return 200 when model is loaded."""
    response = client.get("/api/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["ready"] is True
    assert "model_name" in data

    # Verify root shortcut as well
    root_response = client.get("/ready")
    assert root_response.status_code == 200
    assert root_response.json()["ready"] is True

def test_ready_endpoint_initializing_returns_503(client):
    """Verifies that /ready returns HTTP 503 with Retry-After when initializing."""
    service = ONNXModelInferenceService.get_instance()
    original_status = service.status
    try:
        service.status = ModelLifecycleStatus.INITIALIZING
        response = client.get("/api/ready")
        assert response.status_code == 503
        assert response.headers.get("retry-after") == "5"
        data = response.json()
        assert data["status"] == "initializing"
        assert data["ready"] is False
        assert "loading into memory" in data["detail"]
    finally:
        service.status = original_status

def test_ready_endpoint_error_returns_503(client):
    """Verifies that /ready returns HTTP 503 when model failed to load."""
    service = ONNXModelInferenceService.get_instance()
    original_status = service.status
    original_error = service.load_error
    try:
        service.status = ModelLifecycleStatus.ERROR
        service.load_error = "Mocked disk read failure"
        response = client.get("/api/ready")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "error"
        assert "Mocked disk read failure" in data["detail"]
    finally:
        service.status = original_status
        service.load_error = original_error

def test_analyze_text_real_inference_success(client):
    """Verifies that analyze/text executes real inference and returns expected fields."""
    sample_text = (
        "Artificial intelligence architectures utilize transformer encoders and self-attention "
        "mechanisms to compute representations of input tokens across high-dimensional latent space. "
        "These models are evaluated against standardized benchmarks to measure statistical classification fidelity."
    )
    response = client.post("/api/analyze/text", json={"text": sample_text, "include_sentences": True})
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] in ["Human", "AI-Generated", "Inconclusive"]
    assert 0.0 <= data["ai_score"] <= 1.0
    assert 0.0 <= data["human_score"] <= 1.0
    assert data["word_count"] > 15
    assert len(data["sentence_analyses"]) > 0

def test_analyze_text_without_api_prefix_fallback(client):
    """Verifies that requests to /analyze/text directly succeed without 404."""
    sample_text = (
        "This is an authentic human-written passage specifically written to test "
        "the resilience of direct URL routing when reverse proxies strip the api path prefix."
    )
    response = client.post("/analyze/text", json={"text": sample_text, "include_sentences": False})
    assert response.status_code == 200
    assert "prediction" in response.json()

def test_analyze_text_when_initializing_returns_503(client):
    """Verifies that inference returns 503 when the model is currently loading."""
    service = ONNXModelInferenceService.get_instance()
    original_status = service.status
    try:
        service.status = ModelLifecycleStatus.INITIALIZING
        response = client.post("/api/analyze/text", json={
            "text": "This is a sufficiently long test text that would otherwise trigger statistical inference."
        })
        assert response.status_code == 503
        assert response.headers.get("retry-after") == "5"
        data = response.json()
        assert "initializing" in data["detail"]
    finally:
        service.status = original_status

def test_cors_vercel_preview_origin_allowed(client):
    """Verifies that Vercel preview domains are allowed by regex CORS."""
    headers = {
        "Origin": "https://codewithanil-git-experiment-onnx-int8-anils-projects.vercel.app",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type",
    }
    response = client.options("/api/analyze/text", headers=headers)
    assert response.status_code == 200
    allow_origin = response.headers.get("access-control-allow-origin")
    assert allow_origin == "https://codewithanil-git-experiment-onnx-int8-anils-projects.vercel.app"
