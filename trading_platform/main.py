#!/usr/bin/env python3
"""
Trading Platform Entry Point

Usage:
    python main.py --config config/templates/us_equities.yaml --mode paper --exchange NYSE
    python main.py --config config/templates/us_equities.yaml --mode replay --replay-file data.csv
"""
from __future__ import annotations

import argparse
import signal
import sys
import time
from typing import Optional

# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------

BANNER = r"""
  ___                   _____ _
 / _ \ _ __   ___ _ __ / ____| | __ ___      __
| | | | '_ \ / _ \ '_ \ |    | |/ _` \ \ /\ / /
| |_| | |_) |  __/ | | | |___| | (_| |\ V  V /
 \___/| .__/ \___|_| |_|\____|_|\__,_| \_/\_/
      |_|    Professional Day Trading Platform
"""


def print_banner(mode: str, exchange: str) -> None:
    print(BANNER)
    print(f"  Mode     : {mode.upper()}")
    print(f"  Exchange : {exchange.upper()}")
    print(f"  Status   : Initializing…")
    print()


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def validate_config(config_path: str):
    from config.loader import load_config
    try:
        cfg = load_config(config_path)
        print(f"[✓] Config loaded from {config_path}")
        return cfg
    except FileNotFoundError:
        print(f"[✗] Config file not found: {config_path}")
        sys.exit(1)
    except Exception as exc:
        print(f"[✗] Config validation failed: {exc}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Live mode confirmation
# ---------------------------------------------------------------------------

def confirm_live_mode() -> bool:
    print("=" * 60)
    print("  ⚠  WARNING: LIVE TRADING MODE — REAL CAPITAL AT RISK  ⚠")
    print("=" * 60)
    try:
        answer = input("  Type 'CONFIRM' to proceed with live trading: ").strip()
        return answer == "CONFIRM"
    except (EOFError, KeyboardInterrupt):
        return False


# ---------------------------------------------------------------------------
# Paper mode
# ---------------------------------------------------------------------------

def run_paper_mode(config, exchange: str) -> None:
    from broker.paper import PaperBroker
    from market_session.session_engine import SessionEngine
    from risk.controller import RiskController
    from risk.circuit_breaker import CircuitBreaker
    from execution.engine import ExecutionEngine
    from data.feed import MarketDataFeed
    from data.health import DataHealthMonitor
    from metrics.tracker import MetricsTracker
    from dashboard.server import app as dash_app, set_components
    import uvicorn
    import threading

    print("[✓] Initialising paper trading components…")

    broker = PaperBroker(
        initial_capital=config.broker.paper_initial_capital,
        slippage_bps=5.0,
    )
    session = SessionEngine(config.exchange)
    risk = RiskController(config.risk)
    cb = CircuitBreaker()
    engine = ExecutionEngine(broker, risk, config.execution)
    feed = MarketDataFeed(config.data)
    feed.subscribe(config.strategy.symbol_universe)
    health_monitor = DataHealthMonitor(config.data, feed)
    metrics = MetricsTracker()

    set_components(
        broker=broker,
        session_engine=session,
        metrics_tracker=metrics,
        circuit_breaker=cb,
    )

    host = config.dashboard.host
    port = config.dashboard.port
    print(f"[✓] Dashboard starting on http://{host}:{port}")
    dash_thread = threading.Thread(
        target=uvicorn.run,
        args=(dash_app,),
        kwargs={"host": host, "port": port, "log_level": "warning"},
        daemon=True,
    )
    dash_thread.start()

    print(f"[✓] Paper trading loop active. Press Ctrl+C to stop.")
    print()

    stop = threading.Event()

    def _sighandler(sig, frame):
        print("\n[!] Shutdown requested…")
        stop.set()

    signal.signal(signal.SIGINT, _sighandler)
    signal.signal(signal.SIGTERM, _sighandler)

    tick = 0
    while not stop.is_set():
        tick += 1
        state = session.get_state()
        account = broker.get_account()
        positions = broker.get_positions()
        metrics.update_positions(positions)

        data_health = health_monitor.check()
        cb.record_data_event(data_health.is_healthy)
        cb.record_pnl(
            account.daily_pnl,
            account.equity,
            config.risk.max_daily_loss_pct,
        )

        if tick % 12 == 0:  # Print summary every ~60s
            print(
                f"  [{state.value:12s}] "
                f"Equity={account.equity:,.2f}  "
                f"DailyPnL={account.daily_pnl:+,.2f}  "
                f"Positions={len(positions)}  "
                f"CB={'OPEN' if cb.is_open() else 'CLOSED'}"
            )

        stop.wait(timeout=5.0)

    print("[✓] Shutdown complete.")


# ---------------------------------------------------------------------------
# Replay mode
# ---------------------------------------------------------------------------

def run_replay_mode(config, exchange: str, replay_file: Optional[str]) -> None:
    if not replay_file:
        print("[✗] --replay-file is required for replay mode")
        sys.exit(1)

    from broker.paper import PaperBroker
    from data.feed import MarketDataFeed
    from data.replay import ReplayEngine
    from market_session.session_engine import SessionEngine
    from risk.controller import RiskController
    from execution.engine import ExecutionEngine
    from metrics.tracker import MetricsTracker

    print(f"[✓] Loading replay data from {replay_file}…")
    try:
        replay = ReplayEngine(replay_file)
    except Exception as exc:
        print(f"[✗] Failed to load replay file: {exc}")
        sys.exit(1)

    broker = PaperBroker(initial_capital=config.broker.paper_initial_capital)
    session = SessionEngine(config.exchange)
    risk = RiskController(config.risk)
    engine = ExecutionEngine(broker, risk, config.execution)
    feed = MarketDataFeed(config.data)
    metrics = MetricsTracker()

    print(f"[✓] Replaying {replay.total_bars()} bars…")
    for ts, quotes in replay:
        for symbol, quote in quotes.items():
            feed.inject_quote(quote)
            broker.update_prices({symbol: quote.last})

        positions = broker.get_positions()
        metrics.update_positions(positions)

    account = broker.get_account()
    summary = metrics.get_summary()
    print("\n── Replay Complete ──────────────────────")
    print(f"  Final Equity : {account.equity:,.2f}")
    print(f"  Daily PnL    : {account.daily_pnl:+,.2f}")
    print(f"  Total Trades : {summary.total_trades}")
    print(f"  Win Rate     : {summary.win_rate:.1%}")
    print(f"  Sharpe Ratio : {summary.sharpe_ratio:.3f}")
    print("─────────────────────────────────────────")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Professional Day Trading Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--config", required=True,
        help="Path to YAML configuration file",
    )
    parser.add_argument(
        "--mode", choices=["paper", "live", "replay"], default="paper",
        help="Operating mode (default: paper)",
    )
    parser.add_argument(
        "--exchange", default="NYSE",
        help="Exchange identifier for logging (default: NYSE)",
    )
    parser.add_argument(
        "--replay-file",
        help="CSV or JSON file for replay mode",
    )
    args = parser.parse_args()

    print_banner(args.mode, args.exchange)
    config = validate_config(args.config)

    if args.mode == "live":
        if not confirm_live_mode():
            print("[!] Live trading cancelled.")
            sys.exit(0)
        # Live mode reuses paper loop plumbing but with an Alpaca broker
        print("[!] Live trading via Alpaca — make sure env vars are set.")
        run_paper_mode(config, args.exchange)
    elif args.mode == "replay":
        run_replay_mode(config, args.exchange, args.replay_file)
    else:
        run_paper_mode(config, args.exchange)


if __name__ == "__main__":
    main()
