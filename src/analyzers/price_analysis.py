from __future__ import annotations

from typing import Any

import httpx

from src.config import settings
from src.models.schemas import AnalysisBrief, RiskTag
from src.services.factory import get_market_data_service
from src.services.normalizers import normalize_token_context


CMC_QUOTES_URL = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"


def _fetch_cmc_quote(symbol: str) -> dict[str, Any] | None:
    api_key = settings.coinmarketcap_api_key.strip()
    if not api_key:
        return None

    headers = {
        "Accept": "application/json",
        "X-CMC_PRO_API_KEY": api_key,
    }
    params = {"symbol": symbol.upper(), "convert": "USD"}

    with httpx.Client(timeout=20.0, follow_redirects=True) as client:
        response = client.get(CMC_QUOTES_URL, params=params, headers=headers)
        response.raise_for_status()
        payload = response.json()

    data = payload.get("data") or {}
    entries = data.get(symbol.upper()) or []
    if not entries:
        return None

    entry = entries[0] or {}
    quote = (entry.get("quote") or {}).get("USD") or {}
    slug = entry.get("slug") or ""
    return {
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
    }


def analyze_price(symbol: str) -> AnalysisBrief:
    cmc = _fetch_cmc_quote(symbol)
    if cmc:
        arrow = "📈" if cmc["percent_change_24h"] > 0 else "📉" if cmc["percent_change_24h"] < 0 else "➖"
        return AnalysisBrief(
            entity=f"Price: {cmc['symbol']}",
            quick_verdict=f"{cmc['name']}|{cmc['symbol']}|{cmc['link']}|{cmc['rank']}",
            signal_quality="High",
            top_risks=[],
            why_it_matters=(
                f"{cmc['price']}|{cmc['percent_change_24h']}|{cmc['high_24h']}|{cmc['low_24h']}|"
                f"{cmc['market_cap']}|{cmc['volume_24h']}|{arrow}"
            ),
            what_to_watch_next=[],
            risk_tags=[RiskTag(name="Source", level="Low", note="CoinMarketCap")],
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
        top_risks=[],
        why_it_matters=f"{ctx.price}|0|0|0|0|{ctx.liquidity}|➖",
        what_to_watch_next=[],
        risk_tags=[RiskTag(name="Source", level="Medium", note="Internal fallback")],
        conviction=None,
        beginner_note=None,
    )
