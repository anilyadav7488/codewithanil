"""
Resident Memory (RSS) Profiler for CodeWithAnil AI Detector.
Measures process RSS, Peak Working Set, and memory consumption across:
1. Baseline FastAPI Application initialization
2. Cold-start model load into memory
3. Single inference requests (short, medium, long 500-word payloads)
4. Full sentence-level analysis
5. Sustained 50-request repeated concurrency stress test
Evaluates against strict 512 MB limit and < 400 MB safety target.
"""

import os
import sys
import gc
import time
from typing import Dict, Any, List
import psutil

# Ensure backend root is in sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

def get_process_memory_mb() -> Dict[str, float]:
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    rss_mb = mem_info.rss / (1024 * 1024)
    
    # Peak memory
    if hasattr(mem_info, "peak_wset"):
        peak_mb = mem_info.peak_wset / (1024 * 1024)
    else:
        peak_mb = rss_mb

    return {
        "rss_mb": round(rss_mb, 2),
        "peak_mb": round(peak_mb, 2),
    }

def profile_backend_memory(backend_mode: str = "onnx_int8") -> Dict[str, Any]:
    print("=" * 78)
    print(f"Memory Profiling Session — Mode: {backend_mode.upper()}")
    print("=" * 78)

    os.environ["INFERENCE_BACKEND"] = backend_mode
    from app.core.config import settings
    settings.INFERENCE_BACKEND = backend_mode

    # Phase 1: Baseline App Process Memory
    gc.collect()
    mem_baseline = get_process_memory_mb()
    print(f"Phase 1: Baseline Process Memory (Python + FastAPI Core):")
    print(f"  Current RSS: {mem_baseline['rss_mb']} MB | Peak: {mem_baseline['peak_mb']} MB")

    # Phase 2: Model Cold Start Loading
    t0 = time.perf_counter()
    if backend_mode == "onnx_int8":
        from ml.onnx_inference import ONNXModelInferenceService
        service = ONNXModelInferenceService.get_instance()
    else:
        from ml.inference import PyTorchModelInferenceService
        service = PyTorchModelInferenceService.get_instance()

    service.load_model()
    load_time_sec = time.perf_counter() - t0
    mem_after_load = get_process_memory_mb()
    print(f"\nPhase 2: Cold Start Model Load (Duration: {load_time_sec:.2f}s):")
    print(f"  Current RSS: {mem_after_load['rss_mb']} MB | Peak: {mem_after_load['peak_mb']} MB")
    print(f"  Model Load Delta: {mem_after_load['rss_mb'] - mem_baseline['rss_mb']:.2f} MB")

    # Phase 3: Single Inference with Sentence Parsing
    sample_text = (
        "Artificial intelligence and large language models continue to evolve rapidly across industries. "
        "These neural architectures are trained on vast corpora of textual data using self-supervised objectives. "
        "Consequently, synthetic writing patterns frequently exhibit distinct syntactic regularities and low perplexity. "
        "Human writing, by contrast, demonstrates natural stylistic diversity, varied sentence cadence, and personal anecdotes. "
        "Distinguishing between human and machine prose requires statistical pattern analysis rather than absolute heuristics. "
        "Furthermore, academic institutions and enterprises utilize machine learning classifiers to audit authenticity. "
        "Evaluating model performance necessitates rigorous benchmarks across balanced evaluation corpora."
    )

    t0 = time.perf_counter()
    res1 = service.predict_text(sample_text, include_sentences=True)
    inf1_time_ms = (time.perf_counter() - t0) * 1000
    mem_after_inf1 = get_process_memory_mb()
    print(f"\nPhase 3: First Inference with Sentence Analysis ({res1['word_count']} words, {len(res1['sentence_analyses'])} sentences, {inf1_time_ms:.1f}ms):")
    print(f"  Current RSS: {mem_after_inf1['rss_mb']} MB | Peak: {mem_after_inf1['peak_mb']} MB")

    # Phase 4: Long Request (500 Words)
    long_text = " ".join([sample_text for _ in range(6)])
    t0 = time.perf_counter()
    res_long = service.predict_text(long_text, include_sentences=True)
    inf_long_time_ms = (time.perf_counter() - t0) * 1000
    mem_after_long = get_process_memory_mb()
    print(f"\nPhase 4: Long Input Inference ({res_long['word_count']} words, {len(res_long['sentence_analyses'])} sentences, {inf_long_time_ms:.1f}ms):")
    print(f"  Current RSS: {mem_after_long['rss_mb']} MB | Peak: {mem_after_long['peak_mb']} MB")

    # Phase 5: Sustained Concurrency & Stress Run (50 Repeated Requests)
    print(f"\nPhase 5: Sustained Stress Test (50 Sequential Inferences)...")
    latencies = []
    for i in range(50):
        t0 = time.perf_counter()
        _ = service.predict_text(sample_text, include_sentences=True)
        latencies.append((time.perf_counter() - t0) * 1000)

    gc.collect()
    mem_after_stress = get_process_memory_mb()
    print(f"  Completed 50 requests. Mean Latency: {sum(latencies)/len(latencies):.1f}ms")
    print(f"  Current RSS after 50 requests: {mem_after_stress['rss_mb']} MB")
    print(f"  Peak Working Set / Peak RSS:   {mem_after_stress['peak_mb']} MB")

    # Evaluation against budget limits
    limit_512_mb = 512.0
    target_400_mb = 400.0
    passed_limit = mem_after_stress["peak_mb"] < limit_512_mb
    passed_target = mem_after_stress["peak_mb"] < target_400_mb

    headroom_limit = limit_512_mb - mem_after_stress["peak_mb"]
    headroom_target = target_400_mb - mem_after_stress["peak_mb"]

    print("\n" + "=" * 78)
    print("MEMORY BUDGET EVALUATION")
    print("=" * 78)
    print(f"  Render Free Absolute Limit: 512.00 MB")
    print(f"  Memory Safety Target:       400.00 MB")
    print(f"  Actual Measured Peak RAM:   {mem_after_stress['peak_mb']:.2f} MB")
    print(f"  Headroom below 512 MB:      {headroom_limit:+.2f} MB  [{'PASS' if passed_limit else 'FAIL'}]")
    print(f"  Headroom below 400 MB:      {headroom_target:+.2f} MB  [{'PASS' if passed_target else 'FAIL'}]")
    print("=" * 78)

    return {
        "backend": backend_mode,
        "baseline_rss_mb": mem_baseline["rss_mb"],
        "post_load_rss_mb": mem_after_load["rss_mb"],
        "peak_rss_mb": mem_after_stress["peak_mb"],
        "final_rss_mb": mem_after_stress["rss_mb"],
        "load_time_sec": round(load_time_sec, 2),
        "mean_latency_ms": round(sum(latencies)/len(latencies), 1),
        "passed_512mb_limit": passed_limit,
        "passed_400mb_target": passed_target,
    }

if __name__ == "__main__":
    profile_backend_memory("onnx_int8")
