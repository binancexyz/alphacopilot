from __future__ import annotations

from src.analyzers.judgment_helpers import append_posture_note_to_brief
from src.analyzers.price_analysis import _fetch_market_quote
from src.analyzers.signal_live_brief import build_signal_brief
from src.models.schemas import AnalysisBrief, RiskTag
from src.services.factory import get_market_data_service
from src.services.normalizers import normalize_signal_context


def analyze_signal(token: str) -> AnalysisBrief:
    service = get_market_data_service()
    raw_context = service.get_signal_context(token)
    signal_context = normalize_signal_context(raw_context)
    brief = build_signal_brief(signal_context)

    try:
        quote, source = _fetch_market_quote(token)
    except Exception:
        quote, source = None, ""

    if quote:
        price = float(quote.get("price") or 0)
        change = float(quote.get("percent_change_24h") or 0)
        rank = int(quote.get("rank") or 0)
        brief.risk_tags.insert(0, RiskTag(name="Header Market", level="Info", note=f"{price}|{change}|{rank}"))

    if signal_context.trigger_price > 0:
        zone_low = signal_context.trigger_price * 0.99
        zone_high = signal_context.trigger_price * 1.01
        brief.risk_tags.append(RiskTag(name="Entry Zone", level="Info", note=f"${zone_low:,.2f} – ${zone_high:,.2f}"))

    if quote and source == "Binance Spot":
        pair = str(quote.get("exchange_symbol") or token)
        spread = float(quote.get("spread_pct") or 0)
        change = float(quote.get("percent_change_24h") or 0)
        note = f"{pair} | 24h {change:+.2f}%"
        if spread > 0:
            note += f" | spread {spread:.2f}%"
        brief.risk_tags.insert(1, RiskTag(name="Binance Spot", level="Low" if spread < 0.5 else "Medium", note=note))
        if spread >= 0.5:
            brief.top_risks.insert(0, f"Binance Spot spread is relatively wide at {spread:.2f}%, so live exchange confirmation is less clean than the headline move suggests.")
        elif signal_context.signal_status == "unmatched":
            brief.top_risks.insert(0, f"Binance Spot price is live via {pair}, but the signal itself is still unmatched on the smart-money board.")
        elif brief.why_it_matters:
            brief.why_it_matters += f" Binance Spot confirms active pricing on {pair} with a {change:+.2f}% 24h move."

    append_posture_note_to_brief(brief, signal_context.token)

    invalidation = ""
    if signal_context.audit_gate == "BLOCK":
        invalidation = "Breaks immediately if the audit state stays blocked."
    elif signal_context.trigger_price > 0 and signal_context.current_price > 0:
        if signal_context.current_price >= signal_context.trigger_price:
            invalidation = "Breaks if price loses the trigger zone and follow-through fades."
        else:
            invalidation = "Still unproven until price reclaims the trigger zone with real follow-through."
    elif signal_context.exit_rate >= 70:
        invalidation = "Breaks if exit pressure stays elevated and fresh participation does not replace it."
    elif signal_context.signal_status == "unmatched":
        invalidation = "No smart-money follow-through"
    else:
        invalidation = "Breaks if confirmation does not improve in the next cycle."
    brief.risk_tags.append(RiskTag(name="Invalidation", level="Info", note=invalidation))

    return brief
