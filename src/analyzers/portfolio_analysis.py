from __future__ import annotations

import hashlib
import hmac
import time
from decimal import Decimal
from typing import Any
from urllib.parse import urlencode

from src.config import settings
from src.models.schemas import AnalysisBrief, RiskTag
from src.services.exposure_groups import top_groups
from src.services.portfolio_history import append_snapshot, describe_delta, describe_snapshot_age, describe_trend, earlier_snapshot, latest_snapshot, top_change_note

BINANCE_API_BASE_URL = "https://api.binance.com"
ACCOUNT_INFO_URL = "/api/v3/account"
PRICE_TICKER_URL = "/api/v3/ticker/price"
STABLES = {"USDT", "USDC", "BUSD", "FDUSD", "TUSD", "USDP", "DAI"}
LD_PREFIXES = ("LD",)


class PortfolioFetchError(RuntimeError):
    pass


def _httpx_client(*args, **kwargs):
    try:
        import httpx  # type: ignore
    except ModuleNotFoundError as exc:
        raise PortfolioFetchError("httpx is required for Binance account reads.") from exc
    return httpx.Client(*args, **kwargs)


def _signed_get(path: str, params: dict[str, Any]) -> dict[str, Any]:
    api_key = settings.binance_api_key.strip()
    api_secret = settings.binance_api_secret.strip()
    if not api_key or not api_secret:
        raise PortfolioFetchError("BINANCE_API_KEY and BINANCE_API_SECRET are required for /portfolio.")

    payload = dict(params)
    payload.setdefault("timestamp", int(time.time() * 1000))
    payload.setdefault("recvWindow", 10000)
    query = urlencode(payload)
    signature = hmac.new(api_secret.encode("utf-8"), query.encode("utf-8"), hashlib.sha256).hexdigest()
    headers = {"X-MBX-APIKEY": api_key}

    with _httpx_client(timeout=20.0, follow_redirects=True) as client:
        resp = client.get(f"{BINANCE_API_BASE_URL}{path}?{query}&signature={signature}", headers=headers)
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, dict):
            raise PortfolioFetchError("Unexpected Binance account response shape.")
        return data


def _load_prices() -> dict[str, Decimal]:
    with _httpx_client(timeout=20.0, follow_redirects=True) as client:
        resp = client.get(f"{BINANCE_API_BASE_URL}{PRICE_TICKER_URL}")
        resp.raise_for_status()
        payload = resp.json() or []
    prices: dict[str, Decimal] = {}
    for item in payload:
        if not isinstance(item, dict):
            continue
        symbol = str(item.get("symbol") or "")
        try:
            price = Decimal(str(item.get("price") or "0"))
        except Exception:
            continue
        if symbol and price > 0:
            prices[symbol] = price
    return prices


def _normalize_asset(asset: str) -> tuple[str, bool]:
    normalized = asset.upper().strip()
    wrapped = False
    for prefix in LD_PREFIXES:
        if normalized.startswith(prefix) and len(normalized) > len(prefix):
            normalized = normalized[len(prefix):]
            wrapped = True
            break
    return normalized, wrapped


def _asset_usd_price(asset: str, prices: dict[str, Decimal]) -> Decimal:
    if asset in STABLES:
        return Decimal("1")
    direct_pairs = [f"{asset}USDT", f"{asset}USDC", f"{asset}FDUSD", f"{asset}BUSD"]
    for pair in direct_pairs:
        if pair in prices:
            return prices[pair]
    if asset == "BTC":
        btc_usdt = prices.get("BTCUSDT") or prices.get("BTCUSDC")
        return btc_usdt or Decimal("0")
    btc_pair = f"{asset}BTC"
    btc_usdt = prices.get("BTCUSDT") or prices.get("BTCUSDC")
    if btc_pair in prices and btc_usdt:
        return prices[btc_pair] * btc_usdt
    return Decimal("0")


def get_portfolio_snapshot() -> dict[str, Any]:
    account = _signed_get(ACCOUNT_INFO_URL, {})
    prices = _load_prices()

    balances = account.get("balances") or []
    merged: dict[str, dict[str, Any]] = {}
    unmapped_assets: list[str] = []
    total_value = Decimal("0")
    for item in balances:
        if not isinstance(item, dict):
            continue
        raw_asset = str(item.get("asset") or "").upper()
        normalized_asset, wrapped = _normalize_asset(raw_asset)
        free = Decimal(str(item.get("free") or "0"))
        locked = Decimal(str(item.get("locked") or "0"))
        qty = free + locked
        if qty <= 0:
            continue
        usd_price = _asset_usd_price(normalized_asset, prices)
        usd_value = qty * usd_price
        total_value += usd_value
        slot = merged.setdefault(normalized_asset, {
            "asset": normalized_asset,
            "raw_assets": set(),
            "qty": Decimal("0"),
            "usd_price": Decimal("0"),
            "usd_value": Decimal("0"),
            "locked": Decimal("0"),
            "wrapped": False,
        })
        slot["raw_assets"].add(raw_asset)
        slot["qty"] += qty
        slot["locked"] += locked
        slot["wrapped"] = slot["wrapped"] or wrapped
        if usd_price > 0:
            slot["usd_price"] = usd_price
            slot["usd_value"] += usd_value
        else:
            unmapped_assets.append(raw_asset)

    enriched = sorted(merged.values(), key=lambda x: x["usd_value"], reverse=True)
    priced_assets = [item for item in enriched if item["usd_value"] > 0]
    stable_value = sum(item["usd_value"] for item in priced_assets if item["asset"] in STABLES)
    risk_value = sum(item["usd_value"] for item in priced_assets if item["asset"] not in STABLES)
    stable_pct = (float(stable_value) / float(total_value) * 100) if total_value > 0 else 0.0
    risk_pct = (float(risk_value) / float(total_value) * 100) if total_value > 0 else 0.0
    group_mix = top_groups({"asset": item["asset"], "usd_value": float(item["usd_value"])} for item in priced_assets)
    top = priced_assets[:5]
    top_lines: list[str] = []
    top_weights: list[float] = []
    for item in top:
        value = float(item["usd_value"])
        weight = (value / float(total_value) * 100) if total_value > 0 else 0.0
        top_weights.append(weight)
        locked_note = " | some locked" if item["locked"] > 0 else ""
        wrapped_note = " | includes LD balances" if item["wrapped"] else ""
        top_lines.append(f"{item['asset']} ~${value:,.2f} ({weight:.1f}%){locked_note}{wrapped_note}")

    concentration = top_weights[0] if top_weights else 0.0
    if total_value <= 0:
        verdict = "Thin snapshot. No visible balance value."
        quality = "Thin"
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
    posture_note = "defensive" if stable_pct >= 55 else "risk-on" if stable_pct <= 20 else "mixed"

    risk_lines: list[str] = []
    if total_value <= 0:
        risk_lines.append("No priced Spot balances were visible, so the portfolio read stays incomplete.")
    if concentration >= 70:
        risk_lines.append("Top holding concentration is high enough that one move can dominate portfolio performance.")
    if stable_pct <= 10 and total_value > 0:
        risk_lines.append("Stablecoin dry powder looks thin, so flexibility may be lower if market conditions change quickly.")
    if locked_assets > 0:
        risk_lines.append("Some balances are locked, so immediately available exposure is lower than gross holdings suggest.")
    if unmapped_assets:
        risk_lines.append(f"Some asset codes still need mapping for cleaner valuation: {', '.join(sorted(set(unmapped_assets))[:5])}.")
    if not risk_lines:
        risk_lines.append("This is an estimated read-only snapshot, not a full PnL or cost-basis analysis.")

    lead_groups = ", ".join(f"{name} {pct:.1f}%" for name, pct in group_mix[:3]) if group_mix else "no clear grouped exposure yet"
    why = (
        f"Estimated visible Spot value is about ${float(total_value):,.2f} across {available_assets} priced asset(s). "
        f"Stablecoins are {stable_pct:.1f}% of the priced snapshot and risk assets are {risk_pct:.1f}%. "
        f"Top concentration is {concentration:.1f}%{' with some locked balances in play' if locked_assets else ''}, which makes the current posture look {posture_note}. "
        f"Lead exposure groups: {lead_groups}."
    )

    tags = [
        RiskTag(name="Account Mode", level="Read-only", note="estimated Spot snapshot"),
        RiskTag(name="Source", level="Binance API", note="signed account read + live price map"),
        RiskTag(name="Assets", level=str(available_assets), note="priced balances"),
    ]
    if concentration > 0:
        tags.append(RiskTag(name="Top Concentration", level="High" if concentration >= 70 else "Medium" if concentration >= 40 else "Low", note=f"{concentration:.1f}%"))
    tags.append(RiskTag(name="Stablecoin Share", level="High" if stable_pct >= 55 else "Medium" if stable_pct >= 20 else "Low", note=f"{stable_pct:.1f}%"))
    if group_mix:
        tags.append(RiskTag(name="Lead Group", level="Info", note=f"{group_mix[0][0]} {group_mix[0][1]:.1f}%"))

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
    if snapshot["top_lines"]:
        brief.beginner_note = "\n".join(snapshot["top_lines"])
    if summary_lines:
        brief.what_to_watch_next = summary_lines[:2] + brief.what_to_watch_next[:2]
    return brief
