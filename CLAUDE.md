# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a personal portfolio repository for Ivo Celaye (Data & Analytics Engineer at MercadoLibre, pursuing a Master's in Data Science). It contains independent Python projects and a static portfolio site — there is no shared build system or monorepo tooling.

## Projects

### `ChatbotUNLaM/` — RAG Chatbot (Streamlit + OpenAI)

A Streamlit chatbot for UNLaM's Economics Department. The three-layer pipeline is:
1. `rag_system.py` — `RAGSystem` class holds 9 hardcoded documents as in-memory embeddings (OpenAI `text-embedding-3-small`). On each query it enriches the search using the last 3 conversation turns, then returns top-k chunks above a 0.5 cosine-similarity threshold.
2. `web_search.py` — fallback scraper that hits two hardcoded UNLaM URLs when RAG context is insufficient (< 100 chars).
3. `unlam_chatbot_app.py` — Streamlit entry point; both `RAGSystem` and `OpenAI` client are cached via `@st.cache_resource`. Uses GPT-3.5-turbo at temperature 0.3, passing only the current user message (not full history) to the model.

**Run locally:**
```bash
cd ChatbotUNLaM
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
streamlit run unlam_chatbot_app.py
```

**Required env var:** `OPENAI_API_KEY`

**Deployment:** Streamlit Cloud — set `OPENAI_API_KEY` in the app's Secrets panel.

---

### `stock-alerts/` — Stock Alert Service (FastAPI + Supabase + Telegram)

A containerized FastAPI service deployed on Google Cloud Run. Architecture:
- `main.py` — single-file backend. APScheduler runs `check_prices()` every 60 seconds inside the FastAPI lifespan. Price fetching tries two Yahoo Finance endpoints sequentially, falling back gracefully. All Supabase access goes through four thin wrappers (`supa_get`, `supa_post`, `supa_patch`, `supa_delete`) using the REST API directly (no Supabase SDK).
- `index.html` — served as the frontend from the `/` route via `HTMLResponse`.
- All API routes require `X-API-Key` header matching `API_SECRET_KEY` env var. The `/internal/check` endpoint is called by Google Cloud Scheduler every minute to keep the container warm.
- A `_firing` set prevents duplicate Telegram alerts within a single check cycle. After firing, the ticker is deactivated in Supabase (`is_active = False`).

**Run locally:**
```bash
cd stock-alerts
pip install -r requirements.txt
cp .env.example .env  # fill in values
uvicorn main:app --reload
```

**Required env vars:** `SUPABASE_URL`, `SUPABASE_KEY`, `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`, `API_SECRET_KEY`

**Deploy to Cloud Run:**
```bash
gcloud builds submit --tag us-central1-docker.pkg.dev/YOUR_PROJECT_ID/stock-alerts/app
gcloud run deploy stock-alerts --image ... --env-vars-file env.yaml --max-instances=1
```

**Supabase schema** (run once in Supabase SQL editor — see `stock-alerts/README.md` for the full SQL).

---

### `automations/digestio-scholar/` — Daily Paper Digest (GitHub Actions + OpenAI)

A scheduled script (`DigestoDiarioScholar.py`) that:
1. Queries Semantic Scholar API for ML/AI papers from the past 7 days across 11 keyword queries.
2. Deduplicates against `papers_enviados.txt` (a flat text file committed to the repo by the GitHub Actions bot after each run).
3. Generates structured academic digests via GPT-4o-mini (temperature 0.3, max 300 tokens).
4. Saves an HTML report and emails it via Gmail SMTP to a hardcoded recipient list.

The script calls `os.chdir` to its own directory at startup — always run it from `automations/digestio-scholar/` or via the GitHub Actions workflow.

**Run manually:**
```bash
cd automations/digestio-scholar
pip install openai requests
export OPENAI_API_KEY=sk-...
export GMAIL_PASSWORD=...
python DigestoDiarioScholar.py
```

**GitHub Actions workflow** (`.github/workflows/daily-digest.yml`): runs at 11:00 UTC daily (8:00 AM Argentina), then commits the updated `papers_enviados.txt` back to the repo.

**Required secrets (GitHub):** `OPENAI_API_KEY`, `GMAIL_PASSWORD`

---

### `docs/` — GitHub Pages Portfolio Site

Static single-page portfolio (`docs/index.html`) published via GitHub Pages with Jekyll minimal theme. All CSS and JS are inline in the single HTML file. The contact form posts to Formspree (`https://formspree.io/f/manpleoy`). No build step — edit `index.html` directly.

## Key Conventions

- Each project is fully self-contained with its own `requirements.txt`. There are no shared dependencies between projects.
- All secrets are injected via environment variables. Never hardcode credentials — the patterns already in use are `.env` files (loaded with `python-dotenv`) for local dev, GitHub Secrets for CI, and Cloud Run env vars for the stock-alerts service.
- `papers_enviados.txt` is intentionally committed to the repo — it's the deduplication state for the digest automation. Don't add it to `.gitignore`.
- The `ChatbotUNLaM` knowledge base (the 9 documents in `rag_system.py`) is hardcoded in Python, not in external files. To update UNLaM course information, edit the `_load_documents` method directly.
