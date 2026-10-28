import sys
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from ml.inference import AIModelInferenceService

service = AIModelInferenceService.get_instance()
service.load_model()

test_cases = [
    (
        "AI Tech",
        "Furthermore, it is essential to emphasize that transformer models operate via self-attention mechanisms that compute pairwise dot products between query and key vectors. Consequently, this architecture captures contextual relationships across tokens regardless of their positional distance.",
        1
    ),
    (
        "Human Personal",
        "Yesterday my old station wagon finally sputtered out on the highway near Exit 42. Smoke started billowing from the radiator cap, so I pulled over onto the shoulder and waited for almost two hours in the freezing rain for AAA to show up.",
        0
    ),
    (
        "AI Biology",
        "Photosynthesis is the process by which green plants convert light energy into chemical energy to sustain life on earth. During this biological process, plants absorb sunlight, water, and carbon dioxide to synthesize glucose and release oxygen into the surrounding atmosphere as a byproduct.",
        1
    ),
    (
        "Human Casual",
        "I honestly cannot stand when people leave their grocery carts right in the middle of an empty parking space instead of walking ten yards to the cart corral. It is sheer laziness and I had to swerve around two of them this morning.",
        0
    ),
    (
        "AI History",
        "The Industrial Revolution marked a profound turning point in human history, transitioning agrarian societies into industrialized urban centers. This economic and technological transformation was catalyzed by advancements in steam power, mechanized textile production, and metallurgical innovations.",
        1
    ),
    (
        "Human Narrative",
        "My grandfather kept a small wooden box under his workbench where he stored old brass screws, worn fishing lures, and a silver coin from 1921. Whenever we worked in the shed, he would tell stories about fixing tractor engines before modern replacement parts existed.",
        0
    )
]

print("-" * 75)
print(f"{'Category':<16} | {'True':<5} | {'AI Score':<10} | {'Human Score':<12} | {'Prediction'}")
print("-" * 75)

for name, text, true_label in test_cases:
    res = service.predict_text(text, include_sentences=True)
    true_str = "AI" if true_label == 1 else "Human"
    print(f"{name:<16} | {true_str:<5} | {res['ai_score']*100:>6.1f}%    | {res['human_score']*100:>8.1f}%    | {res['prediction']}")
    if res['sentence_analyses']:
        print(f"   -> Evaluated {len(res['sentence_analyses'])} sentence segments. Sample: {res['sentence_analyses'][0]['text'][:60]}... (AI: {res['sentence_analyses'][0]['ai_score']*100:.1f}%)")

print("-" * 75)
