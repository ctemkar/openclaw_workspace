# Backtesting Guide — Replay Mode

## Overview

OpenClaw's replay engine (`data/replay.py`) allows you to feed historical
OHLCV data through the full strategy, risk, and execution stack to evaluate
performance without touching live markets.

---

## 1. Preparing Historical Data

### CSV Format

```
timestamp,symbol,open,high,low,close,volume
2024-01-02T09:30:00+00:00,SPY,469.84,470.12,469.50,469.90,15234567
2024-01-02T09:30:00+00:00,QQQ,405.11,405.80,404.95,405.60,8765432
2024-01-02T09:35:00+00:00,SPY,469.90,470.55,469.70,470.30,9876543
```

### JSON Format

```json
[
  {
    "timestamp": "2024-01-02T09:30:00+00:00",
    "symbol": "SPY",
    "open": 469.84,
    "high": 470.12,
    "low": 469.50,
    "close": 469.90,
    "volume": 15234567
  }
]
```

---

## 2. Running a Backtest

```bash
python main.py \
  --config config/templates/us_equities.yaml \
  --mode replay \
  --replay-file path/to/data.csv
```

The platform will:
1. Load all bars from the file.
2. Feed each bar through the data feed (`MarketDataFeed.inject_quote`).
3. Update paper broker prices for mark-to-market P&L.
4. At the end, print a summary report.

### Sample Output

```
── Replay Complete ──────────────────────
  Final Equity : 103,241.80
  Daily PnL    : +3,241.80
  Total Trades : 47
  Win Rate     : 57.4%
  Sharpe Ratio : 1.342
─────────────────────────────────────────
```

---

## 3. Fast-Forward

To start a replay at a specific timestamp (e.g. skip pre-market):

```python
from data.replay import ReplayEngine
from datetime import datetime, timezone

engine = ReplayEngine("data.csv")
engine.fast_forward(datetime(2024, 1, 2, 9, 30, 0, tzinfo=timezone.utc))

for ts, quotes in engine:
    # process bar
    pass
```

---

## 4. Customising Strategy Parameters

Edit your YAML config to adjust which strategies run and their universe:

```yaml
strategy:
  enabled_strategies:
    - momentum
  symbol_universe:
    - SPY
    - QQQ
  min_volume: 1000000.0
  min_price: 10.0
```

---

## 5. Interpreting Results

| Metric | Description |
|--------|-------------|
| **Win Rate** | % of round-trip trades that were profitable |
| **Sharpe Ratio** | Annualized risk-adjusted return (>1.0 is good, >2.0 is excellent) |
| **Max Drawdown** | Largest peak-to-trough decline during the test |
| **Expectancy** | Average $ per trade: `win_rate × avg_win + loss_rate × avg_loss` |
| **Avg Slippage (bps)** | Average execution cost above mid-price |

---

## 6. Known Limitations

- The replay engine does not model intraday bid/ask spread dynamics.
- Limit orders are filled deterministically against the bar's close price.
- Slippage is fixed at the `slippage_bps` parameter of `PaperBroker` (default 5 bps).
- There is no partial fill simulation during replay (market orders always fill fully).
- Walk-forward validation requires separate config files for in-sample and out-of-sample periods.

---

## 7. Example Walk-Forward Template

```bash
# In-sample (2022-2023)
python main.py --config config/insample.yaml --mode replay --replay-file data/2022_2023.csv

# Out-of-sample (2024)
python main.py --config config/insample.yaml --mode replay --replay-file data/2024.csv
```

Compare Sharpe ratios.  If the out-of-sample Sharpe is less than 50% of the
in-sample Sharpe, the strategy is likely over-fit and should be re-calibrated
before going live.
