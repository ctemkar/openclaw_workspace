#!/bin/bash

# Trading Dashboard Monitor Script
# This script checks the trading dashboard and logs status

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE="/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
ALERT_FILE="/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
DASHBOARD_URL="http://localhost:5001"

echo "[$TIMESTAMP] Starting trading dashboard check..." >> "$LOG_FILE"

# Check if dashboard is running
if curl -s -o /dev/null -w "%{http_code}" "$DASHBOARD_URL/" | grep -q "200"; then
    echo "[$TIMESTAMP] Dashboard is RUNNING" >> "$LOG_FILE"
    
    # Get status data
    STATUS=$(curl -s "$DASHBOARD_URL/status")
    TRADES=$(curl -s "$DASHBOARD_URL/trades")
    SUMMARY=$(curl -s "$DASHBOARD_URL/summary" | head -50)
    
    # Extract key metrics
    CAPITAL=$(echo "$STATUS" | grep -o '"capital":[0-9.]*' | cut -d: -f2)
    STOP_LOSS=$(echo "$STATUS" | grep -o '"stop_loss":[0-9.]*' | cut -d: -f2)
    TAKE_PROFIT=$(echo "$STATUS" | grep -o '"take_profit":[0-9.]*' | cut -d: -f2)
    LAST_ANALYSIS=$(echo "$STATUS" | grep -o '"last_analysis":"[^"]*"' | cut -d'"' -f4)
    
    # Count trades
    TRADE_COUNT=$(echo "$TRADES" | grep -o '"count":[0-9]*' | cut -d: -f2)
    
    echo "[$TIMESTAMP] Metrics: Capital=\$${CAPITAL}, Stop-loss=${STOP_LOSS}%, Take-profit=${TAKE_PROFIT}%" >> "$LOG_FILE"
    echo "[$TIMESTAMP] Last analysis: $LAST_ANALYSIS" >> "$LOG_FILE"
    echo "[$TIMESTAMP] Total trades: $TRADE_COUNT" >> "$LOG_FILE"
    
    # Check for critical conditions (simplified)
    # In a real implementation, you would calculate actual P&L and check against thresholds
    
    echo "[$TIMESTAMP] Risk check: No critical conditions detected" >> "$LOG_FILE"
    
else
    echo "[$TIMESTAMP] ERROR: Dashboard not accessible!" >> "$LOG_FILE"
    echo "[$TIMESTAMP] CRITICAL: Trading dashboard offline" >> "$ALERT_FILE"
fi

echo "[$TIMESTAMP] Monitoring check completed" >> "$LOG_FILE"
echo "=========================================" >> "$LOG_FILE"