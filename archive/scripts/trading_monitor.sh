#!/bin/bash

# Configuration
LOG_FILE="/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
ALERT_FILE="/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
DASHBOARD_URL="http://localhost:5001/"

# --- Fetch and Parse Data ---
echo "--- $(date) ---" >> "$LOG_FILE"
echo "Fetching data from $DASHBOARD_URL..." >> "$LOG_FILE"

# Fetch data using curl and parse with jq (assuming JSON output)
# Adjust jq filters based on the actual JSON structure of your dashboard
# Example: Extracting 'status', 'capital', 'stop_loss', 'take_profit'
# and checking for 'drawdown_critical' flag.

# Note: This is a placeholder. You will need to adapt the jq filters to match
# the actual JSON response from your trading dashboard.
# For example, if your response looks like:
# {"status": "ok", "capital": 10000, "stop_loss": 9500, "take_profit": 11000, "drawdown_critical": false, "stop_loss_triggered": false, "take_profit_triggered": false}
# Then the jq filters below are appropriate.

FETCHED_DATA=$(curl -s "$DASHBOARD_URL")

if [ $? -ne 0 ]; then
    echo "Error: Failed to fetch data from $DASHBOARD_URL" >> "$LOG_FILE"
    exit 1
fi

# Log the raw fetched data
echo "Raw Data: $FETCHED_DATA" >> "$LOG_FILE"

# --- Parse specific parameters ---
STATUS=$(echo "$FETCHED_DATA" | jq -r '.status // "unknown"')
CAPITAL=$(echo "$FETCHED_DATA" | jq -r '.capital // "N/A"')
STOP_LOSS=$(echo "$FETCHED_DATA" | jq -r '.stop_loss // "N/A"')
TAKE_PROFIT=$(echo "$FETCHED_DATA" | jq -r '.take_profit // "N/A"')
DRAWDOWN_CRITICAL=$(echo "$FETCHED_DATA" | jq -r '.drawdown_critical // false')
STOP_LOSS_TRIGGERED=$(echo "$FETCHED_DATA" | jq -r '.stop_loss_triggered // false')
TAKE_PROFIT_TRIGGERED=$(echo "$FETCHED_DATA" | jq -r '.take_profit_triggered // false')


# --- Log extracted data ---
echo "Log Entry:" >> "$LOG_FILE"
echo "  Status: $STATUS" >> "$LOG_FILE"
echo "  Capital: $CAPITAL" >> "$LOG_FILE"
echo "  Stop Loss: $STOP_LOSS" >> "$LOG_FILE"
echo "  Take Profit: $TAKE_PROFIT" >> "$LOG_FILE"
echo "  Drawdown Critical: $DRAWDOWN_CRITICAL" >> "$LOG_FILE"
echo "  Stop Loss Triggered: $STOP_LOSS_TRIGGERED" >> "$LOG_FILE"
echo "  Take Profit Triggered: $TAKE_PROFIT_TRIGGERED" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# --- Check for critical alerts ---
ALERT_TRIGGERED=false
ALERT_MESSAGE=""


if [ "$STOP_LOSS_TRIGGERED" = true ]; then
    ALERT_TRIGGERED=true
    ALERT_MESSAGE="ALERT: Stop-loss triggered!"
    echo "$(date) - Stop-loss triggered." >> "$ALERT_FILE"
fi

if [ "$TAKE_PROFIT_TRIGGERED" = true ]; then
    ALERT_TRIGGERED=true
    ALERT_MESSAGE="ALERT: Take-profit triggered!"
    echo "$(date) - Take-profit triggered." >> "$ALERT_FILE"
fi

# Check for critical drawdown indicators
if [ "$DRAWDOWN_CRITICAL" = true ]; then
    ALERT_TRIGGERED=true
    ALERT_MESSAGE="ALERT: Critical drawdown detected!"
    echo "$(date) - Critical drawdown detected." >> "$ALERT_FILE"
fi

# If any alert was triggered, append the message to the alert log
if [ "$ALERT_TRIGGERED" = true ]; then
    echo "$ALERT_MESSAGE" >> "$ALERT_FILE"
    echo "Critical alert logged: $ALERT_MESSAGE" >> "$LOG_FILE"
fi

echo "Monitoring complete." >> "$LOG_FILE"
echo "--------------------" >> "$LOG_FILE"

exit 0
