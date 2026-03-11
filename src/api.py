from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from pydantic import BaseModel

from src.analyzers.audit_analysis import analyze_audit
from src.analyzers.market_watch import watch_today
from src.analyzers.meme_analysis import analyze_meme
from src.analyzers.signal_check import analyze_signal
from src.analyzers.token_analysis import analyze_token
from src.analyzers.wallet_analysis import analyze_wallet
from src.config import settings
from src.formatters.brief_formatter import format_brief
from src.services.api_guard import enforce_api_guard, guard_status
from src.services.runtime_report import build_runtime_meta, live_service
from src.utils.parsing import normalize_token_input, normalize_wallet_input
from src.utils.validation import looks_like_wallet_address

app = FastAPI(title="Bibipilot API", version="0.2.1")


class BriefResponse(BaseModel):
    command: str
    entity: str
    mode: str
    rendered: str
    warning: str | None = None
    runtime_state: str | None = None
    runtime: dict | None = None


@app.get("/health")
def health(request: Request, _: None = Depends(enforce_api_guard)) -> dict:
    payload: dict = {"status": "ok", "mode": settings.app_mode, "guard": guard_status()}
    if settings.app_mode == "live":
        payload["runtime"] = live_service().healthcheck()
    return payload


@app.get("/runtime/report")
def runtime_report(request: Request, _: None = Depends(enforce_api_guard)) -> dict:
    if settings.app_mode != "live":
        return {
            "status": "ok",
            "mode": settings.app_mode,
            "runtime": build_runtime_meta("runtime-report", ""),
        }
    health = live_service().healthcheck()
    return {
        "status": "ok",
        "mode": settings.app_mode,
        "runtime": build_runtime_meta("runtime-report", "", health=health),
        "health": health,
    }


@app.get("/brief/token", response_model=BriefResponse)
def brief_token(request: Request, _: None = Depends(enforce_api_guard), symbol: str = Query(..., min_length=1, description="Token symbol, e.g. BNB")) -> BriefResponse:
    normalized = normalize_token_input(symbol)
    brief = analyze_token(normalized)
    health = live_service().healthcheck() if settings.app_mode == "live" else None
    runtime = build_runtime_meta("token", normalized, health=health)
    return BriefResponse(
        command="token",
        entity=normalized,
        mode=settings.app_mode,
        rendered=format_brief(brief),
        warning=runtime.get("warning") or _mode_warning(),
        runtime_state=runtime.get("state"),
        runtime=runtime,
    )


@app.get("/brief/signal", response_model=BriefResponse)
def brief_signal(request: Request, _: None = Depends(enforce_api_guard), token: str = Query(..., min_length=1, description="Token symbol, e.g. DOGE")) -> BriefResponse:
    normalized = normalize_token_input(token)
    brief = analyze_signal(normalized)
    health = live_service().healthcheck() if settings.app_mode == "live" else None
    runtime = build_runtime_meta("signal", normalized, health=health)
    return BriefResponse(
        command="signal",
        entity=normalized,
        mode=settings.app_mode,
        rendered=format_brief(brief),
        warning=runtime.get("warning") or _mode_warning(),
        runtime_state=runtime.get("state"),
        runtime=runtime,
    )


@app.get("/brief/audit", response_model=BriefResponse)
def brief_audit(request: Request, _: None = Depends(enforce_api_guard), symbol: str = Query(..., min_length=1, description="Token symbol, e.g. BNB")) -> BriefResponse:
    normalized = normalize_token_input(symbol)
    brief = analyze_audit(normalized)
    health = live_service().healthcheck() if settings.app_mode == "live" else None
    runtime = build_runtime_meta("audit", normalized, health=health)
    return BriefResponse(
        command="audit",
        entity=normalized,
        mode=settings.app_mode,
        rendered=format_brief(brief),
        warning=runtime.get("warning") or _mode_warning(),
        runtime_state=runtime.get("state"),
        runtime=runtime,
    )


@app.get("/brief/meme", response_model=BriefResponse)
def brief_meme(request: Request, _: None = Depends(enforce_api_guard), symbol: str = Query(..., min_length=1, description="Token symbol, e.g. DOGE")) -> BriefResponse:
    normalized = normalize_token_input(symbol)
    brief = analyze_meme(normalized)
    health = live_service().healthcheck() if settings.app_mode == "live" else None
    runtime = build_runtime_meta("meme", normalized, health=health)
    return BriefResponse(
        command="meme",
        entity=normalized,
        mode=settings.app_mode,
        rendered=format_brief(brief),
        warning=runtime.get("warning") or _mode_warning(),
        runtime_state=runtime.get("state"),
        runtime=runtime,
    )


@app.get("/brief/wallet", response_model=BriefResponse)
def brief_wallet(request: Request, _: None = Depends(enforce_api_guard), address: str = Query(..., min_length=12, description="Wallet address starting with 0x")) -> BriefResponse:
    if not looks_like_wallet_address(address):
        raise HTTPException(status_code=400, detail="Wallet address must start with 0x and look valid.")
    normalized = normalize_wallet_input(address)
    brief = analyze_wallet(normalized)
    health = live_service().healthcheck() if settings.app_mode == "live" else None
    runtime = build_runtime_meta("wallet", normalized, health=health)
    return BriefResponse(
        command="wallet",
        entity=normalized,
        mode=settings.app_mode,
        rendered=format_brief(brief),
        warning=runtime.get("warning") or _mode_warning(),
        runtime_state=runtime.get("state"),
        runtime=runtime,
    )


@app.get("/brief/watchtoday", response_model=BriefResponse)
def brief_watchtoday(request: Request, _: None = Depends(enforce_api_guard)) -> BriefResponse:
    brief = watch_today()
    health = live_service().healthcheck() if settings.app_mode == "live" else None
    runtime = build_runtime_meta("watchtoday", "market", health=health)
    return BriefResponse(
        command="watchtoday",
        entity="market",
        mode=settings.app_mode,
        rendered=format_brief(brief),
        warning=runtime.get("warning") or _mode_warning(),
        runtime_state=runtime.get("state"),
        runtime=runtime,
    )


def _mode_warning() -> str | None:
    if settings.app_mode == "mock":
        return "Running in mock mode; outputs are scaffold/demo quality, not live market calls."
    return None
