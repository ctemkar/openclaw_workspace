#!/bin/bash

# Define log files
TRADING_LOG="/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_LOG="/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
API_URL="http://localhost:5001/"

# Fetch data from the API
response=$(curl -s "$API_URL")

# Log the raw response for analysis
echo "$(date '+%Y-%m-%d %H:%M:%S') - Fetching data from $API_URL" >> "$TRADING_LOG"
echo "$response" >> "$TRADING_LOG"

# Parse and log trading logs, status updates, and risk parameters
# This part heavily depends on the structure of the data returned by http://localhost:5001/
# For demonstration, assuming the response is JSON and contains fields like:
# {
#   "trading_logs": [...],
#   "status_updates": [...],
#   "risk_parameters": {
#     "capital": 100000,
#     "stop_loss": {"level": 95000, "triggered": false},
#     "take_profit": {"level": 110000, "triggered": false}
#   },
#   "drawdown_indicators": {"critical": false}
# }

# Extracting and logging specific fields (example)
echo "$(date '+%Y-%m-%d %H:%M:%S') - Parsing and logging data..." >> "$TRADING_LOG"

# Log trading logs (assuming they are an array of strings or objects)
echo "$(date '+%Y-%m-%d %H:%M:%S') - Trading Logs:" >> "$TRADING_LOG"
echo "$response" | jq -c '.trading_logs[]' >> "$TRADING_LOG"

# Log status updates (assuming similar structure)
echo "$(date '+%Y-%m-%d %H:%M:%S') - Status Updates:" >> "$TRADING_LOG"
echo "$response" | jq -c '.status_updates[]' >> "$TRADING_LOG"

# Log risk parameters
capital=$(echo "$response" | jq '.risk_parameters.capital')
stop_loss_level=$(echo "$response" | jq '.risk_parameters.stop_loss.level')
stop_loss_triggered=$(echo "$response" | jq '.risk_parameters.stop_loss.triggered')
take_profit_level=$(echo "$response" | jq '.risk_parameters.take_profit.level')
take_profit_triggered=$(echo "$response" | jq '.risk_parameters.take_profit.triggered')

echo "$(date '+%Y-%m-%d %H:%M:%S') - Capital: $capital" >> "$TRADING_LOG"
echo "$(date '+%Y-%m-%d %H:%M:%S') - Stop Loss Level: $stop_loss_level (Triggered: $stop_loss_triggered)" >> "$TRADING_LOG"
echo "$(date '+%Y-%m-%d %H:%M:%S') - Take Profit Level: $take_profit_level (Triggered: $take_profit_triggered)" >> "$TRADING_LOG"

# Check for triggered alerts and critical drawdown
alert_message=""

if [ "$stop_loss_triggered" = "true" ]; then
  alert_message="STOP LOSS TRIGGERED! Current capital: $capital. Stop loss level: $stop_loss_level."
  echo "$(date '+%Y-%m-%d %H:%M:%S') - ALERT: $alert_message" >> "$CRITICAL_LOG"
fi

if [ "$take_profit_triggered" = "true" ]; then
  alert_message="TAKE PROFIT TRIGGERED! Current capital: $capital. Take profit level: $take_profit_level."
  echo "$(date '+%Y-%m-%d %H:%M:%S') - ALERT: $alert_message" >> "$CRITICAL_LOG"
fi

drawdown_critical=$(echo "$response" | jq '.drawdown_indicators.critical')
if [ "$drawdown_critical" = "true" ]; then
  alert_message="CRITICAL DRAWDOWN INDICATORS DETECTED. Parameters may be at critical levels."
  echo "$(date '+%Y-%m-%d %H:%M:%S') - ALERT: $alert_message" >> "$CRITICAL_LOG"
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') - Monitoring cycle complete." >> "$TRADING_LOG"