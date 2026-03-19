#!/bin/bash

LOG_FILE="/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
ALERT_LOG_FILE="/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
TRADING_DASHBOARD_URL="http://localhost:5001/"

echo "Starting trading dashboard monitor at $(date)" >> "$LOG_FILE"

# Fetch data and log it
curl -s "$TRADING_DASHBOARD_URL" >> "$LOG_FILE"
echo "---" >> "$LOG_FILE"

# Analyze data for critical alerts
ALERT_DETECTED=false
if curl -s "$TRADING_DASHBOARD_URL" | grep -q "STOP_LOSS_TRIGGERED"; then
  echo "STOP_LOSS_TRIGGERED detected at $(date)" >> "$ALERT_LOG_FILE"
  echo "STOP_LOSS_TRIGGERED detected at $(date)" >> "$LOG_FILE" # Also log to main log
  ALERT_DETECTED=true
fi

if curl -s "$TRADING_DASHBOARD_URL" | grep -q "TAKE_PROFIT_TRIGGERED"; then
  echo "TAKE_PROFIT_TRIGGERED detected at $(date)" >> "$ALERT_LOG_FILE"
  echo "TAKE_PROFIT_TRIGGERED detected at $(date)" >> "$LOG_FILE" # Also log to main log
  ALERT_DETECTED=true
fi

if curl -s "$TRADING_DASHBOARD_URL" | grep -q "CRITICAL_DRAWDOWN"; then
  echo "CRITICAL_DRAWDOWN detected at $(date)" >> "$ALERT_LOG_FILE"
  echo "CRITICAL_DRAWDOWN detected at $(date)" >> "$LOG_FILE" # Also log to main log
  ALERT_DETECTED=true
fi

if [ "$ALERT_DETECTED" = false ]; then
  echo "No critical alerts detected at $(date)" >> "$LOG_FILE"
fi

echo "Trading dashboard monitor finished at $(date)" >> "$LOG_FILE"
echo "---" >> "$LOG_FILE"

# Provide a plain text summary (for cron delivery if needed, though logging is primary)
SUMMARY="Trading dashboard analysis complete at $(date). See logs for details."
if [ "$ALERT_DETECTED" = true ]; then
  SUMMARY="$SUMMARY Critical alerts were detected. Check $ALERT_LOG_FILE for details."
else
  SUMMARY="$SUMMARY No critical alerts were found."
fi

# If this were to be delivered via message, it would go here.
# For now, we rely on the logs.
echo "$SUMMARY" > /tmp/trading_summary.txt # Temporary file for summary if needed by another process
