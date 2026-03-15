from __future__ import annotations

from src.analyzers.judgment_helpers import append_posture_note_to_brief
from src.analyzers.price_analysis import _fetch_market_quote
from src.analyzers.signal_live_brief import build_signal_brief
from src.analyzers.thresholds import ATR_FALLBACK_PCT, ATR_ZONE_MULTIPLIER
from src.models.schemas import AnalysisBrief, RiskTag
from src.services.factory import get_market_data_service
from src.services.normalizers import normalize_signal_context
from src.services.snapshot_history import describe_snapshot_delta, save_snapshot


def _has_risk_tag(brief: AnalysisBrief, name: str) -> bool:
    return any(tag.name == name for tag in brief.risk_tags)


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

    if signal_context.trigger_price > 0 and not _has_risk_tag(brief, "Entry Zone"):
        atr_pct = ATR_FALLBACK_PCT
        if signal_context.price_high_24h > 0 and signal_context.price_low_24h > 0 and signal_context.price_high_24h > signal_context.price_low_24h:
            atr_pct = (signal_context.price_high_24h - signal_context.price_low_24h) / signal_context.trigger_price
            atr_pct = min(atr_pct * ATR_ZONE_MULTIPLIER, 0.10)
            atr_pct = max(atr_pct, 0.005)
        zone_low = signal_context.trigger_price * (1.0 - atr_pct)
        zone_high = signal_context.trigger_price * (1.0 + atr_pct)
        zone_note = f"${zone_low:,.2f} – ${zone_high:,.2f}"
        if atr_pct != ATR_FALLBACK_PCT:
            zone_note += f" (ATR-adjusted ±{atr_pct * 100:.1f}%)"
        brief.risk_tags.append(RiskTag(name="Entry Zone", level="Info", note=zone_note))

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
            
        # Add new ratio checks if they exist in the futures quote (this requires an update to the price fetcher too if they aren't parsed)
        taker_ratio = float(quote.get("taker_buy_sell_ratio") or 0)
        top_trader_ratio = float(quote.get("top_trader_long_short_ratio") or 0)
        
        if taker_ratio > 1.2:
            brief.risk_tags.append(RiskTag(name="Taker Ratio", level="Medium", note=f"Aggressive taker buy volume ({taker_ratio:.2f})"))
        elif taker_ratio > 0 and taker_ratio < 0.8:
            brief.risk_tags.append(RiskTag(name="Taker Ratio", level="High", note=f"Aggressive taker sell volume ({taker_ratio:.2f})"))
            
        if top_trader_ratio > 1.5:
            brief.risk_tags.append(RiskTag(name="Top Traders", level="Medium", note=f"Top traders leaning long ({top_trader_ratio:.2f})"))
        elif top_trader_ratio > 0 and top_trader_ratio < 0.7:
            brief.risk_tags.append(RiskTag(name="Top Traders", level="High", note=f"Top traders leaning short ({top_trader_ratio:.2f})"))

    append_posture_note_to_brief(brief, signal_context.token)

    if not _has_risk_tag(brief, "Invalidation"):
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

    # Historical delta tracking
    snapshot_data = {
        "signal_quality": brief.signal_quality,
        "state": brief.quick_verdict.split(".")[0] if brief.quick_verdict else "",
        "conviction": brief.conviction,
    }
    try:
        delta_summary, delta_watch = describe_snapshot_delta("signal", signal_context.token, snapshot_data)
        if delta_summary:
            brief.risk_tags.append(RiskTag(name="Delta", level="Info", note=delta_summary))
        if delta_watch:
            brief.what_to_watch_next = delta_watch[:1] + brief.what_to_watch_next[:3]
        save_snapshot("signal", signal_context.token, snapshot_data)
    except Exception:
        pass

    return brief
