from __future__ import annotations
import time
import uuid
from dataclasses import dataclass, field
from typing import List, Optional

from broker.base import BrokerAdapter
from broker.models import AccountSummary, Order, OrderRequest, Position
from config.models import ExecutionConfig
from risk.controller import RiskController


@dataclass
class ExecutionResult:
    success: bool
    order: Optional[Order]
    reason: str
    attempts: int = 0


class ExecutionEngine:
    """
    Validates orders against risk limits and submits them to the broker
    with automatic retry and exponential back-off.
    """

    def __init__(
        self,
        broker: BrokerAdapter,
        risk: RiskController,
        config: ExecutionConfig,
    ) -> None:
        self._broker = broker
        self._risk = risk
        self._config = config

    def submit(
        self,
        order: OrderRequest,
        account: AccountSummary,
        positions: List[Position],
        daily_pnl: float,
    ) -> ExecutionResult:
        # Assign idempotency key if not already set
        if not order.idempotency_key:
            order.idempotency_key = str(uuid.uuid4())

        # Pre-trade risk check
        decision = self._risk.check_order(order, account, positions, daily_pnl)
        if not decision.approved:
            return ExecutionResult(
                success=False,
                order=None,
                reason=f"Risk rejected: {decision.reason}",
                attempts=0,
            )

        # Retry loop with exponential back-off
        last_error: str = ""
        for attempt in range(1, self._config.max_retries + 1):
            try:
                placed = self._broker.place_order(order)
                return ExecutionResult(
                    success=True,
                    order=placed,
                    reason="Order placed successfully",
                    attempts=attempt,
                )
            except Exception as exc:
                last_error = str(exc)
                if attempt < self._config.max_retries:
                    backoff = self._config.retry_backoff_seconds * (2 ** (attempt - 1))
                    time.sleep(backoff)

        return ExecutionResult(
            success=False,
            order=None,
            reason=f"Broker error after {self._config.max_retries} attempts: {last_error}",
            attempts=self._config.max_retries,
        )
