from __future__ import annotations


class MockMarketDataService:
    def get_token_context(self, symbol: str) -> dict:
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

    def get_wallet_context(self, address: str) -> dict:
        return {
            "address": address,
            "signal_quality": "Medium",
            "quick_context": "Wallet appears concentrated and worth monitoring for behavior patterns.",
            "risks": [
                "Low diversification can amplify drawdowns.",
                "Wallet size alone does not prove smart-money quality.",
            ],
        }

    def get_watch_today_context(self) -> dict:
        return {
            "signal_quality": "Medium",
            "quick_context": "Multiple narratives are active, but filtering matters more than speed.",
            "risks": [
                "Trending sectors may already be overheated.",
                "Signal quality can vary across the same narrative.",
            ],
        }

    def get_signal_context(self, token: str) -> dict:
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
