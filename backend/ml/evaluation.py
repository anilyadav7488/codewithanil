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
    {
        "id": "hc3_pair_1_chatgpt",
        "category": "reddit_eli5_ai",
        "label": 1,
        "text": "There are many different best seller lists that are published by various organizations, and the New York Times is just one of them. The New York Times best seller list is a weekly list that ranks the best-selling books in the United States based on sales data from a number of different retailers. The list is published in the New York Times newspaper and is widely considered to be one of the most influential best seller lists in the book industry. It's important to note that the New York Times"
    },
    {
        "id": "hc3_pair_1_human",
        "category": "reddit_eli5_human",
        "label": 0,
        "text": "Basically there are many categories of \" Best Seller \" . Replace \" Best Seller \" by something like \" Oscars \" and every \" best seller \" book is basically an \" oscar - winning \" book . May not have won the \" Best film \" , but even if you won the best director or best script , you 're still an \" oscar - winning \" film . Same thing for best sellers . Also , IIRC the rankings change every week or something like that"
    },
    {
        "id": "hc3_pair_2_chatgpt",
        "category": "reddit_eli5_ai",
        "label": 1,
        "text": "Salt is used on roads to help melt ice and snow and improve traction during the winter months. When it's cold outside, water can freeze on the roads and make them very slippery, which can be dangerous for cars and people. Salt helps to melt the ice and snow by lowering the freezing point of water, which means that it can help keep the roads clear and safe to travel on. There are other options for melting ice and snow on roads, such as using chemicals like calcium chloride or"
    },
    {
        "id": "hc3_pair_2_human",
        "category": "reddit_eli5_human",
        "label": 0,
        "text": "salt is good for not dying in car crashes and car crashes are worse for cars then salt . Some places use other things , but salt is really cheap compared to most alternatives , although sand is pretty good ."
    },
    {
        "id": "hc3_pair_3_chatgpt",
        "category": "reddit_eli5_ai",
        "label": 1,
        "text": "There are a few reasons why we still have SD (standard definition) TV channels: 1. Some people still use older TVs that are not compatible with HD (high definition) signals. These TVs can only display SD channels, so if we only had HD channels, those people wouldn't be able to watch TV. 2. HD channels take up more bandwidth than SD channels, so it's not possible to have as many HD channels as we have SD channels. This means that if we only had HD channels, some channels might not"
    },
    {
        "id": "hc3_pair_3_human",
        "category": "reddit_eli5_human",
        "label": 0,
        "text": "The way it works is that old TV stations got a certain amount of bandwidth to replace their old analog TV stations . However , HD takes up more bandwidth then SD - so the stations can choose between 2 or 3 HD stations , or like 7 or 8 SD stations ( or a mix of both ) They can do a bunch of SD stations and make more money in advertizing by running 7 or 8 different reruns of old SD TV shows at a time In fact"
    },
    {
        "id": "hc3_pair_4_chatgpt",
        "category": "reddit_eli5_ai",
        "label": 1,
        "text": "It is generally not acceptable or ethical to advocate for or condone the assassination of any individual, regardless of their actions or beliefs. There are also practical considerations at play in this situation. First and foremost, it is important to remember that assassination is a violent and extreme act that can have serious consequences, both for the person being targeted and for those around them. It can also lead to further conflict and instability in the region. Additionally, the North Korean government is known for being highly secretive and heavily"
    },
    {
        "id": "hc3_pair_4_human",
        "category": "reddit_eli5_human",
        "label": 0,
        "text": "You ca n't just go around assassinating the leaders of countries you do nt like ! The international condemnation would be brutal . Even though noone likes Kim Jong - Un , and everyone thinks North Korea is pretty shitty to its citizens , if say the US were to send agents over ( and do n't think they are n't capable of it ) and they got caught .... every country , every world leader would be a potential target . Who 's next ... Castro ? Angela Merkel"
    },
    {
        "id": "hc3_pair_5_chatgpt",
        "category": "reddit_eli5_ai",
        "label": 1,
        "text": "The color of your eyes is determined by the amount and type of pigments in your iris, which is the colored part of your eye, and by the way that the iris scatters light. The iris contains two types of pigment: one called melanin, which gives your skin, hair, and eyes their color, and another called lipochrome, which is a yellowish pigment. The combination of these pigments, along with the structure of the iris, determines the color of your eyes. There are many different shades of eye color, ranging from"
    },
    {
        "id": "hc3_pair_5_human",
        "category": "reddit_eli5_human",
        "label": 0,
        "text": "Melanin ! Many of the the first known humans existed in the fertile crescent - modern day Iraq and surrounding areas , and it was just as sunny and hot as it is today . Melanin causes skin and eyes to have a darker color , and as a benefit reduced the amount of UV radiation absorbed into the skin . Eventually humans expanded into less hot and sunlit areas allowing for the survival and procreation of people who developed lighter colored eyes and skin because of the lack of"
    },
    {
        "id": "hc3_pair_6_chatgpt",
        "category": "reddit_eli5_ai",
        "label": 1,
        "text": "The First Amendment to the United States Constitution protects the freedom of religion, which means that you have the right to believe and practice whatever religion you choose. However, this freedom is not absolute and can be limited in certain circumstances to protect the rights and safety of others. In the case you described, going to school is not a matter of personal belief or religious practice. It is a legal requirement for children of a certain age to attend school in order to receive an education. By not going"
    },
    {
        "id": "hc3_pair_6_human",
        "category": "reddit_eli5_human",
        "label": 0,
        "text": "Because you 're a minor and your parents get to make that choice for you . Specifically to keep you from doing dumb shit like this . Now go to bed , you are going to school tomorrow ."
    },
    {
        "id": "hc3_pair_7_chatgpt",
        "category": "reddit_eli5_ai",
        "label": 1,
        "text": "There are a few different factors that can contribute to the trend of throwing away products instead of fixing them. One factor is the quality of the products themselves. Some products are designed in a way that makes them difficult or impossible to repair. For example, if a product is made with very cheap materials or is put together in a way that makes it hard to access the parts that need to be repaired, it may be easier or cheaper to just throw it away and buy a new"
    },
    {
        "id": "hc3_pair_7_human",
        "category": "reddit_eli5_human",
        "label": 0,
        "text": "It 's three fold : * Stuff is cheaper to mass produce now then it used to be , making it easy to replace something * Fixing something that 's broken is almost always not a mass - production task . It require human time and effort and unique problem solving skills depending on the issue . This has always been expensive , and is still expensive today . * Many things today are completely impossible for the average person to fix , often not due to people trying to"
    },
    {
        "id": "hc3_pair_8_chatgpt",
        "category": "reddit_eli5_ai",
        "label": 1,
        "text": "Magic: The Gathering is a collectible card game that was first published in 1993. It is played by millions of people around the world, and has a very dedicated and passionate player base. In the game, players use cards that represent magical spells and creatures to battle against each other. Each player has their own deck of cards, and they use them to try to defeat their opponent by reducing their life points to zero. There are many different ways to play Magic, including casual games with friends, organized tournaments,"
    },
    {
        "id": "hc3_pair_8_human",
        "category": "reddit_eli5_human",
        "label": 0,
        "text": "EDIT , Nov 21 : By popular demand , now includes Midrange decks and Limited formats . Also , a new section on where players get their cards . Magic : The Gathering is a collectable card game . It can be played in several different formats , but in the most common , two players create decks out of the cards they own and play against each other . Generally , the cards in a deck are either lands or spells . Lands provide the energy needed to cast"
    },
    {
        "id": "hc3_pair_9_chatgpt",
        "category": "reddit_eli5_ai",
        "label": 1,
        "text": "Prions are tiny particles that can cause serious and often fatal diseases in people and animals. They are made up of proteins, which are important building blocks in the body. Normally, proteins have a specific shape that helps them do their job. But prions are abnormal proteins that have a different shape, and they can cause other proteins around them to change shape too. When this happens, it can cause problems in the body because the proteins are not able to work properly. Prions are not viruses, and they do"
    },
    {
        "id": "hc3_pair_9_human",
        "category": "reddit_eli5_human",
        "label": 0,
        "text": "Like viruses , they are ( groups of ) molecules that reproduce without metabolism . Unlike any other self - replicating system , prions are proteins that have a unique structure . One part of how a protein functions is the amino acid sequence that makes up the primary structure , but the other part is how the proteins folds , either by itself or with the help of other folder - helper proteins . Prions have the same amino acid sequence as their properly folded brethren , but they"
    },
    {
        "id": "hc3_pair_10_chatgpt",
        "category": "reddit_eli5_ai",
        "label": 1,
        "text": "A hacker is someone who uses their computer skills to try to gain access to systems or networks without permission. Hackers might do this for a variety of reasons, such as to steal information, to cause damage or disruption, or just for the challenge of it. Hacking can involve a lot of typing and computer use, because hackers often use special software and programs to try to find weaknesses in a system or network. They might also use tools to try to guess passwords or to find ways to get"
    },
    {
        "id": "hc3_pair_10_human",
        "category": "reddit_eli5_human",
        "label": 0,
        "text": "> I 've always wanted to know why hackers are jamming on their keyboards In reality , this does n't happen . This is done in movies to make it look dramatic and exciting . Real computer hacking involves staring at a computer screen for hours of a time , searching a lot on Google , muttering \" hmmm \" and various expletives to oneself now and then , and stroking one 's hacker - beard while occasionally tapping on a few keys ."
    }
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
