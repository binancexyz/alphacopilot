from __future__ import annotations

import json
from datetime import datetime, timedelta, UTC
from pathlib import Path
from typing import Any

from src.config import settings
from src.models.schemas import AnalysisBrief, RiskTag
from src.services.factory import get_market_data_service
from src.services.normalizers import normalize_token_context


BINANCE_SPOT_BASE_URL = "https://api.binance.com"
BINANCE_SPOT_MARKET_DATA_URL = "https://data-api.binance.vision"
BINANCE_EXCHANGE_INFO_URL = "/api/v3/exchangeInfo"
BINANCE_TICKER_24HR_URL = "/api/v3/ticker/24hr"
BINANCE_BOOK_TICKER_URL = "/api/v3/ticker/bookTicker"
BINANCE_AVG_PRICE_URL = "/api/v3/avgPrice"
CMC_QUOTES_URL = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"
COINGECKO_SEARCH_URL = "https://api.coingecko.com/api/v3/search"
COINGECKO_MARKETS_URL = "https://api.coingecko.com/api/v3/coins/markets"
QUOTE_CACHE_PATH = Path(__file__).resolve().parents[2] / "tmp" / "cmc_quote_cache.json"
CACHE_TTL_MINUTES = 15


class QuoteFetchError(RuntimeError):
    pass


def _httpx_client(*args, **kwargs):
    try:
        import httpx  # type: ignore
    except ModuleNotFoundError as exc:
        raise QuoteFetchError("httpx is required for external market quote fetches.") from exc
    return httpx.Client(*args, **kwargs)


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


def _fetch_binance_spot_quote(symbol: str) -> dict[str, Any] | None:
    base = symbol.upper()
    candidate_pairs = [f"{base}USDT", f"{base}BUSD", f"{base}USDC"]

    with _httpx_client(timeout=20.0, follow_redirects=True) as client:
        chosen_symbol = None
        exchange_symbols: dict[str, Any] = {}
        for root in (BINANCE_SPOT_MARKET_DATA_URL, BINANCE_SPOT_BASE_URL):
            try:
                resp = client.get(root.rstrip("/") + BINANCE_EXCHANGE_INFO_URL, params={"symbols": json.dumps(candidate_pairs)})
                resp.raise_for_status()
                payload = resp.json() or {}
                for item in payload.get("symbols", []) or []:
                    sym = str(item.get("symbol") or "")
                    exchange_symbols[sym] = item
                chosen_symbol = next((pair for pair in candidate_pairs if pair in exchange_symbols and exchange_symbols[pair].get("status") == "TRADING"), None)
                if chosen_symbol:
                    break
            except Exception:
                continue

        if not chosen_symbol:
            return None

        ticker = None
        book = None
        avg = None
        for root in (BINANCE_SPOT_MARKET_DATA_URL, BINANCE_SPOT_BASE_URL):
            try:
                ticker_resp = client.get(root.rstrip("/") + BINANCE_TICKER_24HR_URL, params={"symbol": chosen_symbol})
                ticker_resp.raise_for_status()
                ticker = ticker_resp.json() or {}
                book_resp = client.get(root.rstrip("/") + BINANCE_BOOK_TICKER_URL, params={"symbol": chosen_symbol})
                book_resp.raise_for_status()
                book = book_resp.json() or {}
                avg_resp = client.get(root.rstrip("/") + BINANCE_AVG_PRICE_URL, params={"symbol": chosen_symbol})
                avg_resp.raise_for_status()
                avg = avg_resp.json() or {}
                break
            except Exception:
                continue

    if not ticker:
        return None

    weighted_price = float(ticker.get("weightedAvgPrice") or 0)
    avg_price = float((avg or {}).get("price") or 0)
    bid_price = float((book or {}).get("bidPrice") or 0)
    ask_price = float((book or {}).get("askPrice") or 0)
    spread_pct = 0.0
    if bid_price > 0 and ask_price > 0 and ask_price >= bid_price:
        midpoint = (bid_price + ask_price) / 2
        if midpoint > 0:
            spread_pct = ((ask_price - bid_price) / midpoint) * 100

    return {
        "name": base,
        "symbol": base,
        "slug": chosen_symbol.lower(),
        "rank": 0,
        "price": float(ticker.get("lastPrice") or 0),
        "market_cap": 0.0,
        "volume_24h": float(ticker.get("quoteVolume") or 0),
        "percent_change_24h": float(ticker.get("priceChangePercent") or 0),
        "high_24h": float(ticker.get("highPrice") or 0),
        "low_24h": float(ticker.get("lowPrice") or 0),
        "link": f"https://www.binance.com/en/trade/{base}_USDT" if chosen_symbol.endswith("USDT") else "",
        "source": "Binance Spot",
        "exchange_symbol": chosen_symbol,
        "weighted_avg_price": weighted_price,
        "avg_price": avg_price,
        "bid_price": bid_price,
        "ask_price": ask_price,
        "spread_pct": spread_pct,
    }


def _fetch_coingecko_quote(symbol: str) -> dict[str, Any] | None:
    sym = symbol.upper()
    with _httpx_client(timeout=20.0, follow_redirects=True) as client:
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
            with _httpx_client(timeout=20.0, follow_redirects=True) as client:
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
        binance = _fetch_binance_spot_quote(symbol)
        if binance:
            _cache_quote(symbol, binance)
            return binance, str(binance.get("source") or "Binance Spot")
    except Exception:
        pass
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
        top_risks: list[str] = []
        if source == "Binance Spot":
            spread_pct = float(quote.get("spread_pct") or 0)
            if spread_pct >= 0.5:
                top_risks.append(f"Order-book spread is relatively wide at {spread_pct:.2f}%, so execution quality may be less clean.")
            elif spread_pct > 0:
                top_risks.append(f"Using Binance Spot market data ({quote.get('exchange_symbol') or quote['symbol']}); spread currently reads around {spread_pct:.2f}%.")
            else:
                top_risks.append(f"Using Binance Spot market data ({quote.get('exchange_symbol') or quote['symbol']}).")
        elif source != "CoinGecko":
            top_risks.append(f"Primary Binance Spot/CoinGecko quote unavailable; using {source} market data.")
        return AnalysisBrief(
            entity=f"Price: {quote['symbol']}",
            quick_verdict=f"{quote['name']}|{quote['symbol']}|{quote['link']}|{quote['rank']}",
            signal_quality="High" if source == "Binance Spot" else "Medium",
            top_risks=top_risks,
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
