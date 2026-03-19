#!/bin/bash

# Trading Dashboard Monitor Script
# This script monitors the trading dashboard and logs data

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
DASHBOARD_URL="http://localhost:5001"
MONITORING_LOG="/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_LOG="/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"

# Function to fetch JSON data
fetch_data() {
    local endpoint=$1
    curl -s "$DASHBOARD_URL$endpoint" 2>/dev/null || echo "{}"
}

# Fetch all data
STATUS_DATA=$(fetch_data "/status")
TRADES_DATA=$(fetch_data "/trades")
SUMMARY_DATA=$(fetch_data "/summary" 2>/dev/null || echo "{}")

# Log general monitoring data
echo "[$TIMESTAMP] STATUS: $STATUS_DATA" >> "$MONITORING_LOG"
echo "[$TIMESTAMP] TRADES: $TRADES_DATA" >> "$MONITORING_LOG"

# Parse status for risk parameters
STOP_LOSS=$(echo "$STATUS_DATA" | grep -o '"stop_loss":[0-9.]*' | cut -d: -f2 || echo "0.05")
TAKE_PROFIT=$(echo "$STATUS_DATA" | grep -o '"take_profit":[0-9.]*' | cut -d: -f2 || echo "0.10")
CAPITAL=$(echo "$STATUS_DATA" | grep -o '"capital":[0-9.]*' | cut -d: -f2 || echo "1000")

# Check for critical conditions (simplified logic)
# In a real system, you would check actual trade performance against stop-loss/take-profit

# For demo purposes, we'll check if there are any recent trades
TRADE_COUNT=$(echo "$TRADES_DATA" | grep -o '"count":[0-9]*' | cut -d: -f2 || echo "0")

if [ "$TRADE_COUNT" -gt 0 ]; then
    # Check if any trades mention stop-loss or take-profit
    if echo "$TRADES_DATA" | grep -qi "stop-loss\|stop_loss\|sl\|take-profit\|take_profit\|tp"; then
        echo "[$TIMESTAMP] CRITICAL: Potential stop-loss/take-profit trigger detected in trades" >> "$CRITICAL_LOG"
        echo "$TRADES_DATA" >> "$CRITICAL_LOG"
        CRITICAL_ALERT="YES"
    fi
fi

# Generate summary
echo "=== Trading Dashboard Monitor Summary ==="
echo "Timestamp: $TIMESTAMP"
echo "Dashboard Status: $(echo "$STATUS_DATA" | grep -o '"status":"[^"]*"' | cut -d: -f2 | tr -d '\"')"
echo "Capital: \$$CAPITAL"
echo "Stop-loss: $(echo "scale=2; $STOP_LOSS*100" | bc)%"
echo "Take-profit: $(echo "scale=2; $TAKE_PROFIT*100" | bc)%"
echo "Recent trades count: $TRADE_COUNT"
echo "Critical alerts: ${CRITICAL_ALERT:-NO}"
echo "Logs updated: $MONITORING_LOG"
if [ -n "$CRITICAL_ALERT" ]; then
    echo "Critical alerts logged: $CRITICAL_LOG"
fi
echo "========================================"