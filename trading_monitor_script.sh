#!/bin/bash

# Define log files
TRADING_LOG="./trading_monitoring.log"
CRITICAL_LOG="./critical_alerts.log"

# Ensure log files exist and are writable
touch "$TRADING_LOG" "$CRITICAL_LOG"

# Fetch data from the trading dashboard
# In a real scenario, this would involve `curl` or a more sophisticated script
# For now, we'll simulate data retrieval.
# Example: data=$(curl -s http://localhost:5001/)
# Simulate data:
DATA_PAYLOAD=$(cat <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "status": "Live Trading",
  "risk_parameters": {
    "max_drawdown_pct": 0.05,
    "stop_loss_pct": 0.02,
    "take_profit_pct": 0.10
  },
  "trades": [
    {"id": 1, "entry_price": 100, "exit_price": 102, "status": "closed", "type": "take_profit"},
    {"id": 2, "entry_price": 150, "exit_price": 148, "status": "closed", "type": "stop_loss"},
    {"id": 3, "entry_price": 200, "exit_price": null, "status": "open", "type": "long"}
  ],
  "current_drawdown_pct": 0.03
}
EOF
)

# Process the data
echo "$DATA_PAYLOAD" > temp_data.json

# Extract general trading logs and status updates
echo "---" $(date -u +%Y-%m-%dT%H:%M:%SZ) "---" >> "$TRADING_LOG"
echo "Status: $(jq -r '.status' temp_data.json)" >> "$TRADING_LOG"
echo "Risk Parameters: $(jq -r '.risk_parameters | tostring' temp_data.json)" >> "$TRADING_LOG"
echo "Trades: $(jq -r '.trades | @json' temp_data.json)" >> "$TRADING_LOG"
echo "Current Drawdown: $(jq -r '.current_drawdown_pct * 100' temp_data.json)%" >> "$TRADING_LOG"

# Detect and log critical alerts
MAX_DRAWDOWN=$(jq -r '.risk_parameters.max_drawdown_pct' temp_data.json)
CURRENT_DRAWDOWN=$(jq -r '.current_drawdown_pct' temp_data.json)

if (( $(echo "$CURRENT_DRAWDOWN > $MAX_DRAWDOWN" | bc -l) )); then
  echo "ALERT: CRITICAL DRAWDOWN DETECTED!" >> "$CRITICAL_LOG"
  echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$CRITICAL_LOG"
  echo "Current Drawdown: $(jq -r '.current_drawdown_pct * 100' temp_data.json)%" >> "$CRITICAL_LOG"
  echo "Max Allowed Drawdown: $(jq -r '.risk_parameters.max_drawdown_pct * 100' temp_data.json)%" >> "$CRITICAL_LOG"
fi

# Detect stop-loss/take-profit triggers
jq -c '.trades[]' temp_data.json | while IFS= read -r trade; do
  trade_status=$(echo "$trade" | jq -r '.status')
  trade_type=$(echo "$trade" | jq -r '.type')
  trade_id=$(echo "$trade" | jq -r '.id')

  if [ "$trade_status" == "closed" ]; then
    if [ "$trade_type" == "stop_loss" ]; then
      echo "ALERT: STOP-LOSS TRIGGERED!" >> "$CRITICAL_LOG"
      echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$CRITICAL_LOG"
      echo "Trade ID: $trade_id" >> "$CRITICAL_LOG"
    elif [ "$trade_type" == "take_profit" ]; then
      echo "ALERT: TAKE-PROFIT TRIGGERED!" >> "$CRITICAL_LOG"
      echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$CRITICAL_LOG"
      echo "Trade ID: $trade_id" >> "$CRITICAL_LOG"
    fi
  fi
done

# Generate plain text summary
SUMMARY="Trading Dashboard Analysis ($(date -u +'%Y-%m-%d %H:%M:%S UTC')):\n"
SUMMARY="${SUMMARY}Status: $(jq -r '.status' temp_data.json)\n"
SUMMARY="${SUMMARY}Current Drawdown: $(jq -r '.current_drawdown_pct * 100' temp_data.json)%\n"

CRITICAL_ALERTS_COUNT=$(grep -c "ALERT:" "$CRITICAL_LOG")
if [ "$CRITICAL_ALERTS_COUNT" -gt 0 ]; then
  SUMMARY="${SUMMARY}Critical Alerts: ${CRITICAL_ALERTS_COUNT} detected. Check ${CRITICAL_LOG} for details.\n"
else
  SUMMARY="${SUMMARY}No critical alerts detected.\n"
fi

# Output summary (this will be the final output of the cron job)
echo -e "$SUMMARY"

# Clean up temporary file
rm temp_data.json
