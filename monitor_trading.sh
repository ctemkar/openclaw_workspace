#!/bin/bash

MONITORING_LOG="./trading_monitoring.log"
CRITICAL_ALERTS_LOG="./critical_alerts.log"
URL="http://localhost:5001/"

# Fetch data
data=$(curl -s "$URL")

# Log all data
echo -e "$(date '+%Y-%m-%d %H:%M:%S') - Fetched data:\n$data" | tee -a "$MONITORING_LOG"

# Detect and log critical alerts
# Assuming stop-loss/take-profit orders or critical drawdown are indicated by specific keywords
# Replace 'STOP_LOSS_TRIGGERED|TAKE_PROFIT_TRIGGERED|CRITICAL_DRAWDOWN' with actual patterns if known
# Also adding a check for the content of the critical alerts log itself to avoid duplicates in summary if the script runs multiple times before the summary is seen.
alert_keywords='STOP_LOSS_TRIGGERED|TAKE_PROFIT_TRIGGERED|CRITICAL_DRAWDOWN'
current_alerts=$(echo "$data" | grep -E "$alert_keywords")

if [ -n "$current_alerts" ]; then
  echo -e "$(date '+%Y-%m-%d %H:%M:%S') - CRITICAL ALERTS DETECTED:\n$current_alerts" | tee -a "$CRITICAL_ALERTS_LOG"
fi

# Generate summary
summary="Trading Dashboard Analysis Summary:\n"
summary+="------------------------------------\n"
summary+="Timestamp: $(date '+%Y-%m-%d %H:%M:%S')\n"

if [ -s "$CRITICAL_ALERTS_LOG" ]; then
  # Check if the latest alerts are already in the summary output to avoid re-logging them in the summary if the log file keeps growing.
  # This is a simplistic approach; a more robust solution would involve tracking processed alerts.
  last_log_line_brief=$(tail -n 5 "$CRITICAL_ALERTS_LOG" | head -n 1) # Check last few lines for potential alert indicators
  if echo "$current_alerts" | grep -q -v -F "$last_log_line_brief"; then
      summary+="CRITICAL ALERTS DETECTED and logged to $CRITICAL_ALERTS_LOG.\n"
  else
      summary+="Existing critical alerts are still present (logged to $CRITICAL_ALERTS_LOG).\n"
  fi

else
  summary+="No new critical alerts detected.\n"
fi

# Extract and display key parameters if possible (example: assuming 'Risk Parameter: X' format)
risk_params=$(echo "$data" | grep -i "risk parameter:")
if [ -n "$risk_params" ]; then
  summary+="\nRisk Parameters:\n"
  summary+="$risk_params\n"
fi

# Extract and display status updates (example: assuming 'Status: Y' format)
status_updates=$(echo "$data" | grep -i "status:")
if [ -n "$status_updates" ]; then
  summary+="\nStatus Updates:\n"
  summary+="$status_updates\n"
fi

# Extract and display trading logs (example: assuming lines containing 'Trade ID:')
trading_logs=$(echo "$data" | grep -i "trade id:")
if [ -n "$trading_logs" ]; then
  summary+="\nRecent Trading Logs:\n"
  summary+="$trading_logs\n"
fi

echo -e "$summary"
