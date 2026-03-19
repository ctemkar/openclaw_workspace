#!/bin/bash

# Trading Dashboard Monitor Script
# Fetches data from http://localhost:5001/, analyzes trading logs and risk parameters
# Logs data to trading_monitoring.log and alerts to critical_alerts.log

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
MONITORING_LOG="/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_LOG="/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"

echo "=== Trading Dashboard Monitor - $TIMESTAMP ===" >> "$MONITORING_LOG"

# Check if server is running
if ! curl -s --head http://localhost:5001/ > /dev/null; then
    echo "ERROR: Trading dashboard server not accessible on localhost:5001" >> "$MONITORING_LOG"
    echo "CRITICAL: Trading dashboard server down at $TIMESTAMP" >> "$CRITICAL_LOG"
    exit 1
fi

# Fetch data from endpoints
STATUS=$(curl -s http://localhost:5001/status)
TRADES=$(curl -s http://localhost:5001/trades)
SUMMARY=$(curl -s http://localhost:5001/summary)

# Parse status data
CAPITAL=$(echo "$STATUS" | grep -o '"capital":[0-9.]*' | cut -d: -f2)
STOP_LOSS=$(echo "$STATUS" | grep -o '"stop_loss":[0-9.]*' | cut -d: -f2)
TAKE_PROFIT=$(echo "$STATUS" | grep -o '"take_profit":[0-9.]*' | cut -d: -f2)
MAX_TRADES=$(echo "$STATUS" | grep -o '"max_trades_per_day":[0-9]*' | cut -d: -f2)
LAST_ANALYSIS=$(echo "$STATUS" | grep -o '"last_analysis":"[^"]*"' | cut -d'"' -f4)
SYSTEM_STATUS=$(echo "$STATUS" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

# Parse trades data
TRADE_COUNT=$(echo "$TRADES" | grep -o '"count":[0-9]*' | cut -d: -f2)
RECENT_TRADES=$(echo "$TRADES" | grep -o '"trades":\[.*\]' | head -1)

# Parse summary for P&L and drawdown indicators
TOTAL_PNL=$(echo "$SUMMARY" | grep -o "Total P&L:.*$" | head -1 | sed 's/Total P&L: //' | tr -d '$')
AVAILABLE_CAPITAL=$(echo "$SUMMARY" | grep -o "Available capital:.*$" | head -1 | sed 's/Available capital: //' | tr -d '$')
TODAYS_TRADES=$(echo "$SUMMARY" | grep -o "Today's trades executed:.*$" | head -1 | sed "s/Today's trades executed: //")

# Calculate drawdown if we have previous capital data
if [ -f "/tmp/previous_capital.txt" ]; then
    PREVIOUS_CAPITAL=$(cat /tmp/previous_capital.txt)
    if [ ! -z "$PREVIOUS_CAPITAL" ] && [ ! -z "$AVAILABLE_CAPITAL" ]; then
        DRAWDOWN=$(echo "scale=2; (($PREVIOUS_CAPITAL - $AVAILABLE_CAPITAL) / $PREVIOUS_CAPITAL) * 100" | bc 2>/dev/null || echo "0")
    else
        DRAWDOWN="0"
    fi
else
    DRAWDOWN="0"
fi

# Save current capital for next comparison
echo "$AVAILABLE_CAPITAL" > /tmp/previous_capital.txt

# Log monitoring data
{
    echo "System Status: $SYSTEM_STATUS"
    echo "Capital: \$$CAPITAL"
    echo "Available Capital: \$$AVAILABLE_CAPITAL"
    echo "Stop Loss: $(echo "$STOP_LOSS * 100" | bc 2>/dev/null || echo "$STOP_LOSS")%"
    echo "Take Profit: $(echo "$TAKE_PROFIT * 100" | bc 2>/dev/null || echo "$TAKE_PROFIT")%"
    echo "Max Trades/Day: $MAX_TRADES"
    echo "Today's Trades: $TODAYS_TRADES"
    echo "Total Trades: $TRADE_COUNT"
    echo "Total P&L: \$$TOTAL_PNL"
    echo "Drawdown: ${DRAWDOWN}%"
    echo "Last Analysis: $LAST_ANALYSIS"
    echo ""
} >> "$MONITORING_LOG"

# Check for critical conditions
CRITICAL=false
CRITICAL_MESSAGE=""

# Check if stop-loss or take-profit triggered (simplified check based on P&L)
if [ ! -z "$TOTAL_PNL" ]; then
    STOP_LOSS_PERCENT=$(echo "$STOP_LOSS * 100" | bc 2>/dev/null || echo "$STOP_LOSS")
    TAKE_PROFIT_PERCENT=$(echo "$TAKE_PROFIT * 100" | bc 2>/dev/null || echo "$TAKE_PROFIT")
    
    # Calculate P&L percentage relative to capital
    if [ "$CAPITAL" != "0" ] && [ ! -z "$TOTAL_PNL" ]; then
        PNL_PERCENT=$(echo "scale=2; ($TOTAL_PNL / $CAPITAL) * 100" | bc 2>/dev/null || echo "0")
        
        # Check stop-loss trigger (negative P&L exceeding stop-loss threshold)
        if [ $(echo "$PNL_PERCENT < -$STOP_LOSS_PERCENT" | bc 2>/dev/null || echo "0") -eq 1 ]; then
            CRITICAL=true
            CRITICAL_MESSAGE="STOP-LOSS TRIGGERED: P&L ($PNL_PERCENT%) exceeds stop-loss threshold (-$STOP_LOSS_PERCENT%)"
        fi
        
        # Check take-profit trigger (positive P&L exceeding take-profit threshold)
        if [ $(echo "$PNL_PERCENT > $TAKE_PROFIT_PERCENT" | bc 2>/dev/null || echo "0") -eq 1 ]; then
            CRITICAL=true
            CRITICAL_MESSAGE="TAKE-PROFIT TRIGGERED: P&L ($PNL_PERCENT%) exceeds take-profit threshold ($TAKE_PROFIT_PERCENT%)"
        fi
    fi
fi

# Check for critical drawdown (more than 2x stop-loss threshold)
if [ ! -z "$DRAWDOWN" ]; then
    CRITICAL_DRAWDOWN_THRESHOLD=$(echo "$STOP_LOSS * 2 * 100" | bc 2>/dev/null || echo "10")
    if [ $(echo "$DRAWDOWN > $CRITICAL_DRAWDOWN_THRESHOLD" | bc 2>/dev/null || echo "0") -eq 1 ]; then
        CRITICAL=true
        CRITICAL_MESSAGE="CRITICAL DRAWDOWN: $DRAWDOWN% exceeds critical threshold ($CRITICAL_DRAWDOWN_THRESHOLD%)"
    fi
fi

# Check if max trades reached for the day
if [ ! -z "$TODAYS_TRADES" ]; then
    TRADES_EXECUTED=$(echo "$TODAYS_TRADES" | cut -d'/' -f1)
    TRADES_LIMIT=$(echo "$TODAYS_TRADES" | cut -d'/' -f2)
    if [ "$TRADES_EXECUTED" -eq "$TRADES_LIMIT" ]; then
        echo "ALERT: Daily trade limit reached ($TRADES_EXECUTED/$TRADES_LIMIT)" >> "$MONITORING_LOG"
    fi
fi

# Log critical alerts if any
if [ "$CRITICAL" = true ]; then
    {
        echo "=== CRITICAL ALERT - $TIMESTAMP ==="
        echo "$CRITICAL_MESSAGE"
        echo "System Status: $SYSTEM_STATUS"
        echo "Capital: \$$CAPITAL"
        echo "Available Capital: \$$AVAILABLE_CAPITAL"
        echo "Total P&L: \$$TOTAL_PNL"
        echo "Drawdown: ${DRAWDOWN}%"
        echo "Stop Loss: ${STOP_LOSS_PERCENT}%"
        echo "Take Profit: ${TAKE_PROFIT_PERCENT}%"
        echo ""
    } >> "$CRITICAL_LOG"
    
    # Also add to monitoring log for visibility
    echo "CRITICAL ALERT: $CRITICAL_MESSAGE" >> "$MONITORING_LOG"
fi

echo "Monitoring completed at $TIMESTAMP" >> "$MONITORING_LOG"
echo "" >> "$MONITORING_LOG"

echo "Trading dashboard monitoring completed successfully"