from __future__ import annotations
from typing import Dict, List, Optional

from .base import Direction, FeatureSet, Signal, Strategy
from .features import FeaturePipeline


class MomentumStrategy(Strategy):
    """
    Trend-following momentum strategy.

    Generates a BUY signal when price is above its N-period SMA and volume
    is elevated relative to its average.  Generates a SELL signal when price
    drops below the SMA.  Signal score is the normalized distance from the MA.
    """

    def __init__(self, lookback: int = 20, volume_threshold: float = 1.2) -> None:
        self._lookback = lookback
        self._volume_threshold = volume_threshold
        self._pipeline = FeaturePipeline()

    @property
    def name(self) -> str:
        return "momentum"

    def generate_signals(self, features: Dict[str, FeatureSet]) -> List[Signal]:
        signals: List[Signal] = []
        for symbol, feat in features.items():
            signal = self._evaluate(symbol, feat)
            if signal is not None:
                signals.append(signal)
        return signals

    def _evaluate(self, symbol: str, feat: FeatureSet) -> Optional[Signal]:
        prices = feat.close_prices
        if len(prices) < self._lookback:
            return None

        ma = FeaturePipeline.compute_sma(prices, self._lookback)
        if ma is None or ma == 0:
            return None

        price = feat.last_price
        volume_ratio = feat.volume / feat.avg_volume if feat.avg_volume > 0 else 0.0
        distance = (price - ma) / ma  # signed fractional distance

        if price > ma and volume_ratio >= self._volume_threshold:
            score = min(abs(distance) * 10, 1.0)
            return Signal(
                symbol=symbol,
                direction=Direction.LONG,
                score=score,
                reason=f"Price {price:.2f} > MA {ma:.2f} ({distance:.2%}), vol_ratio={volume_ratio:.2f}",
                strategy_name=self.name,
                metadata={"ma": ma, "volume_ratio": volume_ratio, "distance": distance},
            )
        elif price < ma:
            score = min(abs(distance) * 10, 1.0)
            return Signal(
                symbol=symbol,
                direction=Direction.SHORT,
                score=score,
                reason=f"Price {price:.2f} < MA {ma:.2f} ({distance:.2%})",
                strategy_name=self.name,
                metadata={"ma": ma, "volume_ratio": volume_ratio, "distance": distance},
            )
        return None
