# CodeWithAnil — Model Card

## 1. Model Details

- **Model Name:** `Hello-SimpleAI/chatgpt-detector-roberta`
- **Architecture:** RoBERTa (Robustly Optimized BERT Approach) Sequence Classification
- **Parameters:** ~125 Million parameters (12 attention heads, 12 hidden layers)
- **Primary Framework:** PyTorch & Hugging Face Transformers
- **Inference Mode:** Float32 CPU Inference (`torch.inference_mode()`)
- **License:** Apache 2.0 / Open Access
- **Primary Training Benchmark:** HC3 (Human ChatGPT Comparison Corpus)

## 2. Intended Use

### Supported Applications
- Identification of statistical distributional regularities and uniform perplexity patterns commonly present in autoregressive Large Language Models (e.g., ChatGPT, GPT-4, Claude).
- Educational demonstrations of NLP token probability distributions and sentence burstiness.
- Secondary screening assistance in conjunction with human review, revision histories, and interview dialogue.

### Prohibited / Out-of-Scope Uses
- **Sole Disciplinary Basis:** Using model probability scores as the sole justification for disciplinary, academic, legal, or employment punitive actions.
- **Definitive Attribution:** Claiming the model proves *which* individual or AI model authored a text.
- **Short Texts (< 50 words):** Inferring authorship on phrases, tweet-length excerpts, or single sentences.

## 3. Training Provenance

The primary model was trained on the **HC3 (Human ChatGPT Comparison Corpus)** benchmark containing ~40,000 question-answer pairs spanning:
- Open-domain QA (Reddit ELI5)
- Computer Science & Technical QA
- Wikipedia knowledge summaries
- Medical and legal informational queries
- Academic discourse

## 4. Known Scientific Limitations & Bias

1. **Non-Native English (ESL) Sensitivity:**
   - Non-native writers naturally rely on standard vocabulary choices and structured syntactic transitions. Classifiers often misinterpret this low lexical dispersion as synthetic LLM output.
2. **Adversarial Paraphrasing:**
   - Replacing synonyms, injecting intentional typographical artifacts, or translating text across intermediate languages degrades classification accuracy.
3. **Format & Domain Shift:**
   - Highly formulaic texts (legal contracts, technical specifications, medical protocols) often exhibit characteristics similar to AI-generated text due to standardized jargon.
4. **Length Sensitivity:**
   - Shorter passages (< 50 words) provide too few tokens to compute stable sequence perplexity, resulting in higher variance and potential misclassifications.

## 5. Calibration & Uncertainty Margins

To prevent binary overconfidence, CodeWithAnil employs calibrated boundary thresholds:
- **Calibrated AI Score > 60%:** Classified as *Likely AI-Generated*.
- **Calibrated AI Score < 40%:** Classified as *Likely Human-Written*.
- **Score between 40% and 60%:** Explicitly classified as *Inconclusive*, instructing the user to perform manual qualitative inspection.
