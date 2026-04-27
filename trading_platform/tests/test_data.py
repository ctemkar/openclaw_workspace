import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone, timedelta

from data.feed import MarketDataFeed, Quote
from data.health import DataHealthMonitor, HealthStatus
from config.models import DataConfig


def _make_config(freshness=30, fallback=None):
    return DataConfig(
        primary_feed="polygon",
        fallback_feed=fallback,
        freshness_threshold_seconds=freshness,
        heartbeat_interval_seconds=10,
    )


def _fresh_quote(symbol="SPY", price=450.0):
    return Quote(
        symbol=symbol,
        bid=price - 0.01,
        ask=price + 0.01,
        last=price,
        volume=1_000_000.0,
        timestamp=datetime.now(timezone.utc),
    )


def _stale_quote(symbol="SPY", price=450.0, age_seconds=60):
    return Quote(
        symbol=symbol,
        bid=price - 0.01,
        ask=price + 0.01,
        last=price,
        volume=1_000_000.0,
        timestamp=datetime.now(timezone.utc) - timedelta(seconds=age_seconds),
    )


# ---------------------------------------------------------------------------
# Test 1: freshness check rejects stale data
# ---------------------------------------------------------------------------

def test_stale_data_detection():
    cfg = _make_config(freshness=30)
    feed = MarketDataFeed(cfg)

    stale = _stale_quote(age_seconds=60)
    feed.inject_quote(stale)

    # get_quote should return None because the cached quote is stale
    result = feed.get_quote("SPY")
    assert result is None


# ---------------------------------------------------------------------------
# Test 2: fresh data passes the freshness check
# ---------------------------------------------------------------------------

def test_fresh_data_accepted():
    cfg = _make_config(freshness=30)
    feed = MarketDataFeed(cfg)

    fresh = _fresh_quote()
    feed.inject_quote(fresh)

    result = feed.get_quote("SPY")
    assert result is not None
    assert result.symbol == "SPY"


# ---------------------------------------------------------------------------
# Test 3: fallback triggered when primary fails
# ---------------------------------------------------------------------------

def test_fallback_triggered():
    cfg = _make_config(freshness=30, fallback="backup_feed")
    feed = MarketDataFeed(cfg)

    fallback_quote = _fresh_quote(symbol="AAPL", price=190.0)

    # Override _fetch_fallback to return a known quote
    feed._fetch_fallback = MagicMock(return_value=fallback_quote)
    # Primary cache is empty, so primary returns None → fallback invoked
    result = feed.get_quote("AAPL")

    feed._fetch_fallback.assert_called_once_with("AAPL")
    assert result is not None
    assert result.symbol == "AAPL"


# ---------------------------------------------------------------------------
# Test 4: health monitor detects stale symbols
# ---------------------------------------------------------------------------

def test_health_monitor_stale_symbols():
    cfg = _make_config(freshness=5)
    feed = MarketDataFeed(cfg)
    feed.subscribe(["SPY", "QQQ"])
    monitor = DataHealthMonitor(cfg, feed)

    # Record an update for SPY only – QQQ never updated
    monitor.record_update("SPY")

    # Manually backdate SPY's last update to make it stale
    monitor._last_update["SPY"] = datetime.now(timezone.utc) - timedelta(seconds=30)

    stale = monitor.get_stale_symbols(threshold_seconds=5)
    assert "SPY" in stale
    assert "QQQ" in stale


# ---------------------------------------------------------------------------
# Test 5: health monitor reports healthy when all symbols are fresh
# ---------------------------------------------------------------------------

def test_health_monitor_healthy():
    cfg = _make_config(freshness=30)
    feed = MarketDataFeed(cfg)
    feed.subscribe(["SPY"])
    monitor = DataHealthMonitor(cfg, feed)

    monitor.record_update("SPY")

    status = monitor.check()
    assert status.is_healthy is True
    assert status.stale_symbols == []
