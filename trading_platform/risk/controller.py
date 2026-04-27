from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

from config.models import RiskConfig
from broker.models import AccountSummary, OrderRequest, OrderSide, Position


@dataclass
class RiskDecision:
    approved: bool
    reason: str
    checks_passed: List[str] = field(default_factory=list)
    checks_failed: List[str] = field(default_factory=list)


class RiskController:
    """
    Enforces all pre-trade risk limits before any order reaches the broker.

    Checks (in order):
      1. Kill switch
      2. Daily loss limit
      3. Maximum concurrent positions
      4. Per-trade risk (order notional vs equity)
      5. Per-symbol exposure
      6. Portfolio concentration
    """

    def __init__(self, config: RiskConfig) -> None:
        self._config = config

    def check_order(
        self,
        order: OrderRequest,
        account: AccountSummary,
        positions: List[Position],
        daily_pnl: float,
    ) -> RiskDecision:
        passed: List[str] = []
        failed: List[str] = []

        equity = account.equity
        if equity <= 0:
            return RiskDecision(
                approved=False,
                reason="Equity is zero or negative",
                checks_failed=["equity_positive"],
            )

        # 1. Kill switch
        if self._config.kill_switch:
            failed.append("kill_switch")
            return RiskDecision(
                approved=False,
                reason="Kill switch is active – all orders rejected",
                checks_passed=passed,
                checks_failed=failed,
            )
        passed.append("kill_switch")

        # 2. Daily loss limit
        max_loss = equity * self._config.max_daily_loss_pct / 100.0
        if daily_pnl < -max_loss:
            failed.append("daily_loss_limit")
            return RiskDecision(
                approved=False,
                reason=(
                    f"Daily loss limit breached: P&L={daily_pnl:.2f}, "
                    f"limit=-{max_loss:.2f}"
                ),
                checks_passed=passed,
                checks_failed=failed,
            )
        passed.append("daily_loss_limit")

        # 3. Max concurrent positions (only for new positions, not adding to existing)
        symbols_in_positions = {p.symbol for p in positions}
        is_new_position = order.symbol not in symbols_in_positions
        if is_new_position and len(positions) >= self._config.max_concurrent_positions:
            failed.append("max_positions")
            return RiskDecision(
                approved=False,
                reason=(
                    f"Max concurrent positions reached: "
                    f"{len(positions)}/{self._config.max_concurrent_positions}"
                ),
                checks_passed=passed,
                checks_failed=failed,
            )
        passed.append("max_positions")

        # Estimate order notional (price unknown at this point; use a proxy if available)
        # We use the last position price as a proxy, or skip if unavailable
        existing_position = next(
            (p for p in positions if p.symbol == order.symbol), None
        )
        price_proxy = (
            existing_position.current_price if existing_position else 0.0
        )
        order_notional = price_proxy * order.quantity if price_proxy > 0 else 0.0

        # 4. Per-trade risk
        if order_notional > 0:
            max_trade_value = equity * self._config.max_per_trade_risk_pct / 100.0
            if order_notional > max_trade_value:
                failed.append("per_trade_risk")
                return RiskDecision(
                    approved=False,
                    reason=(
                        f"Per-trade risk exceeded: notional={order_notional:.2f}, "
                        f"limit={max_trade_value:.2f}"
                    ),
                    checks_passed=passed,
                    checks_failed=failed,
                )
        passed.append("per_trade_risk")

        # 5. Per-symbol exposure
        existing_exposure = (
            existing_position.quantity * existing_position.current_price
            if existing_position
            else 0.0
        )
        new_exposure = existing_exposure + order_notional
        max_symbol_exposure = equity * self._config.max_per_symbol_pct / 100.0
        if new_exposure > max_symbol_exposure and order.side == OrderSide.BUY:
            failed.append("per_symbol_exposure")
            return RiskDecision(
                approved=False,
                reason=(
                    f"Per-symbol exposure limit exceeded: "
                    f"exposure={new_exposure:.2f}, limit={max_symbol_exposure:.2f}"
                ),
                checks_passed=passed,
                checks_failed=failed,
            )
        passed.append("per_symbol_exposure")

        # 6. Portfolio concentration
        total_position_value = sum(
            p.quantity * p.current_price for p in positions
        ) + order_notional
        concentration_pct = (total_position_value / equity) * 100.0
        if concentration_pct > self._config.max_portfolio_concentration_pct:
            failed.append("portfolio_concentration")
            return RiskDecision(
                approved=False,
                reason=(
                    f"Portfolio concentration too high: "
                    f"{concentration_pct:.1f}% > {self._config.max_portfolio_concentration_pct}%"
                ),
                checks_passed=passed,
                checks_failed=failed,
            )
        passed.append("portfolio_concentration")

        return RiskDecision(
            approved=True,
            reason="All risk checks passed",
            checks_passed=passed,
            checks_failed=failed,
        )
