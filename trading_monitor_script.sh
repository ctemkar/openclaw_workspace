#!/bin/bash

# --- Configuration ---
URL="http://localhost:5001/"
LOG_FILE="/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERTS_LOG="/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
SUMMARY_FILE="/Users/chetantemkar/.openclaw/workspace/app/trading_summary.txt" # Temporary file for summary

# --- Fetch Data ---
# Using curl with a timeout and capturing output
DATA=$(curl -s --max-time 10 "$URL")

# --- Logging ---
echo "--- $(date) ---" >> "$LOG_FILE"
echo "$DATA" >> "$LOG_FILE"

# --- Analysis and Alerting ---
echo "--- $(date) ---" > "$SUMMARY_FILE"
echo "--- Analysis for $URL ---" >> "$SUMMARY_FILE"

# Basic keyword detection for alerts
STOP_LOSS_ALERT=$(echo "$DATA" | grep -i "STOP-LOSS TRIGGERED\|STOP LOSS HIT\|STOPPED OUT")
TAKE_PROFIT_ALERT=$(echo "$DATA" | grep -i "TAKE-PROFIT TRIGGERED\|TAKE PROFIT HIT\|TAKE GAIN")
CRITICAL_DRAWDOWN_ALERT=$(echo "$DATA" | grep -i "CRITICAL DRAWDOWN\|MAX DRAWDOWN REACHED\|DEEP LOSS")

# Log critical alerts and add to summary
if [ -n "$STOP_LOSS_ALERT" ]; then
  echo "CRITICAL ALERT: STOP-LOSS TRIGGERED at $(date)" >> "$CRITICAL_ALERTS_LOG"
  echo "CRITICAL ALERT: STOP-LOSS TRIGGERED" >> "$SUMMARY_FILE"
  echo "$STOP_LOSS_ALERT" >> "$SUMMARY_FILE"
fi

if [ -n "$TAKE_PROFIT_ALERT" ]; then
  echo "ALERT: TAKE-PROFIT TRIGGERED at $(date)" >> "$LOG_FILE" # Log non-critical alerts to main log
  echo "ALERT: TAKE-PROFIT TRIGGERED" >> "$SUMMARY_FILE"
  echo "$TAKE_PROFIT_ALERT" >> "$SUMMARY_FILE"
fi

if [ -n "$CRITICAL_DRAWDOWN_ALERT" ]; then
  echo "CRITICAL ALERT: CRITICAL DRAWDOWN at $(date)" >> "$CRITICAL_ALERTS_LOG"
  echo "CRITICAL ALERT: CRITICAL DRAWDOWN" >> "$SUMMARY_FILE"
  echo "$CRITICAL_DRAWDOWN_ALERT" >> "$SUMMARY_FILE"
fi

# Extract and log status updates and risk parameters (simplified example)
# Assuming these are lines containing "STATUS:" or "RISK:"
STATUS_UPDATES=$(echo "$DATA" | grep -i "STATUS:")
RISK_PARAMETERS=$(echo "$DATA" | grep -i "RISK PARAMETER:")

echo "--- Status Updates ---" >> "$SUMMARY_FILE"
if [ -n "$STATUS_UPDATES" ]; then
  echo "$STATUS_UPDATES" >> "$SUMMARY_FILE"
else
  echo "No specific status updates found." >> "$SUMMARY_FILE"
fi

echo "--- Risk Parameters ---" >> "$SUMMARY_FILE"
if [ -n "$RISK_PARAMETERS" ]; then
  echo "$RISK_PARAMETERS" >> "$SUMMARY_FILE"
else
  echo "No specific risk parameters found." >> "$SUMMARY_FILE"
fi

# --- Final Summary ---
echo "" >> "$SUMMARY_FILE"
echo "Analysis complete. See '$LOG_FILE' for full logs and '$CRITICAL_ALERTS_LOG' for critical alerts." >> "$SUMMARY_FILE"

# The final output will be the content of the summary file
cat "$SUMMARY_FILE"

# Clean up temporary summary file if needed (though cron will run it again)
# rm "$SUMMARY_FILE"
