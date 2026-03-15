from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from time import perf_counter
import logging

from src.analyzers.alpha_analysis import analyze_alpha
from src.analyzers.audit_analysis import analyze_audit
from src.analyzers.brief_analysis import analyze_brief
from src.analyzers.futures_analysis import analyze_futures
from src.analyzers.market_watch import watch_today
from src.analyzers.portfolio_analysis import analyze_portfolio
from src.analyzers.signal_check import analyze_signal
from src.analyzers.token_analysis import analyze_token
from src.analyzers.wallet_analysis import analyze_wallet
from src.config import config_errors, config_warnings, settings
from src.formatters.brief_formatter import format_brief
from src.services.api_guard import enforce_api_guard, guard_status
from src.services.runtime_report import apply_runtime_meta, build_runtime_meta, live_service
from src.utils.parsing import normalize_token_input, normalize_wallet_input
from src.utils.validation import looks_like_wallet_address
from src.version import __version__

logger = logging.getLogger("bibipilot.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    for warning in config_warnings():
        logger.warning("startup_config_warning warning=%s", warning)
    errors = config_errors("api")
    if errors:
        for error in errors:
            logger.error("startup_config_error error=%s", error)
        raise RuntimeError("Invalid production configuration: " + " | ".join(errors))
    yield


app = FastAPI(title="Bibipilot API", version=__version__, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=[settings.api_auth_header],
)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Content-Security-Policy"] = "default-src 'none'"
    return response


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


def _brief_response(command: str, entity: str, brief) -> BriefResponse:
    health = live_service().healthcheck() if settings.app_mode == "live" else None
    runtime = build_runtime_meta(command, entity, health=health)
    brief = apply_runtime_meta(brief, runtime)
    return BriefResponse(
        command=command,
        entity=entity,
        mode=settings.app_mode,
        rendered=format_brief(brief),
        warning=runtime.get("warning") or _mode_warning(),
        runtime_state=runtime.get("state"),
        runtime=runtime,
    )


@app.get("/brief", response_model=BriefResponse)
def brief(request: Request, _: None = Depends(enforce_api_guard), symbol: str = Query(..., min_length=1, max_length=20, description="Token symbol, e.g. BNB"), deep: bool = Query(False, description="Use deeper asset judgment mode")) -> BriefResponse:
    normalized = normalize_token_input(symbol)
    analysis = analyze_token(normalized) if deep else analyze_brief(normalized)
    command = "token" if deep else "brief"
    return _brief_response(command, normalized, analysis)


@app.get("/signal", response_model=BriefResponse)
def signal(request: Request, _: None = Depends(enforce_api_guard), token: str = Query(..., min_length=1, max_length=20, description="Token symbol, e.g. DOGE")) -> BriefResponse:
    normalized = normalize_token_input(token)
    return _brief_response("signal", normalized, analyze_signal(normalized))


@app.get("/audit", response_model=BriefResponse)
def audit(request: Request, _: None = Depends(enforce_api_guard), symbol: str = Query(..., min_length=1, max_length=20, description="Token symbol, e.g. BNB")) -> BriefResponse:
    normalized = normalize_token_input(symbol)
    return _brief_response("audit", normalized, analyze_audit(normalized))


@app.get("/holdings", response_model=BriefResponse)
def holdings(request: Request, _: None = Depends(enforce_api_guard), address: str | None = Query(None, min_length=12, max_length=128, description="Optional wallet address starting with 0x")) -> BriefResponse:
    if address:
        if not looks_like_wallet_address(address):
            raise HTTPException(status_code=400, detail="Wallet address must start with 0x and look valid.")
        normalized = normalize_wallet_input(address)
        return _brief_response("holdings", normalized, analyze_wallet(normalized))
    return _brief_response("holdings", "portfolio", analyze_portfolio())


@app.get("/watchtoday", response_model=BriefResponse)
def watchtoday(request: Request, _: None = Depends(enforce_api_guard)) -> BriefResponse:
    return _brief_response("watchtoday", "market", watch_today())


@app.get("/alpha", response_model=BriefResponse)
def alpha(request: Request, _: None = Depends(enforce_api_guard), symbol: str | None = Query(None, min_length=1, max_length=20, description="Optional token symbol, e.g. BNB")) -> BriefResponse:
    normalized = normalize_token_input(symbol) if symbol else ""
    svc = live_service()
    context = svc.get_alpha_context(normalized)
    brief = analyze_alpha(normalized or None, context)
    entity = normalized or "binance-alpha"
    runtime = build_runtime_meta("alpha", entity)
    brief = apply_runtime_meta(brief, runtime)
    warning = brief.runtime_warning or runtime.get("warning") or _mode_warning()
    return BriefResponse(
        command="alpha",
        entity=entity,
        mode=settings.app_mode,
        rendered=format_brief(brief),
        warning=warning,
        runtime_state=brief.runtime_state or runtime.get("state"),
        runtime=runtime,
    )


@app.get("/futures", response_model=BriefResponse)
def futures(request: Request, _: None = Depends(enforce_api_guard), symbol: str = Query(..., min_length=1, max_length=20, description="Token symbol, e.g. BTC")) -> BriefResponse:
    normalized = normalize_token_input(symbol)
    svc = live_service()
    context = svc.get_futures_context(normalized)
    brief = analyze_futures(normalized, context)
    runtime = build_runtime_meta("futures", normalized)
    brief = apply_runtime_meta(brief, runtime)
    warning = brief.runtime_warning or runtime.get("warning") or _mode_warning()
    return BriefResponse(
        command="futures",
        entity=normalized,
        mode=settings.app_mode,
        rendered=format_brief(brief),
        warning=warning,
        runtime_state=brief.runtime_state or runtime.get("state"),
        runtime=runtime,
    )

def _mode_warning() -> str | None:
    if settings.app_mode == "mock":
        return "Running in mock mode; outputs are scaffold/demo quality, not live market calls."
    return None
