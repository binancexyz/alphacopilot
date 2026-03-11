from __future__ import annotations

import json
from pathlib import Path

from src.services.live_service import LiveMarketDataService


TOKEN_RAW = {
    "query-token-info": {"symbol": "BNB", "price": 612.5, "liquidity": 125000000.0, "holders": 1850000},
    "crypto-market-rank": {"summary": "Large-cap token with strong liquidity.", "risks": ["Macro weakness"]},
    "trading-signal": {"status": "watch", "summary": "Momentum improving.", "risks": ["Need confirmation"]},
    "query-token-audit": {"flags": [], "risks": []},
}

SIGNAL_RAW = {
    "trading-signal": {
        "status": "watch",
        "summary": "Signal is improving.",
        "trigger_price": 1.2,
        "current_price": 1.1,
        "max_gain": 4.5,
        "exit_rate": 0.2,
        "risks": ["Fragile setup"],
    },
    "query-token-audit": {"flags": ["Owner can pause"], "risks": ["Centralization risk"]},
}

WATCHTODAY_RAW = {
    "crypto-market-rank": {
        "top_narratives": ["AI", "L2"],
        "summary": "Opportunity exists.",
        "risk_zones": ["overheated memes"],
        "risks": ["Broad froth"],
    },
    "meme-rush": {"top_narratives": ["meme"], "risks": ["rotation risk"]},
    "trading-signal": {"strongest_signals": ["BNB strength"], "risks": ["confirmation missing"]},
}

WALLET_RAW = {
    "query-address-info": {
        "portfolio_value": 1234.0,
        "holdings_count": 3,
        "top_holdings": [{"symbol": "BNB", "weight_pct": 55.0}],
        "top_concentration_pct": 55.0,
        "change_24h": 2.5,
        "notable_exposures": ["AI"],
        "major_risks": ["Concentrated wallet"],
    }
}


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_live_service_loads_token_payload_from_file_directory(tmp_path: Path):
    _write_json(tmp_path / "token-bnb.json", TOKEN_RAW)
    service = LiveMarketDataService(base_url=f"file://{tmp_path}")

    out = service.get_token_context("BNB")

    assert out["symbol"] == "BNB"
    assert out["signal_status"] == "watch"
    assert "Need confirmation" in out["major_risks"]


def test_live_service_supports_nested_command_paths(tmp_path: Path):
    _write_json(tmp_path / "signal" / "doge.json", SIGNAL_RAW)
    service = LiveMarketDataService(base_url=f"file://{tmp_path}")

    out = service.get_signal_context("DOGE")

    assert out["token"] == "DOGE"
    assert out["audit_flags"] == ["Owner can pause"]


def test_live_service_watchtoday_and_wallet_file_modes(tmp_path: Path):
    _write_json(tmp_path / "watchtoday.json", WATCHTODAY_RAW)
    _write_json(tmp_path / "wallet" / "0xabc.json", WALLET_RAW)
    service = LiveMarketDataService(base_url=f"file://{tmp_path}")

    watch = service.get_watch_today_context()
    wallet = service.get_wallet_context("0xabc")

    assert watch["top_narratives"] == ["AI", "L2"]
    assert wallet["address"] == "0xabc"
    assert wallet["top_holdings"][0]["symbol"] == "BNB"


def test_live_service_marks_bridge_unavailable_runtime_state():
    service = LiveMarketDataService(base_url="file:///definitely/missing/path")
    out = service.get_signal_context("DOGE")
    assert out["runtime_state"] == "bridge_unavailable"
    assert "Live bridge is unavailable for signal" in out["major_risks"][0]


def test_live_service_marks_partial_watch_board():
    service = LiveMarketDataService(base_url="file:///definitely/missing/path")
    out = service._apply_fallbacks("watchtoday", {"top_narratives": ["AI"], "major_risks": []})
    assert out["major_risks"][0].startswith("Today’s live board is only lightly populated")
