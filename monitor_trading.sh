#!/bin/bash

LOG_FILE="/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
ALERT_LOG_FILE="/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
TRADING_DASHBOARD_URL="http://localhost:5001/"

# Fetch data from the trading dashboard
RAW_DATA=$(curl -s "$TRADING_DASHBOARD_URL")

# Log the raw data
echo "$(date): Raw data fetched." >> "$LOG_FILE"
echo "$RAW_DATA" >> "$LOG_FILE"
echo "--------------------" >> "$LOG_FILE"

# --- Analysis and Alerting ---
SUMMARY="Trading Dashboard Analysis:\n"
ALERTS=""

# Placeholder for status updates and risk parameters extraction
# Assuming RAW_DATA is JSON for this example. If it's plain text, parsing logic will differ.
# If it's not JSON, you'll need to adjust parsing or use different tools.

# Example: Extracting status and risk parameters if data is JSON
if echo "$RAW_DATA" | jq -e . >/dev/null 2>&1; then
    CURRENT_STATUS=$(echo "$RAW_DATA" | jq -r '.status // "N/A"')
    RISK_PARAM=$(echo "$RAW_DATA" | jq -r '.riskParameters | tostring // "N/A"')
    STOP_LOSS_TRIGGERED=$(echo "$RAW_DATA" | jq -r '.stopLossTriggered // "false"')
    TAKE_PROFIT_TRIGGERED=$(echo "$RAW_DATA" | jq -r '.takeProfitTriggered // "false"')
    CRITICAL_DRAWDOWN=$(echo "$RAW_DATA" | jq -r '.criticalDrawdown // "false"')

    SUMMARY+="Current Status: ${CURRENT_STATUS}\n"
    SUMMARY+="Risk Parameters: ${RISK_PARAM}\n"

    if [ "$STOP_LOSS_TRIGGERED" = "true" ]; then
        ALERT="STOP-LOSS ORDER TRIGGERED at $(date)"
        ALERTS+="$ALERT\n"
        echo "$(date): $ALERT" >> "$ALERT_LOG_FILE"
    fi

    if [ "$TAKE_PROFIT_TRIGGERED" = "true" ]; then
        ALERT="TAKE-PROFIT ORDER TRIGGERED at $(date)"
        ALERTS+="$ALERT\n"
        echo "$(date): $ALERT" >> "$ALERT_LOG_FILE"
    fi

    if [ "$CRITICAL_DRAWDOWN" = "true" ]; then
        ALERT="CRITICAL DRAWDOWN DETECTED at $(date)"
        ALERTS+="$ALERT\n"
        echo "$(date): $ALERT" >> "$ALERT_LOG_FILE"
    fi
else
    # Fallback for non-JSON data or if jq is not available
    # This part would need to be more robust based on the actual data format from localhost:5001
    SUMMARY+="Could not parse trading data as JSON. Raw data logged.\n"
    ALERTS+="Could not parse trading data as JSON. Automated alerts may be missed.\n"
    echo "$(date): Could not parse trading data as JSON." >> "$ALERT_LOG_FILE"
fi

if [ -n "$ALERTS" ]; then
    SUMMARY+="\nCritical Alerts:\n${ALERTS}"
fi

# Output the summary
echo -e "$SUMMARY"

# Log the alerts separately if any
if [ -n "$ALERTS" ]; then
    echo "$(date): Critical alerts generated." >> "$LOG_FILE"
fi

exit 0
