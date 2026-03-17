#!/bin/bash

BASE_URL="http://localhost:5001"
TRADING_LOG="/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
ALERT_LOG="/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"

echo "--- $(date) ---" >> "$TRADING_LOG"

# Fetch status data
STATUS_RESPONSE=$(curl -s "$BASE_URL/api/status/all")

# Fetch trading progress data
PROGRESS_RESPONSE=$(curl -s "$BASE_URL/api/trading/progress")

# Basic check if curl commands were successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to fetch data from dashboard APIs" >> "$TRADING_LOG"
    echo "Error: Failed to fetch data from dashboard APIs" >> "$ALERT_LOG"
    exit 1
fi

# Log status updates
echo "Status Update:" >> "$TRADING_LOG"
echo "$STATUS_RESPONSE" | jq '.' >> "$TRADING_LOG"

# Log trading progress
echo "Trading Progress:" >> "$TRADING_LOG"
echo "$PROGRESS_RESPONSE" | jq '.' >> "$TRADING_LOG"

# Extract and analyze data
LAST_UPDATE=$(echo "$STATUS_RESPONSE" | jq -r '.last_update')
TRADING_STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.trading')
TRADE_COUNT=$(echo "$PROGRESS_RESPONSE" | jq '.trades | length')

# Check for critical conditions
echo "--- $(date) ---" >> "$ALERT_LOG"

# Check if trading is not running
if [ "$TRADING_STATUS" != "running" ]; then
    echo "CRITICAL: Trading status is '$TRADING_STATUS' (expected: 'running')" >> "$ALERT_LOG"
fi

# Analyze trades for patterns
BUY_COUNT=0
SELL_COUNT=0
LATEST_SIDE=""
LATEST_STATUS=""

if [ $TRADE_COUNT -gt 0 ]; then
    # Get latest trade
    LATEST_TRADE=$(echo "$PROGRESS_RESPONSE" | jq '.trades[0]')
    LATEST_SIDE=$(echo "$LATEST_TRADE" | jq -r '.side')
    LATEST_STATUS=$(echo "$LATEST_TRADE" | jq -r '.status')
    
    if [ "$LATEST_STATUS" != "filled" ]; then
        echo "ALERT: Latest trade status is '$LATEST_STATUS' (not 'filled')" >> "$ALERT_LOG"
    fi
    
    # Count buy vs sell trades
    BUY_COUNT=$(echo "$PROGRESS_RESPONSE" | jq '[.trades[] | select(.side == "buy")] | length')
    SELL_COUNT=$(echo "$PROGRESS_RESPONSE" | jq '[.trades[] | select(.side == "sell")] | length')
    
    echo "Trade Analysis: $BUY_COUNT buy trades, $SELL_COUNT sell trades" >> "$TRADING_LOG"
    
    # Check for imbalance (more than 80% one direction)
    TOTAL_TRADES=$((BUY_COUNT + SELL_COUNT))
    if [ $TOTAL_TRADES -gt 0 ]; then
        BUY_PERCENTAGE=$((BUY_COUNT * 100 / TOTAL_TRADES))
        if [ $BUY_PERCENTAGE -gt 80 ]; then
            echo "ALERT: Heavy buy bias detected ($BUY_PERCENTAGE% buys)" >> "$ALERT_LOG"
        elif [ $BUY_PERCENTAGE -lt 20 ]; then
            echo "ALERT: Heavy sell bias detected ($((100 - BUY_PERCENTAGE))% sells)" >> "$ALERT_LOG"
        fi
    fi
fi

# Generate plain text summary
SUMMARY="Trading Dashboard Monitoring Summary:\n"
SUMMARY+="Timestamp: $(date)\n"
SUMMARY+="\n--- System Status ---\n"
SUMMARY+="Trading Status: $TRADING_STATUS\n"
SUMMARY+="Last Update: $LAST_UPDATE\n"

SUMMARY+="\n--- Trading Activity ---\n"
SUMMARY+="Total Trades: $TRADE_COUNT\n"
if [ $TRADE_COUNT -gt 0 ]; then
    SUMMARY+="Buy Trades: $BUY_COUNT\n"
    SUMMARY+="Sell Trades: $SELL_COUNT\n"
    SUMMARY+="Latest Trade Side: $LATEST_SIDE\n"
    SUMMARY+="Latest Trade Status: $LATEST_STATUS\n"
fi

SUMMARY+="\n--- Alert Status ---\n"
# Check if there are any alerts from this run
ALERT_CHECK=$(tail -5 "$ALERT_LOG" | grep -E "CRITICAL|WARNING|ALERT" | grep "$(date +"%Y-%m-%d")" || true)
if [ -n "$ALERT_CHECK" ]; then
    SUMMARY+="Active Alerts Detected:\n"
    echo "$ALERT_CHECK" | while read -r line; do
        SUMMARY+="- $line\n"
    done
else
    SUMMARY+="No new critical alerts detected.\n"
fi

echo -e "$SUMMARY"
echo -e "$SUMMARY" > /Users/chetantemkar/.openclaw/workspace/app/trading_summary.txt