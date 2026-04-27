from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

from config.models import DataConfig
from .feed import MarketDataFeed


@dataclass
class HealthStatus:
    is_healthy: bool
    last_heartbeat: Optional[datetime]
    stale_symbols: List[str]
    message: str


class DataHealthMonitor:
    """
    Monitors the freshness of market data per symbol and reports overall
    feed health.
    """

    def __init__(self, config: DataConfig, feed: MarketDataFeed) -> None:
        self._config = config
        self._feed = feed
        self._last_update: Dict[str, datetime] = {}
        self._last_heartbeat: Optional[datetime] = None

    def record_update(self, symbol: str) -> None:
        """Record that a fresh quote was received for *symbol*."""
        self._last_update[symbol] = datetime.now(timezone.utc)
        self._last_heartbeat = datetime.now(timezone.utc)

    def get_stale_symbols(self, threshold_seconds: Optional[int] = None) -> List[str]:
        """Return symbols whose last update is older than threshold_seconds."""
        threshold = threshold_seconds or self._config.freshness_threshold_seconds
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=threshold)
        stale = [
            sym for sym, ts in self._last_update.items() if ts < cutoff
        ]
        # Symbols that were subscribed but never updated are also stale
        for sym in self._feed._symbols:
            if sym not in self._last_update:
                stale.append(sym)
        return list(set(stale))

    def check(self) -> HealthStatus:
        """Return a snapshot of current feed health."""
        stale = self.get_stale_symbols()
        feed_ok = self._feed.is_healthy()
        is_healthy = feed_ok and len(stale) == 0

        if not feed_ok:
            message = "Feed reports unhealthy"
        elif stale:
            message = f"Stale symbols: {', '.join(stale)}"
        else:
            message = "Feed healthy"

        return HealthStatus(
            is_healthy=is_healthy,
            last_heartbeat=self._last_heartbeat,
            stale_symbols=stale,
            message=message,
        )
