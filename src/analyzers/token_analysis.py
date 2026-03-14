from __future__ import annotations

from src.analyzers.judgment_helpers import append_posture_note_to_brief
from src.analyzers.price_analysis import _fetch_market_quote
from src.analyzers.token_live_brief import build_token_brief
from src.models.schemas import AnalysisBrief, RiskTag
from src.services.factory import get_market_data_service
from src.services.normalizers import normalize_token_context


def analyze_token(symbol: str) -> AnalysisBrief:
    service = get_market_data_service()
    raw_context = service.get_token_context(symbol)
    token_context = normalize_token_context(raw_context)

    try:
        quote, source = _fetch_market_quote(symbol)
    except Exception:
        quote, source = None, ""

    if quote:
        if float(quote.get("price") or 0) > 0 and token_context.price <= 0:
            token_context.price = float(quote.get("price") or 0)
        if float(quote.get("volume_24h") or 0) > 0 and token_context.liquidity <= 0:
            token_context.liquidity = float(quote.get("volume_24h") or 0)
        if float(quote.get("volume_24h") or 0) > 0 and token_context.volume_24h <= 0:
            token_context.volume_24h = float(quote.get("volume_24h") or 0)
        if float(quote.get("market_cap") or 0) > 0 and token_context.market_cap <= 0:
            token_context.market_cap = float(quote.get("market_cap") or 0)
        if quote.get("percent_change_24h") is not None:
            token_context.pct_change_24h = float(quote.get("percent_change_24h") or 0)
        if float(quote.get("high_24h") or 0) > 0 and token_context.price_high_24h <= 0:
            token_context.price_high_24h = float(quote.get("high_24h") or 0)
        if float(quote.get("low_24h") or 0) > 0 and token_context.price_low_24h <= 0:
            token_context.price_low_24h = float(quote.get("low_24h") or 0)

    brief = build_token_brief(token_context)

    if quote:
        price = float(quote.get("price") or 0)
        change = float(quote.get("percent_change_24h") or 0)
        rank = int(quote.get("rank") or 0)
        brief.risk_tags.insert(0, RiskTag(name="Header Market", level="Info", note=f"{price}|{change}|{rank}"))

    if quote and source == "Binance Spot":
        pair = str(quote.get("exchange_symbol") or symbol)
        spread = float(quote.get("spread_pct") or 0)
        change = float(quote.get("percent_change_24h") or 0)
        note = f"{pair} | 24h {change:+.2f}%"
        if spread > 0:
            note += f" | spread {spread:.2f}%"
        brief.risk_tags.insert(1, RiskTag(name="Binance Spot", level="Low" if spread < 0.5 else "Medium", note=note))
        if spread >= 0.5:
            brief.top_risks.insert(0, f"Binance Spot spread is relatively wide at {spread:.2f}%, so exchange execution context is less clean than the headline move suggests.")
        elif token_context.signal_status == "unmatched":
            if not any("no matched smart-money signal" in risk.lower() for risk in brief.top_risks):
                brief.top_risks.insert(0, f"Binance Spot price is live via {pair}, but there is still no matched smart-money signal on the board.")
        elif brief.why_it_matters:
            brief.why_it_matters += f" Binance Spot confirms active pricing on {pair} with a {change:+.2f}% 24h move."

    ownership_lines = []
    if token_context.holders > 0:
        ownership_lines.append(f"Holders: {token_context.holders:,}")
    ownership_lines.append(f"Smart money: {token_context.smart_money_count} wallet{'s' if token_context.smart_money_count != 1 else ''}" if token_context.smart_money_count > 0 else "Smart money: none visible")
    if token_context.top_holder_concentration_pct > 0:
        ownership_lines.append(f"Top-10 concentration: {token_context.top_holder_concentration_pct:.1f}%")
    if token_context.kol_holders > 0:
        ownership_lines.append(f"KOL holders: {token_context.kol_holders} ({token_context.kol_holding_pct:.1f}%)")
    if token_context.pro_holders > 0:
        ownership_lines.append(f"Pro holders: {token_context.pro_holders} ({token_context.pro_holding_pct:.1f}%)")
    if ownership_lines:
        brief.beginner_note = "\n".join(ownership_lines[:5])

    if token_context.liquidity >= 10_000_000:
        brief.top_risks = [
            risk for risk in brief.top_risks
            if "low liquidity" not in risk.lower()
            and "liquidity context is missing or weak" not in risk.lower()
            and "liquidity is very thin" not in risk.lower()
        ]

    append_posture_note_to_brief(brief, token_context.symbol)

    return brief
