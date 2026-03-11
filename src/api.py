from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from time import perf_counter
import logging

from src.analyzers.audit_analysis import analyze_audit
from src.analyzers.market_watch import watch_today
from src.analyzers.meme_analysis import analyze_meme
from src.analyzers.signal_check import analyze_signal
from src.analyzers.token_analysis import analyze_token
from src.analyzers.wallet_analysis import analyze_wallet
from src.config import config_warnings, settings
from src.formatters.brief_formatter import format_brief
from src.services.api_guard import enforce_api_guard, guard_status
from src.services.runtime_report import build_runtime_meta, live_service
from src.utils.parsing import normalize_token_input, normalize_wallet_input
from src.utils.validation import looks_like_wallet_address

app = FastAPI(title="Bibipilot API", version="0.2.1")
logger = logging.getLogger("bibipilot.api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["X-API-Key"],
)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.on_event("startup")
def startup_checks() -> None:
    for warning in config_warnings():
        logger.warning("startup_config_warning warning=%s", warning)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    if not settings.api_request_logging_enabled:
        return await call_next(request)
    started = perf_counter()
    response = None
    try:
        response = await call_next(request)
        return response
    finally:
        duration_ms = (perf_counter() - started) * 1000
        logger.info(
            "request method=%s path=%s status=%s duration_ms=%.1f client=%s",
            request.method,
            request.url.path,
            getattr(response, "status_code", "error"),
            duration_ms,
            getattr(request.client, "host", "unknown"),
        )


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
    payload: dict = {"status": "ok", "mode": settings.app_mode, "guard": guard_status(), "config_warnings": config_warnings()}
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
def brief_token(request: Request, _: None = Depends(enforce_api_guard), symbol: str = Query(..., min_length=1, max_length=20, description="Token symbol, e.g. BNB")) -> BriefResponse:
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
def brief_signal(request: Request, _: None = Depends(enforce_api_guard), token: str = Query(..., min_length=1, max_length=20, description="Token symbol, e.g. DOGE")) -> BriefResponse:
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
def brief_audit(request: Request, _: None = Depends(enforce_api_guard), symbol: str = Query(..., min_length=1, max_length=20, description="Token symbol, e.g. BNB")) -> BriefResponse:
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
def brief_meme(request: Request, _: None = Depends(enforce_api_guard), symbol: str = Query(..., min_length=1, max_length=20, description="Token symbol, e.g. DOGE")) -> BriefResponse:
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
def brief_wallet(request: Request, _: None = Depends(enforce_api_guard), address: str = Query(..., min_length=12, max_length=128, description="Wallet address starting with 0x")) -> BriefResponse:
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
