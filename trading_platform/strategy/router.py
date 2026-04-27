from __future__ import annotations
from typing import Dict, List

from config.models import StrategyConfig
from .base import Direction, FeatureSet, Signal, Strategy


class StrategyRouter:
    """
    Runs all configured strategies, deduplicates signals by symbol
    (highest score wins), and applies basic universe filters.
    """

    def __init__(self, strategies: List[Strategy], config: StrategyConfig) -> None:
        self._strategies = strategies
        self._config = config

    def route(self, features: Dict[str, FeatureSet]) -> List[Signal]:
        """
        Execute all strategies, collect signals, deduplicate by symbol
        (highest score wins per symbol), and filter by universe constraints.
        Returns a list of signals sorted by score descending.
        """
        # Filter features to configured universe
        filtered = {
            sym: feat
            for sym, feat in features.items()
            if sym in self._config.symbol_universe
            and feat.last_price >= self._config.min_price
            and feat.volume >= self._config.min_volume
        }

        all_signals: List[Signal] = []
        for strategy in self._strategies:
            try:
                signals = strategy.generate_signals(filtered)
                all_signals.extend(signals)
            except Exception as exc:
                # Log and continue – never let one strategy crash the router
                print(f"[StrategyRouter] strategy={strategy.name} error: {exc}")

        # Deduplicate: per symbol keep the signal with the highest score.
        # FLAT signals from volatility filter always win to suppress trading.
        best: Dict[str, Signal] = {}
        for sig in all_signals:
            if sig.symbol not in best:
                best[sig.symbol] = sig
            else:
                existing = best[sig.symbol]
                # A FLAT signal overrides anything except another FLAT
                if sig.direction == Direction.FLAT:
                    best[sig.symbol] = sig
                elif existing.direction != Direction.FLAT and sig.score > existing.score:
                    best[sig.symbol] = sig

        return sorted(best.values(), key=lambda s: s.score, reverse=True)
