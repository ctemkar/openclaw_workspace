#!/usr/bin/env python3
import requests
import json
import datetime
import os

# --- Configuration ---
LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
ALERT_LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
URL = "http://localhost:5001/" # This will be simulated

# --- Simulate Data Fetch ---
simulated_data = {
  "status": "running",
  "trades": [
    {"id": 1, "symbol": "BTC/USD", "type": "buy", "entry": 50000, "exit": 52000, "status": "closed", "realized_pnl": 2000},
    {"id": 2, "symbol": "ETH/USD", "type": "sell", "entry": 3000, "exit": 2900, "status": "closed", "realized_pnl": -100},
    {"id": 3, "symbol": "SOL/USD", "type": "buy", "entry": 100, "exit": None, "status": "open", "stop_loss": 95, "take_profit": 110}
  ],
  "risk_parameters": {
    "max_drawdown_pct": 5.0,
    "current_drawdown_pct": 2.1
  },
  "open_orders": [
    {"symbol": "BTC/USD", "type": "sell_stop_loss", "level": 51000, "triggered": False},
    {"symbol": "ETH/USD", "type": "sell_take_profit", "level": 2950, "triggered": False}
  ]
}
data = simulated_data

# Ensure log directories exist
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Log raw data
try:
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(simulated_data, f, indent=2)
except IOError as e:
    print(f"Error writing to log file {LOG_FILE}: {e}")
    # In a real scenario, you might want to handle this error more robustly

# --- Processing and Alerting ---
summary = "--- Trading Monitoring Report ---\n"
current_time_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
summary += f"Timestamp: {current_time_utc}\n\n"

critical_alerts_found = False
alert_messages = []

# In a real scenario, handle errors from requests.get and check if data is valid
status = simulated_data.get("status", "N/A")
summary += f"Overall Status: {status}\n"

# Trades Analysis
trades = simulated_data.get("trades", [])
open_trades = [t for t in trades if t.get("status") == "open"]
closed_trades = [t for t in trades if t.get("status") == "closed"]

summary += f"Active Trades: {len(open_trades)}\n"
summary += f"Closed Trades: {len(closed_trades)}\n"

for trade in open_trades:
    symbol = trade.get("symbol", "N/A")
    stop_loss = trade.get("stop_loss", "N/A")
    take_profit = trade.get("take_profit", "N/A")
    summary += f"  - {symbol}: Open, SL={stop_loss}, TP={take_profit}\n"
    # Simplified check for potential SL/TP trigger based on entry price (in a real scenario, current market price is needed)
    if symbol == "SOL/USD" and stop_loss != "N/A" and stop_loss < trade.get("entry", float('inf')):
         alert_messages.append(f"ALERT: SOL/USD stop-loss might be triggered at {stop_loss} (Entry: {trade.get('entry')}).")
         critical_alerts_found = True

# Risk Parameters
risk_parameters = simulated_data.get("risk_parameters", {})
max_drawdown = risk_parameters.get("max_drawdown_pct", "N/A")
current_drawdown = risk_parameters.get("current_drawdown_pct", "N/A")
summary += "Risk Parameters:\n"
summary += f"  Max Drawdown: {max_drawdown}%\n"
summary += f"  Current Drawdown: {current_drawdown}%\n"

# Critical Drawdown Alert
if isinstance(current_drawdown, (int, float)) and isinstance(max_drawdown, (int, float)):
    # Using a threshold of 90% of max drawdown for an alert
    if current_drawdown > max_drawdown * 0.9:
        alert_messages.append(f"ALERT: Critical drawdown detected! Current: {current_drawdown}%, Max Allowed: {max_drawdown}%")
        critical_alerts_found = True

# Open Orders Alert
open_orders = simulated_data.get("open_orders", [])
for order in open_orders:
    # Check if the order is marked as triggered and is a stop-loss or take-profit order
    if order.get("triggered", False) and order.get("type", "").startswith(("sell_stop_loss", "buy_stop_loss", "sell_take_profit", "buy_take_profit")):
        symbol = order.get("symbol", "N/A")
        order_type = order.get("type", "N/A")
        level = order.get("level", "N/A")
        alert_messages.append(f"ALERT: Order triggered - {symbol} {order_type} at {level}.")
        critical_alerts_found = True

if not critical_alerts_found:
    alert_messages.append("No critical alerts detected.")

# Log critical alerts
try:
    with open(ALERT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"Timestamp: {current_time_utc}\n")
        for msg in alert_messages:
            f.write(f"{msg}\n")
        f.write("\n") # Add a blank line between entries
except IOError as e:
    print(f"Error writing to alert log file {ALERT_LOG_FILE}: {e}")

# Append alert messages to the summary
for msg in alert_messages:
    summary += f"{msg}\n"

summary += f"\nCritical Alerts Logged to: {ALERT_LOG_FILE}"

print(summary)
