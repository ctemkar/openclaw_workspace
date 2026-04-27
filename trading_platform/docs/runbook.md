# Operator Runbook — OpenClaw Trading Platform

## 1. Prerequisites

- **Python** 3.9 or higher
- **pip** 22+
- Network access to your data provider (Polygon.io) and broker (Alpaca Markets)

Install all dependencies:

```bash
cd trading_platform
pip install -r requirements.txt
```

Verify installation:

```bash
python -c "import fastapi, pydantic, pytz; print('OK')"
```

---

## 2. Configuration

### YAML Configuration Files

Three templates are provided under `config/templates/`:

| File | Market | Timezone |
|------|--------|----------|
| `us_equities.yaml` | NYSE / NASDAQ | America/New_York |
| `eu_equities.yaml` | Euronext | Europe/Paris |
| `asia_futures.yaml` | TSE / SGX | Asia/Tokyo |

Copy and customise a template before going live:

```bash
cp config/templates/us_equities.yaml config/my_live.yaml
$EDITOR config/my_live.yaml
```

### Environment Variable Overrides

Any YAML key can be overridden at runtime using the `PLATFORM_` prefix with
double-underscores for nested paths:

| Environment Variable | YAML Path |
|---------------------|-----------|
| `PLATFORM_MODE` | `mode` |
| `PLATFORM_RISK__KILL_SWITCH` | `risk.kill_switch` |
| `PLATFORM_RISK__MAX_DAILY_LOSS_PCT` | `risk.max_daily_loss_pct` |
| `PLATFORM_BROKER__ADAPTER` | `broker.adapter` |

### API Keys (Alpaca)

Never hard-code credentials. Set the following environment variables:

```bash
export ALPACA_API_KEY="your-key-here"
export ALPACA_API_SECRET="your-secret-here"
```

For paper trading, these are not required (the `paper` adapter is used by default).

---

## 3. Start Commands

### Paper Trading (safe, no real money)

```bash
python main.py --config config/templates/us_equities.yaml --mode paper --exchange NYSE
```

### Live Trading (⚠ real capital at risk)

```bash
export ALPACA_API_KEY="..."
export ALPACA_API_SECRET="..."
python main.py --config config/my_live.yaml --mode live --exchange NYSE
```

You will be prompted to type `CONFIRM` before trading begins.

### Replay / Backtest Mode

```bash
python main.py \
  --config config/templates/us_equities.yaml \
  --mode replay \
  --replay-file data/spy_2024.csv
```

See `docs/backtest_template.md` for CSV format and usage guidance.

---

## 4. Stop / Recovery Procedures

### Graceful Shutdown

Press **Ctrl+C** once. The platform will:
1. Stop accepting new entry signals.
2. Complete in-flight order submissions.
3. Shut down the dashboard server.
4. Print a final equity/P&L summary.

If the process is unresponsive:

```bash
kill -TERM <PID>
```

### Kill Switch (Emergency)

Set via environment variable — takes effect immediately without restart:

```bash
export PLATFORM_RISK__KILL_SWITCH=true
# Or edit the YAML and restart
```

All new order submissions will be rejected until the kill switch is cleared.

---

## 5. Monitoring

### Dashboard

The web dashboard auto-starts on port 8080:

```
http://localhost:8080/
```

It refreshes every 5 seconds displaying:
- Session state (colour-coded)
- Account equity, cash, P&L
- Open positions table
- Recent fills
- Performance metrics (win rate, Sharpe, drawdown)
- Active alerts (circuit breaker, stale data)

### Health Endpoint

```bash
curl http://localhost:8080/health
# {"status": "ok", "timestamp": "2024-06-03T09:30:00+00:00"}
```

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/status` | Live session state, account, positions, fills, alerts |
| `GET /api/metrics` | Performance metrics (win rate, Sharpe, P&L, drawdown) |
| `GET /health` | Simple health check |

---

## 6. Common Issues and Solutions

### "Config file not found"
Ensure the path is relative to the directory where you run `python main.py`.

### "Alpaca credentials not found"
Set `ALPACA_API_KEY` and `ALPACA_API_SECRET` environment variables before starting.

### Dashboard port already in use
Change `dashboard.port` in your YAML config:
```yaml
dashboard:
  port: 8181
```

### Circuit breaker tripped
Check the dashboard alerts panel for the reason. Common causes:
- 5+ consecutive execution failures → fix broker connectivity
- Data feed unhealthy for >60s → check your data provider
- Daily P&L loss limit exceeded → review risk parameters or wait until next day

To reset the circuit breaker, restart the platform after resolving the underlying issue.

### "No fills" in paper mode
Make sure `update_prices()` is called with current market data.
In standalone mode the feed must be connected to a real or simulated data source.
