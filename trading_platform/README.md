# OpenClaw — Professional Day Trading Platform

A complete, modular day-trading platform for traditional financial markets
(equities, ETFs, futures — **no crypto**).

## Features

- **Multi-exchange support** (NYSE/NASDAQ, Euronext, TSE/SGX) with correct timezone and session logic
- **Multiple strategies**: Momentum, Mean Reversion, Breakout, Volatility filter
- **ATR-based position sizing** with full pre-trade risk checks
- **Circuit breaker** (CLOSED / OPEN / HALF_OPEN) protecting against execution and data failures
- **Paper broker** with realistic fill simulation and slippage
- **Alpaca Markets adapter** for live/paper API trading
- **FastAPI dashboard** with live metrics, positions, fills, and P&L chart
- **Replay engine** for historical backtesting from CSV/JSON files
- **Full test suite** covering session, risk, order, and data components

## Directory Structure

```
trading_platform/
├── config/          # Pydantic models, YAML loader, exchange templates
├── market_session/  # Session engine, trading calendar, session gate
├── broker/          # Abstract adapter, paper broker, Alpaca broker
├── strategy/        # Momentum, mean reversion, breakout, volatility, router
├── risk/            # Pre-trade risk controller, position sizer, circuit breaker
├── execution/       # Execution engine (retry + risk), order manager, attribution
├── data/            # Market data feed, health monitor, replay engine
├── dashboard/       # FastAPI server + Tailwind HTML dashboard
├── metrics/         # Real-time performance metrics tracker
├── tests/           # pytest test suite
├── docs/            # Runbook, risk policy, backtest guide
└── main.py          # Entry point
```

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run paper trading with US equities config
python main.py --config config/templates/us_equities.yaml --mode paper

# 3. Open the dashboard
open http://localhost:8080

# 4. Run the test suite
python -m pytest tests/ -v
```

## Configuration

All parameters are defined in YAML.  Three templates are provided:
- `config/templates/us_equities.yaml` — NYSE/NASDAQ equities
- `config/templates/eu_equities.yaml` — Euronext European equities
- `config/templates/asia_futures.yaml` — TSE/SGX Asia futures

Override any parameter at runtime using `PLATFORM_` environment variables:

```bash
export PLATFORM_RISK__KILL_SWITCH=true
export PLATFORM_MODE=paper
```

## Live Trading (Alpaca)

```bash
export ALPACA_API_KEY="your-key"
export ALPACA_API_SECRET="your-secret"
python main.py --config config/my_live.yaml --mode live --exchange NYSE
```

You will be asked to type `CONFIRM` before any orders are placed.

## Backtesting / Replay

```bash
python main.py \
  --config config/templates/us_equities.yaml \
  --mode replay \
  --replay-file data/spy_2024.csv
```

See `docs/backtest_template.md` for the CSV format and walk-forward methodology.

## Risk Controls

All risk limits are enforced before any order reaches the broker:

| Control | Default |
|---------|---------|
| Daily loss limit | 2% of equity |
| Per-trade risk | 1% of equity |
| Per-symbol exposure | 10% of equity |
| Portfolio concentration | 25% of equity |
| Max concurrent positions | 10 |
| Circuit breaker (failures) | 5 consecutive |

See `docs/risk_policy.md` for full details.

## Disclaimer

This software is provided for **educational and research purposes only**.
It is not financial advice.  Trading financial instruments carries significant
risk of loss.  Always paper-trade and validate strategies before risking real capital.
