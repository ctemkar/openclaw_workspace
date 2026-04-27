from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class OrderStatus(str, Enum):
    NEW = "NEW"
    PENDING = "PENDING"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


@dataclass
class OrderRequest:
    symbol: str
    side: OrderSide
    quantity: float
    order_type: OrderType = OrderType.MARKET
    limit_price: Optional[float] = None
    time_in_force: str = "DAY"
    idempotency_key: Optional[str] = None
    strategy_id: Optional[str] = None


@dataclass
class Order:
    order_id: str
    symbol: str
    side: OrderSide
    quantity: float
    order_type: OrderType
    status: OrderStatus
    submitted_at: datetime
    filled_at: Optional[datetime] = None
    filled_qty: float = 0.0
    filled_avg_price: Optional[float] = None
    limit_price: Optional[float] = None
    time_in_force: str = "DAY"
    idempotency_key: Optional[str] = None
    strategy_id: Optional[str] = None


@dataclass
class Position:
    symbol: str
    quantity: float
    avg_entry_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float = 0.0


@dataclass
class Fill:
    order_id: str
    symbol: str
    side: OrderSide
    quantity: float
    price: float
    timestamp: datetime
    strategy_id: Optional[str] = None


@dataclass
class AccountSummary:
    cash: float
    portfolio_value: float
    equity: float
    daily_pnl: float
    realized_pnl: float
    unrealized_pnl: float
    buying_power: float
    positions_count: int = 0
