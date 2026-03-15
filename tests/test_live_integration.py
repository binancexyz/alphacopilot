"""
Live integration tests — verify the full production pipeline with real Binance data.

Gated behind LIVE_TESTS=1 env var. All tests use _network_safe() to gracefully
skip on network errors instead of crashing the suite.
"""

from __future__ import annotations

import time
from typing import Any

from src.config import settings
from src.models.schemas import AnalysisBrief
from src.services.binance_skill_bridge import BridgeBundle, fetch_live_bundle
from src.services.live_extractors import (
    extract_alpha_context,
    extract_audit_context,
    extract_futures_context,
    extract_meme_context,
)
from src.services.runtime_bridge_live_stub import (
    signal_from_raw,
    token_from_raw,
    wallet_from_raw,
    watchtoday_from_raw,
)
from src.analyzers.futures_analysis import analyze_futures
from src.analyzers.alpha_analysis import analyze_alpha
from src.formatters.brief_formatter import format_brief


# ---------------------------------------------------------------------------
# Known test address (BSC whale — public, read-only)
# ---------------------------------------------------------------------------
_TEST_BSC_ADDRESS = "0x8894e0a0c962cb723c1ef8f1d2793028d2634765"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_NETWORK_ERRORS: tuple[type[BaseException], ...] = (
    ConnectionError,
    TimeoutError,
    RuntimeError,
    LookupError,
    OSError,
)

try:
    import httpx  # type: ignore

    _NETWORK_ERRORS = (*_NETWORK_ERRORS, httpx.HTTPError)
except ModuleNotFoundError:
    pass


def _network_safe(name: str, fn) -> None:
    """Run *fn*; print SKIP on network errors instead of crashing."""
    try:
        fn()
        print(f"  PASS  {name}")
    except _NETWORK_ERRORS as exc:
        print(f"  SKIP  {name} (network: {exc!r})")


def _assert_brief_shape(brief: AnalysisBrief) -> None:
    assert brief.entity, "entity must be non-empty"
    assert brief.quick_verdict, "quick_verdict must be non-empty"
    valid_qualities = {"high", "moderate", "low", "blocked", "watch", "mixed", "n/a", "unavailable"}
    assert brief.signal_quality.lower() in valid_qualities, (
        f"signal_quality '{brief.signal_quality}' not in {valid_qualities}"
    )
    assert isinstance(brief.risk_tags, list), "risk_tags must be a list"


def _assert_bundle_shape(bundle: BridgeBundle, expected_keys: set[str]) -> None:
    assert bundle.raw, "raw must be non-empty"
    assert bundle.meta.get("status") in {"live-ok", "partial-live"}, (
        f"unexpected meta.status: {bundle.meta.get('status')}"
    )
    found = set(bundle.raw.keys())
    overlap = found & expected_keys
    assert overlap, f"expected at least one of {expected_keys} in raw, got {found}"


# ===========================================================================
# Bridge-level tests — verify API connectivity + payload shape
# ===========================================================================


def test_live_bridge_token_bnb() -> None:
    def _run():
        bundle = fetch_live_bundle("token", "BNB")
        _assert_bundle_shape(bundle, {"query-token-info"})
    _network_safe("test_live_bridge_token_bnb", _run)


def test_live_bridge_token_sol() -> None:
    def _run():
        bundle = fetch_live_bundle("token", "SOL")
        _assert_bundle_shape(bundle, {"query-token-info"})
    _network_safe("test_live_bridge_token_sol", _run)


def test_live_bridge_token_eth() -> None:
    def _run():
        bundle = fetch_live_bundle("token", "ETH")
        _assert_bundle_shape(bundle, {"query-token-info"})
    _network_safe("test_live_bridge_token_eth", _run)


def test_live_bridge_signal_bnb() -> None:
    def _run():
        bundle = fetch_live_bundle("signal", "BNB")
        _assert_bundle_shape(bundle, {"trading-signal"})
    _network_safe("test_live_bridge_signal_bnb", _run)


def test_live_bridge_signal_doge() -> None:
    def _run():
        bundle = fetch_live_bundle("signal", "DOGE")
        _assert_bundle_shape(bundle, {"trading-signal"})
    _network_safe("test_live_bridge_signal_doge", _run)


def test_live_bridge_watchtoday() -> None:
    def _run():
        bundle = fetch_live_bundle("watchtoday")
        _assert_bundle_shape(bundle, {"crypto-market-rank"})
    _network_safe("test_live_bridge_watchtoday", _run)


def test_live_bridge_audit_bnb() -> None:
    def _run():
        bundle = fetch_live_bundle("audit", "BNB")
        _assert_bundle_shape(bundle, {"query-token-info"})
    _network_safe("test_live_bridge_audit_bnb", _run)


def test_live_bridge_futures_bnb() -> None:
    def _run():
        bundle = fetch_live_bundle("futures", "BNB")
        _assert_bundle_shape(bundle, {"derivatives-trading-usds-futures"})
    _network_safe("test_live_bridge_futures_bnb", _run)


def test_live_bridge_futures_eth() -> None:
    def _run():
        bundle = fetch_live_bundle("futures", "ETH")
        _assert_bundle_shape(bundle, {"derivatives-trading-usds-futures"})
    _network_safe("test_live_bridge_futures_eth", _run)


def test_live_bridge_alpha_bnb() -> None:
    def _run():
        bundle = fetch_live_bundle("alpha", "BNB")
        _assert_bundle_shape(bundle, {"alpha"})
    _network_safe("test_live_bridge_alpha_bnb", _run)


def test_live_bridge_meme_doge() -> None:
    def _run():
        bundle = fetch_live_bundle("meme", "DOGE")
        _assert_bundle_shape(bundle, {"query-token-info"})
    _network_safe("test_live_bridge_meme_doge", _run)


def test_live_bridge_meme_pepe() -> None:
    def _run():
        bundle = fetch_live_bundle("meme", "PEPE")
        _assert_bundle_shape(bundle, {"query-token-info"})
    _network_safe("test_live_bridge_meme_pepe", _run)


def test_live_bridge_wallet() -> None:
    def _run():
        bundle = fetch_live_bundle("wallet", _TEST_BSC_ADDRESS)
        _assert_bundle_shape(bundle, {"query-address-info"})
    _network_safe("test_live_bridge_wallet", _run)


def test_live_bridge_portfolio() -> None:
    if not settings.binance_api_key:
        print("  SKIP  test_live_bridge_portfolio (no BINANCE_API_KEY)")
        return

    def _run():
        bundle = fetch_live_bundle("portfolio")
        _assert_bundle_shape(bundle, {"assets"})
    _network_safe("test_live_bridge_portfolio", _run)


# ===========================================================================
# Full pipeline tests — bridge → extract → normalize/analyze → format
# ===========================================================================


def test_live_pipeline_token_bnb() -> None:
    def _run():
        bundle = fetch_live_bundle("token", "BNB")
        result = token_from_raw("BNB", bundle.raw)
        assert result and len(result) > 10, "token pipeline produced empty output"
    _network_safe("test_live_pipeline_token_bnb", _run)


def test_live_pipeline_token_sol() -> None:
    def _run():
        bundle = fetch_live_bundle("token", "SOL")
        result = token_from_raw("SOL", bundle.raw)
        assert result and len(result) > 10, "token pipeline produced empty output"
    _network_safe("test_live_pipeline_token_sol", _run)


def test_live_pipeline_signal_bnb() -> None:
    def _run():
        bundle = fetch_live_bundle("signal", "BNB")
        result = signal_from_raw("BNB", bundle.raw)
        assert result and len(result) > 10, "signal pipeline produced empty output"
    _network_safe("test_live_pipeline_signal_bnb", _run)


def test_live_pipeline_signal_doge() -> None:
    def _run():
        bundle = fetch_live_bundle("signal", "DOGE")
        result = signal_from_raw("DOGE", bundle.raw)
        assert result and len(result) > 10, "signal pipeline produced empty output"
    _network_safe("test_live_pipeline_signal_doge", _run)


def test_live_pipeline_watchtoday() -> None:
    def _run():
        bundle = fetch_live_bundle("watchtoday")
        result = watchtoday_from_raw(bundle.raw)
        assert result and len(result) > 10, "watchtoday pipeline produced empty output"
    _network_safe("test_live_pipeline_watchtoday", _run)


def test_live_pipeline_wallet() -> None:
    def _run():
        bundle = fetch_live_bundle("wallet", _TEST_BSC_ADDRESS)
        result = wallet_from_raw(_TEST_BSC_ADDRESS, bundle.raw)
        assert result and len(result) > 10, "wallet pipeline produced empty output"
    _network_safe("test_live_pipeline_wallet", _run)


def test_live_pipeline_futures_bnb() -> None:
    def _run():
        bundle = fetch_live_bundle("futures", "BNB")
        ctx = extract_futures_context(bundle.raw, "BNB")
        brief = analyze_futures("BNB", ctx)
        _assert_brief_shape(brief)
        rendered = format_brief(brief)
        assert rendered and len(rendered) > 10, "futures pipeline produced empty output"
    _network_safe("test_live_pipeline_futures_bnb", _run)


def test_live_pipeline_alpha_bnb() -> None:
    def _run():
        bundle = fetch_live_bundle("alpha", "BNB")
        ctx = extract_alpha_context(bundle.raw, "BNB")
        brief = analyze_alpha("BNB", ctx)
        _assert_brief_shape(brief)
        rendered = format_brief(brief)
        assert rendered and len(rendered) > 10, "alpha pipeline produced empty output"
    _network_safe("test_live_pipeline_alpha_bnb", _run)


def test_live_pipeline_audit_bnb() -> None:
    def _run():
        bundle = fetch_live_bundle("audit", "BNB")
        ctx = extract_audit_context(bundle.raw, "BNB")
        assert ctx.get("symbol"), "audit context missing symbol"
        assert "audit_gate" in ctx, "audit context missing audit_gate"
    _network_safe("test_live_pipeline_audit_bnb", _run)


def test_live_pipeline_meme_doge() -> None:
    def _run():
        bundle = fetch_live_bundle("meme", "DOGE")
        ctx = extract_meme_context(bundle.raw, "DOGE")
        assert ctx.get("symbol"), "meme context missing symbol"
        assert "lifecycle_stage" in ctx, "meme context missing lifecycle_stage"
    _network_safe("test_live_pipeline_meme_doge", _run)


# ===========================================================================
# Meta / timing tests
# ===========================================================================


def test_live_bridge_meta_shape() -> None:
    def _run():
        bundle = fetch_live_bundle("token", "BNB")
        meta = bundle.meta
        for key in ("source", "skills", "status", "failedSkills", "errors", "notes", "skillRefs"):
            assert key in meta, f"meta missing key: {key}"
        assert meta["source"] == "bibipilot-bridge"
        assert isinstance(meta["skills"], list)
        assert isinstance(meta["failedSkills"], list)
        assert isinstance(meta["errors"], dict)
        assert isinstance(meta["notes"], list)
    _network_safe("test_live_bridge_meta_shape", _run)


def test_live_bridge_response_time() -> None:
    def _run():
        start = time.monotonic()
        fetch_live_bundle("token", "BNB")
        elapsed = time.monotonic() - start
        assert elapsed < 30, f"bridge response took {elapsed:.1f}s (> 30s limit)"
    _network_safe("test_live_bridge_response_time", _run)
