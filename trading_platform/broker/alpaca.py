from __future__ import annotations
import os
from typing import List, Optional
from datetime import datetime, timezone

import httpx

from .base import BrokerAdapter
from .models import (
    AccountSummary, Fill, Order, OrderRequest, OrderSide,
    OrderStatus, OrderType, Position,
)


class AlpacaBroker(BrokerAdapter):
    """
    Alpaca Markets REST API broker adapter.

    Reads credentials from environment variables specified in config.
    Supports both paper and live endpoints via base_url.
    """

    _ALPACA_DATE_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"

    def __init__(
        self,
        base_url: str = "https://paper-api.alpaca.markets",
        api_key_env: str = "ALPACA_API_KEY",
        api_secret_env: str = "ALPACA_API_SECRET",
    ) -> None:
        api_key = os.environ.get(api_key_env, "")
        api_secret = os.environ.get(api_secret_env, "")
        if not api_key or not api_secret:
            raise EnvironmentError(
                f"Alpaca credentials not found in env vars: {api_key_env}, {api_secret_env}"
            )
        self._client = httpx.Client(
            base_url=base_url,
            headers={
                "APCA-API-KEY-ID": api_key,
                "APCA-API-SECRET-KEY": api_secret,
            },
            timeout=10.0,
        )

    # ------------------------------------------------------------------
    # BrokerAdapter implementation
    # ------------------------------------------------------------------

    def get_account(self) -> AccountSummary:
        resp = self._client.get("/v2/account")
        resp.raise_for_status()
        data = resp.json()
        return AccountSummary(
            cash=float(data["cash"]),
            portfolio_value=float(data["portfolio_value"]),
            equity=float(data["equity"]),
            daily_pnl=float(data.get("unrealized_intraday_pl", 0.0)),
            realized_pnl=float(data.get("realized_pl", 0.0)),
            unrealized_pnl=float(data.get("unrealized_pl", 0.0)),
            buying_power=float(data["buying_power"]),
            positions_count=0,
        )

    def get_positions(self) -> List[Position]:
        resp = self._client.get("/v2/positions")
        resp.raise_for_status()
        positions = []
        for p in resp.json():
            positions.append(
                Position(
                    symbol=p["symbol"],
                    quantity=float(p["qty"]),
                    avg_entry_price=float(p["avg_entry_price"]),
                    current_price=float(p["current_price"]),
                    unrealized_pnl=float(p["unrealized_pl"]),
                    realized_pnl=float(p.get("realized_pl", 0.0)),
                )
            )
        return positions

    def get_open_orders(self) -> List[Order]:
        resp = self._client.get("/v2/orders", params={"status": "open"})
        resp.raise_for_status()
        return [self._parse_order(o) for o in resp.json()]

    def place_order(self, request: OrderRequest) -> Order:
        payload: dict = {
            "symbol": request.symbol,
            "qty": str(request.quantity),
            "side": request.side.value.lower(),
            "type": request.order_type.value.lower(),
            "time_in_force": request.time_in_force.lower(),
        }
        if request.limit_price is not None:
            payload["limit_price"] = str(request.limit_price)
        if request.idempotency_key:
            payload["client_order_id"] = request.idempotency_key

        resp = self._client.post("/v2/orders", json=payload)
        resp.raise_for_status()
        order = self._parse_order(resp.json())
        order.strategy_id = request.strategy_id
        return order

    def cancel_order(self, order_id: str) -> bool:
        resp = self._client.delete(f"/v2/orders/{order_id}")
        return resp.status_code in (200, 204)

    def get_order(self, order_id: str) -> Optional[Order]:
        resp = self._client.get(f"/v2/orders/{order_id}")
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return self._parse_order(resp.json())

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _parse_order(self, data: dict) -> Order:
        status_map = {
            "new": OrderStatus.NEW,
            "pending_new": OrderStatus.PENDING,
            "partially_filled": OrderStatus.PARTIALLY_FILLED,
            "filled": OrderStatus.FILLED,
            "canceled": OrderStatus.CANCELLED,
            "cancelled": OrderStatus.CANCELLED,
            "rejected": OrderStatus.REJECTED,
            "expired": OrderStatus.CANCELLED,
        }
        submitted_at = datetime.now(timezone.utc)
        if data.get("submitted_at"):
            try:
                submitted_at = datetime.fromisoformat(
                    data["submitted_at"].replace("Z", "+00:00")
                )
            except ValueError:
                pass

        filled_at: Optional[datetime] = None
        if data.get("filled_at"):
            try:
                filled_at = datetime.fromisoformat(
                    data["filled_at"].replace("Z", "+00:00")
                )
            except ValueError:
                pass

        side = OrderSide.BUY if data.get("side", "buy") == "buy" else OrderSide.SELL
        otype = (
            OrderType.LIMIT
            if data.get("type", "market") == "limit"
            else OrderType.MARKET
        )
        return Order(
            order_id=data["id"],
            symbol=data["symbol"],
            side=side,
            quantity=float(data.get("qty") or 0),
            order_type=otype,
            status=status_map.get(data.get("status", "new"), OrderStatus.NEW),
            submitted_at=submitted_at,
            filled_at=filled_at,
            filled_qty=float(data.get("filled_qty") or 0),
            filled_avg_price=(
                float(data["filled_avg_price"])
                if data.get("filled_avg_price")
                else None
            ),
            limit_price=(
                float(data["limit_price"]) if data.get("limit_price") else None
            ),
            time_in_force=data.get("time_in_force", "day").upper(),
            idempotency_key=data.get("client_order_id"),
        )
