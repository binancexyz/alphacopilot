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
    return {
        "name": entry.get("name") or symbol.upper(),
        "symbol": entry.get("symbol") or symbol.upper(),
        "price": float(quote.get("price") or 0),
        "market_cap": float(quote.get("market_cap") or 0),
        "volume_24h": float(quote.get("volume_24h") or 0),
        "percent_change_24h": float(quote.get("percent_change_24h") or 0),
    }


def analyze_price(symbol: str) -> AnalysisBrief:
    cmc = _fetch_cmc_quote(symbol)
    if cmc:
        price_value = f"${cmc['price']:,.2f}" if cmc["price"] > 0 else "Price unavailable"
        change_24h = cmc["percent_change_24h"]
        market_cap = cmc["market_cap"]
        volume_24h = cmc["volume_24h"]

        if cmc["price"] > 0:
            quick_verdict = f"{cmc['symbol']} price is coming from CoinMarketCap and looks clean enough for a direct market check right now."
            quality = "High"
            conviction = "Medium"
        else:
            quick_verdict = f"{cmc['symbol']} quote lookup succeeded, but the returned price is still incomplete."
            quality = "Low"
            conviction = "Low"

        direction = "up" if change_24h > 0 else "down" if change_24h < 0 else "flat"
        top_risks = [
            "A clean price quote still does not tell you whether the broader setup is strong, crowded, or weakening.",
        ]
        why_it_matters = (
            f"Current price: {price_value}. 24h change is {change_24h:+.2f}%, market cap is ${market_cap:,.0f}, "
            f"and 24h volume is ${volume_24h:,.0f}."
        )
        what_to_watch_next = [
            f"whether the {direction} 24h move extends or mean-reverts",
            "whether volume stays supportive around the current price zone",
            "whether the token still looks strong once price is compared with broader signal and risk context",
        ]
        risk_tags = [
            RiskTag(name="Price Source", level="Low", note="CoinMarketCap quote"),
            RiskTag(name="24h Change", level="Low", note=f"{change_24h:+.2f}%"),
            RiskTag(name="24h Volume", level="Low", note=f"${volume_24h:,.0f}"),
        ]
        return AnalysisBrief(
            entity=f"Price: {cmc['symbol']}",
            quick_verdict=quick_verdict,
            signal_quality=quality,
            top_risks=top_risks,
            why_it_matters=why_it_matters,
            what_to_watch_next=what_to_watch_next,
            risk_tags=risk_tags,
            conviction=conviction,
            beginner_note="A good quote is useful, but price alone is never the whole thesis.",
        )

    service = get_market_data_service()
    raw_context = service.get_token_context(symbol)
    ctx = normalize_token_context(raw_context)

    price_value = f"${ctx.price:,.2f}" if ctx.price > 0 else "Price unavailable"
    liquidity_note = (
        f"Liquidity context is visible at roughly ${ctx.liquidity:,.0f}." if ctx.liquidity > 0 else "Liquidity context is missing or weak."
    )

    if ctx.price > 0 and ctx.liquidity > 0:
        quick_verdict = f"{ctx.display_name} price is available from the internal token context, with enough surrounding market detail to make a quick read usable."
        quality = "Medium"
        conviction = "Low"
    elif ctx.price > 0:
        quick_verdict = f"{ctx.display_name} price is available, but supporting market context is still thinner than ideal."
        quality = "Medium"
        conviction = "Low"
    else:
        quick_verdict = f"{ctx.display_name} does not currently have reliable price detail in this fallback path, so treat any quick read cautiously."
        quality = "Low"
        conviction = "Low"

    top_risks = []
    if ctx.price <= 0:
        top_risks.append("Price data is missing or not clean enough to trust fully.")
    if ctx.liquidity <= 0:
        top_risks.append("Liquidity context is limited, which weakens a simple price read.")
    if not top_risks:
        top_risks.append("A visible price alone does not tell you whether the setup is strong, crowded, or weakening.")

    why_it_matters = f"Current price: {price_value}. {liquidity_note}"
    if ctx.market_rank_context:
        why_it_matters += f" {ctx.market_rank_context}"

    what_to_watch_next = [
        "whether price context stays available and consistent",
        "whether liquidity remains supportive around the current level",
        "whether the token setup strengthens or weakens beyond the raw price print",
    ]

    risk_tags: list[RiskTag] = []
    risk_tags.append(RiskTag(name="Price Confidence", level="Low" if ctx.price > 0 else "High", note=price_value))
    risk_tags.append(
        RiskTag(
            name="Liquidity Context",
            level="Low" if ctx.liquidity > 0 else "Medium",
            note=f"~${ctx.liquidity:,.0f} liquidity" if ctx.liquidity > 0 else "Liquidity detail unavailable",
        )
    )

    return AnalysisBrief(
        entity=f"Price: {ctx.symbol}",
        quick_verdict=quick_verdict,
        signal_quality=quality,
        top_risks=top_risks,
        why_it_matters=why_it_matters,
        what_to_watch_next=what_to_watch_next,
        risk_tags=risk_tags,
        conviction=conviction,
        beginner_note="Price is only one layer of the story. Context, liquidity, and risk still matter.",
    )
