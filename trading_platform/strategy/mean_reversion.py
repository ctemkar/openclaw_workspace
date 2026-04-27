from __future__ import annotations
from typing import Dict, List, Optional

from .base import Direction, FeatureSet, Signal, Strategy
from .features import FeaturePipeline


class MeanReversionStrategy(Strategy):
    """
    Z-score based mean-reversion strategy.

    Generates a BUY signal when the return z-score falls below -entry_z
    (price has deviated significantly below its mean) and a SELL signal
    when the z-score exceeds +entry_z.
    """

    def __init__(
        self,
        lookback: int = 20,
        entry_z: float = 2.0,
        exit_z: float = 0.5,
        max_z: float = 4.0,
    ) -> None:
        self._lookback = lookback
        self._entry_z = entry_z
        self._exit_z = exit_z
        self._max_z = max_z

    @property
    def name(self) -> str:
        return "mean_reversion"

    def generate_signals(self, features: Dict[str, FeatureSet]) -> List[Signal]:
        signals: List[Signal] = []
        for symbol, feat in features.items():
            signal = self._evaluate(symbol, feat)
            if signal is not None:
                signals.append(signal)
        return signals

    def _evaluate(self, symbol: str, feat: FeatureSet) -> Optional[Signal]:
        if len(feat.returns) < self._lookback:
            return None

        z = FeaturePipeline.compute_zscore(feat.returns, self._lookback)
        score = min(abs(z) / self._max_z, 1.0)

        if z <= -self._entry_z:
            return Signal(
                symbol=symbol,
                direction=Direction.LONG,
                score=score,
                reason=f"Z-score {z:.2f} below -{self._entry_z}, mean reversion BUY",
                strategy_name=self.name,
                metadata={"zscore": z},
            )
        elif z >= self._entry_z:
            return Signal(
                symbol=symbol,
                direction=Direction.SHORT,
                score=score,
                reason=f"Z-score {z:.2f} above +{self._entry_z}, mean reversion SELL",
                strategy_name=self.name,
                metadata={"zscore": z},
            )
        elif abs(z) < self._exit_z:
            return Signal(
                symbol=symbol,
                direction=Direction.FLAT,
                score=0.0,
                reason=f"Z-score {z:.2f} near mean, exit signal",
                strategy_name=self.name,
                metadata={"zscore": z},
            )
        return None
