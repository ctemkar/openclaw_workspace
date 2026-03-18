#!/bin/bash

URL="http://localhost:5001/"
GENERAL_LOG="/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_LOG="/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
SUMMARY_FILE="/tmp/trading_summary.txt"

# Fetch data from the URL
response=$(curl -s "$URL")

# Check if the response is empty or indicates an error
if [[ -z "$response" ]]; then
  echo "$(date): ERROR - No response from $URL" >> "$GENERAL_LOG"
  echo "There was an error retrieving data from the trading dashboard." > "$SUMMARY_FILE"
  exit 1
fi

echo "$(date): $(echo "$response" | jq -c .)" >> "$GENERAL_LOG"

# Analyze response for critical alerts
stop_loss_triggered=$(echo "$response" | jq -r '.stop_loss_triggered // "false"')
take_profit_triggered=$(echo "$response" | jq -r '.take_profit_triggered // "false"')
critical_drawdown=$(echo "$response" | jq -r '.critical_drawdown // "false"')

ALERT_FOUND=false

if [[ "$stop_loss_triggered" == "true" ]]; then
  echo "$(date): ALERT - Stop-loss order triggered." >> "$CRITICAL_LOG"
  echo "Stop-loss order triggered." >> "$SUMMARY_FILE"
  ALERT_FOUND=true
fi

if [[ "$take_profit_triggered" == "true" ]]; then
  echo "$(date): ALERT - Take-profit order triggered." >> "$CRITICAL_LOG"
  echo "Take-profit order triggered." >> "$SUMMARY_FILE"
  ALERT_FOUND=true
fi

if [[ "$critical_drawdown" == "true" ]]; then
  echo "$(date): ALERT - Critical drawdown detected." >> "$CRITICAL_LOG"
  echo "Critical drawdown detected." >> "$SUMMARY_FILE"
  ALERT_FOUND=true
fi

# If no alerts, state that
if [[ "$ALERT_FOUND" == "false" ]]; then
  echo "No critical alerts detected." > "$SUMMARY_FILE"
fi

# The summary will be read from SUMMARY_FILE by the cron job delivery
