# 📈 Stock Alerts

A cloud-based **Stop Loss** and **Take Profit** alert system for financial assets across multiple markets (BCBA, NYSE, NASDAQ, crypto, etc). Runs 100% in the cloud — no local machine required.

## ✨ Features

- 🔴 **Stop Loss** — alerts when an asset drops below a lower limit
- 🟢 **Take Profit** — alerts when an asset exceeds an upper limit
- 📲 **Telegram notifications** in near real-time
- 🌐 **Web UI** to manage tickers from any browser
- ⏱️ **Price check every 60 seconds**
- 🔁 **One-shot with manual reactivation** — alert deactivates after firing and can be re-enabled anytime
- 📋 **Alert log** — history of the last 50 triggered alerts
- 🔒 **API Key protected** — all UI and endpoints require authentication

## 🏗️ Architecture

```
[Google Cloud Run]
      │
      ├── FastAPI App
      │       ├── Web UI  ←── Browser
      │       ├── REST API (protected with X-API-Key)
      │       └── APScheduler (every 60s)
      │               │
      │               ├── Yahoo Finance → current prices
      │               ├── Supabase → reads tickers & limits
      │               └── If price crosses limit:
      │                       ├── Telegram Bot → message
      │                       └── Supabase → log + deactivate alert
      │
[Google Cloud Scheduler] → ping every 60s to keep container alive
      │
[Supabase]
      ├── table: tickers
      └── table: alerts_log
```

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python + FastAPI |
| Scheduler | APScheduler |
| Database | Supabase (PostgreSQL) |
| Hosting | Google Cloud Run |
| External cron | Google Cloud Scheduler |
| Price data | Yahoo Finance (via REST) |
| Alerts | Telegram Bot API |
| Frontend | Vanilla HTML/CSS/JS |

## 📁 Project Structure

```
stock-alerts/
├── main.py          # Backend: API, scheduler, alert logic
├── index.html       # Web UI
├── requirements.txt # Python dependencies
├── Dockerfile       # Image for Cloud Run
├── .env.example     # Environment variables template
└── .gcloudignore    # Files excluded from build
```

## 🚀 Setup

### 1. Prerequisites

- [Supabase](https://supabase.com) account
- [Google Cloud](https://console.cloud.google.com) account (with billing enabled)
- Telegram bot created via [@BotFather](https://t.me/botfather)
- [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) installed

### 2. Database (Supabase)

Run this SQL in your Supabase project's **SQL Editor**:

```sql
CREATE TABLE tickers (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    symbol TEXT NOT NULL UNIQUE,
    upper_limit NUMERIC,
    lower_limit NUMERIC,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE alerts_log (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    symbol TEXT NOT NULL,
    price NUMERIC NOT NULL,
    limit_type TEXT NOT NULL,
    limit_value NUMERIC NOT NULL,
    triggered_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE tickers DISABLE ROW LEVEL SECURITY;
ALTER TABLE alerts_log DISABLE ROW LEVEL SECURITY;
```

### 3. Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=sb_secret_...
TELEGRAM_TOKEN=123456789:AAF...
TELEGRAM_CHAT_ID=123456789
API_SECRET_KEY=your_long_random_secret
```

> To generate a secure `API_SECRET_KEY`:
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

### 4. Deploy to Google Cloud Run

```bash
# Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudscheduler.googleapis.com cloudbuild.googleapis.com

# Create image repository
gcloud artifacts repositories create stock-alerts --repository-format=docker --location=us-central1

# Build
gcloud builds submit --tag us-central1-docker.pkg.dev/YOUR_PROJECT_ID/stock-alerts/app

# Deploy
gcloud run deploy stock-alerts \
  --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/stock-alerts/app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --env-vars-file env.yaml \
  --max-instances=1
```

### 5. Cloud Scheduler (recommended)

Keeps the container alive and ensures monitoring even with no web traffic:

```bash
gcloud scheduler jobs create http stock-alerts-checker \
  --location=us-central1 \
  --schedule="* * * * *" \
  --uri="https://YOUR_SERVICE_URL.run.app/internal/check" \
  --message-body="{}" \
  --headers="X-API-Key=YOUR_API_SECRET_KEY,Content-Type=application/json" \
  --time-zone="America/Argentina/Buenos_Aires"
```

## 🔄 Redeploying (after code changes)

```bash
gcloud builds submit --tag us-central1-docker.pkg.dev/YOUR_PROJECT_ID/stock-alerts/app
gcloud run deploy stock-alerts \
  --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/stock-alerts/app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --env-vars-file env.yaml \
  --max-instances=1
```

## 💡 Usage

1. Open your service URL in the browser
2. Enter your `API_SECRET_KEY`
3. Add a ticker with symbol (e.g. `AAPL`, `GGAL.BA`, `BTC-USD`) and limits
4. Alerts fire automatically and arrive via Telegram
5. Reactivate any alert from the UI whenever you want

### Supported Symbol Formats

| Market | Example |
|---|---|
| NYSE / NASDAQ | `AAPL`, `MSFT`, `GOOGL` |
| BCBA (Argentina) | `GGAL.BA`, `YPF.BA`, `PAMP.BA` |
| Crypto | `BTC-USD`, `ETH-USD` |
| ETFs | `SPY`, `QQQ` |

## 💰 Estimated Cost

| Service | Cost |
|---|---|
| Google Cloud Run | $0 (free tier) |
| Google Cloud Scheduler | $0 (free tier) |
| Supabase | $0 (free tier, 500MB) |
| Yahoo Finance | $0 |
| Telegram Bot | $0 |
| **Total** | **$0/month** |

## ⚠️ Security Notes

- Never commit `.env` or `env.yaml` to Git — add them to `.gitignore`
- Always use the `sb_secret_...` Supabase key on the backend, never the `publishable` key
- Rotate your Telegram token if accidentally exposed via `@BotFather → /revoke`
- The `API_SECRET_KEY` protects both the Web UI and all REST endpoints
