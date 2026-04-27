from __future__ import annotations
import math
from typing import Dict, List

from .base import Direction, FeatureSet, Signal, Strategy
from .features import FeaturePipeline


class VolatilityFilter(Strategy):
    """
    Volatility regime filter.

    Rather than generating directional signals, this component evaluates
    whether realized volatility for each symbol falls within an acceptable
    regime.  Symbols outside the regime receive a FLAT signal, suppressing
    other strategies' signals downstream.
    """

    def __init__(
        self,
        min_vol: float = 0.05,
        max_vol: float = 0.80,
        lookback: int = 20,
    ) -> None:
        self._min_vol = min_vol
        self._max_vol = max_vol
        self._lookback = lookback

    @property
    def name(self) -> str:
        return "volatility_filter"

    def is_regime_ok(self, features: FeatureSet, min_vol: float, max_vol: float) -> bool:
        """Return True if realized vol is within [min_vol, max_vol]."""
        realized_vol = FeaturePipeline.compute_realized_vol(
            features.returns[-self._lookback:], annualize=True
        )
        return min_vol <= realized_vol <= max_vol

    def generate_signals(self, features: Dict[str, FeatureSet]) -> List[Signal]:
        signals: List[Signal] = []
        for symbol, feat in features.items():
            if not self.is_regime_ok(feat, self._min_vol, self._max_vol):
                realized_vol = FeaturePipeline.compute_realized_vol(
                    feat.returns[-self._lookback:], annualize=True
                )
                signals.append(
                    Signal(
                        symbol=symbol,
                        direction=Direction.FLAT,
                        score=0.0,
                        reason=(
                            f"Volatility regime outside bounds: "
                            f"realized={realized_vol:.2%}, "
                            f"bounds=[{self._min_vol:.2%}, {self._max_vol:.2%}]"
                        ),
                        strategy_name=self.name,
                        metadata={"realized_vol": realized_vol},
                    )
                )
        return signals
