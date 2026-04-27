from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

# These are set by the platform runner after construction
_broker = None
_session_engine = None
_metrics_tracker = None
_circuit_breaker = None

app = FastAPI(title="Trading Platform Dashboard")

_TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=_TEMPLATE_DIR)


def set_components(
    broker=None,
    session_engine=None,
    metrics_tracker=None,
    circuit_breaker=None,
) -> None:
    """Inject live platform components so the API can surface live data."""
    global _broker, _session_engine, _metrics_tracker, _circuit_breaker
    _broker = broker
    _session_engine = session_engine
    _metrics_tracker = metrics_tracker
    _circuit_breaker = circuit_breaker


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/api/status")
async def api_status() -> Dict[str, Any]:
    account: Dict[str, Any] = {}
    positions = []
    fills = []
    session_state = "UNKNOWN"
    alerts = []

    if _broker:
        try:
            acct = _broker.get_account()
            account = {
                "cash": round(acct.cash, 2),
                "portfolio_value": round(acct.portfolio_value, 2),
                "equity": round(acct.equity, 2),
                "daily_pnl": round(acct.daily_pnl, 2),
                "realized_pnl": round(acct.realized_pnl, 2),
                "unrealized_pnl": round(acct.unrealized_pnl, 2),
                "buying_power": round(acct.buying_power, 2),
                "positions_count": acct.positions_count,
            }
        except Exception as exc:
            alerts.append(f"Account error: {exc}")

        try:
            for p in _broker.get_positions():
                positions.append({
                    "symbol": p.symbol,
                    "quantity": p.quantity,
                    "avg_entry_price": round(p.avg_entry_price, 4),
                    "current_price": round(p.current_price, 4),
                    "unrealized_pnl": round(p.unrealized_pnl, 2),
                    "realized_pnl": round(p.realized_pnl, 2),
                })
        except Exception as exc:
            alerts.append(f"Positions error: {exc}")

        if hasattr(_broker, "get_fills"):
            try:
                for f in _broker.get_fills()[-20:]:
                    fills.append({
                        "order_id": f.order_id[:8],
                        "symbol": f.symbol,
                        "side": f.side.value,
                        "quantity": f.quantity,
                        "price": round(f.price, 4),
                        "timestamp": f.timestamp.isoformat(),
                        "strategy_id": f.strategy_id,
                    })
            except Exception as exc:
                alerts.append(f"Fills error: {exc}")

    if _session_engine:
        try:
            session_state = _session_engine.get_state().value
        except Exception as exc:
            alerts.append(f"Session error: {exc}")

    if _circuit_breaker:
        try:
            if _circuit_breaker.is_open():
                alerts.append(
                    f"CIRCUIT BREAKER OPEN: {_circuit_breaker.get_reason()}"
                )
        except Exception:
            pass

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_state": session_state,
        "account": account,
        "positions": positions,
        "recent_fills": fills,
        "alerts": alerts,
    }


@app.get("/api/metrics")
async def api_metrics() -> Dict[str, Any]:
    if _metrics_tracker is None:
        return {"error": "Metrics tracker not initialized"}
    try:
        summary = _metrics_tracker.get_summary()
        return {
            "total_trades": summary.total_trades,
            "winning_trades": summary.winning_trades,
            "losing_trades": summary.losing_trades,
            "win_rate": round(summary.win_rate, 4),
            "gross_pnl": round(summary.gross_pnl, 2),
            "net_pnl": round(summary.net_pnl, 2),
            "avg_win": round(summary.avg_win, 2),
            "avg_loss": round(summary.avg_loss, 2),
            "expectancy": round(summary.expectancy, 2),
            "max_drawdown": round(summary.max_drawdown, 4),
            "current_drawdown": round(summary.current_drawdown, 4),
            "avg_slippage_bps": round(summary.avg_slippage_bps, 2),
            "rejection_count": summary.rejection_count,
            "rejection_rate": round(summary.rejection_rate, 4),
            "sharpe_ratio": round(summary.sharpe_ratio, 4),
        }
    except Exception as exc:
        return {"error": str(exc)}
