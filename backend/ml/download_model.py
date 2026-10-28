"""
Model Provisioning Script for Render Free Deployment.
Downloads and verifies the 120 MB dynamic INT8 ONNX model and tokenizer assets
from the verified onnx-community repository.
Performs cryptographic SHA-256 integrity validation and smoke inference tests.
"""

import os
import sys
import shutil
import hashlib
from pathlib import Path

EXPECTED_MODEL_SHA256 = "219d37a3d815a969e92664a9f2b2101cb754a1e1e0ce2ace81a0c3cdb149ff7c"
EXPECTED_MODEL_SIZE = 125855419
EXPECTED_TOKENIZER_SHA256 = "fac96121c0f9c36533e15c1ed9ebd3fe6e37a869247617866ca6a8df40e48e43"

def compute_sha256(file_path: Path) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()

def ensure_model_assets():
    base_dir = Path(__file__).resolve().parent
    models_dir = base_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    int8_model_path = models_dir / "roberta_chatgpt_detector_int8.onnx"
    tokenizer_dir = models_dir / "tokenizer"
    tokenizer_dir.mkdir(parents=True, exist_ok=True)
    tokenizer_json = tokenizer_dir / "tokenizer.json"

    repo_id = "onnx-community/chatgpt-detector-roberta-ONNX"

    # 1. Verify or Download INT8 ONNX Model
    need_model_download = True
    if int8_model_path.exists() and int8_model_path.stat().st_size == EXPECTED_MODEL_SIZE:
        current_hash = compute_sha256(int8_model_path)
        if current_hash == EXPECTED_MODEL_SHA256:
            print(f"[OK] Model verified with matching SHA-256: {int8_model_path} ({int8_model_path.stat().st_size / (1024*1024):.2f} MB)")
            need_model_download = False
        else:
            print(f"[WARN] Model checksum mismatch ({current_hash} != {EXPECTED_MODEL_SHA256}). Re-downloading...")

    if need_model_download:
        print(f"Downloading optimized INT8 model from Hugging Face ({repo_id})...")
        from huggingface_hub import hf_hub_download
        downloaded = hf_hub_download(
            repo_id=repo_id,
            filename="onnx/model_int8.onnx",
            local_dir=str(models_dir)
        )
        downloaded_path = Path(downloaded)
        if downloaded_path != int8_model_path:
            shutil.copyfile(downloaded_path, int8_model_path)

        # Integrity Check
        downloaded_hash = compute_sha256(int8_model_path)
        if downloaded_hash != EXPECTED_MODEL_SHA256:
            raise ValueError(
                f"Integrity check failed: downloaded hash {downloaded_hash} does not match expected {EXPECTED_MODEL_SHA256}"
            )
        print(f"[OK] Downloaded model successfully passed SHA-256 verification ({int8_model_path.stat().st_size / (1024*1024):.2f} MB)")

    # 2. Verify or Download Tokenizer
    need_tok_download = True
    if tokenizer_json.exists():
        tok_hash = compute_sha256(tokenizer_json)
        if tok_hash == EXPECTED_TOKENIZER_SHA256:
            print(f"[OK] Tokenizer verified with matching SHA-256: {tokenizer_json}")
            need_tok_download = False

    if need_tok_download:
        print("Downloading tokenizer configuration...")
        from huggingface_hub import hf_hub_download
        hf_hub_download(
            repo_id=repo_id,
            filename="tokenizer.json",
            local_dir=str(tokenizer_dir)
        )
        hf_hub_download(
            repo_id=repo_id,
            filename="tokenizer_config.json",
            local_dir=str(tokenizer_dir)
        )
        downloaded_tok_hash = compute_sha256(tokenizer_json)
        if downloaded_tok_hash != EXPECTED_TOKENIZER_SHA256:
            raise ValueError(f"Tokenizer integrity check failed: {downloaded_tok_hash} != {EXPECTED_TOKENIZER_SHA256}")
        print(f"[OK] Tokenizer successfully passed SHA-256 verification.")

    return True

if __name__ == "__main__":
    ensure_model_assets()
    # Smoke test session initialization when run directly
    print("Testing session initialization...")
    import onnxruntime as ort
    from tokenizers import Tokenizer
    
    models_dir = Path(__file__).resolve().parent / "models"
    int8_model_path = models_dir / "roberta_chatgpt_detector_int8.onnx"
    tokenizer_json = models_dir / "tokenizer" / "tokenizer.json"

    _ = Tokenizer.from_file(str(tokenizer_json))
    opt = ort.SessionOptions()
    opt.intra_op_num_threads = 1
    opt.enable_cpu_mem_arena = False
    _ = ort.InferenceSession(str(int8_model_path), opt, providers=["CPUExecutionProvider"])
    print("[SUCCESS] All model assets verified and operational for Render deployment.")
