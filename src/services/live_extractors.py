from __future__ import annotations

from datetime import datetime, timezone
import re
from typing import Any

from src.analyzers.thresholds import (
    SIGNAL_AGE_AGING,
    SIGNAL_AGE_STALE,
    WALLET_CONCENTRATION_EXTREME,
    WALLET_CONCENTRATION_HIGH,
)
from src.services.binance_skill_mapping import COMMAND_SKILL_MAP
from src.utils.converters import safe_float as _to_float, safe_int as _to_int


def extract_token_context(raw: dict[str, Any], symbol: str) -> dict[str, Any]:
    token_info = raw.get("query-token-info", {})
    market_rank = raw.get("crypto-market-rank", {})
    signal = raw.get("trading-signal", {})
    audit = raw.get("query-token-audit", {})
    meme_rush = raw.get("meme-rush", {})

    token_view = _token_info_view(token_info, symbol)
    metadata = token_view["metadata"]
    search_item = token_view["search_item"]
    dynamic = token_view["dynamic"]
    resolved_symbol = token_view["symbol"]
    audit_payload = _normalize_audit_keys(audit.get("data", audit))
    audit_flags, audit_risks = _extract_audit_flags_and_risks(audit_payload)
    market_risks = _extract_market_rank_risks(market_rank, resolved_symbol)
    signal_risks = _extract_signal_risks(signal)
    first_signal = _first_item(signal.get("data")) or signal
    signal_age_hours = _signal_age_hours(first_signal)
    signal_freshness = _signal_freshness(signal_age_hours, has_signal_data=_signal_has_live_data(first_signal))
    audit_gate, blocked_reason = _audit_gate_state(audit_payload, audit_flags)
    matched_rank = _best_symbol_match((market_rank.get("data", {}).get("tokens", []) or market_rank.get("tokens", []) or []), _normalize_match_key(resolved_symbol))

    resolved_signal_status = _signal_status(signal, first_signal)
    top_holder_concentration_pct = _pick_number(matched_rank or {}, "holdersTop10Percent", "top10HoldersPercentage")

    context = {
        "symbol": resolved_symbol,
        "display_name": token_view["display_name"],
        "price": token_view["price"],
        "liquidity": token_view["liquidity"],
        "holders": token_view["holders"],
        "volume_24h": token_view["volume_24h"],
        "pct_change_24h": token_view["pct_change_24h"],
        "market_cap": token_view["market_cap"],
        "top_holder_concentration_pct": top_holder_concentration_pct,
        "market_rank_context": _build_market_rank_context(market_rank, resolved_symbol),
        "signal_status": resolved_signal_status,
        "signal_trigger_context": _build_signal_context(signal),
        "audit_flags": audit_flags,
        "major_risks": _merge_risks(signal_risks, audit_risks, market_risks),
        "smart_money_count": _pick_int(first_signal, "smartMoneyCount"),
        "smart_money_holders": token_view["smart_money_holders"],
        "smart_money_holding_pct": token_view["smart_money_holding_pct"],
        "exit_rate": _pick_number(first_signal, "exitRate", "exit_rate"),
        "signal_age_hours": signal_age_hours,
        "signal_freshness": signal_freshness,
        "audit_gate": audit_gate,
        "blocked_reason": blocked_reason,
    }

    # --- Dynamic data enrichment (buy/sell pressure, momentum, holder quality) ---
    if dynamic:
        vol_buy = _pick_number(dynamic, "volume24hBuy")
        vol_sell = _pick_number(dynamic, "volume24hSell")
        if vol_buy + vol_sell > 0:
            context["buy_sell_ratio"] = round(vol_buy / (vol_buy + vol_sell), 3)
        context["volume_5m"] = _pick_number(dynamic, "volume5m")
        context["volume_1h"] = _pick_number(dynamic, "volume1h")
        context["volume_4h"] = _pick_number(dynamic, "volume4h")
        context["volume_24h"] = _pick_number(dynamic, "volume24h")
        context["pct_change_5m"] = _pick_number(dynamic, "percentChange5m")
        context["pct_change_1h"] = _pick_number(dynamic, "percentChange1h")
        context["pct_change_4h"] = _pick_number(dynamic, "percentChange4h")
        context["pct_change_24h"] = _pick_number(dynamic, "percentChange24h")
        context["tx_count_24h"] = _pick_int(dynamic, "count24h")
        context["tx_buy_count_24h"] = _pick_int(dynamic, "count24hBuy")
        context["tx_sell_count_24h"] = _pick_int(dynamic, "count24hSell")
        context["fdv"] = _pick_number(dynamic, "fdv")
        context["market_cap"] = _pick_number(dynamic, "marketCap")
        context["circulating_supply"] = _pick_number(dynamic, "circulatingSupply")
        context["total_supply"] = _pick_number(dynamic, "totalSupply")
        context["price_high_24h"] = _pick_number(dynamic, "priceHigh24h")
        context["price_low_24h"] = _pick_number(dynamic, "priceLow24h")
        context["kol_holders"] = _pick_int(dynamic, "kolHolders")
        context["kol_holding_pct"] = _pick_number(dynamic, "kolHoldingPercent")
        context["pro_holders"] = _pick_int(dynamic, "proHolders")
        context["pro_holding_pct"] = _pick_number(dynamic, "proHoldingPercent")
        context["smart_money_holders"] = _pick_int(dynamic, "smartMoneyHolders")
        context["smart_money_holding_pct"] = _pick_number(dynamic, "smartMoneyHoldingPercent")

    # --- Smart money inflow match ---
    inflow_match = _matched_smart_money_inflow(market_rank, resolved_symbol)
    if inflow_match:
        context["smart_money_inflow_usd"] = _pick_number(inflow_match, "inflow")
        context["smart_money_inflow_traders"] = _pick_int(inflow_match, "traders")
    context.update(_bridge_runtime_context(raw, "token"))

    spot = raw.get("spot", {})
    if spot:
        ticker = spot.get("ticker", spot)
        context["cex_price"] = _pick_number(ticker, "lastPrice")
        context["cex_volume_24h"] = _pick_number(ticker, "volume", "quoteVolume")
        context["cex_price_change_pct_24h"] = _pick_number(ticker, "priceChangePercent")
        depth = spot.get("depth", {})
        if depth:
            bids = depth.get("bids", [])
            asks = depth.get("asks", [])
            if bids:
                context["spot_bid_depth"] = len(bids)
                context["spot_top_bid"] = _to_float(bids[0][0]) if bids and len(bids[0]) > 0 else 0.0
            if asks:
                context["spot_ask_depth"] = len(asks)
                context["spot_top_ask"] = _to_float(asks[0][0]) if asks and len(asks[0]) > 0 else 0.0

        s_kline = spot.get("kline", {}).get("data", []) if isinstance(spot.get("kline", {}), dict) else spot.get("kline", [])
        if s_kline:
            context["spot_kline_candles"] = len(s_kline)
            if len(s_kline) > 0 and len(s_kline[-1]) >= 5:
                context["spot_kline_latest_close"] = _to_float(s_kline[-1][4])

        s_trades = spot.get("recent_trades", {}).get("data", []) if isinstance(spot.get("recent_trades", {}), dict) else spot.get("recent_trades", [])
        if s_trades:
            context["spot_recent_trades_count"] = len(s_trades)

    # --- K-Line (candlestick) data ---
    token_payload = raw.get("query-token-info", {})
    kline = token_payload.get("kline", [])
    if kline:
        context.update(_token_kline_context(kline))

    alpha_data = raw.get("alpha", {})
    if alpha_data:
        context["is_alpha_listed"] = bool(alpha_data.get("is_alpha_listed", False))
        ticker = alpha_data.get("ticker", {})
        if ticker:
            context["alpha_price"] = _pick_number(ticker, "lastPrice", "price")
            context["alpha_volume_24h"] = _pick_number(ticker, "volume", "quoteVolume")
            
        a_kline = alpha_data.get("kline", [])
        if a_kline:
            context["alpha_kline_candles"] = len(a_kline)
            if len(a_kline) > 0 and len(a_kline[-1]) >= 5:
                context["alpha_kline_latest_close"] = _to_float(a_kline[-1][4])

    futures = raw.get("derivatives-trading-usds-futures", {})
    if futures:
        _enrich_futures_sentiment(context, futures)

    meme_snapshot = _token_meme_snapshot(meme_rush, token_view, resolved_symbol)
    if meme_snapshot:
        context.update(meme_snapshot)

    if _token_has_top_trader_interest(market_rank, resolved_symbol):
        context["top_trader_interest"] = True

    return context


def extract_wallet_context(raw: dict[str, Any], address: str) -> dict[str, Any]:
    address_info = raw.get("query-address-info", {})
    items = address_info.get("list") or address_info.get("data", {}).get("list") or []

    if not items and (address_info.get("top_holdings") or address_info.get("portfolio_value") is not None):
        holdings_count = _to_int(address_info.get("holdings_count"))
        portfolio_value = _to_float(address_info.get("portfolio_value"))
        top_holdings = address_info.get("top_holdings", [])
        top_concentration_pct = _to_float(address_info.get("top_concentration_pct"))
        change_24h = _to_float(address_info.get("change_24h"))
        major_risks = [str(x) for x in address_info.get("major_risks", [])]
        if holdings_count <= 0 and top_holdings:
            holdings_count = len(top_holdings)
        if not major_risks and not top_holdings and portfolio_value <= 0:
            major_risks = ["Thin payload."]
        context = {
            "address": address,
            "portfolio_value": portfolio_value,
            "holdings_count": holdings_count,
            "top_holdings": top_holdings,
            "top_concentration_pct": top_concentration_pct,
            "change_24h": change_24h,
            "notable_exposures": [str(x) for x in address_info.get("notable_exposures", [])],
            "major_risks": major_risks,
            "style_profile": str(address_info.get("style_profile", "")),
            "exposure_breakdown": [str(x) for x in address_info.get("exposure_breakdown", [])],
            "risky_holdings_count": _to_int(address_info.get("risky_holdings_count")),
            "holdings_audit_notes": [str(x) for x in address_info.get("holdings_audit_notes", [])],
        }
        context.update(_bridge_runtime_context(raw, "wallet"))
        return context

    holdings = []
    portfolio_value = 0.0
    biggest = 0.0
    exposure_weights: dict[str, float] = {}
    symbol_weights: list[tuple[str, float]] = []
    for item in items:
        symbol = str(item.get("symbol", "UNKNOWN"))
        price = _to_float(item.get("price"))
        qty = _to_float(item.get("remainQty"))
        value = price * qty
        portfolio_value += value
        biggest = max(biggest, value)
        change_24h = _to_float(item.get("percentChange24h"))
        holdings.append({"symbol": symbol, "value": value, "change_24h": change_24h})
        symbol_weights.append((symbol, value))
        bucket = _wallet_exposure_bucket(symbol)
        exposure_weights[bucket] = exposure_weights.get(bucket, 0.0) + value

    top_holdings = []
    if portfolio_value > 0:
        holdings.sort(key=lambda x: x["value"], reverse=True)
        for item in holdings[:5]:
            top_holdings.append({"symbol": item["symbol"], "weight_pct": (item["value"] / portfolio_value) * 100})

    change_24h = 0.0
    volatility_24h = 0.0
    if portfolio_value > 0:
        weighted_change = 0.0
        weighted_volatility = 0.0
        for item in holdings:
            weighted_change += item["value"] * item["change_24h"]
            weighted_volatility += item["value"] * abs(item["change_24h"])
        change_24h = weighted_change / portfolio_value
        volatility_24h = weighted_volatility / portfolio_value

    top_concentration_pct = (biggest / portfolio_value) * 100 if portfolio_value > 0 else 0.0
    notable_exposures = [name for name, value in sorted(exposure_weights.items(), key=lambda pair: pair[1], reverse=True) if value > 0][:5]
    exposure_breakdown = []
    if portfolio_value > 0:
        for name, value in sorted(exposure_weights.items(), key=lambda pair: pair[1], reverse=True)[:4]:
            exposure_breakdown.append(f"{name} {(value / portfolio_value) * 100:.1f}%")

    risks: list[str] = []
    if top_concentration_pct >= WALLET_CONCENTRATION_HIGH:
        risks.append("Wallet is highly concentrated in one token or theme.")
    if portfolio_value > 0 and len(exposure_weights) <= 1 and len(items) >= 3:
        risks.append("Wallet diversification is weaker than the holding count first suggests because exposures cluster into one theme.")
    if volatility_24h >= 15:
        risks.append(f"Aggregate wallet volatility is very high at {volatility_24h:.1f}%.")

    style_profile = _wallet_style_profile(top_concentration_pct, len(items), exposure_weights, change_24h)
    style_bits: list[str] = []
    if notable_exposures:
        style_bits.append(f"Narrative bias: {', '.join(notable_exposures[:2])}")
    if style_profile:
        style_bits.append(f"Style profile: {style_profile}")
    if top_concentration_pct >= WALLET_CONCENTRATION_EXTREME:
        style_bits.append("Risk posture: concentrated")
    elif len(items) >= 5 and len(exposure_weights) >= 2 and top_concentration_pct < WALLET_CONCENTRATION_HIGH:
        style_bits.append("Risk posture: diversified")
    else:
        style_bits.append("Risk posture: mixed")
    style_read = " | ".join(style_bits)

    risky_holdings_count, holdings_audit_notes = _wallet_audit_overlay(raw, [item["symbol"] for item in holdings[:5]])
    if risky_holdings_count > 0:
        risks.extend(holdings_audit_notes[:2])

    if portfolio_value >= 100_000 and top_concentration_pct < WALLET_CONCENTRATION_HIGH and len(items) >= 5 and len(exposure_weights) >= 2 and risky_holdings_count == 0:
        follow_verdict = "Track"
    elif portfolio_value > 0 or len(items) > 0:
        follow_verdict = "Unknown"
    else:
        follow_verdict = "Don't follow"

    context = {
        "address": address,
        "portfolio_value": portfolio_value,
        "holdings_count": len(items),
        "top_holdings": top_holdings,
        "top_concentration_pct": top_concentration_pct,
        "change_24h": change_24h,
        "volatility_24h": volatility_24h,
        "notable_exposures": notable_exposures[:5],
        "major_risks": risks,
        "follow_verdict": follow_verdict,
        "style_read": style_read,
        "style_profile": style_profile,
        "exposure_breakdown": exposure_breakdown,
        "risky_holdings_count": risky_holdings_count,
        "holdings_audit_notes": holdings_audit_notes,
    }
    context.update(_bridge_runtime_context(raw, "wallet"))
    return context


def extract_watch_today_context(raw: dict[str, Any]) -> dict[str, Any]:
    market_rank = raw.get("crypto-market-rank", {})
    meme_rush = raw.get("meme-rush", {})
    signal = raw.get("trading-signal", {})

    top_narratives = _extract_top_narratives(market_rank, meme_rush)
    strongest_signals = _extract_strongest_signals(signal)
    risk_zones = _extract_risk_zones(market_rank, meme_rush)
    trending_now = _extract_trending_now(market_rank)
    smart_money_flow = _extract_smart_money_flow(market_rank, signal)
    social_hype = _extract_social_hype(market_rank)
    meme_watch = _extract_meme_watch(meme_rush)
    exchange_board = _extract_watchtoday_exchange_board(market_rank)

    if not strongest_signals and exchange_board:
        strongest_signals = [f"{exchange_board[0]} — exchange-led momentum read"]
    if not trending_now and exchange_board:
        trending_now = exchange_board[:2]
    if not smart_money_flow and strongest_signals:
        smart_money_flow = strongest_signals[:3]
    if not social_hype:
        if trending_now:
            social_hype = trending_now[:2]
        elif top_narratives:
            social_hype = [f"{item} — narrative attention visible" for item in top_narratives[:2]]
    if not meme_watch and top_narratives:
        meme_watch = [f"{item} — narrative/meme crossover watch" for item in top_narratives[:2] if any(x in item.lower() for x in ["meme", "dog", "frog", "community", "ai"])]
    top_picks = _extract_top_picks(trending_now, strongest_signals, top_narratives, exchange_board)
    if not top_picks:
        top_picks = _extract_top_picks(trending_now, strongest_signals, top_narratives, exchange_board)

    context = {
        "top_narratives": top_narratives,
        "strongest_signals": strongest_signals,
        "risk_zones": risk_zones,
        "market_takeaway": _build_market_rank_context(market_rank) or _extract_topic_summary(meme_rush),
        "major_risks": _merge_risks(_extract_market_rank_risks(market_rank), _extract_meme_risks(meme_rush), _extract_signal_risks(signal)),
        "trending_now": trending_now,
        "smart_money_flow": smart_money_flow,
        "social_hype": social_hype,
        "meme_watch": meme_watch,
        "top_picks": top_picks,
        "exchange_board": exchange_board,
    }
    context.update(_bridge_runtime_context(raw, "watchtoday"))

    futures = raw.get("derivatives-trading-usds-futures", {})
    if futures:
        futures_lines: list[str] = []
        for sym in ("BTC", "ETH", "BNB", "SOL"):
            data = futures.get(sym)
            if not isinstance(data, dict):
                continue
            rate = data.get("funding_rate", 0.0)
            sentiment = "bullish" if rate < -0.0001 else "bearish" if rate > 0.0003 else "neutral"
            rate_pct = rate * 100
            futures_lines.append(f"{sym} funding {rate_pct:+.4f}% ({sentiment})")
        if futures_lines:
            context["futures_sentiment"] = futures_lines
            risk_zones = context.get("risk_zones", [])
            for line in futures_lines:
                if "bearish" in line:
                    risk_zones.append(f"{line} — elevated short squeeze or crowded longs risk")
            context["risk_zones"] = risk_zones

    # --- Top traders from address PnL leaderboard ---
    top_traders_raw = market_rank.get("top_traders", []) or []
    if top_traders_raw:
        top_traders_lines: list[str] = []
        for trader in top_traders_raw[:5]:
            label = trader.get("addressLabel") or _short_addr(str(trader.get("address", "")))
            pnl = _pick_number(trader, "realizedPnl")
            win_rate = _pick_number(trader, "winRate")
            top_tokens = trader.get("topEarningTokens", []) or []
            top_symbols = [str(t.get("tokenSymbol", "")) for t in top_tokens[:3] if t.get("tokenSymbol")]
            parts = [str(label)]
            if pnl:
                parts.append(f"PnL {_human_money_short(pnl)}")
            if win_rate:
                parts.append(f"WR {win_rate:.0f}%")
            if top_symbols:
                parts.append(f"top: {', '.join(top_symbols)}")
            top_traders_lines.append(" — ".join(parts))
        if top_traders_lines:
            context["top_traders"] = top_traders_lines

    return context


def extract_signal_context(raw: dict[str, Any], token: str) -> dict[str, Any]:
    token_info = raw.get("query-token-info", {})
    market_rank = raw.get("crypto-market-rank", {})
    signal = raw.get("trading-signal", {})
    futures = raw.get("derivatives-trading-usds-futures", {})
    first_signal = _first_item(signal.get("data")) or signal
    audit = raw.get("query-token-audit", {})
    audit_payload = _normalize_audit_keys(audit.get("data", audit))
    audit_flags, audit_risks = _extract_audit_flags_and_risks(audit_payload)
    token_view = _token_info_view(token_info, token)
    resolved_symbol = token_view["symbol"]
    futures_snapshot = _futures_snapshot(futures)
    inflow_match = _matched_smart_money_inflow(market_rank, resolved_symbol)

    direction = str(first_signal.get("direction", "")).lower()
    status = _signal_status(signal, first_signal)
    if first_signal == signal and not signal.get("data"):
        status = "unmatched"
    supporting_context = _build_signal_context(signal)
    signal_age_hours = _signal_age_hours(first_signal)
    signal_freshness = _signal_freshness(signal_age_hours, has_signal_data=_signal_has_live_data(first_signal))
    audit_gate, blocked_reason = _audit_gate_state(audit_payload, audit_flags)

    context = {
        "token": first_signal.get("ticker") or resolved_symbol or token,
        "signal_status": status,
        "trigger_price": _pick_number(first_signal, "alertPrice", "trigger_price"),
        "current_price": _pick_number(first_signal, "currentPrice", "current_price") or token_view["price"],
        "max_gain": _pick_number(first_signal, "maxGain", "max_gain"),
        "exit_rate": _pick_number(first_signal, "exitRate", "exit_rate"),
        "liquidity": token_view["liquidity"],
        "holders": token_view["holders"],
        "volume_24h": token_view["volume_24h"],
        "pct_change_24h": token_view["pct_change_24h"],
        "market_cap": token_view["market_cap"],
        "audit_flags": audit_flags,
        "supporting_context": supporting_context,
        "major_risks": _merge_risks(_extract_signal_risks(signal), _extract_market_rank_risks(market_rank, resolved_symbol), audit_risks, futures_snapshot.get("major_risks", [])),
        "smart_money_count": _pick_int(first_signal, "smartMoneyCount"),
        "smart_money_holders": token_view["smart_money_holders"],
        "smart_money_holding_pct": token_view["smart_money_holding_pct"],
        "smart_money_inflow_usd": _pick_number(inflow_match or {}, "inflow"),
        "signal_age_hours": signal_age_hours,
        "signal_freshness": signal_freshness,
        "audit_gate": audit_gate,
        "blocked_reason": blocked_reason,
        "funding_rate": _to_float(futures_snapshot.get("funding_rate")),
        "long_short_ratio": _to_float(futures_snapshot.get("long_short_ratio")),
        "funding_sentiment": str(futures_snapshot.get("funding_sentiment", "")),
    }
    context.update(_bridge_runtime_context(raw, "signal"))
    return context


def extract_audit_context(raw: dict[str, Any], symbol: str) -> dict[str, Any]:
    token_info = raw.get("query-token-info", {})
    signal = raw.get("trading-signal", {})
    audit = raw.get("query-token-audit", {})
    audit_payload = _normalize_audit_keys(audit.get("data", audit))
    token_view = _token_info_view(token_info, symbol)
    display_symbol = str(token_view["symbol"] or symbol)
    display_name = str(token_view["display_name"] or display_symbol)
    audit_flags, audit_risks = _extract_audit_flags_and_risks(audit_payload)
    audit_gate, blocked_reason = _audit_gate_state(audit_payload, audit_flags)
    extra = audit_payload.get("extraInfo") or {}
    buy_tax = _to_float(extra.get("buyTax"))
    sell_tax = _to_float(extra.get("sellTax"))
    risk_level = str(audit_payload.get("riskLevelEnum") or ("HIGH" if audit_gate == "BLOCK" else "MEDIUM" if audit_gate == "WARN" else "LOW")).title()
    first_signal = _first_item(signal.get("data")) or signal
    signal_status = _signal_status(signal, first_signal)
    signal_age_hours = _signal_age_hours(first_signal)
    signal_freshness = _signal_freshness(signal_age_hours, has_signal_data=_signal_has_live_data(first_signal))
    summary_bits: list[str] = []
    if audit_payload.get("hasResult") and audit_payload.get("isSupported"):
        summary_bits.append(f"Risk level {audit_payload.get('riskLevel', 0)} ({risk_level.upper()})")
    if buy_tax > 0 or sell_tax > 0:
        summary_bits.append(f"Buy tax {buy_tax:.2f}% | Sell tax {sell_tax:.2f}%")
    if not summary_bits:
        summary_bits.append(blocked_reason or "Audit output is limited right now.")

    context = {
        "symbol": display_symbol,
        "display_name": display_name,
        "audit_gate": audit_gate,
        "blocked_reason": blocked_reason,
        "audit_flags": audit_flags,
        "major_risks": _merge_risks(audit_risks),
        "risk_level": risk_level,
        "audit_summary": "; ".join(summary_bits),
        "has_result": bool(audit_payload.get("hasResult")),
        "is_supported": bool(audit_payload.get("isSupported")),
        "price": token_view["price"],
        "liquidity": token_view["liquidity"],
        "volume_24h": token_view["volume_24h"],
        "market_cap": token_view["market_cap"],
        "buy_tax": buy_tax,
        "sell_tax": sell_tax,
        "signal_status": signal_status,
        "smart_money_count": _pick_int(first_signal, "smartMoneyCount"),
        "signal_age_hours": signal_age_hours,
        "signal_freshness": signal_freshness,
    }
    context.update(_bridge_runtime_context(raw, "audit"))
    return context


def extract_meme_context(raw: dict[str, Any], symbol: str) -> dict[str, Any]:
    token = extract_token_context(raw, symbol)
    token_info = raw.get("query-token-info", {})
    market_rank = raw.get("crypto-market-rank", {})
    signal = raw.get("trading-signal", {})
    meme_rush = raw.get("meme-rush", {})
    first_signal = _first_item(signal.get("data")) or {}
    metadata = token_info.get("metadata", {}) or {}
    search_item = _best_token_match(token_info.get("search"), symbol, metadata) or metadata or {}
    market_tokens = market_rank.get("data", {}).get("tokens", []) or market_rank.get("tokens", []) or []
    matched_rank = _best_symbol_match(market_tokens, _normalize_match_key(token.get("symbol", symbol))) if market_tokens else None
    meme_items = meme_rush.get("data", []) or meme_rush.get("tokens", []) or []
    matched_meme = _best_symbol_match(meme_items, _normalize_match_key(token.get("symbol", symbol))) if meme_items else None

    launch_platform = str(first_signal.get("launchPlatform") or search_item.get("launchPlatform") or metadata.get("launchPlatform") or "")
    is_alpha = bool(first_signal.get("isAlpha"))
    status = str(first_signal.get("status") or "").lower()
    exit_rate = _pick_number(first_signal, "exitRate", "exit_rate")
    progress = _pick_number(first_signal, "progress")
    top_holder_concentration_pct = _pick_number(matched_rank or {}, "holdersTop10Percent", "top10HoldersPercentage") or _pick_number(matched_meme or {}, "holdersTop10Percent")
    social_brief = ""
    if matched_rank:
        social_info = matched_rank.get("socialHypeInfo") or {}
        social_brief = str(social_info.get("socialSummaryBriefTranslated") or social_info.get("socialSummaryBrief") or "")
    meme_score = _pick_number(matched_meme or {}, "topicHeatScore", "score")

    tag_values = []
    for source in (search_item.get("tokenTag") or {}, metadata.get("tokenTag") or {}):
        if isinstance(source, dict):
            tag_values.extend([str(k).lower() for k in source.keys()])
    market_context = str(token.get("market_rank_context", "")).lower()
    symbol_upper = str(token.get("symbol", symbol)).upper()
    display_name = str(token.get("display_name", symbol))

    meme_like = any(x in market_context for x in ["meme", "community"]) or any(x in " ".join(tag_values) for x in ["meme", "community", "dog", "frog"])
    if social_brief and any(x in social_brief.lower() for x in ["meme", "community", "viral", "trend"]):
        meme_like = True
    known_meme_symbols = {"DOGE", "SHIB", "PEPE", "BONK", "FLOKI", "WIF"}
    if symbol_upper in known_meme_symbols:
        meme_like = True

    lifecycle = "unknown"
    if progress >= 90:
        lifecycle = "finalizing"
    elif status in {"timeout", "exitrate", "exited"} or exit_rate >= 70:
        lifecycle = "late"
    elif status in {"valid", "watch", "bullish", "triggered", "active"} or token.get("smart_money_count", 0) > 0:
        lifecycle = "active"
    elif meme_like or meme_score > 0:
        lifecycle = "attention"

    risks = list(token.get("major_risks", []))
    if top_holder_concentration_pct >= 85:
        risks.append(f"Top-holder concentration is extreme at {top_holder_concentration_pct:.1f}%.")
    elif top_holder_concentration_pct >= 70:
        risks.append(f"Top-holder concentration is high at {top_holder_concentration_pct:.1f}%.")
    if not meme_like:
        risks.insert(0, "This asset does not currently read as a clear meme candidate from the available live context.")

    context = {
        "symbol": token.get("symbol", symbol),
        "display_name": display_name,
        "price": token.get("price", 0.0),
        "liquidity": token.get("liquidity", 0.0),
        "market_rank_context": token.get("market_rank_context", ""),
        "signal_status": token.get("signal_status", "unknown"),
        "audit_flags": token.get("audit_flags", []),
        "major_risks": _unique(risks),
        "smart_money_count": token.get("smart_money_count", 0),
        "exit_rate": token.get("exit_rate", 0.0),
        "signal_age_hours": token.get("signal_age_hours", 0.0),
        "signal_freshness": token.get("signal_freshness", "UNKNOWN"),
        "audit_gate": token.get("audit_gate", "ALLOW"),
        "blocked_reason": token.get("blocked_reason", ""),
        "launch_platform": launch_platform,
        "is_alpha": is_alpha,
        "lifecycle_stage": lifecycle,
        "bonded_progress": progress,
        "meme_score": meme_score,
        "social_brief": social_brief,
        "top_holder_concentration_pct": top_holder_concentration_pct,
    }
    context.update(_bridge_runtime_context(raw, "meme"))
    return context


def extract_alpha_context(raw: dict[str, Any], symbol: str) -> dict[str, Any]:
    alpha = raw.get("alpha", {})
    token_info = raw.get("query-token-info", {})
    audit = raw.get("query-token-audit", {})
    spot = raw.get("spot", {})
    token_list = alpha.get("token_list") or []

    metadata = token_info.get("metadata", {})
    alpha_match = None
    if symbol:
        for item in token_list:
            if not isinstance(item, dict):
                continue
            item_symbol = str(item.get("symbol") or "").upper()
            if item_symbol and item_symbol == str(symbol).upper():
                alpha_match = item
                break
    search_item = _best_token_match(token_info.get("search"), symbol, metadata) or metadata or token_info
    resolved_symbol = str((alpha_match or {}).get("symbol") or search_item.get("symbol") or metadata.get("symbol") or symbol)
    display_name = str((alpha_match or {}).get("name") or search_item.get("name") or metadata.get("name") or resolved_symbol or "Binance Alpha")
    audit_payload = _normalize_audit_keys(audit.get("data", audit))
    audit_flags, audit_risks = _extract_audit_flags_and_risks(audit_payload)
    audit_gate, blocked_reason = _audit_gate_state(audit_payload, audit_flags)

    is_alpha_listed = bool(alpha_match) or bool(alpha.get("is_alpha_listed", False))
    ticker = alpha.get("ticker", {})

    context: dict[str, Any] = {
        "symbol": resolved_symbol,
        "display_name": display_name,
        "is_alpha_listed": is_alpha_listed,
        "alpha_token_list": token_list,
        "alpha_listed_count": len(token_list),
        "alpha_rank_score": _to_float((alpha_match or {}).get("score")),
        "alpha_id": str((alpha_match or {}).get("alphaId") or ""),
        "alpha_market_cap": _to_float((alpha_match or {}).get("marketCap")),
        "alpha_fdv": _to_float((alpha_match or {}).get("fdv")),
        "alpha_liquidity": _to_float((alpha_match or {}).get("liquidity")),
        "alpha_holders": _to_int((alpha_match or {}).get("holders")),
        "alpha_listing_time": _to_int((alpha_match or {}).get("listingTime")),
        "alpha_price": _pick_number(alpha_match or ticker, "price", "lastPrice"),
        "alpha_volume_24h": _pick_number(alpha_match or ticker, "volume24h", "volume", "quoteVolume"),
        "alpha_price_change_24h": _pick_number(alpha_match or ticker, "percentChange24h", "priceChangePercent"),
        "alpha_high_24h": _pick_number(alpha_match or ticker, "priceHigh24h", "highPrice"),
        "alpha_low_24h": _pick_number(alpha_match or ticker, "priceLow24h", "lowPrice"),
        "audit_gate": audit_gate,
        "blocked_reason": blocked_reason,
        "audit_flags": audit_flags,
        "major_risks": _merge_risks(audit_risks),
    }

    if spot:
        context["cex_price"] = _pick_number(spot, "lastPrice")
        context["cex_volume_24h"] = _pick_number(spot, "volume", "quoteVolume")

    context.update(_bridge_runtime_context(raw, "alpha"))
    return context


def extract_futures_context(raw: dict[str, Any], symbol: str) -> dict[str, Any]:
    futures = raw.get("derivatives-trading-usds-futures", {})
    token_info = raw.get("query-token-info", {})
    token_view = _token_info_view(token_info, symbol)
    resolved_symbol = token_view["symbol"]
    snapshot = _futures_snapshot(futures)

    context: dict[str, Any] = {
        "symbol": resolved_symbol,
        "funding_rate": _to_float(snapshot.get("funding_rate")),
        "funding_rate_sentiment": str(snapshot.get("funding_sentiment", "neutral")),
        "open_interest": _to_float(snapshot.get("open_interest")),
        "long_short_ratio": _to_float(snapshot.get("long_short_ratio")),
        "taker_buy_sell_ratio": _to_float(snapshot.get("taker_buy_sell_ratio")),
        "taker_buy_volume_1d": _to_float(snapshot.get("taker_buy_volume_1d")),
        "taker_sell_volume_1d": _to_float(snapshot.get("taker_sell_volume_1d")),
        "top_trader_long_short_ratio": _to_float(snapshot.get("top_trader_long_short_ratio")),
        "mark_price": _to_float(snapshot.get("mark_price")),
        "index_price": _to_float(snapshot.get("index_price")),
        "major_risks": [str(x) for x in snapshot.get("major_risks", [])],
    }
    if snapshot.get("ticker_volume_24h"):
        context["futures_ticker_volume_24h"] = _to_float(snapshot.get("ticker_volume_24h"))
    if snapshot.get("price_change_pct_24h"):
        context["futures_price_change_pct_24h"] = _to_float(snapshot.get("price_change_pct_24h"))
    if snapshot.get("kline_candles"):
        context["futures_kline_candles"] = _to_int(snapshot.get("kline_candles"))
        context["futures_kline_latest_close"] = _to_float(snapshot.get("kline_latest_close"))
    context.update(_bridge_runtime_context(raw, "futures"))
    return context


def _enrich_futures_sentiment(context: dict[str, Any], futures: dict[str, Any]) -> None:
    snapshot = _futures_snapshot(futures)
    context["futures_funding_rate"] = _to_float(snapshot.get("funding_rate"))
    context["futures_open_interest"] = _to_float(snapshot.get("open_interest"))
    context["futures_long_short_ratio"] = _to_float(snapshot.get("long_short_ratio"))
    context["futures_taker_buy_sell_ratio"] = _to_float(snapshot.get("taker_buy_sell_ratio"))
    context["futures_taker_buy_volume_1d"] = _to_float(snapshot.get("taker_buy_volume_1d"))
    context["futures_taker_sell_volume_1d"] = _to_float(snapshot.get("taker_sell_volume_1d"))
    context["futures_top_trader_long_short_ratio"] = _to_float(snapshot.get("top_trader_long_short_ratio"))
    context["futures_mark_price"] = _to_float(snapshot.get("mark_price"))
    if snapshot.get("ticker_volume_24h"):
        context["futures_ticker_volume_24h"] = _to_float(snapshot.get("ticker_volume_24h"))
    if snapshot.get("price_change_pct_24h"):
        context["futures_price_change_pct_24h"] = _to_float(snapshot.get("price_change_pct_24h"))
    if snapshot.get("kline_candles"):
        context["futures_kline_candles"] = _to_int(snapshot.get("kline_candles"))
        context["futures_kline_latest_close"] = _to_float(snapshot.get("kline_latest_close"))
    context["futures_sentiment"] = str(snapshot.get("funding_sentiment", "neutral"))

    risks = list(context.get("major_risks", []))
    risks.extend([str(x) for x in snapshot.get("major_risks", [])])
    context["major_risks"] = _unique(risks)


def _futures_snapshot(futures: dict[str, Any]) -> dict[str, Any]:
    mark = futures.get("mark_price", {})
    funding = futures.get("funding_rate", {})
    oi = futures.get("open_interest", {})
    ls = futures.get("long_short_ratio", {})
    taker = futures.get("taker_volume", {})
    top_ls = futures.get("top_trader_ls", {})
    ticker = futures.get("ticker", {})
    kline = futures.get("kline", {}).get("data", []) if isinstance(futures.get("kline", {}), dict) else futures.get("kline", [])

    rate_items = funding.get("data", []) if isinstance(funding.get("data"), list) else []
    last_rate = float(rate_items[-1].get("fundingRate", 0)) if rate_items else 0.0
    long_short_items = ls.get("data", []) if isinstance(ls.get("data"), list) else []
    last_ls_ratio = float(long_short_items[-1].get("longShortRatio", 1.0)) if long_short_items else 1.0

    taker_items = taker.get("data", []) if isinstance(taker.get("data"), list) else []
    last_taker_ratio = float(taker_items[-1].get("buySellRatio", 1.0)) if taker_items else 1.0
    last_taker_buy = float(taker_items[-1].get("buyVol", 0.0)) if taker_items else 0.0
    last_taker_sell = float(taker_items[-1].get("sellVol", 0.0)) if taker_items else 0.0

    top_ls_items = top_ls.get("data", []) if isinstance(top_ls.get("data"), list) else []
    last_top_ls_ratio = float(top_ls_items[-1].get("longShortRatio", 1.0)) if top_ls_items else 1.0

    if last_rate < -0.0001:
        funding_sentiment = "bullish"
    elif last_rate > 0.0003:
        funding_sentiment = "bearish"
    else:
        funding_sentiment = "neutral"

    risks: list[str] = []
    if abs(last_rate) > 0.001:
        risks.append(f"Funding rate is extreme at {last_rate * 100:+.4f}% — liquidation cascades possible.")
    if last_ls_ratio > 2.5:
        risks.append(f"Long/short ratio is {last_ls_ratio:.2f} — crowded longs risk.")
    elif 0 < last_ls_ratio < 0.5:
        risks.append(f"Long/short ratio is {last_ls_ratio:.2f} — crowded shorts risk.")

    snapshot = {
        "funding_rate": last_rate,
        "funding_sentiment": funding_sentiment,
        "open_interest": _to_float(oi.get("openInterest")),
        "long_short_ratio": last_ls_ratio,
        "taker_buy_sell_ratio": last_taker_ratio,
        "taker_buy_volume_1d": last_taker_buy,
        "taker_sell_volume_1d": last_taker_sell,
        "top_trader_long_short_ratio": last_top_ls_ratio,
        "mark_price": _to_float(mark.get("markPrice")),
        "index_price": _to_float(mark.get("indexPrice")),
        "major_risks": risks,
    }

    if ticker:
        snapshot["ticker_volume_24h"] = _pick_number(ticker, "volume", "quoteVolume")
        snapshot["price_change_pct_24h"] = _pick_number(ticker, "priceChangePercent")

    if kline:
        snapshot["kline_candles"] = len(kline)
        if len(kline[-1]) >= 5:
            snapshot["kline_latest_close"] = _to_float(kline[-1][4])

    return snapshot


def _token_info_view(token_info: dict[str, Any], symbol: str) -> dict[str, Any]:
    metadata = token_info.get("metadata", {})
    search_item = _best_token_match(token_info.get("search"), symbol, metadata) or metadata or token_info
    dynamic = token_info.get("dynamic", {})
    resolved_symbol = str(search_item.get("symbol") or metadata.get("symbol") or token_info.get("symbol") or symbol)
    return {
        "metadata": metadata,
        "search_item": search_item,
        "dynamic": dynamic,
        "symbol": resolved_symbol,
        "display_name": str(search_item.get("name") or metadata.get("name") or token_info.get("name") or resolved_symbol),
        "price": _pick_number(dynamic, "price") or _pick_number(search_item, "price"),
        "liquidity": _pick_number(dynamic, "liquidity") or _pick_number(search_item, "liquidity"),
        "holders": _pick_int(dynamic, "holders", "kycHolderCount") or _pick_int(search_item, "holders"),
        "volume_24h": _pick_number(dynamic, "volume24h") or _pick_number(search_item, "volume24h", "volume_24h"),
        "pct_change_24h": _pick_number(dynamic, "percentChange24h", "pctChange24h") or _pick_number(search_item, "percentChange24h", "pct_change_24h"),
        "market_cap": _pick_number(dynamic, "marketCap", "market_cap") or _pick_number(search_item, "marketCap", "market_cap"),
        "smart_money_holders": _pick_int(dynamic, "smartMoneyHolders") or _pick_int(search_item, "smartMoneyHolders", "smart_money_holders"),
        "smart_money_holding_pct": _pick_number(dynamic, "smartMoneyHoldingPercent") or _pick_number(search_item, "smartMoneyHoldingPercent", "smart_money_holding_pct"),
    }


def _matched_smart_money_inflow(market_rank: dict[str, Any], symbol: str) -> dict[str, Any] | None:
    inflow_items = market_rank.get("smart_money_inflow", []) or []
    target = _normalize_match_key(symbol)
    for item in inflow_items:
        item_symbol = _normalize_match_key(str(item.get("tokenName") or item.get("symbol") or ""))
        if item_symbol and item_symbol == target:
            return item
    return None


def _token_kline_context(kline: list[Any]) -> dict[str, Any]:
    context: dict[str, Any] = {"kline_candles": len(kline)}
    latest = kline[-1] if kline else []
    if isinstance(latest, list) and len(latest) >= 5:
        context["kline_latest_close"] = _to_float(latest[3])
        context["kline_latest_volume"] = _to_float(latest[4])
    trend, above_ma20 = _compute_kline_trend(kline)
    if trend:
        context["kline_trend"] = trend
    if kline:
        context["kline_above_ma20"] = above_ma20
    return context


def _compute_kline_trend(candles: list[Any]) -> tuple[str, bool]:
    closes = [_to_float(item[3]) for item in candles if isinstance(item, list) and len(item) >= 4]
    if not closes:
        return "", False
    ma_window = closes[-20:] if len(closes) >= 20 else closes
    ma20 = sum(ma_window) / len(ma_window) if ma_window else 0.0
    recent = closes[-5:] if len(closes) >= 5 else closes
    first_close = recent[0] if recent else 0.0
    last_close = recent[-1] if recent else 0.0
    if first_close > 0 and last_close >= first_close * 1.01:
        trend = "rising"
    elif first_close > 0 and last_close <= first_close * 0.99:
        trend = "falling"
    else:
        trend = "flat"
    return trend, bool(ma20 and closes[-1] >= ma20)


def _token_meme_snapshot(meme_rush: dict[str, Any], token_view: dict[str, Any], symbol: str) -> dict[str, Any]:
    items = meme_rush.get("tokens", []) or meme_rush.get("data", []) or []
    matched = _best_symbol_match(items, _normalize_match_key(symbol)) if items else None
    search_item = token_view["search_item"]
    metadata = token_view["metadata"]

    tag_values: list[str] = []
    for source in (search_item.get("tokenTag") or {}, metadata.get("tokenTag") or {}):
        if isinstance(source, dict):
            tag_values.extend(str(key).lower() for key in source.keys())

    symbol_upper = str(symbol).upper()
    known_meme_symbols = {"DOGE", "SHIB", "PEPE", "BONK", "FLOKI", "WIF"}
    is_meme_candidate = bool(matched) or any(tag in {"meme", "community", "dog", "frog"} for tag in tag_values) or symbol_upper in known_meme_symbols
    if not is_meme_candidate:
        return {}

    progress = _pick_number(matched or {}, "progress")
    migrate_status = _to_int((matched or {}).get("migrateStatus"))
    if migrate_status == 1:
        lifecycle = "migrated"
    elif progress >= 90:
        lifecycle = "finalizing"
    elif progress > 0:
        lifecycle = "active"
    else:
        lifecycle = "attention"

    return {
        "meme_lifecycle": lifecycle,
        "meme_bonded_progress": progress,
        "is_meme_candidate": True,
    }


def _token_has_top_trader_interest(market_rank: dict[str, Any], symbol: str) -> bool:
    target = _normalize_match_key(symbol)
    for trader in market_rank.get("top_traders", []) or []:
        for token in trader.get("topEarningTokens", []) or []:
            if _normalize_match_key(token.get("tokenSymbol")) == target:
                return True
    return False


def _wallet_audit_overlay(raw: dict[str, Any], symbols: list[str]) -> tuple[int, list[str]]:
    audit_payload = raw.get("query-token-audit")
    if not audit_payload or not symbols:
        return 0, []

    requested_symbols = [_normalize_match_key(symbol) for symbol in symbols if _normalize_match_key(symbol)]
    entries = list(_iter_audit_entries(audit_payload))
    if not entries:
        return 0, []

    notes: list[str] = []
    risky_count = 0
    for symbol in requested_symbols:
        matched_entry = next((entry for entry in entries if _normalize_match_key(_audit_entry_symbol(entry)) == symbol), None)
        if matched_entry is None and len(entries) == 1 and len(requested_symbols) == 1:
            matched_entry = entries[0]
        if matched_entry is None:
            continue
        normalized = _normalize_audit_keys(matched_entry.get("data", matched_entry))
        flags, risks = _extract_audit_flags_and_risks(normalized)
        gate, blocked_reason = _audit_gate_state(normalized, flags)
        if gate == "ALLOW" and not flags:
            continue
        risky_count += 1
        display_symbol = _audit_entry_symbol(matched_entry) or symbol
        note = blocked_reason or (flags[0] if flags else risks[0] if risks else "Audit caution visible.")
        notes.append(f"{display_symbol} — {note}")
    return risky_count, _unique(notes)


def _iter_audit_entries(payload: Any):
    if isinstance(payload, list):
        for entry in payload:
            if isinstance(entry, dict):
                yield entry
        return
    if not isinstance(payload, dict):
        return

    if isinstance(payload.get("data"), list):
        for entry in payload.get("data", []):
            if isinstance(entry, dict):
                yield entry
        return

    if isinstance(payload.get("tokens"), list):
        for entry in payload.get("tokens", []):
            if isinstance(entry, dict):
                yield entry
        return

    audit_keys = {"hasResult", "has_result", "isSupported", "is_supported", "flags", "risks", "riskItems", "risk_items"}
    if any(key in payload for key in audit_keys):
        yield payload
        return

    for key, value in payload.items():
        if isinstance(value, dict):
            entry = dict(value)
            entry.setdefault("symbol", key)
            yield entry


def _audit_entry_symbol(entry: dict[str, Any]) -> str:
    nested = entry.get("data", {}) if isinstance(entry.get("data"), dict) else {}
    return str(
        entry.get("symbol")
        or entry.get("ticker")
        or entry.get("tokenSymbol")
        or nested.get("symbol")
        or nested.get("ticker")
        or nested.get("tokenSymbol")
        or ""
    )


def _normalize_audit_keys(audit: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(audit, dict):
        return {}
    normalized = dict(audit)
    aliases = {
        "has_result": "hasResult",
        "is_supported": "isSupported",
        "risk_level": "riskLevel",
        "risk_level_enum": "riskLevelEnum",
        "extra_info": "extraInfo",
        "risk_items": "riskItems",
        "is_hidden": "isHidden",
    }
    for source, target in aliases.items():
        if source in normalized and target not in normalized:
            normalized[target] = normalized[source]
    return normalized


def _signal_status(signal: dict[str, Any], first_signal: dict[str, Any]) -> str:
    status = str(first_signal.get("status") or signal.get("status") or "").strip().lower()
    if status:
        return status
    direction = str(first_signal.get("direction") or signal.get("direction") or "").strip().lower()
    if direction == "buy":
        return "bullish"
    if direction == "sell":
        return "bearish"
    return "watch" if _signal_has_live_data(first_signal) else "unmatched"


def _signal_has_live_data(signal_item: dict[str, Any]) -> bool:
    if not isinstance(signal_item, dict):
        return False
    return any([
        bool(str(signal_item.get("direction") or "").strip()),
        bool(str(signal_item.get("status") or "").strip()),
        _pick_int(signal_item, "smartMoneyCount") > 0,
        _pick_number(signal_item, "alertPrice", "trigger_price") > 0,
        _pick_number(signal_item, "currentPrice", "current_price") > 0,
    ])


def _coerce_timestamp_ms(value: Any) -> float:
    if value in (None, ""):
        return 0.0
    if isinstance(value, (int, float)):
        numeric = float(value)
    else:
        text = str(value).strip()
        try:
            numeric = float(text)
        except ValueError:
            try:
                parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
            except ValueError:
                return 0.0
            return parsed.astimezone(timezone.utc).timestamp() * 1000
    if numeric <= 0:
        return 0.0
    if numeric >= 1_000_000_000_000:
        return numeric
    if numeric >= 1_000_000_000:
        return numeric * 1000
    return 0.0


def _bridge_meta(raw: dict[str, Any]) -> dict[str, Any]:
    meta = raw.get("__bridge_meta__")
    return meta if isinstance(meta, dict) else {}


def _bridge_runtime_context(raw: dict[str, Any], command: str) -> dict[str, str]:
    meta = _bridge_meta(raw)
    status = str(meta.get("status") or "").lower()
    failed_skills = [str(x) for x in meta.get("failedSkills", []) if str(x).strip()]
    expected = COMMAND_SKILL_MAP.get(command, [])
    relevant = [name for name in failed_skills if not expected or name in expected] or failed_skills

    if "partial" not in status and not relevant:
        return {}

    if relevant:
        detail = ", ".join(relevant[:3])
        warning = f"Live {command} payload is partial: missing {detail}."
    else:
        notes = [str(x) for x in meta.get("notes", []) if str(x).strip()]
        warning = notes[0] if notes else f"Live {command} payload is only partially populated right now."

    return {
        "runtime_state": "partial_live",
        "runtime_warning": warning,
    }


def _extract_audit_flags_and_risks(audit: dict[str, Any]) -> tuple[list[str], list[str]]:
    audit = _normalize_audit_keys(audit)
    if not audit:
        return [], []

    if "flags" in audit or "risks" in audit:
        return _unique([str(x) for x in audit.get("flags", [])]), _unique([str(x) for x in audit.get("risks", [])])

    if not audit.get("hasResult") or not audit.get("isSupported"):
        return [], []

    flags: list[str] = []
    risks: list[str] = []
    level = _to_int(audit.get("riskLevel"))
    suppress_unverified_only = bool(audit.get("isHidden")) and level == 0 and not (audit.get("extraInfo") or {}).get("isVerified", False)
    if level >= 4:
        flags.append(f"Risk level {level} ({audit.get('riskLevelEnum', 'HIGH')})")
    elif level >= 2:
        flags.append(f"Risk level {level} ({audit.get('riskLevelEnum', 'MEDIUM')})")

    buy_tax = _to_float((audit.get("extraInfo") or {}).get("buyTax"))
    sell_tax = _to_float((audit.get("extraInfo") or {}).get("sellTax"))
    for label, value in (("Buy tax", buy_tax), ("Sell tax", sell_tax)):
        if value > 10:
            flags.append(f"{label} above 10%")
        elif value >= 5:
            risks.append(f"{label} is elevated at {value:.2f}%.")

    for item in audit.get("riskItems", []) or []:
        category = item.get("name") or item.get("id") or "Risk"
        for detail in item.get("details", []) or []:
            if detail.get("isHit"):
                title = detail.get("title") or "Risk detected"
                desc = detail.get("description") or ""
                if suppress_unverified_only and title == "Contract Code Not Verified":
                    continue
                flags.append(title)
                risks.append(f"{category}: {title}. {desc}".strip())
    return _unique(flags), _unique(risks)


def _extract_market_rank_risks(market_rank: dict[str, Any], symbol: str | None = None) -> list[str]:
    risks = list(market_rank.get("risks", []) or [])
    tokens = market_rank.get("data", {}).get("tokens", []) or market_rank.get("tokens", []) or []
    if symbol is None:
        for token in tokens[:5]:
            top10 = _pick_number(token, "holdersTop10Percent", "top10HoldersPercentage")
            if top10 >= 90:
                risks.append(f"{token.get('symbol', 'Token')} has extreme top-10 holder concentration.")
            elif top10 >= 80:
                risks.append(f"{token.get('symbol', 'Token')} has very high top-10 holder concentration.")
            audit_info = token.get("auditInfo") or {}
            risk_num = _to_int(audit_info.get("riskNum"))
            caution_num = _to_int(audit_info.get("cautionNum"))
            if risk_num > 0 or caution_num > 0:
                risks.append(f"{token.get('symbol', 'Token')} shows audit cautions in market rank context.")
        return _unique(risks)

    target = _normalize_match_key(symbol)
    token = _best_symbol_match(tokens, target) if target else None
    if not token:
        return _unique(risks)

    top10 = _pick_number(token, "holdersTop10Percent", "top10HoldersPercentage")
    if top10 >= 80:
        risks.append(f"{token.get('symbol', 'Token')} has very high top-10 holder concentration.")
    audit_info = token.get("auditInfo") or {}
    risk_num = _to_int(audit_info.get("riskNum"))
    caution_num = _to_int(audit_info.get("cautionNum"))
    if risk_num > 0 or caution_num > 0:
        risks.append(f"{token.get('symbol', 'Token')} shows audit cautions in market rank context.")
    return _unique(risks)


def _extract_signal_risks(signal: dict[str, Any]) -> list[str]:
    risks = list(signal.get("risks", []) or [])
    first = _first_item(signal.get("data")) or signal
    exit_rate = _pick_number(first, "exitRate", "exit_rate")
    status = str(first.get("status", "")).lower()
    age_hours = _signal_age_hours(first)
    if status == "timeout":
        risks.append("Signal timed out and may no longer be actionable.")
    if exit_rate >= 70:
        risks.append("Smart money exit rate is high, which may indicate the move is aging.")
    elif exit_rate >= 40:
        risks.append("Smart money exit rate is already mixed, so follow-through may be less clean.")
    if age_hours >= SIGNAL_AGE_STALE:
        risks.append("Signal is stale enough that timing quality may already be degraded.")
    elif age_hours >= SIGNAL_AGE_AGING:
        risks.append("Signal is aging and needs fresher confirmation.")
    return _unique(risks)


def _extract_meme_risks(meme_rush: dict[str, Any]) -> list[str]:
    risks = list(meme_rush.get("risks", []) or [])
    items = meme_rush.get("tokens", []) or meme_rush.get("data", []) or []
    for item in items[:5]:
        if _to_int(item.get("tagDevWashTrading")) == 1:
            risks.append(f"{item.get('symbol', 'Token')} shows dev wash-trading risk.")
        if _to_int(item.get("tagInsiderWashTrading")) == 1:
            risks.append(f"{item.get('symbol', 'Token')} shows insider wash-trading risk.")
        if _pick_number(item, "holdersTop10Percent") >= 80:
            risks.append(f"{item.get('symbol', 'Token')} has concentrated top-10 holders.")
    return _unique(risks)


def _build_market_rank_context(market_rank: dict[str, Any], symbol: str | None = None) -> str:
    tokens = market_rank.get("data", {}).get("tokens", []) or market_rank.get("tokens", []) or []
    if symbol is None:
        if not tokens:
            return ""
        leaders = [str(item.get("symbol") or "Token") for item in tokens[:3]]
        return f"Current rank leaders: {', '.join(leaders)}. Opportunity exists, but selectivity matters."

    target = _normalize_match_key(symbol)
    matched = _best_symbol_match(tokens, target) if target else None
    if matched:
        matched_symbol = matched.get("symbol", symbol or "This token")
        return f"{matched_symbol} appears in current market-rank screens with visible liquidity and activity context."

    return ""


def _build_signal_context(signal: dict[str, Any]) -> str:
    first = _first_item(signal.get("data"))
    if not first:
        summary = str(signal.get("summary") or "").strip()
        if summary:
            return summary
        return "No matched smart-money signal is visible for this token in the current live board."

    ticker = first.get("ticker", "This token")
    direction = str(first.get("direction", "")).lower()
    platform = first.get("launchPlatform") or ""
    count = _to_int(first.get("smartMoneyCount"))
    status = first.get("status") or "unknown"
    freshness = _signal_freshness(_signal_age_hours(first), has_signal_data=_signal_has_live_data(first))
    parts = [f"{ticker} has a {direction or 'smart-money'} signal"]
    if count:
        parts.append(f"from {count} smart-money addresses")
    if platform:
        parts.append(f"on {platform}")
    parts.append(f"with status {status}")
    if freshness != "UNKNOWN":
        parts.append(f"and {freshness.lower()} timing")
    return " ".join(parts).strip() + "."


WALLET_EXPOSURE_BUCKETS = {
    "meme": {"DOGE", "SHIB", "PEPE", "BONK", "FLOKI", "WIF"},
    "ai": {"AI", "FET", "AGIX", "OCEAN", "TAO", "ARKM"},
    "l1": {"BTC", "ETH", "BNB", "SOL", "AVAX", "SUI", "APT"},
    "defi": {"UNI", "AAVE", "MKR", "SNX", "CRV", "COMP"},
    "infra": {"LINK", "ATOM", "OP", "ARB", "TIA", "PYTH"},
}


def _wallet_exposure_bucket(symbol: str) -> str:
    upper = str(symbol or "").upper()
    for bucket, symbols in WALLET_EXPOSURE_BUCKETS.items():
        if upper in symbols:
            return bucket.upper()
    return upper



def _wallet_style_profile(top_concentration_pct: float, holdings_count: int, exposure_weights: dict[str, float], change_24h: float) -> str:
    if top_concentration_pct >= WALLET_CONCENTRATION_EXTREME:
        base = "high-conviction concentrated"
    elif holdings_count >= 8 and len(exposure_weights) >= 3:
        base = "multi-theme diversified"
    elif holdings_count >= 5:
        base = "selective diversified"
    else:
        base = "narrow watchlist"

    if change_24h >= 8:
        return base + " momentum-seeking"
    if change_24h <= -8:
        return base + " under pressure"
    return base



def _extract_watchtoday_exchange_board(market_rank: dict[str, Any]) -> list[str]:
    rows: list[str] = []
    tokens = market_rank.get("data", {}).get("tokens", []) or market_rank.get("tokens", []) or []
    for item in tokens[:5]:
        symbol = item.get("symbol") or "Token"
        change = _pick_number(item, "priceChangePercent24h", "priceChange24h", "change24h", "percentChange24h")
        liq = _pick_number(item, "liquidity", "liquidityUsd")
        if change or liq:
            bits = [f"{symbol} {change:+.1f}%" if change else str(symbol)]
            if liq > 0:
                bits.append(f"liq ${liq/1_000_000:.1f}M")
            rows.append(" | ".join(bits))
    return _unique(rows)[:3]


def _extract_top_narratives(market_rank: dict[str, Any], meme_rush: dict[str, Any]) -> list[str]:
    direct_market = [str(x) for x in market_rank.get("top_narratives", []) or []]
    if direct_market:
        return direct_market

    out: list[str] = []
    tokens = market_rank.get("data", {}).get("tokens", []) or market_rank.get("tokens", []) or []
    for item in tokens[:8]:
        for label in (item.get("tokenTag") or {}).keys():
            out.append(str(label))
    leaderboard = market_rank.get("data", {}).get("leaderBoardList", []) or market_rank.get("leaderBoardList", []) or []
    for item in leaderboard[:3]:
        brief = item.get("socialHypeInfo", {}).get("socialSummaryBriefTranslated") or item.get("socialHypeInfo", {}).get("socialSummaryBrief")
        if brief:
            out.append(brief)
    topics = meme_rush.get("topics", []) or meme_rush.get("data", []) or []
    for topic in topics[:3]:
        name = topic.get("name", {}).get("topicNameEn") or topic.get("name", {}).get("topicNameCn") or topic.get("type")
        if name:
            out.append(str(name))
    out.extend([str(x) for x in meme_rush.get("top_narratives", []) or []])
    cleaned = []
    for item in out:
        short = str(item).strip()
        if short and len(short) <= 40:
            cleaned.append(short)
    return _unique(cleaned)[:5]


def _extract_topic_summary(meme_rush: dict[str, Any]) -> str:
    topics = meme_rush.get("topics", []) or meme_rush.get("data", []) or []
    if topics:
        top = topics[0]
        name = top.get("name", {}).get("topicNameEn") or top.get("type") or "topic"
        inflow = top.get("topicNetInflow") or top.get("topicNetInflowAth")
        if inflow:
            return f"{name} is a leading topic with visible net inflow of {inflow}."
        return f"{name} is a leading topic in current topic-rush context."
    return ""


def _signal_age_hours(signal_item: dict[str, Any]) -> float:
    raw = signal_item.get("timeFrame") or signal_item.get("timeframe") or signal_item.get("signalAgeMs") or signal_item.get("ageMs")
    try:
        ms = float(raw or 0)
    except (TypeError, ValueError):
        ms = 0.0
    if ms <= 0:
        for key in ("createdAt", "createTime", "createdTime", "signalTime", "timestamp"):
            timestamp_ms = _coerce_timestamp_ms(signal_item.get(key))
            if timestamp_ms > 0:
                age_ms = (datetime.now(timezone.utc).timestamp() * 1000) - timestamp_ms
                if age_ms > 0:
                    return age_ms / 3_600_000
        return 0.0
    return ms / 3_600_000



def _signal_freshness(age_hours: float, has_signal_data: bool = False) -> str:
    if age_hours <= 0:
        if has_signal_data:
            return "FRESH"
        return "UNKNOWN"
    if age_hours < SIGNAL_AGE_AGING:
        return "FRESH"
    if age_hours < SIGNAL_AGE_STALE:
        return "AGING"
    return "STALE"



def _audit_gate_state(audit: dict[str, Any], audit_flags: list[str]) -> tuple[str, str]:
    audit = _normalize_audit_keys(audit)
    if not audit or not audit.get("hasResult") or not audit.get("isSupported"):
        return "WARN", "Audit coverage is partial or unavailable."

    level = _to_int(audit.get("riskLevel"))
    risk_enum = str(audit.get("riskLevelEnum") or "").upper()
    extra = audit.get("extraInfo") or {}
    combined = " ".join(str(x) for x in audit_flags).lower()

    blocked_terms = ["honeypot", "scam", "malicious", "phishing"]
    if level >= 5 or any(term in combined for term in blocked_terms):
        return "BLOCK", "Critical audit flags detected."
    if level >= 4 or risk_enum == "HIGH":
        return "BLOCK", f"Audit risk is high ({risk_enum or level})."
    if _to_float(extra.get("buyTax")) > 10 or _to_float(extra.get("sellTax")) > 10:
        return "WARN", "Token taxes are elevated above 10%."
    if audit_flags:
        return "WARN", "Audit returned structural caution flags."
    return "ALLOW", ""


def _extract_strongest_signals(signal: dict[str, Any]) -> list[str]:
    items = signal.get("data", []) or []
    if signal.get("strongest_signals"):
        return [str(x) for x in signal.get("strongest_signals", [])]
    if not items and signal.get("status"):
        return [str(signal.get("summary") or signal.get("status"))]
    out = []
    for item in items[:5]:
        ticker = item.get("ticker") or "Token"
        direction = str(item.get("direction") or "signal").upper()
        status = item.get("status") or "unknown"
        wallets = _to_int(item.get("smartMoneyCount"))
        age_hours = _signal_age_hours(item)
        age_suffix = f" {age_hours:.0f}h ago" if age_hours > 0 else ""
        if wallets > 0:
            out.append(f"{ticker} — {wallets} smart-money wallets | {direction}{' ⏱️' if status == 'timeout' else ''}{age_suffix}")
        else:
            out.append(f"{ticker}: {direction} ({status}){age_suffix}")
    return _unique(out)


def _extract_symbol_and_liquidity(item: dict[str, Any]) -> tuple[str, float]:
    symbol = str(item.get("symbol") or item.get("baseAsset") or item.get("name") or "Token")
    liquidity = _pick_number(item, "liquidity", "liquidityUsd")
    return symbol, liquidity



def _watch_liquidity_quality(liquidity: float) -> str:
    if liquidity <= 0:
        return ""
    if liquidity < 1_000_000:
        return "⚠️ very thin"
    if liquidity < 10_000_000:
        return "⚠️ thin"
    if liquidity < 50_000_000:
        return "🟡 moderate"
    return "✅ deep"


def _extract_trending_now(market_rank: dict[str, Any]) -> list[str]:
    direct = [str(x) for x in market_rank.get("trending_now", []) or []]
    if direct:
        return direct[:3]

    out: list[str] = []
    tokens = market_rank.get("data", {}).get("tokens", []) or market_rank.get("tokens", []) or []
    for item in tokens[:3]:
        symbol, liquidity = _extract_symbol_and_liquidity(item)
        search_count = _to_int(item.get("searchCount24h"))
        liq_part = f"{_human_money_short(liquidity)} liq {_watch_liquidity_quality(liquidity)}".strip() if liquidity > 0 else "liq —"
        if search_count > 0:
            out.append(f"{symbol} {search_count} searches · {liq_part}")
        else:
            out.append(f"{symbol} · {liq_part}")
    leaderboard = market_rank.get("data", {}).get("leaderBoardList", []) or market_rank.get("leaderBoardList", []) or []
    for item in leaderboard[:3]:
        symbol = item.get("symbol") or item.get("baseAsset") or item.get("name") or "Token"
        brief = item.get("socialHypeInfo", {}).get("socialSummaryBriefTranslated") or item.get("socialHypeInfo", {}).get("socialSummaryBrief")
        out.append(f"{symbol} — {brief}" if brief else str(symbol))
    return _unique(out)[:3]



def _extract_smart_money_flow(market_rank: dict[str, Any], signal: dict[str, Any]) -> list[str]:
    direct = [str(x) for x in market_rank.get("smart_money_flow", []) or []]
    if direct:
        return direct[:3]

    out: list[str] = []
    inflow_items = market_rank.get("smart_money_inflow", []) or []
    for item in inflow_items[:3]:
        symbol = item.get("symbol") or item.get("tokenName") or "Token"
        traders = _to_int(item.get("traders"))
        inflow = _pick_number(item, "inflow")
        bits = [str(symbol)]
        if traders > 0:
            bits.append(f"{traders} smart-money wallets")
        if inflow > 0:
            bits.append(f"inflow {_human_money_short(inflow)}")
        out.append(" — ".join(bits))
    if out:
        return _unique(out)[:3]

    items = signal.get("data", []) or []
    for item in items[:3]:
        ticker = item.get("ticker") or "Token"
        count = _to_int(item.get("smartMoneyCount"))
        direction = str(item.get("direction") or "signal").upper()
        if count:
            out.append(f"{ticker} — {count} smart-money wallets | {direction}")
        else:
            out.append(f"{ticker} — {direction}")
    return _unique(out)[:3]



def _extract_social_hype(market_rank: dict[str, Any]) -> list[str]:
    direct = [str(x) for x in market_rank.get("social_hype", []) or []]
    if direct:
        return direct[:2]

    out: list[str] = []
    leaderboard = market_rank.get("data", {}).get("leaderBoardList", []) or market_rank.get("leaderBoardList", []) or []
    for item in leaderboard[:3]:
        symbol = item.get("symbol") or item.get("baseAsset") or item.get("name") or "Token"
        brief = item.get("socialHypeInfo", {}).get("socialSummaryBriefTranslated") or item.get("socialHypeInfo", {}).get("socialSummaryBrief")
        if brief:
            out.append(f"{symbol} — {brief}")
        else:
            out.append(f"{symbol} — social attention visible")
    if out:
        return _unique(out)[:2]

    tokens = market_rank.get("data", {}).get("tokens", []) or market_rank.get("tokens", []) or []
    for item in tokens[:2]:
        symbol = item.get("symbol") or "Token"
        search_count = _to_int(item.get("searchCount24h"))
        if search_count > 0:
            out.append(f"{symbol} — {search_count} searches in 24h")
    return _unique(out)[:2]



def _extract_meme_watch(meme_rush: dict[str, Any]) -> list[str]:
    direct = [str(x) for x in meme_rush.get("meme_watch", []) or []]
    if direct:
        return direct[:3]

    out: list[str] = []
    items = meme_rush.get("tokens", []) or meme_rush.get("data", []) or []
    for item in items[:3]:
        symbol = item.get("symbol") or item.get("name", {}).get("topicNameEn") or item.get("type") or "Token"
        progress = _pick_number(item, "progress")
        migrate = _to_int(item.get("migrateStatus"))
        if migrate == 1:
            out.append(f"{symbol} — migrated")
        elif progress >= 90:
            out.append(f"{symbol} — near migration ({progress:.0f}% bonded)")
        elif progress > 0:
            out.append(f"{symbol} — building ({progress:.0f}% bonded)")
        else:
            out.append(str(symbol))
    return _unique(out)[:3]



def _extract_top_picks(trending_now: list[str], strongest_signals: list[str], top_narratives: list[str], exchange_board: list[str] | None = None) -> list[str]:
    picks: list[str] = []
    if strongest_signals:
        picks.append(f"{strongest_signals[0]} — best visible setup")
    if trending_now:
        picks.append(f"{trending_now[0]} — strongest broad attention")
    if top_narratives:
        picks.append(f"{top_narratives[0]} — narrative worth ranking, not chasing")
    if exchange_board:
        picks.append(f"{exchange_board[0]} — exchange board anchor")
    return _unique(picks)[:3]


def _human_money_short(value: float) -> str:
    if value >= 1_000_000_000:
        return f"${value/1_000_000_000:.1f}B"
    if value >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    if value >= 1_000:
        return f"${value/1_000:.1f}K"
    if value > 0:
        return f"${value:.0f}"
    return "n/a"


def _short_addr(address: str) -> str:
    if len(address) > 12:
        return f"{address[:6]}…{address[-4:]}"
    return address or "unknown"


def _extract_risk_zones(market_rank: dict[str, Any], meme_rush: dict[str, Any]) -> list[str]:
    zones = list(market_rank.get("risk_zones", []) or [])
    items = meme_rush.get("tokens", []) or meme_rush.get("data", []) or []
    for item in items[:5]:
        if _to_int(item.get("tagDevWashTrading")) == 1 or _to_int(item.get("tagInsiderWashTrading")) == 1:
            zones.append(f"{item.get('symbol', 'Token')} shows wash-trading related caution.")
        if _to_int(item.get("migrateStatus")) == 0 and _pick_number(item, "progress") >= 90:
            zones.append(f"{item.get('symbol', 'Token')} is near migration and may be volatile.")
    return _unique(zones)


def _first_item(value: Any) -> dict[str, Any] | None:
    if isinstance(value, list) and value:
        first = value[0]
        if isinstance(first, dict):
            return first
    return None


def _best_token_match(items: Any, symbol: str, metadata: dict[str, Any] | None = None) -> dict[str, Any] | None:
    if not isinstance(items, list):
        return metadata if metadata else None

    target = _normalize_match_key(symbol)
    target_contract = _normalize_contract((metadata or {}).get("contractAddress"))
    scored: list[tuple[int, dict[str, Any]]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        score = _token_match_score(item, target, target_contract)
        if score > 0:
            scored.append((score, item))

    if scored:
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return scored[0][1]

    return metadata if metadata else _first_item(items)


def _best_symbol_match(items: Any, target: str) -> dict[str, Any] | None:
    if not isinstance(items, list) or not target:
        return None
    scored: list[tuple[int, dict[str, Any]]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        score = _token_match_score(item, target)
        if score > 0:
            scored.append((score, item))
    if not scored:
        return None
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return scored[0][1]


def _token_match_score(item: dict[str, Any], target: str, target_contract: str = "") -> int:
    if target_contract:
        item_contract = _normalize_contract(item.get("contractAddress"))
        token_addresses = item.get("tokenAddresses") or []
        if item_contract == target_contract:
            return 200
        for entry in token_addresses:
            if isinstance(entry, dict) and _normalize_contract(entry.get("contractAddress")) == target_contract:
                return 200

    symbol_fields = ["symbol", "ticker", "tokenSymbol", "baseAsset"]
    name_fields = ["name", "tokenName", "baseAssetName"]

    for field in symbol_fields:
        if _normalize_match_key(item.get(field)) == target:
            return 120
    for field in name_fields:
        if _normalize_match_key(item.get(field)) == target:
            return 90
    for field in symbol_fields + name_fields:
        candidate = _normalize_match_key(item.get(field))
        if not candidate:
            continue
        if candidate.startswith(target) or target.startswith(candidate):
            return 40
        if target in candidate:
            return 20
    return 0


def _normalize_match_key(value: Any) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(value or "").upper())


def _normalize_contract(value: Any) -> str:
    return str(value or "").strip().lower()


def _pick_number(data: dict[str, Any], *keys: str) -> float:
    for key in keys:
        if key in data:
            return _to_float(data.get(key))
    return 0.0


def _pick_int(data: dict[str, Any], *keys: str) -> int:
    for key in keys:
        if key in data:
            return _to_int(data.get(key))
    return 0


def _unique(items: list[str]) -> list[str]:
    out: list[str] = []
    for item in items:
        text = str(item).strip()
        if text and text not in out:
            out.append(text)
    return out


def _merge_risks(*risk_lists: list[Any]) -> list[str]:
    merged: list[str] = []
    for risk_list in risk_lists:
        for item in risk_list or []:
            text = str(item).strip()
            if text and text not in merged:
                merged.append(text)
    return merged
