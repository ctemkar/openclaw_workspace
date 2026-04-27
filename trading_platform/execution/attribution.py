from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from broker.models import Fill


@dataclass
class AttributionSummary:
    avg_slippage_bps: float
    total_fills: int
    total_adverse_slippage: float   # sum of adverse slippage amounts (in bps)
    total_favorable_slippage: float  # sum of favorable slippage amounts (in bps)


class TradeAttributor:
    """
    Records expected (intended) prices and actual fill prices to compute
    execution quality metrics (slippage).

    Slippage is expressed in basis points:
        slippage_bps = (fill_price - expected_price) / expected_price * 10_000
    A positive value for a BUY means the fill was more expensive than expected
    (adverse slippage).
    """

    def __init__(self) -> None:
        self._expected: Dict[str, float] = {}     # order_id -> expected price
        self._slippage: Dict[str, float] = {}     # order_id -> slippage_bps
        self._fills: List[Fill] = []

    def record_order_intent(self, order_id: str, expected_price: float) -> None:
        """Record the price we expected to fill at before submitting the order."""
        self._expected[order_id] = expected_price

    def record_fill(self, fill: Fill) -> None:
        """Record an actual fill and compute slippage if we have an expected price."""
        self._fills.append(fill)
        expected = self._expected.get(fill.order_id)
        if expected and expected > 0:
            slip_bps = (fill.price - expected) / expected * 10_000.0
            self._slippage[fill.order_id] = slip_bps

    def get_slippage(self, order_id: str) -> Optional[float]:
        """Return slippage in bps for the given order, or None if not available."""
        return self._slippage.get(order_id)

    def get_attribution_summary(self) -> AttributionSummary:
        slippages = list(self._slippage.values())
        if not slippages:
            return AttributionSummary(
                avg_slippage_bps=0.0,
                total_fills=len(self._fills),
                total_adverse_slippage=0.0,
                total_favorable_slippage=0.0,
            )
        avg = sum(slippages) / len(slippages)
        adverse = sum(s for s in slippages if s > 0)
        favorable = sum(abs(s) for s in slippages if s < 0)
        return AttributionSummary(
            avg_slippage_bps=avg,
            total_fills=len(self._fills),
            total_adverse_slippage=adverse,
            total_favorable_slippage=favorable,
        )
