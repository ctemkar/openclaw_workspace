#!/bin/bash

# Configuration
URL="http://localhost:5001/"
TRADING_LOG="/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_LOG="/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
TEMP_LOG=$(mktemp)

# Ensure log files exist
touch "$TRADING_LOG" "$CRITICAL_LOG"

# Fetch data from the URL
if ! curl -s "$URL" > "$TEMP_LOG"; then
    echo "$(date): Failed to fetch data from $URL" >&2
    exit 1
fi

# Extract trading logs, status updates, and risk parameters
# This is a placeholder; actual extraction logic will depend on the data format from the URL
# Assuming the output is JSON for this example
if ! jq -s '.' "$TEMP_LOG" > /dev/null 2>&1; then
    echo "$(date): Data is not valid JSON. Logging raw data."
    cat "$TEMP_LOG" >> "$TRADING_LOG"
else
    echo "$(date): Processing JSON data..."
    # Example: Extracting specific fields if data is JSON
    # This needs to be customized based on the actual JSON structure
    STATUS_UPDATES=$(jq -c '.status_updates[]' "$TEMP_LOG" || echo "No status updates found")
    RISK_PARAMS=$(jq -c '.risk_parameters' "$TEMP_LOG" || echo "No risk parameters found")

    echo "$(date): Status Updates: $STATUS_UPDates" >> "$TRADING_LOG"
    echo "$(date): Risk Parameters: $RISK_PARAMS" >> "$TRADING_LOG"

    # Detect stop-loss/take-profit orders or critical drawdown
    # This is a placeholder; actual detection logic will depend on the data
    STOP_LOSS_TRIGGERED=$(jq '.alerts[] | select(.type == "stop_loss") | .message' "$TEMP_LOG" || echo "")
    TAKE_PROFIT_TRIGGERED=$(jq '.alerts[] | select(.type == "take_profit") | .message' "$TEMP_LOG" || echo "")
    CRITICAL_DRAWDOWN=$(jq '.alerts[] | select(.type == "critical_drawdown") | .message' "$TEMP_LOG" || echo "")

    if [ -n "$STOP_LOSS_TRIGGERED" ]; then
        echo "$(date): STOP-LOSS TRIGGERED: $STOP_LOSS_TRIGGERED" >> "$CRITICAL_LOG"
    fi
    if [ -n "$TAKE_PROFIT_TRIGGERED" ]; then
        echo "$(date): TAKE-PROFIT TRIGGERED: $TAKE_PROFIT_TRIGGERED" >> "$CRITICAL_LOG"
    fi
    if [ -n "$CRITICAL_DRAWDOWN" ]; then
        echo "$(date): CRITICAL DRAWDOWN: $CRITICAL_DRAWDOWN" >> "$CRITICAL_LOG"
    fi
fi

# Generate summary (plain text)
SUMMARY=""
if [ -s "$CRITICAL_LOG" ]; then
    SUMMARY+="CRITICAL ALERTS DETECTED:\n"
    SUMMARY+=$(cat "$CRITICAL_LOG")
    SUMMARY+="\n\n"
fi
SUMMARY+="Trading logs and status updates have been logged to $TRADING_LOG."

# The summary will be automatically delivered by the cron job's systemEvent payload.
# If a specific external recipient was requested, it would be noted here.

rm "$TEMP_LOG"

exit 0