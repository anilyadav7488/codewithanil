"""
Inference Module for CodeWithAnil.
Provides unified access to the machine learning inference engine,
supporting both decoupled ONNX Runtime Dynamic INT8 (low memory)
and PyTorch FP32 (baseline reference).
"""

import os
import time
import logging
import threading
from typing import Optional, List, Dict, Any, Tuple

from app.core.config import settings
from ml.preprocessing import clean_text, split_into_sentences, compute_text_metrics
from ml.onnx_inference import ModelNotReadyError, ModelInitializingError

logger = logging.getLogger("codewithanil.ml.inference")

class PyTorchModelInferenceService:
    """
    Production-grade baseline inference service wrapping Hugging Face Transformers
    with PyTorch inference mode, softmax calibration, and segment parsing.
    """
    _instance: Optional["PyTorchModelInferenceService"] = None
    _singleton_lock = threading.Lock()

    def __init__(self, model_name: Optional[str] = None):
        import torch
        self.model_name = model_name or settings.HF_MODEL_NAME
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cpu")
        self.is_loaded = False
        self.is_loading = False
        self.load_error: Optional[str] = None
        self.load_time_sec: Optional[float] = None
        self._load_lock = threading.Lock()
        self.id2label: Dict[str, str] = {}
        self.model_version = "roberta-base-hc3-v1"
        self.framework = "PyTorch CPU & Hugging Face Transformers"

    @classmethod
    def get_instance(cls) -> "PyTorchModelInferenceService":
        if cls._instance is None:
            with cls._singleton_lock:
                if cls._instance is None:
                    cls._instance = PyTorchModelInferenceService()
        return cls._instance

    def is_ready(self) -> bool:
        return self.is_loaded and self.model is not None

    def get_readiness_info(self) -> Dict[str, Any]:
        return {
            "status": "ready" if self.is_ready() else ("initializing" if self.is_loading else "unloaded"),
            "ready": self.is_ready(),
            "model_name": self.model_name,
            "model_version": self.model_version,
            "framework": self.framework,
            "load_time_sec": self.load_time_sec,
            "error": self.load_error,
        }

    def load_model(self) -> bool:
        """
        Loads the pretrained model and tokenizer into memory with thread safety.
        """
        if self.is_loaded:
            return True

        with self._load_lock:
            if self.is_loaded:
                return True

            self.is_loading = True
            self.load_error = None
            t0 = time.perf_counter()
            logger.info(f"Loading transformer model '{self.model_name}' on CPU...")
            try:
                from transformers import AutoTokenizer, AutoModelForSequenceClassification
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
                self.model.eval()
                self.model.to(self.device)

                # Read configuration label mapping
                if hasattr(self.model.config, "id2label") and self.model.config.id2label:
                    self.id2label = {str(k): str(v) for k, v in self.model.config.id2label.items()}
                else:
                    self.id2label = {"0": "Human", "1": "ChatGPT"}

                self.is_loaded = True
                self.is_loading = False
                self.load_time_sec = round(time.perf_counter() - t0, 3)
                logger.info(f"Successfully loaded '{self.model_name}' with labels {self.id2label}")
                return True
            except Exception as e:
                self.is_loaded = False
                self.is_loading = False
                self.load_error = f"Failed to load Hugging Face model '{self.model_name}': {str(e)}"
                logger.error(self.load_error, exc_info=True)
                return False

    def predict_text(
        self,
        raw_text: str,
        include_sentences: bool = True
    ) -> Dict[str, Any]:
        """
        Performs real neural inference on user text using PyTorch.
        """
        import torch
        import torch.nn.functional as F

        if not self.is_loaded:
            if self.is_loading:
                raise ModelInitializingError(
                    "Inference service is currently initializing. Please try again in a few seconds."
                )
            loaded = self.load_model()
            if not loaded:
                raise ModelNotReadyError(self.load_error or "Model is not loaded.")

        start_time = time.perf_counter()
        cleaned = clean_text(raw_text)

        word_count, char_count = compute_text_metrics(cleaned)
        if word_count == 0:
            raise ValueError("Input text is empty.")

        if word_count < 15:
            raise ValueError(
                f"Input text has {word_count} words. Minimum 15 words required for statistical inference."
            )

        inputs = self.tokenizer(
            cleaned,
            return_tensors="pt",
            max_length=settings.MAX_SEQUENCE_LENGTH,
            truncation=True,
            padding=False,
        ).to(self.device)

        with torch.inference_mode():
            outputs = self.model(**inputs)
            logits = outputs.logits[0]
            probabilities = F.softmax(logits, dim=-1).tolist()

        ai_idx = 1
        human_idx = 0
        if "0" in self.id2label:
            lbl0 = self.id2label["0"].lower()
            if "fake" in lbl0 or "ai" in lbl0 or "chatgpt" in lbl0:
                ai_idx = 0
                human_idx = 1

        raw_human_prob = float(probabilities[human_idx])
        raw_ai_prob = float(probabilities[ai_idx])

        lower_bound = settings.INCONCLUSIVE_LOWER_THRESHOLD
        upper_bound = settings.INCONCLUSIVE_UPPER_THRESHOLD

        is_inconclusive = lower_bound <= raw_ai_prob <= upper_bound

        if is_inconclusive:
            prediction = "Inconclusive"
            confidence = "Low"
        elif raw_ai_prob > upper_bound:
            prediction = "AI-Generated"
            confidence = "High" if raw_ai_prob >= 0.80 else "Medium"
        else:
            prediction = "Human"
            confidence = "High" if raw_human_prob >= 0.80 else "Medium"

        sentence_analyses: List[Dict[str, Any]] = []
        if include_sentences:
            sentences = split_into_sentences(cleaned)
            for idx, sentence in enumerate(sentences):
                s_words = len(sentence.split())
                if s_words < 6:
                    continue

                s_inputs = self.tokenizer(
                    sentence,
                    return_tensors="pt",
                    max_length=128,
                    truncation=True,
                ).to(self.device)

                with torch.inference_mode():
                    s_out = self.model(**s_inputs)
                    s_probs = F.softmax(s_out.logits[0], dim=-1).tolist()

                s_ai_score = float(s_probs[ai_idx])
                s_human_score = float(s_probs[human_idx])

                s_pred = (
                    "Inconclusive"
                    if (0.42 <= s_ai_score <= 0.58)
                    else ("AI-Generated" if s_ai_score > 0.58 else "Human")
                )

                sentence_analyses.append({
                    "sentence_index": idx,
                    "text": sentence,
                    "ai_score": round(s_ai_score, 4),
                    "human_score": round(s_human_score, 4),
                    "prediction": s_pred,
                    "is_highlighted": s_ai_score >= 0.58,
                    "confidence_rating": "High" if abs(s_ai_score - 0.5) > 0.3 else "Moderate",
                })

        processing_time_ms = int((time.perf_counter() - start_time) * 1000)

        limitations = [
            "Classification is probabilistic: high scores indicate stylistic overlap with synthetic corpora, not absolute proof.",
            "Short texts (< 50 words) provide reduced signal density and carry higher variance.",
            "ESL / Non-native English writing often features uniform syntactic patterns that can increase false-positive likelihood.",
            "Adversarial rewrites or paraphrasing tools intentionally distort token perplexity markers."
        ]

        logger.info(
            f"[PyTorch Inference Complete] {word_count} words | Result: {prediction} "
            f"(AI: {raw_ai_prob:.4f}, Human: {raw_human_prob:.4f}) | Latency: {processing_time_ms}ms"
        )

        return {
            "input_text": cleaned,
            "word_count": word_count,
            "character_count": char_count,
            "prediction": prediction,
            "ai_score": round(raw_ai_prob, 4),
            "human_score": round(raw_human_prob, 4),
            "raw_logits": {
                "human_logit": round(float(logits[human_idx].item()), 4),
                "ai_logit": round(float(logits[ai_idx].item()), 4),
            },
            "is_inconclusive": is_inconclusive,
            "confidence_level": confidence,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "processing_time_ms": processing_time_ms,
            "limitations": limitations,
            "sentence_analyses": sentence_analyses if include_sentences else None,
        }

def get_inference_service():
    """
    Factory function returning the active inference service according to settings.
    Defaults to ONNX INT8 for Render Free memory safety (< 400 MB RAM).
    """
    backend = getattr(settings, "INFERENCE_BACKEND", "onnx_int8").lower()
    if backend == "pytorch_fp32":
        return PyTorchModelInferenceService.get_instance()
    else:
        from ml.onnx_inference import ONNXModelInferenceService
        return ONNXModelInferenceService.get_instance()

class AIModelInferenceService:
    """
    Unified factory / router class preserving 100% backward compatibility
    with existing callers while seamlessly switching inference engines.
    """
    @classmethod
    def get_instance(cls):
        return get_inference_service()
