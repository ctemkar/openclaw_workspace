from __future__ import annotations
from typing import Dict, List, Optional

from .base import Direction, FeatureSet, Signal, Strategy
from .features import FeaturePipeline


class BreakoutStrategy(Strategy):
    """
    N-period price breakout strategy with ATR-based confirmation.

    Signals when price breaks above the N-period high (LONG) or below the
    N-period low (SHORT), confirmed by ATR expansion (current ATR > ATR MA).
    """

    def __init__(self, lookback: int = 20, atr_ma_period: int = 5) -> None:
        self._lookback = lookback
        self._atr_ma_period = atr_ma_period

    @property
    def name(self) -> str:
        return "breakout"

    def generate_signals(self, features: Dict[str, FeatureSet]) -> List[Signal]:
        signals: List[Signal] = []
        for symbol, feat in features.items():
            signal = self._evaluate(symbol, feat)
            if signal is not None:
                signals.append(signal)
        return signals

    def _evaluate(self, symbol: str, feat: FeatureSet) -> Optional[Signal]:
        prices = feat.close_prices
        if len(prices) < self._lookback + 1:
            return None

        # Breakout levels use all bars except the most recent
        lookback_prices = prices[-(self._lookback + 1):-1]
        period_high = max(lookback_prices)
        period_low = min(lookback_prices)
        current = feat.last_price

        atr = feat.atr or 0.0
        atr_ok = self._check_atr_expansion(feat)

        if current > period_high and atr_ok and atr > 0:
            magnitude = (current - period_high) / atr
            score = min(magnitude, 1.0)
            return Signal(
                symbol=symbol,
                direction=Direction.LONG,
                score=score,
                reason=(
                    f"Breakout above {period_high:.2f} (ATR={atr:.2f}, "
                    f"magnitude={magnitude:.2f}x ATR)"
                ),
                strategy_name=self.name,
                metadata={
                    "period_high": period_high,
                    "period_low": period_low,
                    "atr": atr,
                    "magnitude": magnitude,
                },
            )
        elif current < period_low and atr_ok and atr > 0:
            magnitude = (period_low - current) / atr
            score = min(magnitude, 1.0)
            return Signal(
                symbol=symbol,
                direction=Direction.SHORT,
                score=score,
                reason=(
                    f"Breakdown below {period_low:.2f} (ATR={atr:.2f}, "
                    f"magnitude={magnitude:.2f}x ATR)"
                ),
                strategy_name=self.name,
                metadata={
                    "period_high": period_high,
                    "period_low": period_low,
                    "atr": atr,
                    "magnitude": magnitude,
                },
            )
        return None

    def _check_atr_expansion(self, feat: FeatureSet) -> bool:
        """Return True if current ATR is above its short-term average (expansion)."""
        prices = feat.close_prices
        if len(prices) < self._atr_ma_period + 2:
            return True  # Not enough data – assume expansion

        # Estimate ATR for each of the last atr_ma_period bars using a rolling window
        atrs: List[float] = []
        for i in range(self._atr_ma_period):
            end = len(prices) - i
            if end < 3:
                continue
            window_prices = prices[max(0, end - 15): end]
            h = [p * 1.001 for p in window_prices]  # proxy high
            l = [p * 0.999 for p in window_prices]  # proxy low
            atrs.append(FeaturePipeline.compute_atr(h, l, window_prices))

        if not atrs:
            return True

        atr_ma = sum(atrs) / len(atrs)
        current_atr = feat.atr or 0.0
        return current_atr >= atr_ma
