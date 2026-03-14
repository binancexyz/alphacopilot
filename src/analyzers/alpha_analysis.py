from __future__ import annotations

from src.models.schemas import AnalysisBrief, BriefSection, RiskTag


def _alpha_overview_items(ctx: dict) -> list[str]:
    token_list = ctx.get("alpha_token_list") or []
    items: list[str] = []
    for item in token_list[:8]:
        symbol = str(item.get("symbol") or item.get("ticker") or "?")
        name = str(item.get("name") or item.get("tokenName") or "").strip()
        if name and name.lower() != symbol.lower():
            items.append(f"{symbol} — {name}")
        else:
            items.append(symbol)
    return items


def analyze_alpha(symbol: str | None, ctx: dict) -> AnalysisBrief:
    runtime_warning = str(ctx.get("runtime_warning") or "").strip()
    risks = [str(x) for x in ctx.get("major_risks", []) if str(x).strip()]

    if not symbol:
        listed_count = int(ctx.get("alpha_listed_count") or 0)
        items = _alpha_overview_items(ctx)
        quick_verdict = (
            f"Binance Alpha overview ready with {listed_count} listed tokens."
            if listed_count > 0
            else "Binance Alpha overview is thin right now."
        )
        why = (
            f"Use this as the discovery surface for Binance Alpha Token names. "
            f"Currently showing {listed_count} listed tokens"
            + (f", including {', '.join(items[:3])}." if items else ".")
        )
        watch = [
            "which newly visible Alpha names keep showing up instead of rotating out fast",
            "whether any Alpha token graduates from curiosity into real follow-through",
            "whether the Alpha list stays available and live instead of degrading into a thin bridge state",
        ]
        sections = []
        if items:
            sections.append(BriefSection(title="🧭 Binance Alpha", content="\n".join(f"- {item}" for item in items)))
        tags = [
            RiskTag(name="Feature", level="Medium", note="Binance Alpha Token discovery surface."),
        ]
        if runtime_warning:
            tags.append(RiskTag(name="Runtime", level="High", note=runtime_warning))
        return AnalysisBrief(
            entity="Binance Alpha",
            quick_verdict=quick_verdict,
            signal_quality="Medium" if listed_count > 0 and not runtime_warning else "Low",
            top_risks=risks,
            why_it_matters=why,
            what_to_watch_next=watch,
            risk_tags=tags,
            sections=sections,
            conviction="Medium" if listed_count > 0 and not runtime_warning else "Low",
            beginner_note="Alpha is a discovery surface, not a quality guarantee. Listed does not mean safe.",
        )

    resolved = str(ctx.get("symbol") or symbol).upper()
    is_listed = bool(ctx.get("is_alpha_listed"))
    price = float(ctx.get("alpha_price") or 0.0)
    change = float(ctx.get("alpha_price_change_24h") or 0.0)
    volume = float(ctx.get("alpha_volume_24h") or 0.0)
    audit_gate = str(ctx.get("audit_gate") or "WARN").upper()

    if audit_gate == "BLOCK":
        verdict = f"{resolved} is visible in Alpha context but currently blocked on audit posture."
        conviction = "Low"
    elif is_listed and price > 0:
        verdict = f"{resolved} is listed on Binance Alpha and has live market context."
        conviction = "Medium" if not runtime_warning else "Low"
    elif is_listed:
        verdict = f"{resolved} appears on Binance Alpha, but live price context is thin."
        conviction = "Low"
    else:
        verdict = f"{resolved} is not clearly present in Binance Alpha listing context right now."
        conviction = "Low"

    why_parts = []
    if is_listed:
        why_parts.append(f"{resolved} is visible in Binance Alpha")
    else:
        why_parts.append(f"{resolved} does not currently resolve cleanly inside Binance Alpha")
    if price > 0:
        why_parts.append(f"price ${price:,.4f}")
    if change:
        why_parts.append(f"24h {change:+.2f}%")
    if volume > 0:
        why_parts.append(f"volume about ${volume:,.0f}")
    if runtime_warning:
        why_parts.append(runtime_warning)
    why = ". ".join(part.rstrip(".") for part in why_parts) + "."

    watch = [
        "whether Alpha listing context stays available and does not degrade",
        "whether price action builds follow-through instead of one-candle attention",
        "whether audit posture improves or worsens before treating the token as higher-conviction",
    ]
    tags = [RiskTag(name="Alpha Listed", level="Medium" if is_listed else "Low", note="Binance Alpha Token listing context.")]
    if audit_gate == "BLOCK":
        tags.append(RiskTag(name="Audit Gate", level="High", note=str(ctx.get("blocked_reason") or "Audit gate is blocking.")))
    if runtime_warning:
        tags.append(RiskTag(name="Runtime", level="High", note=runtime_warning))

    sections = []
    market_lines = []
    if price > 0:
        market_lines.append(f"- Price: ${price:,.4f}")
    if change:
        market_lines.append(f"- 24h change: {change:+.2f}%")
    if volume > 0:
        market_lines.append(f"- 24h volume: ${volume:,.0f}")
    if market_lines:
        sections.append(BriefSection(title="📈 Alpha Market", content="\n".join(market_lines)))

    return AnalysisBrief(
        entity=f"Alpha · {resolved}",
        quick_verdict=verdict,
        signal_quality="Medium" if is_listed and price > 0 and not runtime_warning else "Low",
        top_risks=risks,
        why_it_matters=why,
        what_to_watch_next=watch,
        risk_tags=tags,
        sections=sections,
        conviction=conviction,
        beginner_note="Binance Alpha visibility is useful discovery context, but not a safety or upside guarantee.",
        audit_gate=ctx.get("audit_gate"),
        blocked_reason=ctx.get("blocked_reason"),
        runtime_state=ctx.get("runtime_state"),
        runtime_warning=ctx.get("runtime_warning"),
    )
