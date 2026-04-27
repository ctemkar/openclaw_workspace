from __future__ import annotations
import threading
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .base import BrokerAdapter
from .models import (
    AccountSummary, Fill, Order, OrderRequest, OrderSide,
    OrderStatus, OrderType, Position,
)


class PaperBroker(BrokerAdapter):
    """
    In-memory paper trading broker.

    Fill model:
    - MARKET orders are filled immediately at the last known price
      adjusted by slippage_bps (basis points).
    - LIMIT orders are filled if the limit price is reachable given the
      last known price.
    - Thread-safe via a single reentrant lock.
    """

    def __init__(self, initial_capital: float = 100_000.0, slippage_bps: float = 5.0) -> None:
        self._lock = threading.RLock()
        self._initial_capital = initial_capital
        self._cash: float = initial_capital
        self._slippage_bps: float = slippage_bps

        # symbol -> last price
        self._prices: Dict[str, float] = {}

        # order_id -> Order
        self._orders: Dict[str, Order] = {}

        # symbol -> Position
        self._positions: Dict[str, Position] = {}

        self._fills: List[Fill] = []
        self._realized_pnl: float = 0.0
        self._daily_start_equity: float = initial_capital

    # ------------------------------------------------------------------
    # Price management
    # ------------------------------------------------------------------

    def update_prices(self, prices: Dict[str, float]) -> None:
        """Update market prices and recalculate unrealized PnL."""
        with self._lock:
            self._prices.update(prices)
            for symbol, position in self._positions.items():
                if symbol in self._prices:
                    price = self._prices[symbol]
                    position.current_price = price
                    position.unrealized_pnl = (price - position.avg_entry_price) * position.quantity

    # ------------------------------------------------------------------
    # BrokerAdapter implementation
    # ------------------------------------------------------------------

    def get_account(self) -> AccountSummary:
        with self._lock:
            unrealized = sum(p.unrealized_pnl for p in self._positions.values())
            portfolio_value = self._cash + sum(
                p.quantity * p.current_price for p in self._positions.values()
            )
            equity = portfolio_value
            daily_pnl = equity - self._daily_start_equity
            return AccountSummary(
                cash=self._cash,
                portfolio_value=portfolio_value,
                equity=equity,
                daily_pnl=daily_pnl,
                realized_pnl=self._realized_pnl,
                unrealized_pnl=unrealized,
                buying_power=self._cash,
                positions_count=len(self._positions),
            )

    def get_positions(self) -> List[Position]:
        with self._lock:
            return list(self._positions.values())

    def get_open_orders(self) -> List[Order]:
        with self._lock:
            terminal = {OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED}
            return [o for o in self._orders.values() if o.status not in terminal]

    def place_order(self, request: OrderRequest) -> Order:
        with self._lock:
            order_id = request.idempotency_key or str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            order = Order(
                order_id=order_id,
                symbol=request.symbol,
                side=request.side,
                quantity=request.quantity,
                order_type=request.order_type,
                status=OrderStatus.PENDING,
                submitted_at=now,
                limit_price=request.limit_price,
                time_in_force=request.time_in_force,
                idempotency_key=request.idempotency_key,
                strategy_id=request.strategy_id,
            )
            self._orders[order_id] = order
            self._try_fill(order)
            return order

    def cancel_order(self, order_id: str) -> bool:
        with self._lock:
            order = self._orders.get(order_id)
            if order is None:
                return False
            terminal = {OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED}
            if order.status in terminal:
                return False
            order.status = OrderStatus.CANCELLED
            return True

    def get_order(self, order_id: str) -> Optional[Order]:
        with self._lock:
            return self._orders.get(order_id)

    def get_fills(self) -> List[Fill]:
        with self._lock:
            return list(self._fills)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _try_fill(self, order: Order) -> None:
        """Attempt to fill an order based on current prices."""
        price = self._prices.get(order.symbol)
        if price is None:
            # No price available – leave as PENDING
            return

        if order.order_type == OrderType.MARKET:
            fill_price = self._apply_slippage(price, order.side)
        elif order.order_type == OrderType.LIMIT:
            lp = order.limit_price
            if lp is None:
                order.status = OrderStatus.REJECTED
                return
            # For buys: fill if market price <= limit; for sells: fill if market price >= limit
            if order.side == OrderSide.BUY and price <= lp:
                fill_price = min(price, lp)
            elif order.side == OrderSide.SELL and price >= lp:
                fill_price = max(price, lp)
            else:
                # Limit not yet reachable
                return
        else:
            order.status = OrderStatus.REJECTED
            return

        # Check sufficient cash for buys
        if order.side == OrderSide.BUY:
            cost = fill_price * order.quantity
            if cost > self._cash:
                order.status = OrderStatus.REJECTED
                return

        self._execute_fill(order, fill_price, order.quantity)

    def _apply_slippage(self, price: float, side: OrderSide) -> float:
        factor = self._slippage_bps / 10_000.0
        if side == OrderSide.BUY:
            return price * (1 + factor)
        return price * (1 - factor)

    def _execute_fill(self, order: Order, fill_price: float, fill_qty: float) -> None:
        now = datetime.now(timezone.utc)
        order.filled_qty = fill_qty
        order.filled_avg_price = fill_price
        order.filled_at = now
        order.status = OrderStatus.FILLED

        fill = Fill(
            order_id=order.order_id,
            symbol=order.symbol,
            side=order.side,
            quantity=fill_qty,
            price=fill_price,
            timestamp=now,
            strategy_id=order.strategy_id,
        )
        self._fills.append(fill)

        self._update_position(order.symbol, order.side, fill_qty, fill_price)

    def _update_position(
        self, symbol: str, side: OrderSide, qty: float, price: float
    ) -> None:
        if side == OrderSide.BUY:
            self._cash -= qty * price
            if symbol in self._positions:
                pos = self._positions[symbol]
                new_qty = pos.quantity + qty
                pos.avg_entry_price = (
                    (pos.avg_entry_price * pos.quantity + price * qty) / new_qty
                )
                pos.quantity = new_qty
                pos.current_price = price
                pos.unrealized_pnl = (price - pos.avg_entry_price) * new_qty
            else:
                self._positions[symbol] = Position(
                    symbol=symbol,
                    quantity=qty,
                    avg_entry_price=price,
                    current_price=price,
                    unrealized_pnl=0.0,
                )
        else:  # SELL
            self._cash += qty * price
            if symbol in self._positions:
                pos = self._positions[symbol]
                sold = min(qty, pos.quantity)
                pnl = (price - pos.avg_entry_price) * sold
                self._realized_pnl += pnl
                pos.realized_pnl += pnl
                pos.quantity -= sold
                if pos.quantity <= 0:
                    del self._positions[symbol]
                else:
                    pos.current_price = price
                    pos.unrealized_pnl = (price - pos.avg_entry_price) * pos.quantity

    def reset_daily(self) -> None:
        """Call at the start of each trading day to reset daily PnL tracking."""
        with self._lock:
            account = self.get_account()
            self._daily_start_equity = account.equity
