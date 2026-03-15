import time

from src.services.cache import cache_clear, cache_get, cache_set, cache_stats


def test_cache_set_and_get():
    cache_clear()
    cache_set("token", "BTC", {"price": 100}, ttl=10)
    result = cache_get("token", "BTC")
    assert result is not None
    assert result["price"] == 100
    print("PASS test_cache_set_and_get")


def test_cache_miss_returns_none():
    cache_clear()
    result = cache_get("token", "NONEXISTENT")
    assert result is None
    print("PASS test_cache_miss_returns_none")


def test_cache_expiry():
    cache_clear()
    cache_set("token", "BTC", {"price": 100}, ttl=0.01)
    time.sleep(0.02)
    result = cache_get("token", "BTC")
    assert result is None
    print("PASS test_cache_expiry")


def test_cache_stats_counts():
    cache_clear()
    cache_set("token", "BTC", {"price": 100}, ttl=60)
    cache_set("signal", "ETH", {"status": "watch"}, ttl=60)
    stats = cache_stats()
    assert stats["total"] == 2
    assert stats["active"] == 2
    assert stats["expired"] == 0
    print("PASS test_cache_stats_counts")


def test_cache_clear():
    cache_set("token", "BTC", {"price": 100}, ttl=60)
    cache_clear()
    assert cache_get("token", "BTC") is None
    stats = cache_stats()
    assert stats["total"] == 0
    print("PASS test_cache_clear")
