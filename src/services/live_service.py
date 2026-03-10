from __future__ import annotations


class LiveMarketDataService:
    def __init__(self, base_url: str, api_key: str = "", api_secret: str = "") -> None:
        self.base_url = base_url
        self.api_key = api_key
        self.api_secret = api_secret

    def get_token_context(self, symbol: str) -> dict:
        raise NotImplementedError("Wire this to real Binance/OpenClaw-backed token context.")

    def get_wallet_context(self, address: str) -> dict:
        raise NotImplementedError("Wire this to real Binance/OpenClaw-backed wallet context.")

    def get_watch_today_context(self) -> dict:
        raise NotImplementedError("Wire this to real Binance/OpenClaw-backed watch-today context.")

    def get_signal_context(self, token: str) -> dict:
        raise NotImplementedError("Wire this to real Binance/OpenClaw-backed signal context.")
