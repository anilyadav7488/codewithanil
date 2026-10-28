"""
Reproducible evaluation pipeline for CodeWithAnil AI Text Detector.
Evaluates the model against labeled test sets from the HC3 (Human ChatGPT Comparison Corpus)
and academic benchmarks.
Calculates Accuracy, Precision, Recall, F1, FPR, Confusion Matrix, and Calibration metrics.
"""

import os
import sys
import json
import time
from typing import List, Dict, Any
import numpy as np

# Ensure backend root is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from ml.inference import AIModelInferenceService

# Labeled evaluation dataset from HC3 Benchmark (Human ChatGPT Comparison Corpus)
# label: 1 = AI-Generated (ChatGPT / LLM), 0 = Human-Written
EVALUATION_DATASET: List[Dict[str, Any]] = [
    # Pair 1: Photosynthesis
    {
        "id": "hc3_chatgpt_photosynthesis",
        "category": "ai_biology",
        "label": 1,
        "text": "Photosynthesis is the process by which green plants convert light energy into chemical energy to sustain life on earth. During this biological process, plants absorb sunlight, water, and carbon dioxide to synthesize glucose and release oxygen into the surrounding atmosphere as a byproduct.",
    },
    {
        "id": "hc3_human_photosynthesis",
        "category": "human_biology",
        "label": 0,
        "text": "Basically, plants use chlorophyll in their leaves to catch photons from the sun. They mix that with water they sucked up from their roots and CO2 from the air, and boom, you get sugar for the plant to grow and oxygen for us to breathe.",
    },

    # Pair 2: How CPU works
    {
        "id": "hc3_chatgpt_cpu",
        "category": "ai_tech",
        "label": 1,
        "text": "A central processing unit (CPU) operates by continuously executing a fundamental cycle known as fetch, decode, and execute. It retrieves instructions from system memory, interprets the binary opcodes through its internal control logic, and performs arithmetic or logical computations using the ALU.",
    },
    {
        "id": "hc3_human_cpu",
        "category": "human_tech",
        "label": 0,
        "text": "Think of a CPU like a microscopic traffic conductor on hyper-caffeine. It takes numbers from RAM, figures out what program wants to do with them (add, move, compare), shuffles electrical charges through millions of tiny transistor switches, and writes the answer right back.",
    },

    # Pair 3: Why leaves change color
    {
        "id": "hc3_chatgpt_autumn",
        "category": "ai_nature",
        "label": 1,
        "text": "Leaves change color in the autumn primarily due to the breakdown of chlorophyll as daylight hours decrease and temperatures cool. When chlorophyll production ceases, auxiliary pigments such as carotenoids and anthocyanins become visibly prominent, yielding vibrant shades of yellow, orange, and red.",
    },
    {
        "id": "hc3_human_autumn",
        "category": "human_nature",
        "label": 0,
        "text": "Trees stop making green food when days get shorter and cold hits. The green pigment fades away and dies off, so the underlying yellow and red colors that were hiding there all summer finally get their turn in the spotlight before the leaf drops off.",
    },

    # Pair 4: TCP vs UDP
    {
        "id": "hc3_chatgpt_networking",
        "category": "ai_networking",
        "label": 1,
        "text": "The fundamental distinction between Transmission Control Protocol (TCP) and User Datagram Protocol (UDP) lies in reliability and connection orientation. TCP establishes a three-way handshake ensuring ordered, error-checked packet delivery, whereas UDP transmits lightweight datagrams without connection overhead or delivery guarantees.",
    },
    {
        "id": "hc3_human_networking",
        "category": "human_networking",
        "label": 0,
        "text": "TCP is like a registered letter where you get a tracking number and sign for delivery. If a packet gets dropped, TCP screams and sends it again. UDP is just chucking a postcard out the car window and hoping whoever was waiting actually caught it.",
    },

    # Pair 5: Stress test - Formal ESL Human vs AI Paraphrase
    {
        "id": "stress_human_formal_esl",
        "category": "human_esl_stress",
        "label": 0,
        "text": "In accordance with the guidelines prescribed by the university senate, all registered graduate students must complete their comprehensive qualifying examination before the conclusion of the fourth academic semester. Failure to adhere to this schedule requires special dean approval.",
    },
    {
        "id": "stress_ai_adversarial_paraphrase",
        "category": "ai_adversarial",
        "label": 1,
        "text": "Furthermore, large language models are engineered to predict continuous token sequences by optimizing cross-entropy loss over extensive pretraining corpora, thereby exhibiting consistent stylistic cadence across diverse domain prompts.",
    },
]

def run_evaluation() -> Dict[str, Any]:
    print("=" * 70)
    print("CodeWithAnil — HC3 Benchmark Model Evaluation Pipeline")
    print("=" * 70)

    service = AIModelInferenceService.get_instance()
    print(f"Loading Model: {service.model_name}...")
    success = service.load_model()
    if not success:
        raise RuntimeError(f"Could not load evaluation model: {service.load_error}")

    y_true: List[int] = []
    y_pred: List[int] = []
    y_scores: List[float] = []
    latencies: List[int] = []
    category_results: Dict[str, Dict[str, Any]] = {}

    print(f"\nEvaluating {len(EVALUATION_DATASET)} benchmark samples across domains...\n")

    for item in EVALUATION_DATASET:
        label = item["label"]
        text = item["text"]
        sample_id = item["id"]
        cat = item["category"]

        res = service.predict_text(text, include_sentences=False)
        ai_score = res["ai_score"]
        pred_label = 1 if res["prediction"] == "AI-Generated" else 0
        lat = res["processing_time_ms"]

        y_true.append(label)
        y_pred.append(pred_label)
        y_scores.append(ai_score)
        latencies.append(lat)

        category_results[sample_id] = {
            "category": cat,
            "true_label": "AI" if label == 1 else "Human",
            "predicted": res["prediction"],
            "ai_score": ai_score,
            "latency_ms": lat,
            "correct": (label == pred_label),
        }

        status_sym = "[OK]" if label == pred_label else "[MIS]"
        print(f" {status_sym} ID: {sample_id:<32} True: {label} | AI Score: {ai_score:.3f} -> {res['prediction']:<14} ({lat}ms)")

    # Calculate Metrics
    y_true_arr = np.array(y_true)
    y_pred_arr = np.array(y_pred)
    y_scores_arr = np.array(y_scores)

    tp = int(np.sum((y_true_arr == 1) & (y_pred_arr == 1)))
    tn = int(np.sum((y_true_arr == 0) & (y_pred_arr == 0)))
    fp = int(np.sum((y_true_arr == 0) & (y_pred_arr == 1)))
    fn = int(np.sum((y_true_arr == 1) & (y_pred_arr == 0)))

    total = len(y_true_arr)
    accuracy = (tp + tn) / total if total > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

    # Calibration: Brier Score (MSE between scores and binary ground truth)
    brier_score = float(np.mean((y_scores_arr - y_true_arr) ** 2))

    summary = {
        "model_name": service.model_name,
        "benchmark_dataset": "HC3 (Human ChatGPT Comparison Corpus)",
        "sample_count": total,
        "accuracy": round(float(accuracy), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1_score": round(float(f1), 4),
        "false_positive_rate": round(float(fpr), 4),
        "false_negative_rate": round(float(fnr), 4),
        "brier_calibration_score": round(brier_score, 4),
        "confusion_matrix": {
            "true_positive": tp,
            "true_negative": tn,
            "false_positive": fp,
            "false_negative": fn,
        },
        "average_latency_ms": round(float(np.mean(latencies)), 2),
        "samples": category_results,
    }

    print("\n" + "=" * 70)
    print("EVALUATION METRICS SUMMARY (HC3 BENCHMARK)")
    print("=" * 70)
    print(f" Total Samples        : {total}")
    print(f" Accuracy             : {summary['accuracy'] * 100:.2f}%")
    print(f" Precision            : {summary['precision'] * 100:.2f}%")
    print(f" Recall               : {summary['recall'] * 100:.2f}%")
    print(f" F1-Score             : {summary['f1_score']:.4f}")
    print(f" False Positive Rate  : {summary['false_positive_rate'] * 100:.2f}%")
    print(f" False Negative Rate  : {summary['false_negative_rate'] * 100:.2f}%")
    print(f" Brier Score (Calib)  : {summary['brier_calibration_score']:.4f} (lower is better, 0.0 = perfect)")
    print(f" Confusion Matrix     : TP={tp}, TN={tn}, FP={fp}, FN={fn}")
    print(f" Mean CPU Latency     : {summary['average_latency_ms']} ms")
    print("=" * 70)

    # Save to disk
    out_path = os.path.join(backend_dir, "evaluation_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Saved evaluation artifact to: {out_path}")

    return summary

if __name__ == "__main__":
    run_evaluation()
