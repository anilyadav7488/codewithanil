"""
Side-by-Side Comparative Evaluation Benchmark.
Evaluates both PyTorch FP32 and ONNX Runtime Dynamic INT8 models on an expanded
30-sample benchmark dataset across diverse domains and writing styles.
Calculates Accuracy, Precision, Recall, F1, FPR, FNR, Prob Drift, and Latency.
"""

import os
import sys
import time
import numpy as np
from typing import List, Dict, Any

# Ensure backend root is in sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from ml.inference import PyTorchModelInferenceService
from ml.onnx_inference import ONNXModelInferenceService

# Representative 30-sample evaluation dataset (15 AI, 15 Human)
BENCHMARK_DATASET: List[Dict[str, Any]] = [
    # 1. Biology: Photosynthesis
    {
        "id": "bio_ai_photosynthesis",
        "category": "biology",
        "label": 1,
        "text": "Photosynthesis is the process by which green plants convert light energy into chemical energy to sustain life on earth. During this biological process, plants absorb sunlight, water, and carbon dioxide to synthesize glucose and release oxygen into the surrounding atmosphere as a byproduct.",
    },
    {
        "id": "bio_human_photosynthesis",
        "category": "biology",
        "label": 0,
        "text": "Basically, plants use chlorophyll in their leaves to catch photons from the sun. They mix that with water they sucked up from their roots and CO2 from the air, and boom, you get sugar for the plant to grow and oxygen for us to breathe.",
    },

    # 2. Tech: CPU Operations
    {
        "id": "tech_ai_cpu",
        "category": "computer_architecture",
        "label": 1,
        "text": "A central processing unit (CPU) operates by continuously executing a fundamental cycle known as fetch, decode, and execute. It retrieves instructions from system memory, interprets the binary opcodes through its internal control logic, and performs arithmetic or logical computations using the ALU.",
    },
    {
        "id": "tech_human_cpu",
        "category": "computer_architecture",
        "label": 0,
        "text": "Think of a CPU like a microscopic traffic conductor on hyper-caffeine. It takes numbers from RAM, figures out what program wants to do with them (add, move, compare), shuffles electrical charges through millions of tiny transistor switches, and writes the answer right back.",
    },

    # 3. Nature: Autumn Leaves
    {
        "id": "nature_ai_autumn",
        "category": "nature",
        "label": 1,
        "text": "Leaves change color in the autumn primarily due to the breakdown of chlorophyll as daylight hours decrease and temperatures cool. When chlorophyll production ceases, auxiliary pigments such as carotenoids and anthocyanins become visibly prominent, yielding vibrant shades of yellow, orange, and red.",
    },
    {
        "id": "nature_human_autumn",
        "category": "nature",
        "label": 0,
        "text": "Trees stop making green food when days get shorter and cold hits. The green pigment fades away and dies off, so the underlying yellow and red colors that were hiding there all summer finally get their turn in the spotlight before the leaf drops off.",
    },

    # 4. Networking: TCP vs UDP
    {
        "id": "net_ai_tcp_udp",
        "category": "networking",
        "label": 1,
        "text": "The fundamental distinction between Transmission Control Protocol (TCP) and User Datagram Protocol (UDP) lies in reliability and connection orientation. TCP establishes a three-way handshake ensuring ordered, error-checked packet delivery, whereas UDP transmits lightweight datagrams without connection overhead or delivery guarantees.",
    },
    {
        "id": "net_human_tcp_udp",
        "category": "networking",
        "label": 0,
        "text": "TCP is like a registered letter where you get a tracking number and sign for delivery. If a packet gets dropped, TCP screams and sends it again. UDP is just chucking a postcard out the car window and hoping whoever was waiting actually caught it.",
    },

    # 5. Physics: Quantum Entanglement
    {
        "id": "phys_ai_entanglement",
        "category": "physics",
        "label": 1,
        "text": "Quantum entanglement is a phenomenon in quantum mechanics where two or more particles become interconnected such that the quantum state of each particle cannot be described independently of the others, regardless of the physical distance separating them in space.",
    },
    {
        "id": "phys_human_entanglement",
        "category": "physics",
        "label": 0,
        "text": "Imagine you have a pair of magic shoes. You put one in a shoebox and mail it to Tokyo, and you keep the other one in London. The moment you open your box and see a left shoe, you know instantly that the one in Tokyo is a right shoe, without checking.",
    },

    # 6. History: Fall of Rome
    {
        "id": "hist_ai_rome",
        "category": "history",
        "label": 1,
        "text": "The decline of the Western Roman Empire was a multifaceted historical process driven by a convergence of military vulnerabilities, domestic economic stagnation, political instability, and incursions by migrating Germanic tribal confederations over several centuries.",
    },
    {
        "id": "hist_human_rome",
        "category": "history",
        "label": 0,
        "text": "Rome didn't just collapse overnight because barbarians kicked down the gates. It was more like a slow bleed of corrupt senators, runaway inflation ruining coin values, mercenary armies turning on their bosses, and plagues wiping out taxpayers.",
    },

    # 7. Economics: Supply Chain & Inflation
    {
        "id": "econ_ai_inflation",
        "category": "economics",
        "label": 1,
        "text": "Supply chain disruptions exacerbate inflationary pressures by creating acute shortages of intermediate goods, which subsequently escalates production costs and diminishes consumer purchasing power across multiple commercial sectors.",
    },
    {
        "id": "econ_human_inflation",
        "category": "economics",
        "label": 0,
        "text": "When cargo ships get stuck outside the harbor for three weeks waiting to unload containers, truck drivers can't move goods and factories run out of spare parts. Stores have fewer items on the shelves, so prices shoot through the roof.",
    },

    # 8. Chemistry: Coffee Extraction
    {
        "id": "chem_ai_coffee",
        "category": "chemistry",
        "label": 1,
        "text": "The chemistry of coffee extraction involves the selective dissolution of volatile organic compounds, lipids, and soluble solids from roasted Coffea beans into heated water at temperatures typically ranging between ninety and ninety-six degrees Celsius.",
    },
    {
        "id": "chem_human_coffee",
        "category": "chemistry",
        "label": 0,
        "text": "If you brew your espresso too fast with water that is lukewarm, it tastes like sour lemon juice. Grind it too fine and let it sit forever, and you end up with bitter battery acid because you pulled out all the harsh tannins.",
    },

    # 9. Climate: Ice-Albedo Feedback
    {
        "id": "clim_ai_feedback",
        "category": "climate_science",
        "label": 1,
        "text": "Positive feedback mechanisms in the climate system accelerate global warming trends. Specifically, the reduction of polar ice diminishes planetary albedo, thereby causing increased absorption of solar radiation by darker ocean waters and reinforcing temperature escalation.",
    },
    {
        "id": "clim_human_feedback",
        "category": "climate_science",
        "label": 0,
        "text": "White sea ice works like a giant mirror reflecting sunlight back out into space. As the planet gets hotter and the ice melts into dark blue water, that open ocean soaks in heat instead of bouncing it away, making everything melt even faster.",
    },

    # 10. Psychology: Confirmation Bias
    {
        "id": "psych_ai_bias",
        "category": "psychology",
        "label": 1,
        "text": "Confirmation bias designates the systematic cognitive tendency of human individuals to process information by searching for, interpreting, and remembering data that aligns with preexisting beliefs, while disproportionately discounting contradictory evidence.",
    },
    {
        "id": "psych_human_bias",
        "category": "psychology",
        "label": 0,
        "text": "People don't actually browse news feeds to discover new truths; they browse to find whatever agrees with what their uncle told them at dinner. Anything that doesn't fit the narrative gets scrolled past in half a second flat.",
    },

    # 11. Machine Learning: Overfitting
    {
        "id": "ml_ai_overfitting",
        "category": "machine_learning",
        "label": 1,
        "text": "Overfitting manifests when a machine learning algorithm memorizes idiosyncratic noise present within the training partition rather than discerning underlying statistical patterns, yielding degraded generalization capabilities on unseen test distributions.",
    },
    {
        "id": "ml_human_overfitting",
        "category": "machine_learning",
        "label": 0,
        "text": "Overfitting is what happens when a student memorizes the exact multiple-choice answers from last year's practice quiz word for word, and then completely bombs the actual exam because the teacher switched the order of the questions.",
    },

    # 12. Philosophy: Free Will & Determinism
    {
        "id": "phil_ai_freewill",
        "category": "philosophy",
        "label": 1,
        "text": "The philosophical discourse surrounding free will examines whether moral agents possess autonomous control over deliberative actions, contrasting deterministic paradigms with compatibilist formulations and libertarian concepts of metaphysical indeterminacy.",
    },
    {
        "id": "phil_human_freewill",
        "category": "philosophy",
        "label": 0,
        "text": "Whether you chose to eat that pizza or your brain chemistry forced you to do it because you smelled melted cheese is the oldest debate in philosophy. Either we have a steering wheel, or we're just passengers watching our own movie.",
    },

    # 13. Narrative / Creative
    {
        "id": "narr_ai_lighthouse",
        "category": "creative_narrative",
        "label": 1,
        "text": "The abandoned lighthouse loomed solemnly against the tempestuous coastal horizon, its weathered granite facade standing as an enduring testament to decades of maritime resilience amid crashing ocean tides and encroaching darkness.",
    },
    {
        "id": "narr_human_kitchen",
        "category": "creative_narrative",
        "label": 0,
        "text": "Rain slammed sideways against the kitchen window while Jerry cursed at the rusty can opener. The electricity had flickered out an hour ago, leaving him with three tea candles and half a jar of crunchy peanut butter.",
    },

    # 14. Stress Test: Formal Academic / University Guidelines (Human ESL vs AI)
    {
        "id": "stress_human_senate",
        "category": "administrative_formal",
        "label": 0,
        "text": "In accordance with the guidelines prescribed by the university senate, all registered graduate students must complete their comprehensive qualifying examination before the conclusion of the fourth academic semester. Failure to adhere to this schedule requires special dean approval.",
    },
    {
        "id": "stress_ai_adversarial",
        "category": "adversarial_paraphrase",
        "label": 1,
        "text": "Furthermore, large language models are engineered to predict continuous token sequences by optimizing cross-entropy loss over extensive pretraining corpora, thereby exhibiting consistent stylistic cadence across diverse domain prompts.",
    },

    # 15. Medical: Vaccination & Immune Response
    {
        "id": "med_ai_vaccines",
        "category": "medicine",
        "label": 1,
        "text": "Vaccines elicit protective immunity by introducing an attenuated pathogen or harmless synthetic antigen into the host, thereby prompting antigen-presenting cells to activate helper T cells and stimulate B lymphocytes to produce neutralizing antibodies.",
    },
    {
        "id": "med_human_vaccines",
        "category": "medicine",
        "label": 0,
        "text": "A vaccine is basically a wanted poster for your immune system. You give your white blood cells a safe dummy target so they learn what the bad bug looks like, so when the real virus shows up later, your antibodies can jump on it immediately.",
    },
]

def evaluate_model(service, model_label: str) -> Dict[str, Any]:
    print(f"\n--- Running Evaluation: {model_label} ---")
    y_true = []
    y_pred = []
    y_scores = []
    latencies = []
    predictions = []

    for item in BENCHMARK_DATASET:
        label = item["label"]
        text = item["text"]
        sample_id = item["id"]

        t0 = time.perf_counter()
        res = service.predict_text(text, include_sentences=False)
        lat = int((time.perf_counter() - t0) * 1000)

        ai_score = res["ai_score"]
        pred_label = 1 if res["prediction"] == "AI-Generated" else 0

        y_true.append(label)
        y_pred.append(pred_label)
        y_scores.append(ai_score)
        latencies.append(lat)
        predictions.append(res["prediction"])

    y_true_arr = np.array(y_true)
    y_pred_arr = np.array(y_pred)
    y_scores_arr = np.array(y_scores)

    tp = int(np.sum((y_true_arr == 1) & (y_pred_arr == 1)))
    tn = int(np.sum((y_true_arr == 0) & (y_pred_arr == 0)))
    fp = int(np.sum((y_true_arr == 0) & (y_pred_arr == 1)))
    fn = int(np.sum((y_true_arr == 1) & (y_pred_arr == 0)))

    total = len(y_true_arr)
    accuracy = (tp + tn) / total
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (tp + fn) if (tp + fn) > 0 else 0.0

    return {
        "model_label": model_label,
        "total": total,
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "fpr": fpr,
        "fnr": fnr,
        "mean_latency_ms": float(np.mean(latencies)),
        "median_latency_ms": float(np.median(latencies)),
        "p95_latency_ms": float(np.percentile(latencies, 95)),
        "scores": y_scores,
        "predictions": predictions,
    }

def run_comparative_benchmark():
    print("=" * 78)
    print("CodeWithAnil — FP32 PyTorch vs ONNX INT8 Comparative Benchmark")
    print(f"Total representative samples: {len(BENCHMARK_DATASET)} (15 AI, 15 Human)")
    print("=" * 78)

    # 1. Evaluate FP32 PyTorch Baseline
    pt_service = PyTorchModelInferenceService.get_instance()
    pt_loaded = pt_service.load_model()
    if not pt_loaded:
        raise RuntimeError("Failed to load PyTorch baseline model.")
    pt_results = evaluate_model(pt_service, "PyTorch FP32 (Baseline)")

    # 2. Evaluate ONNX Dynamic INT8 Model
    onnx_service = ONNXModelInferenceService.get_instance()
    onnx_loaded = onnx_service.load_model()
    if not onnx_loaded:
        raise RuntimeError("Failed to load ONNX INT8 model.")
    onnx_results = evaluate_model(onnx_service, "ONNX Dynamic INT8")

    # 3. Calculate Model Agreement & Score Drift
    pt_scores = np.array(pt_results["scores"])
    onnx_scores = np.array(onnx_results["scores"])
    abs_score_diffs = np.abs(pt_scores - onnx_scores)
    max_drift = float(np.max(abs_score_diffs))
    mean_drift = float(np.mean(abs_score_diffs))

    agreements = [
        1 if pt_results["predictions"][i] == onnx_results["predictions"][i] else 0
        for i in range(len(BENCHMARK_DATASET))
    ]
    agreement_rate = (sum(agreements) / len(agreements)) * 100.0

    # 4. Print Comparison Table
    print("\n" + "=" * 78)
    print("COMPARATIVE BENCHMARK RESULTS")
    print("=" * 78)
    print(f"{'Metric':<28} | {'PyTorch FP32':<18} | {'ONNX Dynamic INT8':<18} | {'Delta / Parity'}")
    print("-" * 78)
    print(f"{'Accuracy':<28} | {pt_results['accuracy'] * 100:>17.2f}% | {onnx_results['accuracy'] * 100:>17.2f}% | {(onnx_results['accuracy'] - pt_results['accuracy']) * 100:+.2f}%")
    print(f"{'Precision (AI class)':<28} | {pt_results['precision'] * 100:>17.2f}% | {onnx_results['precision'] * 100:>17.2f}% | {(onnx_results['precision'] - pt_results['precision']) * 100:+.2f}%")
    print(f"{'Recall (AI class)':<28} | {pt_results['recall'] * 100:>17.2f}% | {onnx_results['recall'] * 100:>17.2f}% | {(onnx_results['recall'] - pt_results['recall']) * 100:+.2f}%")
    print(f"{'F1-Score':<28} | {pt_results['f1'] * 100:>17.2f}% | {onnx_results['f1'] * 100:>17.2f}% | {(onnx_results['f1'] - pt_results['f1']) * 100:+.2f}%")
    print(f"{'False Positive Rate (FPR)':<28} | {pt_results['fpr'] * 100:>17.2f}% | {onnx_results['fpr'] * 100:>17.2f}% | {(onnx_results['fpr'] - pt_results['fpr']) * 100:+.2f}%")
    print(f"{'False Negative Rate (FNR)':<28} | {pt_results['fnr'] * 100:>17.2f}% | {onnx_results['fnr'] * 100:>17.2f}% | {(onnx_results['fnr'] - pt_results['fnr']) * 100:+.2f}%")
    print(f"{'Mean Latency per Request':<28} | {pt_results['mean_latency_ms']:>16.1f} ms | {onnx_results['mean_latency_ms']:>16.1f} ms | {onnx_results['mean_latency_ms'] - pt_results['mean_latency_ms']:+.1f} ms")
    print(f"{'Median Latency':<28} | {pt_results['median_latency_ms']:>16.1f} ms | {onnx_results['median_latency_ms']:>16.1f} ms | {onnx_results['median_latency_ms'] - pt_results['median_latency_ms']:+.1f} ms")
    print(f"{'P95 Latency':<28} | {pt_results['p95_latency_ms']:>16.1f} ms | {onnx_results['p95_latency_ms']:>16.1f} ms | {onnx_results['p95_latency_ms'] - pt_results['p95_latency_ms']:+.1f} ms")
    print("-" * 78)
    print(f"{'Classification Agreement':<28} | {agreement_rate:>17.1f}%")
    print(f"{'Mean Prob Drift (|PT - ONNX|)':<28} | {mean_drift:>18.4f}")
    print(f"{'Max Prob Drift':<28} | {max_drift:>18.4f}")
    print("=" * 78)

    # 5. Detail per-sample predictions
    print("\nDetailed Per-Sample Results:")
    for i, item in enumerate(BENCHMARK_DATASET):
        pt_pred = pt_results["predictions"][i]
        onnx_pred = onnx_results["predictions"][i]
        pt_sc = pt_results["scores"][i]
        onnx_sc = onnx_results["scores"][i]
        match_sym = "MATCH" if pt_pred == onnx_pred else "DIFF"
        print(f"[{match_sym:5}] ID: {item['id']:<28} True: {item['label']} | PT: {pt_sc:.3f} ({pt_pred}) | INT8: {onnx_sc:.3f} ({onnx_pred})")

if __name__ == "__main__":
    run_comparative_benchmark()
