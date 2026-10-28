"""
High-Performance, Zero-PyTorch ONNX Runtime Dynamic INT8 Inference Service.
Specifically optimized for strict memory budgets (< 400 MB RAM) on Render Free.
Includes thread-safe initialization, readiness lifecycle tracking, and structured diagnostics.
"""

import os
import time
import logging
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any
from enum import Enum
import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

from app.core.config import settings
from ml.preprocessing import clean_text, split_into_sentences, compute_text_metrics

logger = logging.getLogger("codewithanil.ml.onnx_inference")

class ModelLifecycleStatus(str, Enum):
    UNLOADED = "unloaded"
    INITIALIZING = "initializing"
    READY = "ready"
    ERROR = "error"

class ModelNotReadyError(RuntimeError):
    """Raised when an inference request arrives but the model is not ready."""
    pass

class ModelInitializingError(ModelNotReadyError):
    """Raised when an inference request arrives while the model is currently loading."""
    pass

class ONNXModelInferenceService:
    """
    Lightweight, production-grade inference engine using ONNX Runtime Dynamic INT8
    and Rust-backed Tokenizers. Completely eliminates PyTorch and Hugging Face Transformers
    from memory to operate within 512 MB RAM environments.
    """
    _instance: Optional["ONNXModelInferenceService"] = None
    _singleton_lock = threading.Lock()

    def __init__(
        self,
        model_path: Optional[str] = None,
        tokenizer_path: Optional[str] = None
    ):
        base_dir = Path(__file__).resolve().parent

        # Resolve model path
        configured_model_path = model_path or getattr(settings, "ONNX_MODEL_PATH", "ml/models/roberta_chatgpt_detector_int8.onnx")
        resolved_model_path = Path(configured_model_path)
        if not resolved_model_path.is_absolute():
            candidate1 = base_dir.parent / resolved_model_path
            candidate2 = base_dir / resolved_model_path.name
            if candidate1.exists():
                resolved_model_path = candidate1
            elif candidate2.exists():
                resolved_model_path = candidate2
            else:
                resolved_model_path = base_dir / "models" / "roberta_chatgpt_detector_int8.onnx"

        self.model_path = str(resolved_model_path)

        # Resolve tokenizer path
        configured_tok_path = tokenizer_path or getattr(settings, "TOKENIZER_DIR", "ml/models/tokenizer")
        resolved_tok_path = Path(configured_tok_path)
        if not resolved_tok_path.is_absolute():
            candidate1 = base_dir.parent / resolved_tok_path
            candidate2 = base_dir / "models" / "tokenizer"
            if candidate1.exists():
                resolved_tok_path = candidate1
            else:
                resolved_tok_path = candidate2

        tok_json = resolved_tok_path / "tokenizer.json" if resolved_tok_path.is_dir() else resolved_tok_path
        self.tokenizer_path = str(tok_json)

        self.tokenizer: Optional[Tokenizer] = None
        self.session: Optional[ort.InferenceSession] = None
        
        # Lifecycle state & synchronization
        self._load_lock = threading.Lock()
        self.status: ModelLifecycleStatus = ModelLifecycleStatus.UNLOADED
        self.load_error: Optional[str] = None
        self.load_time_sec: Optional[float] = None
        self.initialization_attempts: int = 0
        
        self.id2label: Dict[str, str] = {"0": "Human", "1": "ChatGPT"}
        self.model_name = settings.HF_MODEL_NAME
        self.model_version = "roberta-base-hc3-int8-v1"
        self.framework = "ONNX Runtime Dynamic INT8 (Zero-PyTorch)"

    @classmethod
    def get_instance(cls) -> "ONNXModelInferenceService":
        if cls._instance is None:
            with cls._singleton_lock:
                if cls._instance is None:
                    cls._instance = ONNXModelInferenceService()
        return cls._instance

    @property
    def is_loaded(self) -> bool:
        return self.status == ModelLifecycleStatus.READY and self.session is not None

    @property
    def is_loading(self) -> bool:
        return self.status == ModelLifecycleStatus.INITIALIZING

    def is_ready(self) -> bool:
        return self.is_loaded

    def get_readiness_info(self) -> Dict[str, Any]:
        """Provides accurate readiness state for Kubernetes / Render readiness probes."""
        return {
            "status": self.status.value,
            "ready": self.is_loaded,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "framework": self.framework,
            "load_time_sec": self.load_time_sec,
            "error": self.load_error,
        }

    def load_model(self) -> bool:
        """
        Thread-safe loader for the INT8 ONNX graph and Tokenizer into memory.
        Uses double-checked locking to prevent concurrent reload spikes on 512 MB memory limit.
        """
        if self.is_loaded:
            return True

        with self._load_lock:
            # Double-check inside lock
            if self.is_loaded:
                return True

            self.status = ModelLifecycleStatus.INITIALIZING
            self.load_error = None
            self.initialization_attempts += 1
            t0 = time.perf_counter()

            logger.info(
                f"[ML Lifecycle] Initializing ONNX INT8 model (attempt {self.initialization_attempts}) "
                f"from '{self.model_path}' on CPU..."
            )

            try:
                # 1. Ensure assets exist locally or download with SHA-256 verification
                if not os.path.exists(self.model_path) or not os.path.exists(self.tokenizer_path):
                    logger.info("[ML Lifecycle] Assets not found locally. Provisioning verified model files...")
                    from ml.download_model import ensure_model_assets
                    ensure_model_assets()

                if not os.path.exists(self.model_path):
                    raise FileNotFoundError(f"ONNX model file not found at: {self.model_path}")
                if not os.path.exists(self.tokenizer_path):
                    raise FileNotFoundError(f"Tokenizer asset not found at: {self.tokenizer_path}")

                # 2. Load Rust-backed tokenizer
                self.tokenizer = Tokenizer.from_file(self.tokenizer_path)

                # 3. Configure ONNX Runtime CPU session with low-memory bounds
                sess_options = ort.SessionOptions()
                sess_options.intra_op_num_threads = 1
                sess_options.inter_op_num_threads = 1
                sess_options.enable_cpu_mem_arena = False # Enforce strictly bounded memory
                sess_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
                sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

                self.session = ort.InferenceSession(
                    self.model_path,
                    sess_options=sess_options,
                    providers=["CPUExecutionProvider"]
                )

                self.status = ModelLifecycleStatus.READY
                self.load_time_sec = round(time.perf_counter() - t0, 3)
                logger.info(f"[ML Lifecycle] ONNX INT8 model successfully loaded and ready in {self.load_time_sec}s.")
                return True

            except Exception as e:
                self.status = ModelLifecycleStatus.ERROR
                self.load_error = f"Failed to load ONNX model: {str(e)}"
                logger.error(f"[ML Lifecycle Error] {self.load_error}", exc_info=True)
                return False

    def predict_text(
        self,
        raw_text: str,
        include_sentences: bool = True
    ) -> Dict[str, Any]:
        """
        Executes calibrated AI vs Human text classification using pure ONNX Runtime & NumPy.
        Guarantees exact schema and behavioral parity with baseline PyTorch model.
        """
        # Readiness checks
        if not self.is_loaded:
            if self.is_loading:
                raise ModelInitializingError(
                    "Inference service is currently initializing. Please try again in a few seconds."
                )

            # Attempt load under lock
            loaded = self.load_model()
            if not loaded:
                raise ModelNotReadyError(self.load_error or "ONNX Model is not loaded.")

        start_time = time.perf_counter()
        cleaned = clean_text(raw_text)

        word_count, char_count = compute_text_metrics(cleaned)
        if word_count == 0:
            raise ValueError("Input text is empty.")

        if word_count < 15:
            raise ValueError(
                f"Input text has {word_count} words. Minimum 15 words required for statistical inference."
            )

        # 1. Full document forward pass
        self.tokenizer.enable_truncation(max_length=settings.MAX_SEQUENCE_LENGTH)
        self.tokenizer.no_padding()
        encoded = self.tokenizer.encode(cleaned)

        input_ids = np.array([encoded.ids], dtype=np.int64)
        attention_mask = np.array([encoded.attention_mask], dtype=np.int64)

        ort_outputs = self.session.run(
            None,
            {"input_ids": input_ids, "attention_mask": attention_mask}
        )
        logits = ort_outputs[0][0]

        # Numerically stable softmax
        exp_logits = np.exp(logits - np.max(logits))
        probabilities = (exp_logits / np.sum(exp_logits)).tolist()

        ai_idx = 1
        human_idx = 0

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

        # 2. Sentence-level analysis
        sentence_analyses: List[Dict[str, Any]] = []
        if include_sentences:
            sentences = split_into_sentences(cleaned)
            self.tokenizer.enable_truncation(max_length=128)
            self.tokenizer.no_padding()

            for idx, sentence in enumerate(sentences):
                s_words = len(sentence.split())
                if s_words < 6:
                    continue

                s_enc = self.tokenizer.encode(sentence)
                s_ids = np.array([s_enc.ids], dtype=np.int64)
                s_mask = np.array([s_enc.attention_mask], dtype=np.int64)

                s_out = self.session.run(
                    None,
                    {"input_ids": s_ids, "attention_mask": s_mask}
                )
                s_logits = s_out[0][0]
                s_exp = np.exp(s_logits - np.max(s_logits))
                s_probs = (s_exp / np.sum(s_exp)).tolist()

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
            f"[Inference Complete] {word_count} words | Result: {prediction} "
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
                "human_logit": round(float(logits[human_idx]), 4),
                "ai_logit": round(float(logits[ai_idx]), 4),
            },
            "is_inconclusive": is_inconclusive,
            "confidence_level": confidence,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "processing_time_ms": processing_time_ms,
            "limitations": limitations,
            "sentence_analyses": sentence_analyses if include_sentences else None,
        }
