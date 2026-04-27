# Risk Policy — OpenClaw Trading Platform

## Purpose

This document defines the risk limits, controls, escalation procedures, and
circuit-breaker conditions that govern all trading activity on the OpenClaw
platform.  All operators must read and acknowledge this policy before enabling
live trading.

---

## 1. Risk Limits and Rationale

| Limit | Default | Rationale |
|-------|---------|-----------|
| `max_daily_loss_pct` | 2.0% | Caps intraday loss to preserve capital and force a structured review. |
| `max_per_trade_risk_pct` | 1.0% | ATR-based stop ensures no single trade risks more than 1% of equity. |
| `max_per_symbol_pct` | 10.0% | Prevents over-concentration in a single name. |
| `max_portfolio_concentration_pct` | 25.0% | Keeps the total invested portion manageable relative to equity. |
| `max_concurrent_positions` | 10 | Limits operational complexity and correlation risk. |
| `atr_period` | 14 | Standard 14-period ATR is well-established for stop placement. |
| `atr_multiplier` | 2.0 | 2× ATR provides a reasonable buffer beyond normal noise. |

All limits are configured in the YAML file and can be overridden by the
environment variables documented in the runbook.

---

## 2. Kill Switch Procedure

The kill switch immediately halts all new order submissions without requiring a restart.

### Activation (emergency)

```bash
# Via environment variable (takes effect on next order attempt):
export PLATFORM_RISK__KILL_SWITCH=true

# Via YAML (requires restart):
# risk:
#   kill_switch: true
```

The dashboard will display a red alert when the kill switch is active.

### Deactivation

1. Identify and resolve the root cause.
2. Obtain approval from a senior risk officer (see §4).
3. Clear the environment variable or set `kill_switch: false` in the YAML.
4. Restart the platform in paper mode and verify normal operation.
5. Resume live trading only after sign-off.

---

## 3. Approval Process for Limit Changes

| Change | Approval Required |
|--------|--------------------|
| Increase any limit by ≤10% | Team lead sign-off |
| Increase any limit by >10% | Risk Officer + CTO approval |
| Decrease any limit | Team lead acknowledgement |
| Enable live trading on a new exchange | Full risk review + compliance sign-off |
| Modify kill switch logic | Risk Officer + engineering peer review |

All limit changes must be:
1. Documented with a rationale.
2. Applied first in paper mode for ≥2 trading days.
3. Recorded in the audit log with timestamps and approver names.

---

## 4. Escalation Path for Breaches

| Severity | Trigger | Action |
|----------|---------|--------|
| **P3** | Daily P&L approaches 75% of the loss limit | Alert sent to team Slack channel |
| **P2** | Daily loss limit breached | Kill switch auto-activates; on-call engineer notified |
| **P1** | Circuit breaker opens due to execution failures | On-call engineer + team lead paged immediately |
| **P0** | Unexpected broker connectivity loss during open positions | Risk Officer + CTO notified; manual position closure considered |

Contacts and pager schedules are maintained in the internal runbook wiki.

---

## 5. Circuit Breaker Conditions and Reset Procedures

The `CircuitBreaker` class (`risk/circuit_breaker.py`) has three states:

| State | Meaning |
|-------|---------|
| `CLOSED` | Normal operation |
| `OPEN` | All order submissions blocked |
| `HALF_OPEN` | One probe order allowed to test recovery |

### Trip Conditions

| Condition | Default Threshold | Source |
|-----------|-------------------|--------|
| Consecutive execution failures | 5 failures | `record_execution_result(False)` |
| Data feed unhealthy duration | 60 seconds | `record_data_event(False)` |
| Daily P&L loss limit | `max_daily_loss_pct` of equity | `record_pnl()` |

### Automatic Recovery

After the circuit breaker opens, it will automatically transition to `HALF_OPEN`
after a 5-minute cooldown period.  A single successful execution or healthy
data event will close the circuit.

### Manual Reset

If automatic recovery is not appropriate:

1. Stop the platform.
2. Investigate and resolve the root cause (connectivity, P&L breach, data issue).
3. If P&L breach: wait until the next trading day (daily P&L resets).
4. Restart in paper mode and confirm circuit is `CLOSED` for ≥30 minutes.
5. Resume live trading with team lead approval.

---

## 6. Position Sizing Policy

The `PositionSizer` uses ATR-based sizing:

```
risk_per_trade  = equity × max_per_trade_risk_pct / 100
stop_distance   = ATR × atr_multiplier
shares          = risk_per_trade / stop_distance
```

Sizes are floored to whole shares and capped by the `max_per_symbol_pct` limit.

This ensures that under normal volatility conditions, a stop-out on any single
trade results in a loss no greater than `max_per_trade_risk_pct` of equity.
