from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from src.analyzers.market_watch import watch_today
from src.analyzers.signal_check import analyze_signal
from src.analyzers.token_analysis import analyze_token
from src.analyzers.wallet_analysis import analyze_wallet
from src.formatters.brief_formatter import format_brief
from src.utils.parsing import normalize_token_input, normalize_wallet_input
from src.utils.validation import looks_like_wallet_address

app = FastAPI(title="Binance Alpha Copilot API", version="0.2.0")


class BriefResponse(BaseModel):
    command: str
    entity: str
    rendered: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/brief/token", response_model=BriefResponse)
def brief_token(symbol: str = Query(..., min_length=1, description="Token symbol, e.g. BNB")) -> BriefResponse:
    normalized = normalize_token_input(symbol)
    brief = analyze_token(normalized)
    return BriefResponse(command="token", entity=normalized, rendered=format_brief(brief))


@app.get("/brief/signal", response_model=BriefResponse)
def brief_signal(token: str = Query(..., min_length=1, description="Token symbol, e.g. DOGE")) -> BriefResponse:
    normalized = normalize_token_input(token)
    brief = analyze_signal(normalized)
    return BriefResponse(command="signal", entity=normalized, rendered=format_brief(brief))


@app.get("/brief/wallet", response_model=BriefResponse)
def brief_wallet(address: str = Query(..., min_length=12, description="Wallet address starting with 0x")) -> BriefResponse:
    if not looks_like_wallet_address(address):
        raise HTTPException(status_code=400, detail="Wallet address must start with 0x and look valid.")
    normalized = normalize_wallet_input(address)
    brief = analyze_wallet(normalized)
    return BriefResponse(command="wallet", entity=normalized, rendered=format_brief(brief))


@app.get("/brief/watchtoday", response_model=BriefResponse)
def brief_watchtoday() -> BriefResponse:
    brief = watch_today()
    return BriefResponse(command="watchtoday", entity="market", rendered=format_brief(brief))
