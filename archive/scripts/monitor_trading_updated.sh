#!/bin/bash

# Get the actual port from the .active_port file
ACTIVE_PORT_FILE="/Users/chetantemkar/.openclaw/workspace/app/.active_port"
if [ -f "$ACTIVE_PORT_FILE" ]; then
    PORT=$(cat "$ACTIVE_PORT_FILE")
    URL="http://localhost:$PORT"
else
    # Fallback to provided URL or default
    URL="${1:-http://localhost:5001/}"
fi

TRADING_LOG="${2:-/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log}"
ALERT_LOG="${3:-/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log}"

echo "--- $(date) ---" >> "$TRADING_LOG"

# Fetch data from the actual endpoints
STATUS_RESPONSE=$(curl -s "${URL}/status")
TRADES_RESPONSE=$(curl -s "${URL}/trades")
SUMMARY_RESPONSE=$(curl -s "${URL}/summary")

# Basic check if curl command was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to fetch data from ${URL}" >> "$TRADING_LOG"
    echo "Error: Failed to fetch data from ${URL}" >> "$ALERT_LOG"
    exit 1
fi

# Log status updates
echo "Status:" >> "$TRADING_LOG"
echo "$STATUS_RESPONSE" | jq '.' >> "$TRADING_LOG"

echo "Recent Trades:" >> "$TRADING_LOG"
echo "$TRADES_RESPONSE" | jq '.' >> "$TRADING_LOG"

echo "Summary:" >> "$TRADING_LOG"
echo "$SUMMARY_RESPONSE" >> "$TRADING_LOG"

# Extract and log trading information
TRADE_COUNT=$(echo "$TRADES_RESPONSE" | jq '.count // 0')
LAST_TRADE_TIME="N/A"
if [ "$TRADE_COUNT" -gt 0 ]; then
    LAST_TRADE_TIME=$(echo "$TRADES_RESPONSE" | jq -r '.trades[0].time // .trades[0].time // "N/A"')
fi

# Get system status
SYSTEM_STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status // "unknown"')
CAPITAL=$(echo "$STATUS_RESPONSE" | jq -r '.capital // 0')
STOP_LOSS=$(echo "$STATUS_RESPONSE" | jq -r '.risk_parameters.stop_loss // 0')
TAKE_PROFIT=$(echo "$STATUS_RESPONSE" | jq -r '.risk_parameters.take_profit // 0')

# Detect and log alerts
echo "--- Alerts ---" >> "$ALERT_LOG"
echo "System Status: $SYSTEM_STATUS" >> "$ALERT_LOG"
echo "Capital: \$$CAPITAL" >> "$ALERT_LOG"
echo "Stop-loss: $(echo "$STOP_LOSS * 100" | bc -l)%" >> "$ALERT_LOG"
echo "Take-profit: $(echo "$TAKE_PROFIT * 100" | bc -l)%" >> "$ALERT_LOG"

if [ "$TRADE_COUNT" -gt 0 ]; then
    echo "Active Trades: $TRADE_COUNT" >> "$ALERT_LOG"
    echo "Last Trade Time: $LAST_TRADE_TIME" >> "$ALERT_LOG"
    
    # Check if last trade was more than 2 hours ago (potential issue)
    if [ "$LAST_TRADE_TIME" != "N/A" ] && [ "$LAST_TRADE_TIME" != "null" ]; then
        # Extract hour from time (format: HH:MM:SS)
        TRADE_HOUR=$(echo "$LAST_TRADE_TIME" | cut -d: -f1 | sed 's/^0//')
        CURRENT_HOUR=$(date +%H | sed 's/^0//')
        
        if [ ! -z "$TRADE_HOUR" ] && [ "$TRADE_HOUR" -lt $((CURRENT_HOUR - 2)) ]; then
            echo "Alert: Last trade was more than 2 hours ago at $LAST_TRADE_TIME" >> "$ALERT_LOG"
        fi
    fi
else
    echo "No trades recorded" >> "$ALERT_LOG"
fi

# Check for critical conditions
if [ "$(echo "$CAPITAL < 900" | bc -l)" -eq 1 ]; then
    echo "CRITICAL: Capital below \$900 (current: \$$CAPITAL)" >> "$ALERT_LOG"
fi

# Generate plain text summary
SUMMARY="Trading Dashboard Monitoring Summary:\n"
SUMMARY+="Timestamp: $(date)\n"
SUMMARY+="\n--- System Status ---\n"
SUMMARY+="Status: $SYSTEM_STATUS\n"
SUMMARY+="Capital: \$$CAPITAL\n"
SUMMARY+="Stop-loss: $(echo "$STOP_LOSS * 100" | bc -l)%\n"
SUMMARY+="Take-profit: $(echo "$TAKE_PROFIT * 100" | bc -l)%\n"
SUMMARY+="Trading Pairs: $(echo "$STATUS_RESPONSE" | jq -r '.trading_pairs | join(", ")')\n"

SUMMARY+="\n--- Trading Activity ---\n"
SUMMARY+="Total Trades: $TRADE_COUNT\n"
if [ "$TRADE_COUNT" -gt 0 ]; then
    SUMMARY+="Last trade at: $LAST_TRADE_TIME\n"
fi

SUMMARY+="\n--- Critical Alerts ---\n"
if [ "$SYSTEM_STATUS" != "running" ]; then
    SUMMARY+="ALERT: System status is '$SYSTEM_STATUS' (expected: 'running')\n"
fi

if [ "$(echo "$CAPITAL < 900" | bc -l)" -eq 1 ]; then
    SUMMARY+="CRITICAL: Capital below \$900 (current: \$$CAPITAL)\n"
fi

if [ "$TRADE_COUNT" -eq 0 ]; then
    SUMMARY+="No trades recorded. Trading may not be active.\n"
elif [ "$LAST_TRADE_TIME" != "N/A" ] && [ "$LAST_TRADE_TIME" != "null" ]; then
    TRADE_HOUR=$(echo "$LAST_TRADE_TIME" | cut -d: -f1 | sed 's/^0//')
    CURRENT_HOUR=$(date +%H | sed 's/^0//')
    if [ ! -z "$TRADE_HOUR" ] && [ "$TRADE_HOUR" -lt $((CURRENT_HOUR - 2)) ]; then
        SUMMARY+="ALERT: Last trade was more than 2 hours ago at $LAST_TRADE_TIME\n"
    fi
fi

echo -e "$SUMMARY"
echo -e "$SUMMARY" > /Users/chetantemkar/.openclaw/workspace/app/trading_summary.txt