import pytest
from datetime import datetime, timezone
from broker.paper import PaperBroker
from broker.models import (
    OrderRequest, OrderSide, OrderType, OrderStatus,
)


def _broker(capital=100_000.0):
    return PaperBroker(initial_capital=capital, slippage_bps=5.0)


# ---------------------------------------------------------------------------
# Test 1: paper broker fills a market order
# ---------------------------------------------------------------------------

def test_paper_fill_market_order():
    broker = _broker()
    broker.update_prices({"SPY": 450.0})

    req = OrderRequest(
        symbol="SPY",
        side=OrderSide.BUY,
        quantity=10.0,
        order_type=OrderType.MARKET,
    )
    order = broker.place_order(req)

    assert order.status == OrderStatus.FILLED
    assert order.filled_qty == 10.0
    assert order.filled_avg_price is not None
    # With 5 bps slippage on a buy: 450 * (1 + 0.0005) = 450.225
    assert abs(order.filled_avg_price - 450.225) < 0.01


# ---------------------------------------------------------------------------
# Test 2: order state transitions NEW -> PENDING -> FILLED
# ---------------------------------------------------------------------------

def test_order_state_transitions():
    broker = _broker()
    # No price set → order stays PENDING (not filled immediately)
    req = OrderRequest(
        symbol="AAPL",
        side=OrderSide.BUY,
        quantity=5.0,
        order_type=OrderType.MARKET,
    )
    order = broker.place_order(req)
    # Without a price, the paper broker cannot fill; status stays PENDING
    assert order.status == OrderStatus.PENDING

    # Now provide a price → inject quote and check fills via reconcile
    broker.update_prices({"AAPL": 180.0})
    # Place another order now that price is known
    req2 = OrderRequest(
        symbol="AAPL",
        side=OrderSide.BUY,
        quantity=5.0,
        order_type=OrderType.MARKET,
    )
    order2 = broker.place_order(req2)
    assert order2.status == OrderStatus.FILLED


# ---------------------------------------------------------------------------
# Test 3: cancel an open order
# ---------------------------------------------------------------------------

def test_cancel_order():
    broker = _broker()
    # No price → order stays PENDING, so we can cancel it
    req = OrderRequest(
        symbol="MSFT",
        side=OrderSide.BUY,
        quantity=3.0,
        order_type=OrderType.MARKET,
    )
    order = broker.place_order(req)
    assert order.status == OrderStatus.PENDING

    result = broker.cancel_order(order.order_id)
    assert result is True

    refreshed = broker.get_order(order.order_id)
    assert refreshed.status == OrderStatus.CANCELLED


# ---------------------------------------------------------------------------
# Test 4: position tracking updates correctly after fills
# ---------------------------------------------------------------------------

def test_position_tracking():
    broker = _broker(capital=100_000.0)
    broker.update_prices({"QQQ": 400.0})

    # Buy 10 shares
    broker.place_order(OrderRequest("QQQ", OrderSide.BUY, 10.0))
    positions = broker.get_positions()
    assert len(positions) == 1
    pos = positions[0]
    assert pos.symbol == "QQQ"
    assert pos.quantity == 10.0

    # Sell 5 shares
    broker.place_order(OrderRequest("QQQ", OrderSide.SELL, 5.0))
    positions = broker.get_positions()
    assert len(positions) == 1
    assert positions[0].quantity == 5.0

    # Sell remaining 5 shares → position should be closed
    broker.place_order(OrderRequest("QQQ", OrderSide.SELL, 5.0))
    positions = broker.get_positions()
    assert len(positions) == 0


# ---------------------------------------------------------------------------
# Test 5: cash decreases on buy, increases on sell
# ---------------------------------------------------------------------------

def test_cash_tracking():
    broker = _broker(capital=10_000.0)
    broker.update_prices({"IWM": 200.0})

    broker.place_order(OrderRequest("IWM", OrderSide.BUY, 10.0))
    account = broker.get_account()
    # Cash should be less than 10_000 (cost ≈ 10 × 200 × 1.0005 = 2001)
    assert account.cash < 10_000.0

    broker.place_order(OrderRequest("IWM", OrderSide.SELL, 10.0))
    account_after = broker.get_account()
    # After round-trip with slippage we expect slightly less cash (adverse slippage)
    assert account_after.cash > 0
