#!/bin/bash

URL="http://localhost:5001/"
TRADING_LOG="/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
ALERT_LOG="/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"

echo "--- $(date) ---" >> "$TRADING_LOG"

# Fetch data from the URL
RESPONSE=$(curl -s "$URL")

# Basic check if curl command was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to fetch data from $URL" >> "$TRADING_LOG"
    echo "Error: Failed to fetch data from $URL" >> "$ALERT_LOG"
    exit 1
fi

# Assuming the response is JSON. Adjust parsing as needed.
# For demonstration, let's assume a structure like:
# {
#   "status": "ok",
#   "logs": [...],
#   "risk_parameters": {...},
#   "orders": [...],
#   "drawdown": 0.05
# }

# Log status updates and risk parameters
echo "Status updates and risk parameters:" >> "$TRADING_LOG"
echo "$RESPONSE" | jq '.status' >> "$TRADING_LOG"
echo "Risk Parameters:" >> "$TRADING_LOG"
echo "$RESPONSE" | jq '.risk_parameters' >> "$TRADING_LOG"

# Extract and log trading logs
echo "Trading Logs:" >> "$TRADING_LOG"
echo "$RESPONSE" | jq '.logs[]' >> "$TRADING_LOG" # Assuming logs is an array of strings or objects

# Detect and log stop-loss/take-profit orders or critical drawdown
echo "--- Alerts ---" >> "$ALERT_LOG"
echo "$RESPONSE" | jq -c '.orders[] | select(.type == "stop-loss" or .type == "take-profit")' >> "$ALERT_LOG"
CRITICAL_DRAWDOWN=$(echo "$RESPONSE" | jq '.drawdown')
if (( $(echo "$CRITICAL_DRAWDOWN > 0.10" | bc -l) )); then # Example: 10% drawdown is critical
    echo "Critical Drawdown detected: $CRITICAL_DRAWDOWN" >> "$ALERT_LOG"
fi

# Generate plain text summary
SUMMARY="Trading Dashboard Monitoring Summary:\n"
SUMMARY+="\n--- Logged Data ---\n"
SUMMARY+="Status: $(echo "$RESPONSE" | jq '.status')\n"
SUMMARY+="Risk Parameters: $(echo "$RESPONSE" | jq '.risk_parameters')\n"
SUMMARY+="Recent Logs: $(echo "$RESPONSE" | jq '.logs | length') entries\n"

SUMMARY+="\n--- Critical Alerts ---\n"
ALERT_COUNT=$(grep -c "Critical Drawdown" "$ALERT_LOG")
if [ "$ALERT_COUNT" -gt 0 ]; then
    SUMMARY+="Critical Drawdown detected.\n"
else
    ORDERS=$(echo "$RESPONSE" | jq '.orders[] | select(.type == "stop-loss" or .type == "take-profit")')
    if [ -n "$ORDERS" ]; then
        SUMMARY+="Triggered Stop-Loss/Take-Profit Orders detected.\n"
    else
        SUMMARY+="No critical alerts.\n"
    fi
fi

echo -e "$SUMMARY"
echo -e "$SUMMARY" > /Users/chetantemkar/.openclaw/workspace/app/trading_summary.txt
