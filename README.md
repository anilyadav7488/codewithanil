# CodeWithAnil — AI Text Detector

**Detect AI Writing. Analyze Text. Explore Authenticity.**

[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-blue?logo=typescript)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-18.3-61dafb?logo=react)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-CPU%20Inference-ee4c2c?logo=pytorch)](https://pytorch.org/)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Transformers-yellow?logo=huggingface)](https://huggingface.co/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)

**CodeWithAnil** is a full-stack, machine-learning-powered text analysis and authenticity evaluation website. It enables users to detect linguistic and statistical signals associated with AI-generated content (such as ChatGPT, GPT-4, and Claude) using a real pretrained transformer neural network running locally on CPU.

---

## Key Highlights

- **Real Machine Learning Inference:** Powered by an optimized RoBERTa sequence classifier trained on the Human ChatGPT Comparison Corpus (HC3). No simulated percentages or fake heuristics.
- **Calibrated Uncertainty Bounds:** Explicitly separates calibrated probabilities from raw model logits and flags marginal scores (40% - 60%) as **Inconclusive** to protect users against binary false positives.
- **Sentence-Level Breakdown:** Inspects individual sentences to reveal local token regularities with strict warnings that isolated sentences do not prove authorship.
- **Prompt Analyzer & Refiner:** Audits LLM prompt instructions against a 7-dimension structural rubric (clarity, specificity, context, constraints, formatting, completeness, ambiguity) and outputs actionable suggestions with a refactored version.
- **Multi-Format Document Scanner:** Safely uploads PDF, DOCX, and TXT files, detects image-only scanned PDFs requiring OCR, and generates downloadable **PDF Audit Certificates**.
- **Secure Authentication & Private History:** Bcrypt-hashed credentials, JWT session management, and strict zero-data-retention by default.
- **Modern Dark Navy UI:** Glassmorphism cards, electric blue and purple gradients, dark/light mode toggle, responsive mobile navigation, and accessible UX.

---

## Repository Structure

```
codewithanil/
  frontend/
    src/
      components/          # Navbar, Footer, ScoreGauge, SentenceHighlighter, ModelTransparencyCard
      pages/               # HomePage, DetectorPage, PromptAnalyzerPage, DocumentScannerPage, DashboardPage, AboutPage, AuthPages
      layouts/             # MainLayout with responsive container
      services/            # Axios API client with auth interceptors
      contexts/            # ThemeContext (dark/light) & AuthContext (JWT)
      types/               # TypeScript interfaces
      App.tsx              # React Router v6 routing
      main.tsx             # Entrypoint
    package.json           # React 18, Vite, Tailwind CSS, Lucide React, Recharts
    vite.config.ts         # Vite bundler with /api proxy
  backend/
    app/
      main.py              # FastAPI application with startup lifespan & SlowAPI
      api/v1/              # Endpoints: /analyze, /auth, /model, /analysis, /reports
      core/                # Settings & Bcrypt/JWT security utilities
      models/              # SQLAlchemy User, Analysis, Document, Report models
      schemas/             # Pydantic v2 schemas
      services/            # Document extraction, Prompt rubric, ReportLab PDF generator
      database/            # SQLAlchemy session & DB engine
    alembic/               # Alembic database migrations (PostgreSQL/SQLite)
    ml/
      inference.py         # PyTorch inference service with RoBERTa sequence classification
      preprocessing.py     # Cleaners, zero-width strippers & sentence boundary parsers
      evaluation.py        # Reproducible evaluation pipeline on labeled benchmarks
      training.py          # Reference fine-tuning orchestrator
    tests/                 # Pytest test suite (11 automated tests)
    Dockerfile             # Production Docker container
    render.yaml            # Render Blueprint deployment definition
    requirements.txt       # Python dependencies
  docs/
    architecture.md        # Technical architecture & dataflow diagrams
    model-card.md          # Model provenance, operational bounds, and ethics
    deployment.md          # Local Windows execution & production deployment
  README.md                # Project documentation
  .gitignore               # Repository ignore rules
```

---

## Windows Quick Start Guide

### Prerequisites
- Node.js v18+ and npm
- Python 3.11, 3.12, or 3.13 (64-bit)

### 1. Set Up Backend
```cmd
cd codewithanil\backend
py -3.13 -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements.txt
```

### 2. Run Tests & Evaluation
```cmd
pytest -v
python ml\evaluation.py
```

### 3. Start Backend Server
```cmd
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive API Swagger Docs: `http://127.0.0.1:8000/docs`

### 4. Set Up Frontend & Start Web Client
In a new Command Prompt:
```cmd
cd codewithanil\frontend
npm install
npm test
npm run dev
```
Open your browser at `http://localhost:3000`.

---

## Machine Learning Model Specifications

| Parameter | Specification |
|---|---|
| Model Name | `Hello-SimpleAI/chatgpt-detector-roberta` |
| Architecture | RoBERTa Sequence Classification |
| Parameters | ~125 Million |
| Inference Engine | PyTorch CPU (`torch.inference_mode()`) |
| Benchmark Dataset | HC3 (Human ChatGPT Comparison Corpus) |
| Calibrated Thresholds | AI > 60%, Human < 40%, Inconclusive: 40% - 60% |
| License | Apache 2.0 / Open Access |

---

## Ethical Disclosure & Responsible Use

> [!IMPORTANT]
> **Probabilistic Disclaimer:** CodeWithAnil is an analytical research tool. It measures statistical and syntactic overlap with known LLM distributions. It does **NOT** provide definitive legal proof of authorship. High formal conformity or technical writing can elevate AI scores on human work. Always corroborate automated findings with holistic human judgment.

---

## License

This project is licensed under the Apache 2.0 License.
