# CodeWithAnil — Production Deployment & Operations Guide

This guide provides end-to-end instructions for deploying **CodeWithAnil** to production:
- **Frontend:** Vercel (Global Edge Network)
- **Backend:** Render (Python Web Service with CPU inference)
- **Database:** Managed PostgreSQL (Render, Supabase, Neon, or AWS RDS)

---

## 1. Production Readiness Audit Summary

| Component | Status | Audit Findings |
|---|---|---|
| **Real ML Inference** | **Verified** | `Hello-SimpleAI/chatgpt-detector-roberta` running on CPU float32 via PyTorch. |
| **API Endpoints** | **Verified (11/11 Passed)** | All endpoints validated via automated Pytest suite. |
| **Frontend Test Suite** | **Verified (5/5 Passed)** | Vitest unit and rubric logic tests passing cleanly. |
| **Frontend Production Build** | **Verified** | `vite build` generated optimized chunk bundle (333kB JS, 36kB CSS). |
| **Document Scanner & PDF** | **Verified** | PDF text extraction (`pypdf`), DOCX (`python-docx`), and PDF report creation (`reportlab`) tested. |
| **Database Migrations** | **Configured** | Alembic migration framework (`alembic/versions/894d575482c6_initial_schema.py`) generated and tested. |
| **PostgreSQL Support** | **Configured** | `psycopg2-binary` installed; auto-normalization from `postgres://` to `postgresql://` implemented. |
| **Secrets & Privacy** | **Secured** | Zero data retention by default; `.env` and `.db` files strictly excluded in `.gitignore`. |
| **SPA Routing on Vercel** | **Configured** | `vercel.json` rewrite rules configured for client-side routing and security headers. |

---

## 2. GitHub Upload Commands

Run these exact Windows Command Prompt or PowerShell commands from `C:\Users\DELL\OneDrive\Desktop\ak-classes\codewithanil`:

```cmd
cd /d C:\Users\DELL\OneDrive\Desktop\ak-classes\codewithanil

:: Initialize Git repository if not already initialized
git init

:: Verify status to confirm .venv, node_modules, and .env are excluded
git status

:: Add all tracked production files
git add .

:: Commit production-ready release
git commit -m "feat: release production-ready CodeWithAnil AI text detector"

:: Link to your GitHub repository
git branch -M main
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/codewithanil.git

:: Push to GitHub
git push -u origin main
```

---

## 3. Backend Deployment on Render

### Method A: One-Click Render Blueprint (Recommended)
1. Log in to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** -> **Blueprint**.
3. Connect your GitHub repository `codewithanil`.
4. Render will detect [`backend/render.yaml`](file:///c:/Users/DELL/OneDrive/Desktop/ak-classes/codewithanil/backend/render.yaml) and automatically create:
   - A managed PostgreSQL instance (`codewithanil-postgres`).
   - A Python 3.11 web service (`codewithanil-backend`).
5. Click **Apply**.

### Method B: Manual Web Service Setup
If creating the service manually:
- **Root Directory:** `backend`
- **Environment:** `Python 3`
- **Build Command:**
  ```bash
  pip install --upgrade pip && pip install torch --index-url https://download.pytorch.org/whl/cpu && pip install -r requirements.txt && alembic upgrade head
  ```
- **Start Command:**
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1
  ```
- **Health Check Path:** `/api/health`
- **Plan:** Starter (minimum 1GB RAM recommended for RoBERTa transformer inference).

### Production Environment Variables for Render
Configure these in the Render Dashboard under **Environment**:

| Key | Example Value | Description |
|---|---|---|
| `ENVIRONMENT` | `production` | Switches logging and error modes |
| `API_V1_STR` | `/api` | Base API route prefix |
| `SECRET_KEY` | *(Generate via `openssl rand -hex 32`)* | JWT signing secret |
| `DATABASE_URL` | `postgresql://user:pass@host:5432/codewithanil` | Managed PostgreSQL connection string |
| `CORS_ORIGINS` | `["https://codewithanil.vercel.app"]` | Whitelisted frontend origins |
| `HF_MODEL_NAME` | `Hello-SimpleAI/chatgpt-detector-roberta` | Pretrained Hugging Face checkpoint |
| `INFERENCE_DEVICE` | `cpu` | PyTorch execution target |
| `RATE_LIMIT_PER_MINUTE` | `60` | SlowAPI rate limit per IP |

---

## 4. Frontend Deployment on Vercel

1. Log in to [Vercel](https://vercel.com).
2. Click **Add New...** -> **Project**.
3. Import the `codewithanil` repository.
4. Configure Project Settings:
   - **Framework Preset:** `Vite`
   - **Root Directory:** Edit and select `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
5. Configure Environment Variables:
   - `VITE_API_URL`: Set to your deployed Render backend API URL:
     ```
     https://codewithanil-backend.onrender.com/api
     ```
6. Click **Deploy**.

---

## 5. Post-Deployment Verification Checklist

Once deployed, complete this checklist:

- [ ] **Health Check:** Open `https://your-backend.onrender.com/api/health` and verify `"status": "healthy"` and `"model_loaded": true`.
- [ ] **API Documentation:** Open `https://your-backend.onrender.com/docs` to verify Swagger UI.
- [ ] **CORS Verification:** Test submitting text from your Vercel URL to verify no CORS errors occur in the browser console.
- [ ] **Real AI Inference:** Paste a test paragraph on the Detector page and verify that calibrated scores and sentence highlights return within ~500ms.
- [ ] **Document Upload & PDF Report:** Upload a sample `.txt` or `.pdf` file and click "Download PDF Audit Report" to confirm ReportLab generates a valid PDF download.
- [ ] **Database Persistence:** Create a new user account, run an analysis with "Save to my dashboard history" checked, and verify that the entry appears in the Dashboard history table.
