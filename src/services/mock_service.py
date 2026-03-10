from __future__ import annotations


class MockMarketDataService:
    def get_token_context(self, symbol: str) -> dict:
        return {
            "symbol": symbol,
            "signal_quality": "Medium",
            "quick_context": f"{symbol} has early positive context but still requires confirmation.",
            "risks": [
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
            "signal_quality": "Medium",
            "quick_context": f"{token} has a monitor-worthy setup, but the signal remains fragile.",
            "risks": [
                "A visible signal does not guarantee continuation.",
                "Weak follow-through can turn momentum into noise.",
            ],
        }
