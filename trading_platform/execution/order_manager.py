from __future__ import annotations
from typing import Dict, List, Optional

from broker.base import BrokerAdapter
from broker.models import Order, OrderRequest, OrderStatus


class OrderManager:
    """
    Local order book that keeps state in sync with the broker.

    Maintains an in-memory cache of all orders submitted this session and
    periodically reconciles against the broker to capture external fills,
    cancellations, and rejections.
    """

    _TERMINAL = {OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED}

    def __init__(self, broker: BrokerAdapter) -> None:
        self._broker = broker
        self._orders: Dict[str, Order] = {}  # order_id -> Order

    def submit(self, request: OrderRequest) -> Order:
        """Submit an order through the broker and track it locally."""
        order = self._broker.place_order(request)
        self._orders[order.order_id] = order
        return order

    def cancel(self, order_id: str) -> bool:
        """Cancel an order by ID.  Returns True on success."""
        cancelled = self._broker.cancel_order(order_id)
        if cancelled and order_id in self._orders:
            self._orders[order_id].status = OrderStatus.CANCELLED
        return cancelled

    def reconcile(self) -> None:
        """Sync in-flight orders with the broker's current state."""
        active = [
            o for o in self._orders.values()
            if o.status not in self._TERMINAL
        ]
        for order in active:
            try:
                fresh = self._broker.get_order(order.order_id)
                if fresh is not None:
                    self._orders[order.order_id] = fresh
            except Exception:
                pass  # Keep stale state; will retry on next reconcile

    def get_active_orders(self) -> List[Order]:
        """Return orders that have not yet reached a terminal state."""
        return [
            o for o in self._orders.values()
            if o.status not in self._TERMINAL
        ]

    def get_order_history(self) -> List[Order]:
        """Return all orders tracked this session, including terminal ones."""
        return list(self._orders.values())
