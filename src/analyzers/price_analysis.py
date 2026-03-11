from __future__ import annotations

import json
from datetime import datetime, timedelta, UTC
from pathlib import Path
from typing import Any

import httpx

from src.config import settings
from src.models.schemas import AnalysisBrief, RiskTag
from src.services.factory import get_market_data_service
from src.services.normalizers import normalize_token_context


CMC_QUOTES_URL = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"
COINGECKO_SEARCH_URL = "https://api.coingecko.com/api/v3/search"
COINGECKO_MARKETS_URL = "https://api.coingecko.com/api/v3/coins/markets"
QUOTE_CACHE_PATH = Path(__file__).resolve().parents[2] / "tmp" / "cmc_quote_cache.json"
CACHE_TTL_MINUTES = 15


class QuoteFetchError(RuntimeError):
    pass


def _load_quote_cache() -> dict[str, Any]:
    if QUOTE_CACHE_PATH.exists():
        try:
            return json.loads(QUOTE_CACHE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_quote_cache(cache: dict[str, Any]) -> None:
    QUOTE_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    QUOTE_CACHE_PATH.write_text(json.dumps(cache, indent=2), encoding="utf-8")


def _get_cached_quote(symbol: str) -> dict[str, Any] | None:
    cache = _load_quote_cache()
    item = cache.get(symbol.upper())
    if not isinstance(item, dict):
        return None
    fetched_at = item.get("fetched_at")
    if not fetched_at:
        return None
    try:
        ts = datetime.fromisoformat(fetched_at)
    except Exception:
        return None
    if datetime.now(UTC) - ts > timedelta(minutes=CACHE_TTL_MINUTES):
        return None
    return item.get("quote") if isinstance(item.get("quote"), dict) else None


def _cache_quote(symbol: str, quote: dict[str, Any]) -> None:
    cache = _load_quote_cache()
    cache[symbol.upper()] = {
        "fetched_at": datetime.now(UTC).isoformat(),
        "quote": quote,
    }
    _save_quote_cache(cache)


def _fetch_coingecko_quote(symbol: str) -> dict[str, Any] | None:
    sym = symbol.upper()
    with httpx.Client(timeout=20.0, follow_redirects=True) as client:
        search_resp = client.get(COINGECKO_SEARCH_URL, params={"query": sym})
        search_resp.raise_for_status()
        coins = (search_resp.json() or {}).get("coins") or []
        match = next((c for c in coins if str(c.get("symbol", "")).upper() == sym), None)
        if not match:
            return None
        market_resp = client.get(
            COINGECKO_MARKETS_URL,
            params={"vs_currency": "usd", "ids": match.get("id"), "price_change_percentage": "24h"},
        )
        market_resp.raise_for_status()
        items = market_resp.json() or []
        if not items:
            return None
        item = items[0]
    return {
        "name": item.get("name") or sym,
        "symbol": str(item.get("symbol") or sym).upper(),
        "slug": item.get("id") or "",
        "rank": int(item.get("market_cap_rank") or 0),
        "price": float(item.get("current_price") or 0),
        "market_cap": float(item.get("market_cap") or 0),
        "volume_24h": float(item.get("total_volume") or 0),
        "percent_change_24h": float(item.get("price_change_percentage_24h") or 0),
        "high_24h": float(item.get("high_24h") or 0),
        "low_24h": float(item.get("low_24h") or 0),
        "link": f"https://coinmarketcap.com/currencies/{(item.get('id') or '').replace(' ', '-')}/",
        "source": "CoinGecko",
    }


def _fetch_cmc_quote(symbol: str) -> dict[str, Any] | None:
    api_key = settings.coinmarketcap_api_key.strip()
    if not api_key:
        return None

    headers = {
        "Accept": "application/json",
        "X-CMC_PRO_API_KEY": api_key,
    }
    params = {"symbol": symbol.upper(), "convert": "USD"}

    last_exc: Exception | None = None
    payload: dict[str, Any] | None = None
    for _ in range(2):
        try:
            with httpx.Client(timeout=20.0, follow_redirects=True) as client:
                response = client.get(CMC_QUOTES_URL, params=params, headers=headers)
                response.raise_for_status()
                payload = response.json()
            break
        except Exception as exc:
            last_exc = exc
            payload = None
    if payload is None:
        cached = _get_cached_quote(symbol)
        if cached:
            return cached
        raise QuoteFetchError(f"CoinMarketCap quote fetch failed for {symbol}: {last_exc}") from last_exc

    data = payload.get("data") or {}
    entries = data.get(symbol.upper()) or []
    if not entries:
        return None

    entry = entries[0] or {}
    quote = (entry.get("quote") or {}).get("USD") or {}
    slug = entry.get("slug") or ""
    normalized = {
        "name": entry.get("name") or symbol.upper(),
        "symbol": entry.get("symbol") or symbol.upper(),
        "slug": slug,
        "rank": int(entry.get("cmc_rank") or 0),
        "price": float(quote.get("price") or 0),
        "market_cap": float(quote.get("market_cap") or 0),
        "volume_24h": float(quote.get("volume_24h") or 0),
        "percent_change_24h": float(quote.get("percent_change_24h") or 0),
        "high_24h": float(quote.get("high_24h") or 0),
        "low_24h": float(quote.get("low_24h") or 0),
        "link": f"https://coinmarketcap.com/currencies/{slug}/" if slug else "",
        "source": "CoinMarketCap",
    }
    _cache_quote(symbol, normalized)
    return normalized


def _fetch_market_quote(symbol: str) -> tuple[dict[str, Any] | None, str]:
    try:
        gecko = _fetch_coingecko_quote(symbol)
        if gecko:
            _cache_quote(symbol, gecko)
            return gecko, str(gecko.get("source") or "CoinGecko")
    except Exception:
        pass
    try:
        cmc = _fetch_cmc_quote(symbol)
        if cmc:
            return cmc, str(cmc.get("source") or "CoinMarketCap")
    except QuoteFetchError:
        pass
    cached = _get_cached_quote(symbol)
    if cached:
        return cached, str(cached.get("source") or "Cached quote")
    return None, ""


def analyze_price(symbol: str) -> AnalysisBrief:
    quote, source = _fetch_market_quote(symbol)

    if quote:
        arrow = "📈" if quote["percent_change_24h"] > 0 else "📉" if quote["percent_change_24h"] < 0 else "➖"
        return AnalysisBrief(
            entity=f"Price: {quote['symbol']}",
            quick_verdict=f"{quote['name']}|{quote['symbol']}|{quote['link']}|{quote['rank']}",
            signal_quality="High",
            top_risks=[] if source == "CoinGecko" else [f"Primary CoinGecko quote unavailable; using {source} market data."],
            why_it_matters=(
                f"{quote['price']}|{quote['percent_change_24h']}|{quote['high_24h']}|{quote['low_24h']}|"
                f"{quote['market_cap']}|{quote['volume_24h']}|{arrow}"
            ),
            what_to_watch_next=[],
            risk_tags=[RiskTag(name="Source", level="Low", note=source or "market quote")],
            conviction=None,
            beginner_note=None,
        )

    service = get_market_data_service()
    raw_context = service.get_token_context(symbol)
    ctx = normalize_token_context(raw_context)

    return AnalysisBrief(
        entity=f"Price: {ctx.symbol}",
        quick_verdict=f"{ctx.display_name}|{ctx.symbol}||0",
        signal_quality="Low" if ctx.price <= 0 else "Medium",
        top_risks=["Live market quote unavailable; showing internal fallback data."],
        why_it_matters=f"{ctx.price}|0|0|0|0|{ctx.liquidity}|➖",
        what_to_watch_next=[],
        risk_tags=[RiskTag(name="Source", level="Medium", note="Internal fallback")],
        conviction=None,
        beginner_note=None,
    )
