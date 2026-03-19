#!/bin/bash

BASE_URL="http://localhost:5001"
TRADING_LOG="./trading_monitoring.log"
ALERT_LOG="./critical_alerts.log"
TIMESTAMP=$(date)

echo "--- $TIMESTAMP ---" >> "$TRADING_LOG"

# Fetch all relevant data
STATUS_RESPONSE=$(curl -s "$BASE_URL/status")
TRADES_RESPONSE=$(curl -s "$BASE_URL/trades")
SUMMARY_RESPONSE=$(curl -s "$BASE_URL/summary")

# Check if services are responding
if [ $? -ne 0 ] || [ -z "$STATUS_RESPONSE" ]; then
    echo "CRITICAL: Trading dashboard is not responding" >> "$ALERT_LOG"
    echo "Error: Dashboard not responding" >> "$TRADING_LOG"
    echo "Trading Dashboard Monitoring Summary:"
    echo "Timestamp: $TIMESTAMP"
    echo "Status: CRITICAL - Dashboard not responding"
    exit 1
fi

# Parse status data
STATUS=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('status', 'unknown'))")
CAPITAL=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('capital', 0))")
LAST_ANALYSIS=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('last_analysis', 'unknown'))")
TRADING_PAIRS=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(', '.join(data.get('trading_pairs', [])))")

# Parse trades data
TRADE_COUNT=$(echo "$TRADES_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('count', 0))")
TRADES=$(echo "$TRADES_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); trades=data.get('trades', []); print(len(trades))")

# Log all data
echo "Status: $STATUS_RESPONSE" >> "$TRADING_LOG"
echo "Trades: $TRADES_RESPONSE" >> "$TRADING_LOG"
echo "Summary: $SUMMARY_RESPONSE" >> "$TRADING_LOG"

# Check for critical conditions
echo "--- $TIMESTAMP ---" >> "$ALERT_LOG"

# 1. Check trading status
if [ "$STATUS" != "running" ]; then
    echo "CRITICAL: Trading status is '$STATUS'" >> "$ALERT_LOG"
fi

# 2. Check if capital is below threshold
if [ $(echo "$CAPITAL < 900" | bc -l 2>/dev/null || echo "0") -eq 1 ]; then
    echo "CRITICAL: Capital below $900 (current: $CAPITAL)" >> "$ALERT_LOG"
fi

# 3. Check for recent trades
if [ $TRADE_COUNT -eq 0 ]; then
    echo "WARNING: No trades recorded in recent history" >> "$ALERT_LOG"
fi

# 4. Analyze trade patterns
BUY_COUNT=0
SELL_COUNT=0
if [ $TRADE_COUNT -gt 0 ]; then
    # Count buys vs sells
    BUY_COUNT=$(echo "$TRADES_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
trades = data.get('trades', [])
buy_count = sum(1 for t in trades if t.get('side', '').lower() == 'buy')
print(buy_count)
")
    SELL_COUNT=$((TRADE_COUNT - BUY_COUNT))
    
    # Check for trade bias
    if [ $BUY_COUNT -gt $((TRADE_COUNT * 80 / 100)) ]; then
        echo "ALERT: Heavy buy bias ($BUY_COUNT buys out of $TRADE_COUNT total trades)" >> "$ALERT_LOG"
    fi
fi

# Generate comprehensive summary
SUMMARY="TRADING DASHBOARD MONITORING REPORT\n"
SUMMARY+="=====================================\n"
SUMMARY+="Timestamp: $TIMESTAMP\n\n"

SUMMARY+="SYSTEM STATUS\n"
SUMMARY+="-------------\n"
SUMMARY+="Trading Status: $STATUS\n"
SUMMARY+="Capital: \$$CAPITAL\n"
SUMMARY+="Last Analysis: $LAST_ANALYSIS\n"
SUMMARY+="Trading Pairs: $TRADING_PAIRS\n\n"

SUMMARY+="TRADING ACTIVITY\n"
SUMMARY+="----------------\n"
SUMMARY+="Total Trades: $TRADE_COUNT\n"
if [ $TRADE_COUNT -gt 0 ]; then
    SUMMARY+="Buy Trades: $BUY_COUNT\n"
    SUMMARY+="Sell Trades: $SELL_COUNT\n"
    
    # Get latest trade
    LATEST_TRADE=$(echo "$TRADES_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
trades = data.get('trades', [])
if trades:
    latest = trades[0]
    symbol = latest.get('symbol', 'N/A')
    side = latest.get('side', 'N/A')
    price = latest.get('price', 'N/A')
    time = latest.get('time', 'N/A')
    print(f'{symbol} {side} at \${price} ({time})')
else:
    print('No trade details')
")
    SUMMARY+="Latest Trade: $LATEST_TRADE\n"
fi
SUMMARY+="\n"

SUMMARY+="ALERT STATUS\n"
SUMMARY+="------------\n"
# Get alerts from this run
RECENT_ALERTS=$(tail -10 "$ALERT_LOG" | grep -E "CRITICAL|WARNING|ALERT" | grep "$(date +"%Y-%m-%d")" || true)
if [ -n "$RECENT_ALERTS" ]; then
    echo "$RECENT_ALERTS" | while read -r alert; do
        SUMMARY+="• $alert\n"
    done
else
    SUMMARY+="✓ No new critical alerts\n"
fi

SUMMARY+="\nRECOMMENDED ACTIONS\n"
SUMMARY+="------------------\n"
if [ "$STATUS" != "running" ]; then
    SUMMARY+="1. RESTART TRADING: System is not running\n"
fi
if [ $(echo "$CAPITAL < 950" | bc -l 2>/dev/null || echo "0") -eq 1 ]; then
    SUMMARY+="2. MONITOR CAPITAL: Capital below \$950\n"
fi
if [ $TRADE_COUNT -eq 0 ] && [ "$STATUS" = "running" ]; then
    SUMMARY+="3. CHECK STRATEGY: Running but no trades executed\n"
fi
if [ -z "$RECENT_ALERTS" ] || [ $(echo "$RECENT_ALERTS" | grep -c "CRITICAL") -eq 0 ]; then
    SUMMARY+="✓ System operational\n"
fi

# Output summary
echo -e "$SUMMARY"

# Save summary to file
echo -e "$SUMMARY" > ./trading_summary.txt

# Also append to monitoring log
echo -e "\nSummary generated at $TIMESTAMP" >> "$TRADING_LOG"