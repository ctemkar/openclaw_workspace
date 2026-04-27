import pytest
from risk.controller import RiskController, RiskDecision
from risk.circuit_breaker import CircuitBreaker, CircuitState
from broker.models import (
    OrderRequest, OrderSide, OrderType, AccountSummary, Position,
)
from config.models import RiskConfig


def _make_risk_config(**overrides):
    defaults = dict(
        max_daily_loss_pct=2.0,
        max_per_trade_risk_pct=10.0,
        max_per_symbol_pct=20.0,
        max_portfolio_concentration_pct=80.0,
        max_concurrent_positions=5,
        kill_switch=False,
        atr_period=14,
        atr_multiplier=2.0,
    )
    defaults.update(overrides)
    return RiskConfig(**defaults)


def _make_account(equity=100_000.0, daily_pnl=0.0):
    return AccountSummary(
        cash=equity,
        portfolio_value=equity,
        equity=equity,
        daily_pnl=daily_pnl,
        realized_pnl=0.0,
        unrealized_pnl=0.0,
        buying_power=equity,
    )


def _make_order(symbol="SPY", qty=10.0, side=OrderSide.BUY):
    return OrderRequest(symbol=symbol, side=side, quantity=qty)


# ---------------------------------------------------------------------------
# Test 1: kill switch blocks all orders
# ---------------------------------------------------------------------------

def test_kill_switch_blocks():
    cfg = _make_risk_config(kill_switch=True)
    controller = RiskController(cfg)
    decision = controller.check_order(
        _make_order(), _make_account(), [], 0.0
    )
    assert decision.approved is False
    assert "kill_switch" in decision.checks_failed


# ---------------------------------------------------------------------------
# Test 2: daily loss limit is enforced
# ---------------------------------------------------------------------------

def test_daily_loss_limit():
    cfg = _make_risk_config(max_daily_loss_pct=2.0)
    controller = RiskController(cfg)
    # equity=100k, loss limit=2k, current daily pnl=-2500 (over limit)
    account = _make_account(equity=100_000.0)
    decision = controller.check_order(
        _make_order(), account, [], daily_pnl=-2_500.0
    )
    assert decision.approved is False
    assert "daily_loss_limit" in decision.checks_failed


# ---------------------------------------------------------------------------
# Test 3: max concurrent positions is enforced
# ---------------------------------------------------------------------------

def test_max_positions():
    cfg = _make_risk_config(max_concurrent_positions=2)
    controller = RiskController(cfg)
    existing_positions = [
        Position("AAPL", 10, 150.0, 150.0, 0.0),
        Position("MSFT", 5, 300.0, 300.0, 0.0),
    ]
    # Attempting to open a 3rd position (QQQ is not in existing_positions)
    order = _make_order(symbol="QQQ", qty=5)
    decision = controller.check_order(
        order, _make_account(), existing_positions, 0.0
    )
    assert decision.approved is False
    assert "max_positions" in decision.checks_failed


# ---------------------------------------------------------------------------
# Test 4: per-trade risk is enforced
# ---------------------------------------------------------------------------

def test_per_trade_risk():
    # max_per_trade_risk_pct=1%, equity=100k → max order = $1000
    cfg = _make_risk_config(max_per_trade_risk_pct=1.0)
    controller = RiskController(cfg)
    account = _make_account(equity=100_000.0)
    # Create an existing position to provide a price proxy
    positions = [Position("SPY", 10, 500.0, 500.0, 0.0)]
    # qty=10 @ $500 = $5000 notional, which > $1000 limit
    order = _make_order(symbol="SPY", qty=10)
    decision = controller.check_order(order, account, positions, 0.0)
    assert decision.approved is False
    assert "per_trade_risk" in decision.checks_failed


# ---------------------------------------------------------------------------
# Test 5: circuit breaker trips after consecutive failures and blocks
# ---------------------------------------------------------------------------

def test_circuit_breaker_trips():
    cb = CircuitBreaker(failure_threshold=3)
    assert cb.get_state() == CircuitState.CLOSED
    cb.record_execution_result(False)
    cb.record_execution_result(False)
    assert cb.get_state() == CircuitState.CLOSED
    cb.record_execution_result(False)
    assert cb.get_state() == CircuitState.OPEN
    assert cb.is_open() is True


def test_circuit_breaker_resets_on_success():
    cb = CircuitBreaker(failure_threshold=2)
    cb.record_execution_result(False)
    cb.record_execution_result(False)
    assert cb.get_state() == CircuitState.OPEN
    # Manually force half-open state
    cb._state = CircuitState.HALF_OPEN
    cb.record_execution_result(True)
    assert cb.get_state() == CircuitState.CLOSED


def test_circuit_breaker_pnl_trip():
    cb = CircuitBreaker()
    # 3% loss on 100k equity with 2% max loss → should trip
    cb.record_pnl(-3_000.0, 100_000.0, max_loss_pct=2.0)
    assert cb.is_open() is True
