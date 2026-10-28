"""
Export and Dynamic INT8 Quantization Script for CodeWithAnil AI Detector.
Exports 'Hello-SimpleAI/chatgpt-detector-roberta' to ONNX format and applies
ONNX Runtime dynamic INT8 quantization.
"""

import os
import sys

# Force UTF-8 encoding on standard streams to prevent Windows cp1252 emoji encoding errors
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
os.environ["PYTHONIOENCODING"] = "utf-8"

import time
from pathlib import Path
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import onnx
import onnxruntime as ort
from onnxruntime.quantization import quantize_dynamic, QuantType

def export_and_quantize():
    model_name = "Hello-SimpleAI/chatgpt-detector-roberta"
    output_dir = Path(__file__).resolve().parent / "models"
    output_dir.mkdir(parents=True, exist_ok=True)

    fp32_onnx_path = output_dir / "roberta_chatgpt_detector.onnx"
    int8_onnx_path = output_dir / "roberta_chatgpt_detector_int8.onnx"
    tokenizer_dir = output_dir / "tokenizer"

    print("=" * 70)
    print("CodeWithAnil — ONNX Export & INT8 Dynamic Quantization Pipeline")
    print("=" * 70)
    print(f"Source Model: {model_name}")
    print(f"Destination:  {output_dir}\n")

    # 1. Load Pretrained PyTorch Model & Tokenizer
    print("Step 1: Loading PyTorch model and tokenizer...")
    t0 = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    model.eval()
    print(f"Model loaded in {time.perf_counter() - t0:.2f}s")
    print(f"Model config labels: {model.config.id2label}")

    # Save tokenizer locally so production inference does not require internet connection
    print(f"Saving tokenizer assets to {tokenizer_dir}...")
    tokenizer.save_pretrained(tokenizer_dir)

    # 2. Prepare Dummy Input for Tracing
    dummy_text = "This is a representative benchmark sample for tracing sequence classification."
    encoded = tokenizer(
        dummy_text,
        padding="max_length",
        max_length=128,
        truncation=True,
        return_tensors="pt"
    )
    input_ids = encoded["input_ids"]
    attention_mask = encoded["attention_mask"]

    # Measure PyTorch reference output
    with torch.no_grad():
        pt_outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        pt_logits = pt_outputs.logits.detach().cpu().numpy()
        pt_probs = torch.softmax(pt_outputs.logits, dim=-1).detach().cpu().numpy()

    print(f"PyTorch baseline logits: {pt_logits[0]} | Probabilities: {pt_probs[0]}")

    # 3. Export to ONNX (FP32)
    print("\nStep 2: Exporting to ONNX format (opset 17 with dynamic axes)...")
    t0 = time.perf_counter()

    # PyTorch export (dynamo=False uses proven TorchScript exporter for HuggingFace Transformers)
    torch.onnx.export(
        model,
        (input_ids, attention_mask),
        str(fp32_onnx_path),
        input_names=["input_ids", "attention_mask"],
        output_names=["logits"],
        dynamic_axes={
            "input_ids": {0: "batch_size", 1: "sequence_length"},
            "attention_mask": {0: "batch_size", 1: "sequence_length"},
            "logits": {0: "batch_size"}
        },
        opset_version=17,
        do_constant_folding=True,
        dynamo=False,
    )
    export_duration = time.perf_counter() - t0
    fp32_size_mb = fp32_onnx_path.stat().st_size / (1024 * 1024)
    print(f"Exported to {fp32_onnx_path} in {export_duration:.2f}s ({fp32_size_mb:.2f} MB)")

    # Validate ONNX model
    print("Verifying FP32 ONNX model structure...")
    onnx_model = onnx.load(str(fp32_onnx_path))
    onnx.checker.check_model(onnx_model)
    print("ONNX model structure verified successfully.")

    # 4. Verify FP32 ONNX runtime session output parity
    session_fp32 = ort.InferenceSession(str(fp32_onnx_path), providers=["CPUExecutionProvider"])
    ort_inputs = {
        "input_ids": input_ids.numpy(),
        "attention_mask": attention_mask.numpy()
    }
    ort_logits = session_fp32.run(None, ort_inputs)[0]
    max_fp32_diff = np.max(np.abs(pt_logits - ort_logits))
    print(f"Max absolute logit difference (PyTorch vs ONNX FP32): {max_fp32_diff:.6f}")

    # 5. Apply Dynamic INT8 Quantization
    print("\nStep 3: Quantizing to Dynamic INT8 with ONNX Runtime...")
    t0 = time.perf_counter()
    quantize_dynamic(
        model_input=str(fp32_onnx_path),
        model_output=str(int8_onnx_path),
        weight_type=QuantType.QInt8,
        op_types_to_quantize=["MatMul", "Gemm"]
    )
    quant_duration = time.perf_counter() - t0
    int8_size_mb = int8_onnx_path.stat().st_size / (1024 * 1024)
    compression_pct = (1.0 - (int8_size_mb / fp32_size_mb)) * 100

    print(f"Quantized to {int8_onnx_path} in {quant_duration:.2f}s ({int8_size_mb:.2f} MB)")
    print(f"Weight compression: {compression_pct:.2f}% reduction")

    # 6. Verify INT8 ONNX output parity & numerical fidelity
    session_int8 = ort.InferenceSession(str(int8_onnx_path), providers=["CPUExecutionProvider"])
    int8_logits = session_int8.run(None, ort_inputs)[0]
    
    # Softmax probabilities
    def softmax(x):
        e_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
        return e_x / e_x.sum(axis=-1, keepdims=True)

    int8_probs = softmax(int8_logits)
    max_int8_diff = np.max(np.abs(pt_logits - int8_logits))
    prob_diff = np.max(np.abs(pt_probs - int8_probs))

    print("\nNumerical Fidelity Check:")
    print(f"  PyTorch FP32 Probs: {pt_probs[0]}")
    print(f"  ONNX INT8 Probs:    {int8_probs[0]}")
    print(f"  Max Logit Diff:     {max_int8_diff:.4f}")
    print(f"  Max Prob Diff:      {prob_diff:.4f}")

    print("\nSummary of Artifact Sizes:")
    print(f"  FP32 ONNX Model: {fp32_size_mb:.2f} MB")
    print(f"  INT8 ONNX Model: {int8_size_mb:.2f} MB")
    print("Export and INT8 quantization completed successfully!")

if __name__ == "__main__":
    export_and_quantize()
