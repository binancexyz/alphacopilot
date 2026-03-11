from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from src.analyzers.audit_analysis import analyze_audit
from src.analyzers.market_watch import watch_today
from src.analyzers.meme_analysis import analyze_meme
from src.analyzers.signal_check import analyze_signal
from src.analyzers.token_analysis import analyze_token
from src.analyzers.wallet_analysis import analyze_wallet
from src.config import settings
from src.formatters.brief_formatter import format_brief
from src.services.live_service import LiveMarketDataService
from src.utils.parsing import normalize_token_input, normalize_wallet_input
from src.utils.validation import looks_like_wallet_address

app = FastAPI(title="Bibipilot API", version="0.2.1")


class BriefResponse(BaseModel):
    command: str
    entity: str
    mode: str
    rendered: str
    warning: str | None = None


@app.get("/health")
def health() -> dict:
    payload: dict = {"status": "ok", "mode": settings.app_mode}
    if settings.app_mode == "live":
        live = LiveMarketDataService(
            base_url=settings.binance_skills_base_url,
            api_key=settings.binance_api_key,
            api_secret=settings.binance_api_secret,
        )
        payload["runtime"] = live.healthcheck()
    return payload


@app.get("/brief/token", response_model=BriefResponse)
def brief_token(symbol: str = Query(..., min_length=1, description="Token symbol, e.g. BNB")) -> BriefResponse:
    normalized = normalize_token_input(symbol)
    brief = analyze_token(normalized)
    return BriefResponse(
        command="token",
        entity=normalized,
        mode=settings.app_mode,
        rendered=format_brief(brief),
        warning=_mode_warning(),
    )


@app.get("/brief/signal", response_model=BriefResponse)
def brief_signal(token: str = Query(..., min_length=1, description="Token symbol, e.g. DOGE")) -> BriefResponse:
    normalized = normalize_token_input(token)
    brief = analyze_signal(normalized)
    return BriefResponse(
        command="signal",
        entity=normalized,
        mode=settings.app_mode,
        rendered=format_brief(brief),
        warning=_mode_warning(),
    )


@app.get("/brief/audit", response_model=BriefResponse)
def brief_audit(symbol: str = Query(..., min_length=1, description="Token symbol, e.g. BNB")) -> BriefResponse:
    normalized = normalize_token_input(symbol)
    brief = analyze_audit(normalized)
    return BriefResponse(
        command="audit",
        entity=normalized,
        mode=settings.app_mode,
        rendered=format_brief(brief),
        warning=_mode_warning(),
    )


@app.get("/brief/meme", response_model=BriefResponse)
def brief_meme(symbol: str = Query(..., min_length=1, description="Token symbol, e.g. DOGE")) -> BriefResponse:
    normalized = normalize_token_input(symbol)
    brief = analyze_meme(normalized)
    return BriefResponse(
        command="meme",
        entity=normalized,
        mode=settings.app_mode,
        rendered=format_brief(brief),
        warning=_mode_warning(),
    )


@app.get("/brief/wallet", response_model=BriefResponse)
def brief_wallet(address: str = Query(..., min_length=12, description="Wallet address starting with 0x")) -> BriefResponse:
    if not looks_like_wallet_address(address):
        raise HTTPException(status_code=400, detail="Wallet address must start with 0x and look valid.")
    normalized = normalize_wallet_input(address)
    brief = analyze_wallet(normalized)
    return BriefResponse(
        command="wallet",
        entity=normalized,
        mode=settings.app_mode,
        rendered=format_brief(brief),
        warning=_mode_warning(),
    )


@app.get("/brief/watchtoday", response_model=BriefResponse)
def brief_watchtoday() -> BriefResponse:
    brief = watch_today()
    return BriefResponse(
        command="watchtoday",
        entity="market",
        mode=settings.app_mode,
        rendered=format_brief(brief),
        warning=_mode_warning(),
    )


def _mode_warning() -> str | None:
    if settings.app_mode == "mock":
        return "Running in mock mode; outputs are scaffold/demo quality, not live market calls."
    return None
