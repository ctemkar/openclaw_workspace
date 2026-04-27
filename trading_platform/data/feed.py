from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

from config.models import DataConfig


@dataclass
class Quote:
    symbol: str
    bid: float
    ask: float
    last: float
    volume: float
    timestamp: datetime


class MarketDataFeed:
    """
    Abstract market data feed with primary/fallback provider support
    and freshness checking.

    In a real deployment the get_quote() method would call a live
    data provider (e.g. Polygon.io).  Here we provide a simulation-friendly
    implementation that accepts injected prices and routes to a fallback
    when the primary fails.
    """

    def __init__(self, config: DataConfig) -> None:
        self._config = config
        self._symbols: List[str] = []
        self._cache: Dict[str, Quote] = {}
        self._healthy: bool = True

    # ------------------------------------------------------------------
    # Subscription
    # ------------------------------------------------------------------

    def subscribe(self, symbols: List[str]) -> None:
        """Register the list of symbols to track."""
        self._symbols = list(symbols)

    # ------------------------------------------------------------------
    # Quote retrieval
    # ------------------------------------------------------------------

    def get_quote(self, symbol: str) -> Optional[Quote]:
        """
        Fetch a quote for *symbol*.

        Tries the primary feed first; on failure falls back to the secondary
        feed if configured.  Returns None if both feeds fail or if the quote
        is stale.
        """
        quote = self._fetch_primary(symbol)
        if quote is None and self._config.fallback_feed:
            quote = self._fetch_fallback(symbol)
        if quote is None:
            return None
        if not self._is_fresh(quote):
            return None
        self._cache[symbol] = quote
        return quote

    def get_latest(self, symbol: str) -> Optional[Quote]:
        """Return the last cached quote, regardless of freshness."""
        return self._cache.get(symbol)

    def inject_quote(self, quote: Quote) -> None:
        """
        Inject a quote directly into the cache.

        Used by the paper trading loop and replay engine to feed prices
        without calling an external API.
        """
        self._cache[quote.symbol] = quote

    def is_healthy(self) -> bool:
        return self._healthy

    def set_healthy(self, healthy: bool) -> None:
        self._healthy = healthy

    # ------------------------------------------------------------------
    # Internal feed implementations (override in subclasses for live use)
    # ------------------------------------------------------------------

    def _fetch_primary(self, symbol: str) -> Optional[Quote]:
        """Fetch from the configured primary feed.  Returns cached value as default."""
        return self._cache.get(symbol)

    def _fetch_fallback(self, symbol: str) -> Optional[Quote]:
        """Fetch from the configured fallback feed."""
        return None

    def _is_fresh(self, quote: Quote) -> bool:
        threshold = timedelta(seconds=self._config.freshness_threshold_seconds)
        now = datetime.now(timezone.utc)
        if quote.timestamp.tzinfo is None:
            quote_ts = quote.timestamp.replace(tzinfo=timezone.utc)
        else:
            quote_ts = quote.timestamp
        return (now - quote_ts) <= threshold
