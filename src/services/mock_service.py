from __future__ import annotations

from src.services.types import NormalizedDict


class MockMarketDataService:
    def get_token_context(self, symbol: str) -> NormalizedDict:
        return {
            "symbol": symbol,
            "display_name": symbol,
            "price": 0.0,
            "liquidity": 1000000.0,
            "holders": 10000,
            "market_rank_context": f"{symbol} has visible market relevance, but attention still needs confirmation.",
            "signal_status": "watch",
            "signal_trigger_context": f"{symbol} has early positive context but still requires confirmation.",
            "audit_flags": [],
            "major_risks": [
                "Signal may weaken if volume does not confirm.",
                "Market sentiment can reverse short-term strength.",
            ],
        }

    def get_wallet_context(self, address: str) -> NormalizedDict:
        return {
            "address": address,
            "portfolio_value": 245000.0,
            "holdings_count": 12,
            "top_holdings": [
                {"symbol": "BNB", "weight_pct": 41.2},
                {"symbol": "DOGE", "weight_pct": 19.8},
            ],
            "top_concentration_pct": 61.0,
            "change_24h": 8.4,
            "notable_exposures": ["meme", "AI"],
            "major_risks": [
                "Low diversification can amplify drawdowns.",
                "Wallet size alone does not prove smart-money quality.",
            ],
            "follow_verdict": "Track",
            "style_read": "Narrative bias: meme, AI | Risk posture: mixed",
        }

    def get_watch_today_context(self) -> NormalizedDict:
        return {
            "top_narratives": ["AI", "meme rotation", "L2"],
            "strongest_signals": ["BNB strength", "AI inflows"],
            "risk_zones": ["overheated meme names"],
            "market_takeaway": "Opportunity exists, but selectivity matters.",
            "major_risks": [
                "Trending sectors may already be overheated.",
                "Signal quality can vary across the same narrative.",
            ],
            "exchange_board": [
                "BNB +2.4% | Binance Spot leader board anchor",
                "BTC +1.1% | broad risk tone stable",
                "SOL -0.6% | momentum softer than BNB",
            ],
        }

    def get_signal_context(self, token: str) -> NormalizedDict:
        return {
            "token": token,
            "signal_status": "watch",
            "trigger_price": 0.0,
            "current_price": 0.0,
            "max_gain": 0.0,
            "exit_rate": 0.0,
            "audit_flags": [],
            "supporting_context": f"{token} has a monitor-worthy setup, but the signal remains fragile.",
            "major_risks": [
                "A visible signal does not guarantee continuation.",
                "Weak follow-through can turn momentum into noise.",
            ],
        }

    def get_audit_context(self, symbol: str) -> NormalizedDict:
        return {
            "symbol": symbol,
            "display_name": symbol,
            "audit_gate": "WARN",
            "blocked_reason": "Audit coverage is partial or unavailable.",
            "audit_flags": ["Contract Code Not Verified"],
            "major_risks": ["Liquidity context is incomplete right now."],
            "risk_level": "Medium",
            "audit_summary": "No live audit payload available in mock mode.",
        }

    def get_meme_context(self, symbol: str) -> NormalizedDict:
        return {
            "symbol": symbol,
            "display_name": symbol,
            "price": 0.0,
            "liquidity": 250000.0,
            "market_rank_context": f"{symbol} has meme-style attention but still needs proper filtering.",
            "signal_status": "watch",
            "audit_flags": [],
            "major_risks": ["Meme setups can reverse quickly when attention fades."],
            "smart_money_count": 2,
            "exit_rate": 15.0,
            "signal_age_hours": 0.8,
            "signal_freshness": "FRESH",
            "audit_gate": "WARN",
            "blocked_reason": "Audit coverage is partial or unavailable.",
            "launch_platform": "Fourmeme",
            "is_alpha": True,
            "lifecycle_stage": "new",
            "bonded_progress": 42.0,
        }

    def get_alpha_context(self, symbol: str) -> NormalizedDict:
        if symbol:
            return {
                "symbol": symbol,
                "display_name": symbol,
                "is_alpha_listed": False,
                "alpha_price": 0.0,
                "alpha_volume_24h": 0.0,
                "major_risks": ["No live Binance Alpha payload available in mock mode."],
                "audit_gate": "WARN",
                "blocked_reason": "Alpha coverage is unavailable in mock mode.",
            }
        return {
            "alpha_listed_count": 0,
            "alpha_token_list": [],
            "major_risks": ["No live Binance Alpha payload available in mock mode."],
        }

    def get_futures_context(self, symbol: str) -> NormalizedDict:
        return {
            "symbol": symbol,
            "funding_rate": 0.0,
            "funding_rate_sentiment": "neutral",
            "open_interest": 0.0,
            "long_short_ratio": 1.0,
            "top_trader_long_short_ratio": 1.0,
            "taker_buy_sell_ratio": 1.0,
            "mark_price": 0.0,
            "index_price": 0.0,
            "ticker_volume_24h": 0.0,
            "price_change_pct_24h": 0.0,
            "major_risks": ["No live Binance Futures payload available in mock mode."],
            "funding_rate_8h_ago": 0.0,
            "funding_rate_24h_ago": 0.0,
            "oi_change_pct_24h": 0.0,
            "oi_change_pct_4h": 0.0,
            "premium_pct": 0.0,
            "liquidation_24h_long": 0.0,
            "liquidation_24h_short": 0.0,
        }

    def get_portfolio_context(self) -> NormalizedDict:
        return {
            "_raw": {
                "assets": {"data": []},
                "funding-wallet": {"data": []},
                "account-snapshot": {},
                "margin-trading": {},
            },
            "prices": {},
            "major_risks": ["No live portfolio payload available in mock mode."],
        }
