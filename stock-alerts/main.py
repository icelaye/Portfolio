import os
import logging
from datetime import datetime, timezone
from contextlib import asynccontextmanager

import requests
import httpx
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
SUPABASE_URL     = os.environ["SUPABASE_URL"]
SUPABASE_KEY     = os.environ["SUPABASE_KEY"]
TELEGRAM_TOKEN   = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
API_SECRET_KEY   = os.environ["API_SECRET_KEY"]

# ── Supabase REST helpers ─────────────────────────────────────────────────────
def supa_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }

def supa_get(table: str, params: dict = None):
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=supa_headers(),
        params=params,
        timeout=10
    )
    r.raise_for_status()
    return r.json()

def supa_post(table: str, data: dict):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=supa_headers(),
        json=data,
        timeout=10
    )
    r.raise_for_status()
    return r.json()

def supa_patch(table: str, filters: dict, data: dict):
    params = {k: f"eq.{v}" for k, v in filters.items()}
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=supa_headers(),
        params=params,
        json=data,
        timeout=10
    )
    r.raise_for_status()
    return r.json()

def supa_delete(table: str, filters: dict):
    params = {k: f"eq.{v}" for k, v in filters.items()}
    r = requests.delete(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=supa_headers(),
        params=params,
        timeout=10
    )
    r.raise_for_status()
    return r.json()

# ── Security ──────────────────────────────────────────────────────────────────
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def require_api_key(key: str = Depends(api_key_header)):
    if key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return key

# ── Telegram ──────────────────────────────────────────────────────────────────
async def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(url, json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML"
            })
            logger.info(f"Telegram response: {r.status_code}")
        except Exception as e:
            logger.error(f"Telegram error: {e}")

# ── Price fetcher ─────────────────────────────────────────────────────────────
def get_price(symbol: str) -> float | None:
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
    })

    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d"
        r = session.get(url, timeout=10)
        data = r.json()
        meta = data["chart"]["result"][0]["meta"]
        price = meta.get("regularMarketPrice") or meta.get("previousClose")
        if price:
            return float(price)
    except Exception as e:
        logger.warning(f"Metodo 1 fallo para {symbol}: {e}")

    try:
        url = f"https://query2.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
        r = session.get(url, timeout=10)
        data = r.json()
        price = data["quoteResponse"]["result"][0]["regularMarketPrice"]
        if price:
            return float(price)
    except Exception as e:
        logger.warning(f"Metodo 2 fallo para {symbol}: {e}")

    return None

# Set para evitar alertas duplicadas en el mismo ciclo
_firing: set = set()

# ── Price checker ─────────────────────────────────────────────────────────────
async def check_prices():
    logger.info("Running price check...")
    try:
        tickers = supa_get("tickers", {"is_active": "eq.true", "select": "*"})
    except Exception as e:
        logger.error(f"Supabase read error: {e}")
        return

    if not tickers:
        logger.info("No active tickers to check.")
        return

    for ticker in tickers:
        symbol = ticker["symbol"]

        # Evitar doble disparo si ya se procesó en este ciclo
        if symbol in _firing:
            continue

        upper  = ticker.get("upper_limit")
        lower  = ticker.get("lower_limit")

        price = get_price(symbol)
        if not price:
            logger.warning(f"No data for {symbol}")
            continue

        logger.info(f"{symbol}: ${price:.2f} | upper={upper} lower={lower}")

        alert_type  = None
        limit_value = None

        if upper is not None and price >= float(upper):
            alert_type  = "upper"
            limit_value = upper
        elif lower is not None and price <= float(lower):
            alert_type  = "lower"
            limit_value = lower

        if alert_type:
            _firing.add(symbol)
            emoji = "🟢" if alert_type == "upper" else "🔴"
            direction = "superó el límite superior" if alert_type == "upper" else "cayó por debajo del límite inferior"
            msg = (
                f"{emoji} <b>ALERTA {symbol}</b>\n"
                f"Precio actual: <b>${price:.2f}</b>\n"
                f"El precio {direction}: ${float(limit_value):.2f}\n"
                f"🕐 {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
            )
            await send_telegram(msg)

            try:
                supa_post("alerts_log", {
                    "symbol": symbol,
                    "price": price,
                    "limit_type": alert_type,
                    "limit_value": float(limit_value)
                })
                supa_patch("tickers", {"id": ticker["id"]}, {"is_active": False})
                logger.info(f"Alert fired for {symbol}, deactivated.")
            except Exception as e:
                logger.error(f"Supabase write error: {e}")
            finally:
                _firing.discard(symbol)

# ── Scheduler ─────────────────────────────────────────────────────────────────
scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(check_prices, "interval", seconds=60, id="price_check")
    scheduler.start()
    logger.info("Scheduler started")
    yield
    scheduler.shutdown()

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="Stock Alerts", lifespan=lifespan)

# ── Models ────────────────────────────────────────────────────────────────────
class TickerCreate(BaseModel):
    symbol: str
    upper_limit: float | None = None
    lower_limit: float | None = None

class TickerUpdate(BaseModel):
    upper_limit: float | None = None
    lower_limit: float | None = None
    is_active: bool | None = None

# ── REST API ──────────────────────────────────────────────────────────────────
@app.get("/api/tickers", dependencies=[Depends(require_api_key)])
def get_tickers():
    return supa_get("tickers", {"select": "*", "order": "created_at.desc"})

@app.post("/api/tickers", dependencies=[Depends(require_api_key)])
def create_ticker(body: TickerCreate):
    if not body.upper_limit and not body.lower_limit:
        raise HTTPException(status_code=400, detail="At least one limit required")
    try:
        result = supa_post("tickers", {
            "symbol": body.symbol.upper().strip(),
            "upper_limit": body.upper_limit,
            "lower_limit": body.lower_limit,
            "is_active": True
        })
        return result[0] if isinstance(result, list) else result
    except Exception as e:
        logger.error(f"create_ticker error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/tickers/{ticker_id}", dependencies=[Depends(require_api_key)])
def update_ticker(ticker_id: str, body: TickerUpdate):
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    result = supa_patch("tickers", {"id": ticker_id}, updates)
    return result[0] if isinstance(result, list) else result

@app.delete("/api/tickers/{ticker_id}", dependencies=[Depends(require_api_key)])
def delete_ticker(ticker_id: str):
    supa_delete("tickers", {"id": ticker_id})
    return {"ok": True}

@app.get("/api/alerts", dependencies=[Depends(require_api_key)])
def get_alerts():
    return supa_get("alerts_log", {"select": "*", "order": "triggered_at.desc", "limit": "50"})

@app.post("/internal/check", dependencies=[Depends(require_api_key)])
async def trigger_check():
    await check_prices()
    return {"ok": True}

# ── Frontend ──────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def serve_ui(request: Request):
    with open("index.html", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())
