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
            "audit_flags": [],
            "major_risks": ["Audit context is incomplete right now, so security conclusions should stay cautious."],
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
