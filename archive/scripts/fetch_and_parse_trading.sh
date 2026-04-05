#!/bin/bash

URL="http://localhost:5001/"
RAW_LOG="/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
ALERT_LOG="/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
SUMMARY_FILE="/Users/chetantemkar/.openclaw/workspace/app/trading_summary.txt" # Temporary file for summary

echo "--- $(date) ---" >> "$RAW_LOG"
curl -s "$URL" >> "$RAW_LOG"

# Assuming JSON output. Adjust 'jq' queries if format is different.
# Example: looking for 'stop_loss', 'take_profit', or 'drawdown' fields
# This is a placeholder; actual parsing will depend on the data structure.
ALERT_DATA=$(curl -s "$URL" | jq -c '[.orders[]? | select(.type == "stop-loss" or .type == "take-profit")], .drawdown? | select(.level == "critical")' || true)

if [ -n "$ALERT_DATA" ] && [ "$ALERT_DATA" != "[]" ]; then
    echo "--- CRITICAL ALERT DETECTED: $(date) ---" >> "$ALERT_LOG"
    echo "$ALERT_DATA" >> "$ALERT_LOG"
    echo "Critical alerts found. See $ALERT_LOG for details." > "$SUMMARY_FILE"
else
    echo "No critical alerts detected." > "$SUMMARY_FILE"
fi

# Append a simple status to the summary
echo "Raw data logged to $RAW_LOG" >> "$SUMMARY_FILE"

# The final output will be the content of SUMMARY_FILE, which will be read and returned.
cat "$SUMMARY_FILE"
