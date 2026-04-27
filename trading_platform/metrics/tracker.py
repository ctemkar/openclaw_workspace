from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from broker.models import Fill, Position


@dataclass
class MetricsSummary:
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    gross_pnl: float
    net_pnl: float
    avg_win: float
    avg_loss: float
    expectancy: float
    max_drawdown: float
    current_drawdown: float
    avg_slippage_bps: float
    rejection_count: int
    rejection_rate: float
    sharpe_ratio: float


class MetricsTracker:
    """
    Tracks real-time performance metrics across all trades in the session.
    """

    def __init__(self) -> None:
        self._fills: List[Fill] = []
        self._expected_prices: Dict[str, float] = {}  # order_id -> expected price
        self._slippages: List[float] = []
        self._pnl_series: List[float] = []
        self._peak_equity: float = 0.0
        self._current_equity: float = 0.0
        self._rejection_reasons: List[str] = []
        self._positions_value: float = 0.0

    # ------------------------------------------------------------------
    # Update methods
    # ------------------------------------------------------------------

    def record_fill(
        self, fill: Fill, expected_price: Optional[float] = None
    ) -> None:
        self._fills.append(fill)
        if expected_price and expected_price > 0:
            slip = (fill.price - expected_price) / expected_price * 10_000.0
            self._slippages.append(slip)

    def record_rejection(self, reason: str) -> None:
        self._rejection_reasons.append(reason)

    def update_positions(self, positions: List[Position]) -> None:
        """Called periodically with current position list to update equity tracking."""
        unrealized = sum(p.unrealized_pnl for p in positions)
        realized = sum(p.realized_pnl for p in positions)
        self._current_equity = realized + unrealized
        if self._current_equity > self._peak_equity:
            self._peak_equity = self._current_equity
        self._pnl_series.append(self._current_equity)

    # ------------------------------------------------------------------
    # Aggregation
    # ------------------------------------------------------------------

    def get_summary(self) -> MetricsSummary:
        trade_pnls = self._compute_trade_pnls()
        total = len(trade_pnls)
        wins = [p for p in trade_pnls if p > 0]
        losses = [p for p in trade_pnls if p <= 0]

        win_rate = len(wins) / total if total > 0 else 0.0
        avg_win = sum(wins) / len(wins) if wins else 0.0
        avg_loss = sum(losses) / len(losses) if losses else 0.0
        gross_pnl = sum(trade_pnls)
        net_pnl = gross_pnl  # No commission model in this tracker
        expectancy = win_rate * avg_win + (1 - win_rate) * avg_loss

        max_drawdown = self._compute_max_drawdown()
        current_drawdown = (
            (self._peak_equity - self._current_equity) / self._peak_equity
            if self._peak_equity > 0
            else 0.0
        )
        avg_slip = (
            sum(self._slippages) / len(self._slippages) if self._slippages else 0.0
        )
        total_signals = total + len(self._rejection_reasons)
        rejection_rate = (
            len(self._rejection_reasons) / total_signals if total_signals > 0 else 0.0
        )
        sharpe = self._compute_sharpe()

        return MetricsSummary(
            total_trades=total,
            winning_trades=len(wins),
            losing_trades=len(losses),
            win_rate=win_rate,
            gross_pnl=gross_pnl,
            net_pnl=net_pnl,
            avg_win=avg_win,
            avg_loss=avg_loss,
            expectancy=expectancy,
            max_drawdown=max_drawdown,
            current_drawdown=current_drawdown,
            avg_slippage_bps=avg_slip,
            rejection_count=len(self._rejection_reasons),
            rejection_rate=rejection_rate,
            sharpe_ratio=sharpe,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _compute_trade_pnls(self) -> List[float]:
        """
        Pair BUY and SELL fills per symbol to compute realized P&L per round trip.
        Simple FIFO matching.
        """
        from broker.models import OrderSide
        buys: Dict[str, List[Fill]] = {}
        pnls: List[float] = []

        for fill in self._fills:
            sym = fill.symbol
            if fill.side == OrderSide.BUY:
                buys.setdefault(sym, []).append(fill)
            else:
                queue = buys.get(sym, [])
                remaining_qty = fill.quantity
                while queue and remaining_qty > 0:
                    buy_fill = queue[0]
                    matched = min(buy_fill.quantity, remaining_qty)
                    pnl = (fill.price - buy_fill.price) * matched
                    pnls.append(pnl)
                    buy_fill.quantity -= matched
                    remaining_qty -= matched
                    if buy_fill.quantity <= 0:
                        queue.pop(0)
        return pnls

    def _compute_max_drawdown(self) -> float:
        if not self._pnl_series:
            return 0.0
        peak = self._pnl_series[0]
        max_dd = 0.0
        for val in self._pnl_series:
            if val > peak:
                peak = val
            if peak > 0:
                dd = (peak - val) / peak
                max_dd = max(max_dd, dd)
        return max_dd

    def _compute_sharpe(self, risk_free: float = 0.0) -> float:
        """Annualized Sharpe ratio from P&L series (assumes daily bars)."""
        if len(self._pnl_series) < 2:
            return 0.0
        returns = [
            (self._pnl_series[i] - self._pnl_series[i - 1]) / abs(self._pnl_series[i - 1])
            if self._pnl_series[i - 1] != 0 else 0.0
            for i in range(1, len(self._pnl_series))
        ]
        if not returns:
            return 0.0
        mean_r = sum(returns) / len(returns)
        variance = sum((r - mean_r) ** 2 for r in returns) / len(returns)
        std_r = math.sqrt(variance)
        if std_r == 0:
            return 0.0
        return (mean_r - risk_free) / std_r * math.sqrt(252)
