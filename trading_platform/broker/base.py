from abc import ABC, abstractmethod
from typing import List, Optional
from .models import AccountSummary, Order, OrderRequest, Position


class BrokerAdapter(ABC):
    """Abstract base class for all broker adapters."""

    @abstractmethod
    def get_account(self) -> AccountSummary:
        """Return current account summary."""

    @abstractmethod
    def get_positions(self) -> List[Position]:
        """Return list of open positions."""

    @abstractmethod
    def get_open_orders(self) -> List[Order]:
        """Return list of currently open (non-terminal) orders."""

    @abstractmethod
    def place_order(self, request: OrderRequest) -> Order:
        """Submit an order and return the resulting Order object."""

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order by ID.  Returns True if cancelled successfully."""

    @abstractmethod
    def get_order(self, order_id: str) -> Optional[Order]:
        """Fetch a single order by its ID."""
