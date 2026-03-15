import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from src.services.snapshot_history import (
    describe_snapshot_delta,
    latest_snapshot,
    save_snapshot,
)


def test_save_and_load_snapshot(tmp_path: Path | None = None):
    if tmp_path is None:
        tmp_path = Path(tempfile.mkdtemp())
    snapshot_dir = tmp_path / "snapshots"
    with patch("src.services.snapshot_history.SNAPSHOT_DIR", snapshot_dir):
        save_snapshot("brief", "BTC", {"signal_quality": "High", "conviction": "High"})
        result = latest_snapshot("brief", "BTC")
        assert result is not None
        assert result["signal_quality"] == "High"
        assert "saved_at" in result
    print("PASS test_save_and_load_snapshot")


def test_snapshot_delta_detects_quality_shift(tmp_path: Path | None = None):
    if tmp_path is None:
        tmp_path = Path(tempfile.mkdtemp())
    snapshot_dir = tmp_path / "snapshots"
    with patch("src.services.snapshot_history.SNAPSHOT_DIR", snapshot_dir):
        save_snapshot("brief", "BTC", {"signal_quality": "High", "conviction": "High", "quick_verdict": "Strong"})
        current = {"signal_quality": "Low", "conviction": "Low", "quick_verdict": "Weak"}
        summary, watch = describe_snapshot_delta("brief", "BTC", current)
        assert "shifted" in summary.lower() or "changed" in summary.lower()
    print("PASS test_snapshot_delta_detects_quality_shift")


def test_snapshot_delta_returns_empty_when_no_previous():
    import tempfile
    snapshot_dir = Path(tempfile.mkdtemp()) / "snapshots"
    with patch("src.services.snapshot_history.SNAPSHOT_DIR", snapshot_dir):
        current = {"signal_quality": "High"}
        summary, watch = describe_snapshot_delta("brief", "NEWTOKEN", current)
        assert summary == ""
        assert watch == []
    print("PASS test_snapshot_delta_returns_empty_when_no_previous")


def test_signal_delta_detects_state_shift(tmp_path: Path | None = None):
    if tmp_path is None:
        tmp_path = Path(tempfile.mkdtemp())
    snapshot_dir = tmp_path / "snapshots"
    with patch("src.services.snapshot_history.SNAPSHOT_DIR", snapshot_dir):
        save_snapshot("signal", "DOGE", {"state": "active", "signal_quality": "High", "conviction": "High"})
        current = {"state": "late", "signal_quality": "Low", "conviction": "Low"}
        summary, watch = describe_snapshot_delta("signal", "DOGE", current)
        assert "shifted" in summary.lower()
    print("PASS test_signal_delta_detects_state_shift")


def test_watchtoday_delta_detects_regime_shift(tmp_path: Path | None = None):
    if tmp_path is None:
        tmp_path = Path(tempfile.mkdtemp())
    snapshot_dir = tmp_path / "snapshots"
    with patch("src.services.snapshot_history.SNAPSHOT_DIR", snapshot_dir):
        save_snapshot("watchtoday", "", {"signal_count": 3, "market_regime": "trending-up", "signal_quality": "High"})
        current = {"signal_count": 1, "market_regime": "ranging", "signal_quality": "Low"}
        summary, watch = describe_snapshot_delta("watchtoday", "", current)
        assert "regime" in summary.lower() or "signal" in summary.lower()
    print("PASS test_watchtoday_delta_detects_regime_shift")
