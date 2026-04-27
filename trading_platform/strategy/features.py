from __future__ import annotations
import math
from typing import List, Optional


class FeaturePipeline:
    """Compute technical features from raw OHLCV price lists."""

    @staticmethod
    def compute_returns(prices: List[float]) -> List[float]:
        """Return list of period-over-period percent returns."""
        if len(prices) < 2:
            return []
        return [(prices[i] - prices[i - 1]) / prices[i - 1] for i in range(1, len(prices))]

    @staticmethod
    def compute_atr(
        highs: List[float],
        lows: List[float],
        closes: List[float],
        period: int = 14,
    ) -> float:
        """
        Compute Average True Range.
        Requires at least period+1 bars to have a prior close.
        """
        if len(highs) < 2 or len(lows) < 2 or len(closes) < 2:
            return 0.0
        true_ranges: List[float] = []
        for i in range(1, len(closes)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i - 1]),
                abs(lows[i] - closes[i - 1]),
            )
            true_ranges.append(tr)
        window = min(period, len(true_ranges))
        if window == 0:
            return 0.0
        return sum(true_ranges[-window:]) / window

    @staticmethod
    def compute_zscore(values: List[float], window: int) -> float:
        """
        Z-score of the most recent value relative to the rolling window.
        Returns 0.0 if standard deviation is zero.
        """
        if len(values) < window:
            sample = values
        else:
            sample = values[-window:]
        if len(sample) < 2:
            return 0.0
        mean = sum(sample) / len(sample)
        variance = sum((x - mean) ** 2 for x in sample) / len(sample)
        std = math.sqrt(variance)
        if std == 0:
            return 0.0
        return (sample[-1] - mean) / std

    @staticmethod
    def compute_sma(prices: List[float], period: int) -> Optional[float]:
        """Simple moving average of the last `period` prices."""
        if len(prices) < period:
            return None
        return sum(prices[-period:]) / period

    @staticmethod
    def compute_realized_vol(returns: List[float], annualize: bool = True) -> float:
        """Annualized realized volatility from a list of percent returns."""
        if len(returns) < 2:
            return 0.0
        mean = sum(returns) / len(returns)
        variance = sum((r - mean) ** 2 for r in returns) / len(returns)
        std = math.sqrt(variance)
        if annualize:
            return std * math.sqrt(252)
        return std

    def compute(
        self,
        symbol: str,
        prices: List[float],
        volumes: List[float],
        highs: List[float],
        lows: List[float],
    ) -> "FeatureSet":
        """Build a complete FeatureSet from raw OHLCV lists."""
        from .base import FeatureSet  # local import to avoid circular

        returns = self.compute_returns(prices)
        atr = self.compute_atr(highs, lows, prices, period=14)
        current_volume = volumes[-1] if volumes else 0.0
        avg_volume = sum(volumes) / len(volumes) if volumes else 0.0
        return FeatureSet(
            symbol=symbol,
            last_price=prices[-1] if prices else 0.0,
            returns=returns,
            volume=current_volume,
            avg_volume=avg_volume,
            high=highs[-1] if highs else 0.0,
            low=lows[-1] if lows else 0.0,
            close_prices=list(prices),
            atr=atr,
        )
