from __future__ import annotations

from decimal import Decimal
from math import fsum
from typing import Any

from src.models.schemas import AnalysisBrief, RiskTag
from src.services.binance_skill_bridge import fetch_live_bundle
from src.services.exposure_groups import top_groups
from src.services.portfolio_history import append_snapshot, describe_delta, describe_snapshot_age, describe_trend, earlier_snapshot, latest_snapshot, top_change_note
from src.services.live_service import LiveMarketDataService
from src.config import settings

STABLES = {"USDT", "USDC", "BUSD", "FDUSD", "TUSD", "USDP", "DAI"}
LD_PREFIXES = ("LD",)


def _effective_positions(weights: list[float]) -> float:
    if not weights:
        return 0.0
    squared = fsum((w / 100.0) ** 2 for w in weights if w > 0)
    return (1.0 / squared) if squared > 0 else 0.0


def _style_profile(stable_pct: float, concentration: float, borrowed_pct: float, positions: int) -> str:
    if borrowed_pct >= 20:
        return "Levered"
    if stable_pct >= 70:
        return "Defensive cash-heavy"
    if concentration >= 70:
        return "Concentrated conviction"
    if positions >= 6 and stable_pct < 30:
        return "Diversified risk-on"
    if positions <= 2 and stable_pct < 30:
        return "Narrow risk-on"
    return "Mixed posture"

def _normalize_asset(asset: str) -> tuple[str, bool]:
    normalized = asset.upper().strip()
    wrapped = False
    for prefix in LD_PREFIXES:
        if normalized.startswith(prefix) and len(normalized) > len(prefix):
            normalized = normalized[len(prefix):]
            wrapped = True
            break
    return normalized, wrapped


def _asset_qty(item: dict[str, Any]) -> Decimal:
    free = Decimal(str(item.get("free") or "0"))
    locked = Decimal(str(item.get("locked") or "0"))
    return free + locked


def _asset_btc_value(item: dict[str, Any]) -> Decimal:
    return Decimal(str(item.get("btcValuation") or "0"))


def _is_dust_position(qty: Decimal, usd_value: Decimal) -> bool:
    return qty > 0 and usd_value < Decimal("1")


def _infer_btc_price(balances: list[dict[str, Any]], prices: dict[str, Any]) -> Decimal:
    explicit = Decimal(str(prices.get("BTC") or prices.get("WBTC") or "0"))
    if explicit > 0:
        return explicit

    for item in balances:
        raw_asset = str(item.get("asset") or "").upper()
        normalized_asset, _ = _normalize_asset(raw_asset)
        qty = _asset_qty(item)
        btc_value = _asset_btc_value(item)
        if normalized_asset in STABLES and qty > 0 and btc_value > 0:
            return qty / btc_value
    return Decimal("0")


def _margin_snapshot(margin_account: dict[str, Any], prices: dict[str, Any], btc_price: Decimal) -> dict[str, Any]:
    if not isinstance(margin_account, dict):
        return {
            "borrowed_value": Decimal("0"),
            "net_equity_value": Decimal("0"),
            "interest_value": Decimal("0"),
            "positions": 0,
            "margin_level": Decimal("0"),
        }

    borrowed_value = Decimal("0")
    net_equity_value = Decimal("0")
    interest_value = Decimal("0")
    positions = 0
    user_assets = margin_account.get("userAssets", []) if isinstance(margin_account.get("userAssets"), list) else []

    for item in user_assets:
        if not isinstance(item, dict):
            continue
        asset = str(item.get("asset") or "").upper()
        normalized_asset, _ = _normalize_asset(asset)
        borrowed = Decimal(str(item.get("borrowed") or "0"))
        interest = Decimal(str(item.get("interest") or "0"))
        net_asset = Decimal(str(item.get("netAsset") or "0"))
        if borrowed > 0 or interest > 0 or net_asset != 0:
            positions += 1

        usd_price = Decimal(str(prices.get(normalized_asset) or "0"))
        if usd_price <= 0:
            if normalized_asset in STABLES:
                usd_price = Decimal("1")
            elif normalized_asset == "BTC" and btc_price > 0:
                usd_price = btc_price

        if usd_price > 0:
            borrowed_value += borrowed * usd_price
            interest_value += interest * usd_price
            net_equity_value += net_asset * usd_price

    total_liability_btc = Decimal(str(margin_account.get("totalLiabilityOfBtc") or "0"))
    total_net_asset_btc = Decimal(str(margin_account.get("totalNetAssetOfBtc") or "0"))
    if borrowed_value <= 0 and total_liability_btc > 0 and btc_price > 0:
        borrowed_value = total_liability_btc * btc_price
    if net_equity_value == 0 and total_net_asset_btc != 0 and btc_price > 0:
        net_equity_value = total_net_asset_btc * btc_price

    return {
        "borrowed_value": borrowed_value,
        "net_equity_value": net_equity_value,
        "interest_value": interest_value,
        "positions": positions,
        "margin_level": Decimal(str(margin_account.get("marginLevel") or "0")),
    }

def get_portfolio_snapshot() -> dict[str, Any]:
    live_service = LiveMarketDataService(
        base_url=settings.binance_skills_base_url,
        api_key=settings.binance_api_key,
        api_secret=settings.binance_api_secret,
    )

    context = live_service.get_portfolio_context()

    raw_context = context.get("_raw", context)
    account = raw_context.get("assets", {}).get("data", [])
    funding_wallet = raw_context.get("funding-wallet", {}).get("data", [])
    account_snapshot = raw_context.get("account-snapshot", {})
    margin_account = raw_context.get("margin-trading", {})
    prices = context.get("prices", {})
    alpha_symbols: set[str] = set()

    if not account and not funding_wallet:
        try:
            bundle = fetch_live_bundle("portfolio", "")
            raw_context = bundle.raw or raw_context
            account = raw_context.get("assets", {}).get("data", [])
            funding_wallet = raw_context.get("funding-wallet", {}).get("data", [])
            account_snapshot = raw_context.get("account-snapshot", account_snapshot)
            margin_account = raw_context.get("margin-trading", margin_account)
        except Exception:
            pass

    try:
        alpha_bundle = fetch_live_bundle("alpha", "")
        alpha_items = (alpha_bundle.raw.get("alpha", {}) or {}).get("token_list") or []
        alpha_symbols = {str(item.get("symbol") or "").upper() for item in alpha_items if isinstance(item, dict) and item.get("symbol")}
    except Exception:
        alpha_symbols = set()

    balances: list[dict[str, Any]] = []
    source_counts = {"spot": 0, "funding": 0, "snapshot": 0}
    if isinstance(account, list):
        items = [item for item in account if isinstance(item, dict)]
        balances.extend({**item, "_source": "spot"} for item in items)
        source_counts["spot"] = len(items)
    if isinstance(funding_wallet, list):
        items = [item for item in funding_wallet if isinstance(item, dict)]
        balances.extend({**item, "_source": "funding"} for item in items)
        source_counts["funding"] = len(items)
    if isinstance(account_snapshot, dict):
        snapshot_vos = account_snapshot.get("snapshotVos") or []
        if snapshot_vos and isinstance(snapshot_vos, list):
            latest = snapshot_vos[-1] if isinstance(snapshot_vos[-1], dict) else {}
            snap_balances = ((latest.get("data") or {}).get("balances") or []) if isinstance(latest, dict) else []
            if isinstance(snap_balances, list):
                items = [item for item in snap_balances if isinstance(item, dict)]
                balances.extend({**item, "_source": "snapshot"} for item in items)
                source_counts["snapshot"] = len(items)
    btc_price = _infer_btc_price(balances, prices)
    merged: dict[str, dict[str, Any]] = {}
    unmapped_assets: list[str] = []
    spot_total_value = Decimal("0")
    for item in balances:
        if not isinstance(item, dict):
            continue
        raw_asset = str(item.get("asset") or "").upper()
        normalized_asset, wrapped = _normalize_asset(raw_asset)
        locked = Decimal(str(item.get("locked") or "0"))
        qty = _asset_qty(item)
        if qty <= 0:
            continue
        usd_price = Decimal(str(prices.get(normalized_asset) or "0"))
        usd_value = Decimal("0")
        if usd_price > 0:
            usd_value = qty * usd_price
        elif btc_price > 0 and _asset_btc_value(item) > 0:
            usd_value = _asset_btc_value(item) * btc_price
            if usd_value > 0 and qty > 0:
                usd_price = usd_value / qty

        spot_total_value += usd_value
        slot = merged.setdefault(normalized_asset, {
            "asset": normalized_asset,
            "raw_assets": set(),
            "sources": set(),
            "is_alpha": normalized_asset in alpha_symbols,
            "qty": Decimal("0"),
            "usd_price": Decimal("0"),
            "usd_value": Decimal("0"),
            "locked": Decimal("0"),
            "wrapped": False,
        })
        slot["raw_assets"].add(raw_asset)
        slot["sources"].add(str(item.get("_source") or "spot"))
        slot["is_alpha"] = slot["is_alpha"] or (normalized_asset in alpha_symbols)
        slot["qty"] += qty
        slot["locked"] += locked
        slot["wrapped"] = slot["wrapped"] or wrapped
        if usd_price > 0:
            slot["usd_price"] = usd_price
            slot["usd_value"] += usd_value
        elif usd_value <= 0:
            unmapped_assets.append(raw_asset)

    enriched = sorted(merged.values(), key=lambda x: x["usd_value"], reverse=True)
    priced_assets = [item for item in enriched if item["usd_value"] > 0]
    dust_assets = [item for item in enriched if item["qty"] > 0 and item["usd_value"] <= 0]
    margin = _margin_snapshot(margin_account, prices, btc_price)
    margin_net_value = margin["net_equity_value"]
    borrowed_value = margin["borrowed_value"]
    interest_value = margin["interest_value"]
    margin_positions = int(margin["positions"])
    margin_level = margin["margin_level"]

    total_value = spot_total_value + margin_net_value
    if total_value <= 0 and spot_total_value > 0:
        total_value = spot_total_value

    stable_value = sum(item["usd_value"] for item in priced_assets if item["asset"] in STABLES)
    risk_value = sum(item["usd_value"] for item in priced_assets if item["asset"] not in STABLES) + max(margin_net_value, Decimal("0"))
    alpha_value = sum(item["usd_value"] for item in priced_assets if item.get("is_alpha"))
    stable_pct = (float(stable_value) / float(total_value) * 100) if total_value > 0 else 0.0
    risk_pct = (float(risk_value) / float(total_value) * 100) if total_value > 0 else 0.0
    alpha_pct = (float(alpha_value) / float(total_value) * 100) if total_value > 0 else 0.0
    group_mix = top_groups({"asset": item["asset"], "usd_value": float(item["usd_value"])} for item in priced_assets)
    components = list(priced_assets)
    if margin_net_value > 0:
        components.append({
            "asset": "CROSS-MARGIN",
            "usd_value": margin_net_value,
            "locked": Decimal("0"),
            "wrapped": False,
            "synthetic": True,
        })
    components = sorted(components, key=lambda x: x["usd_value"], reverse=True)
    top = components[:5]
    top_lines: list[str] = []
    top_weights: list[float] = []
    for item in top:
        value = float(item["usd_value"])
        weight = (value / float(total_value) * 100) if total_value > 0 else 0.0
        top_weights.append(weight)
        if item.get("synthetic"):
            top_lines.append(f"{item['asset']} ~${value:,.2f} ({weight:.1f}%) | net equity")
            continue
        locked_note = " | some locked" if item["locked"] > 0 else ""
        wrapped_note = " | includes LD balances" if item["wrapped"] else ""
        alpha_note = " | Alpha" if item.get("is_alpha") else ""
        source_note = ""
        if item.get("sources"):
            ordered = "/".join(sorted(str(src) for src in item["sources"]))
            source_note = f" | {ordered}"
        top_lines.append(f"{item['asset']} ~${value:,.2f} ({weight:.1f}%){locked_note}{wrapped_note}{alpha_note}{source_note}")

    concentration = top_weights[0] if top_weights else 0.0
    top3_concentration = sum(top_weights[:3]) if top_weights else 0.0
    effective_positions = _effective_positions(top_weights)
    borrowed_pct = (float(borrowed_value) / float(total_value) * 100) if total_value > 0 and borrowed_value > 0 else 0.0
    style_profile = _style_profile(stable_pct, concentration, borrowed_pct, len(priced_assets))
    dust_asset_count = len(dust_assets)
    if total_value <= 0 and (enriched or dust_assets):
        verdict = "Only dust-sized Spot balances are visible. No meaningful active exposure."
        quality = "Dust"
    elif total_value <= 0:
        verdict = "Thin snapshot. No visible balance value."
        quality = "Thin"
    elif borrowed_pct >= 20:
        verdict = "Levered posture. Margin exposure is material."
        quality = "Aggressive"
    elif stable_pct >= 70 and concentration >= 70:
        verdict = "Very defensive. Capital is concentrated in stablecoins rather than spread across risk assets."
        quality = "Defensive"
    elif concentration >= 70:
        verdict = "Highly concentrated. One position dominates."
        quality = "Concentrated"
    elif stable_pct >= 55 and concentration < 40:
        verdict = "Defensive. Dry powder ready. No overconcentration."
        quality = "Defensive"
    elif concentration >= 40:
        verdict = "Lead position clear. Diversification still present."
        quality = "Moderate"
    else:
        verdict = "Balanced posture. No dominant single bet."
        quality = "Balanced"

    available_assets = len(priced_assets)
    locked_assets = sum(1 for item in enriched if item["locked"] > 0)
    posture_note = "levered risk-on" if borrowed_pct >= 20 else "defensive" if stable_pct >= 55 else "risk-on" if stable_pct <= 20 else "mixed"

    risk_lines: list[str] = []
    if total_value <= 0 and (enriched or dust_assets):
        risk_lines.append("Only dust-sized Spot balances were visible, so there is no meaningful active portfolio exposure to judge.")
    elif total_value <= 0:
        risk_lines.append("No priced Spot balances were visible, so the portfolio read stays incomplete.")
    if concentration >= 70 and stable_pct < 70:
        risk_lines.append("Top holding concentration is high enough that one move can dominate portfolio performance.")
    elif concentration >= 70 and stable_pct >= 70:
        risk_lines.append("Most visible capital is parked in stablecoins, so the account is concentrated but still structurally defensive.")
    if stable_pct <= 10 and total_value > 0:
        risk_lines.append("Stablecoin dry powder looks thin, so flexibility may be lower if market conditions change quickly.")
    if locked_assets > 0:
        risk_lines.append("Some balances are locked, so immediately available exposure is lower than gross holdings suggest.")
    if borrowed_value > 0:
        margin_line = f"Margin borrowed is about ${float(borrowed_value):,.2f}"
        if interest_value > 0:
            margin_line += f" with roughly ${float(interest_value):,.2f} in interest accruing."
        else:
            margin_line += "."
        risk_lines.append(margin_line)
    if margin_level > 0 and margin_level < Decimal("3"):
        risk_lines.append(f"Margin level is {float(margin_level):.2f}, so leverage buffer is not especially wide.")
    if unmapped_assets:
        risk_lines.append(f"Some asset codes still need mapping for cleaner valuation: {', '.join(sorted(set(unmapped_assets))[:5])}.")
    if not risk_lines:
        risk_lines.append("This is an estimated read-only snapshot, not a full PnL or cost-basis analysis.")

    dust_lines: list[str] = []
    if total_value <= 0:
        for item in dust_assets[:5]:
            qty = item["qty"]
            if qty <= 0:
                continue
            dust_lines.append(f"{item['asset']} {qty.normalize()}")

    lead_groups = ", ".join(f"{name} {pct:.1f}%" for name, pct in group_mix[:3]) if group_mix else "no clear grouped exposure yet"
    if total_value <= 0 and dust_lines:
        why = (
            f"Only residual Spot balances are visible right now ({', '.join(dust_lines[:3])}). "
            f"That is a dust-state account, not a meaningful active portfolio."
        )
    else:
        why = (
            f"Estimated visible Spot value is about ${float(total_value):,.2f} across {available_assets} priced asset(s). "
            f"Stablecoins are {stable_pct:.1f}% of the priced snapshot, risk assets are {risk_pct:.1f}%, and Alpha-token exposure is {alpha_pct:.1f}%. "
            f"Top concentration is {concentration:.1f}% and top-3 concentration is {top3_concentration:.1f}%{' with some locked balances in play' if locked_assets else ''}, which makes the current posture look {posture_note}. "
            f"Style profile: {style_profile}. Effective positions: {effective_positions:.1f}. Lead exposure groups: {lead_groups}."
        )
    if margin_net_value != 0:
        why += f" Cross-margin net equity contributes about ${float(margin_net_value):,.2f}."
    if borrowed_value > 0:
        why += f" Borrowed margin exposure is about ${float(borrowed_value):,.2f}."

    source_bits = []
    if source_counts["spot"]:
        source_bits.append(f"spot {source_counts['spot']}")
    if source_counts["funding"]:
        source_bits.append(f"funding {source_counts['funding']}")
    if source_counts["snapshot"]:
        source_bits.append(f"snapshot {source_counts['snapshot']}")

    tags = [
        RiskTag(name="Account Mode", level="Read-only", note="estimated Spot snapshot"),
        RiskTag(name="Source", level="Binance API", note="signed account read + live price map"),
        RiskTag(name="Coverage", level="Good" if len(source_bits) >= 2 else "Limited", note=" | ".join(source_bits) if source_bits else "spot only"),
        RiskTag(name="Assets", level=str(available_assets), note="priced balances"),
        RiskTag(name="Style Profile", level="Info", note=style_profile),
    ]
    if total_value <= 0 and dust_lines:
        tags.append(RiskTag(name="Dust State", level="Info", note=f"{len(dust_lines)} residual balance(s) visible"))
    if concentration > 0:
        tags.append(RiskTag(name="Top Concentration", level="High" if concentration >= 70 else "Medium" if concentration >= 40 else "Low", note=f"{concentration:.1f}%"))
    if top3_concentration > 0:
        tags.append(RiskTag(name="Top 3", level="Info", note=f"{top3_concentration:.1f}%"))
    if effective_positions > 0:
        tags.append(RiskTag(name="Effective Positions", level="Info", note=f"{effective_positions:.1f}"))
    tags.append(RiskTag(name="Stablecoin Share", level="High" if stable_pct >= 55 else "Medium" if stable_pct >= 20 else "Low", note=f"{stable_pct:.1f}%"))
    if alpha_pct > 0:
        tags.append(RiskTag(name="Alpha Exposure", level="Info", note=f"{alpha_pct:.1f}%"))
    if group_mix:
        tags.append(RiskTag(name="Lead Group", level="Info", note=f"{group_mix[0][0]} {group_mix[0][1]:.1f}%"))
    if borrowed_value > 0 or margin_net_value != 0:
        margin_note = f"Net equity ${float(margin_net_value):,.2f}"
        if borrowed_value > 0:
            margin_note += f" | borrowed ${float(borrowed_value):,.2f}"
        tags.append(RiskTag(name="Margin Exposure", level="High" if borrowed_pct >= 20 else "Medium" if borrowed_value > 0 else "Low", note=margin_note))

    if total_value <= 0 and dust_lines:
        top_lines = [f"Dust balance — {line}" for line in dust_lines[:5]]

    return {
        "verdict": verdict,
        "quality": quality,
        "why": why,
        "top_lines": top_lines,
        "top_risks": risk_lines,
        "tags": tags,
        "available_assets": available_assets,
        "stable_pct": stable_pct,
        "risk_pct": risk_pct,
        "concentration": concentration,
        "posture": posture_note,
        "total_value": float(total_value),
        "margin_borrowed_value": float(borrowed_value),
        "margin_net_equity": float(margin_net_value),
        "priced_assets": [
            {"asset": item["asset"], "usd_value": float(item["usd_value"]), "wrapped": bool(item["wrapped"])}
            for item in priced_assets
        ],
    }


def analyze_portfolio() -> AnalysisBrief:
    try:
        snapshot = get_portfolio_snapshot()
    except Exception as exc:
        message = str(exc)
        return AnalysisBrief(
            entity="Portfolio: Binance Spot",
            quick_verdict="Portfolio read is unavailable right now.",
            signal_quality="Unavailable",
            top_risks=[message],
            why_it_matters="This command is read-only, but it still depends on valid Binance API credentials and account-read permission.",
            what_to_watch_next=[
                "confirm BINANCE_API_KEY and BINANCE_API_SECRET are set",
                "make sure the API key has Spot read permissions",
            ],
        )

    previous = latest_snapshot()
    prior_trend = earlier_snapshot(steps_back=3)
    previous_age = describe_snapshot_age(previous)
    delta_summary, delta_watch = describe_delta(previous, snapshot)
    strongest_change = top_change_note(previous, snapshot)
    trend_summary = describe_trend(prior_trend, snapshot)
    append_snapshot(snapshot)

    why = snapshot["why"]
    if previous_age:
        why = f"{why} Last local snapshot was {previous_age}."
        snapshot["tags"].append(RiskTag(name="Freshness", level="Info", note=previous_age))
    if delta_summary:
        why = f"{why} {delta_summary}"
    if strongest_change:
        why = f"{why} {strongest_change}"
        snapshot["tags"].append(RiskTag(name="Top Change", level="Info", note=strongest_change.replace('Strongest recent change: ', '').rstrip('.')))
    if trend_summary:
        why = f"{why} Short local trend: {trend_summary}."
        snapshot["tags"].append(RiskTag(name="Short Trend", level="Info", note=trend_summary))

    watch_items = [
        "whether the top holding keeps growing relative to the rest of the account",
        "whether stablecoin dry powder changes meaningfully after the next rotation",
    ]
    if float(snapshot.get("margin_borrowed_value") or 0) > 0:
        watch_items.insert(0, "whether borrowed margin exposure is being expanded, reduced, or rolled into new positions")
    if delta_watch:
        watch_items = delta_watch[:2] + watch_items

    brief = AnalysisBrief(
        entity="Portfolio: Binance Spot",
        quick_verdict=snapshot["verdict"],
        signal_quality=snapshot["quality"],
        top_risks=snapshot["top_risks"],
        why_it_matters=why,
        what_to_watch_next=watch_items[:3],
        risk_tags=snapshot["tags"],
        beginner_note="\n".join(snapshot["top_lines"]) if snapshot["top_lines"] else None
    )
    summary_lines: list[str] = []
    if previous_age:
        summary_lines.append(f"Freshness: {previous_age}")
    if strongest_change:
        summary_lines.append(strongest_change)
    elif delta_summary:
        summary_lines.append(delta_summary)
    if trend_summary:
        summary_lines.append(f"Short trend: {trend_summary}")
    if summary_lines:
        brief.what_to_watch_next = summary_lines[:2] + brief.what_to_watch_next[:2]
    return brief
