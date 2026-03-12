from __future__ import annotations

import hashlib
import hmac
import time
from decimal import Decimal
from typing import Any
from urllib.parse import urlencode

from src.config import settings
from src.models.schemas import AnalysisBrief, RiskTag

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


def analyze_portfolio() -> AnalysisBrief:
    try:
        account = _signed_get(ACCOUNT_INFO_URL, {})
        prices = _load_prices()
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
        verdict = "The account read worked, but there is no visible spot balance value to summarize yet."
        quality = "Thin"
    elif concentration >= 70:
        verdict = "This Spot portfolio is highly concentrated, so one position is dominating the account posture."
        quality = "Concentrated"
    elif concentration >= 40:
        verdict = "This Spot portfolio has a clear lead position, with some diversification underneath it."
        quality = "Moderate"
    else:
        verdict = "This Spot portfolio looks more balanced than single-bet, with value spread across multiple assets."
        quality = "Balanced"

    available_assets = len(priced_assets)
    locked_assets = sum(1 for item in enriched if item["locked"] > 0)
    risk_lines: list[str] = []
    if total_value <= 0:
        risk_lines.append("No priced Spot balances were visible, so the portfolio read stays incomplete.")
    if concentration >= 70:
        risk_lines.append("Top holding concentration is high enough that one move can dominate portfolio performance.")
    if locked_assets > 0:
        risk_lines.append("Some balances are locked, so immediately available exposure is lower than gross holdings suggest.")
    if unmapped_assets:
        risk_lines.append(f"Some asset codes still need mapping for cleaner valuation: {', '.join(sorted(set(unmapped_assets))[:5])}.")
    if not risk_lines:
        risk_lines.append("This is a read-only snapshot, not a full PnL or cost-basis analysis.")

    watch = [
        "whether the top holding keeps growing relative to the rest of the account",
        "whether stablecoin dry powder is high enough to change opportunity posture quickly",
    ]

    why = (
        f"Estimated visible Spot value is about ${float(total_value):,.2f} across {available_assets} priced asset(s). "
        f"Top concentration is {concentration:.1f}%{' with some locked balances in play' if locked_assets else ''}."
    )

    tags = [
        RiskTag(name="Account Mode", level="Read-only", note="Spot account snapshot"),
        RiskTag(name="Assets", level=str(available_assets), note="priced balances"),
    ]
    if concentration > 0:
        tags.append(RiskTag(name="Top Concentration", level="High" if concentration >= 70 else "Medium" if concentration >= 40 else "Low", note=f"{concentration:.1f}%"))

    brief = AnalysisBrief(
        entity="Portfolio: Binance Spot",
        quick_verdict=verdict,
        signal_quality=quality,
        top_risks=risk_lines,
        why_it_matters=why,
        what_to_watch_next=watch,
        risk_tags=tags,
    )
    if top_lines:
        brief.sections = []
        brief.beginner_note = "\n".join(top_lines)
    return brief
