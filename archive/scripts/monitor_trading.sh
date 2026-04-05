#!/bin/bash

LOG_FILE="/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
ALERT_LOG_FILE="/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
TRADING_DASHBOARD_URL="http://localhost:5001"

# Fetch status data from the trading dashboard
STATUS_DATA=$(curl -s "${TRADING_DASHBOARD_URL}/status")
TRADES_DATA=$(curl -s "${TRADING_DASHBOARD_URL}/trades")

# Log the raw data
echo "$(date): Raw data fetched." >> "$LOG_FILE"
echo "$STATUS_DATA" >> "$LOG_FILE"
echo "--------------------" >> "$LOG_FILE"

# --- Analysis and Alerting ---
SUMMARY="Trading Dashboard Analysis:\n"
ALERTS=""

# Parse JSON data if available
if echo "$STATUS_DATA" | jq -e . >/dev/null 2>&1; then
    CURRENT_STATUS=$(echo "$STATUS_DATA" | jq -r '.status // "N/A"')
    CAPITAL=$(echo "$STATUS_DATA" | jq -r '.capital // "N/A"')
    LAST_ANALYSIS=$(echo "$STATUS_DATA" | jq -r '.last_analysis // "N/A"')
    PORT=$(echo "$STATUS_DATA" | jq -r '.port // "N/A"')
    
    # Extract risk parameters
    STOP_LOSS=$(echo "$STATUS_DATA" | jq -r '.risk_parameters.stop_loss // "N/A"')
    TAKE_PROFIT=$(echo "$STATUS_DATA" | jq -r '.risk_parameters.take_profit // "N/A"')
    MAX_TRADES=$(echo "$STATUS_DATA" | jq -r '.risk_parameters.max_trades_per_day // "N/A"')
    
    # Get trading pairs
    TRADING_PAIRS=$(echo "$STATUS_DATA" | jq -r '.trading_pairs | join(", ") // "N/A"')
    
    SUMMARY+="Current Status: ${CURRENT_STATUS}\n"
    SUMMARY+="Capital: \$${CAPITAL}\n"
    SUMMARY+="Port: ${PORT}\n"
    SUMMARY+="Last Analysis: ${LAST_ANALYSIS}\n"
    SUMMARY+="Trading Pairs: ${TRADING_PAIRS}\n"
    SUMMARY+="Risk Parameters:\n"
    SUMMARY+="  Stop-loss: $(echo "scale=1; ${STOP_LOSS} * 100" | bc)%\n"
    SUMMARY+="  Take-profit: $(echo "scale=1; ${TAKE_PROFIT} * 100" | bc)%\n"
    SUMMARY+="  Max trades/day: ${MAX_TRADES}\n"
    
    # Check trades for recent activity
    if echo "$TRADES_DATA" | jq -e . >/dev/null 2>&1; then
        TRADE_COUNT=$(echo "$TRADES_DATA" | jq -r '.count // 0')
        
        # Get latest trades with proper formatting
        LATEST_TRADES_JSON=$(echo "$TRADES_DATA" | jq -r '.trades[-2:]')
        LATEST_TRADES=""
        
        # Process each trade
        for i in 0 1; do
            TRADE=$(echo "$LATEST_TRADES_JSON" | jq -r ".[$i]")
            if [ "$TRADE" != "null" ]; then
                SIDE=$(echo "$TRADE" | jq -r '.side // "N/A"')
                SYMBOL=$(echo "$TRADE" | jq -r '.symbol // "Unknown"')
                PRICE=$(echo "$TRADE" | jq -r '.price // "N/A"')
                TIME=$(echo "$TRADE" | jq -r '.time // "N/A"')
                
                if [ "$LATEST_TRADES" != "" ]; then
                    LATEST_TRADES="${LATEST_TRADES}, "
                fi
                LATEST_TRADES="${LATEST_TRADES}${SIDE} ${SYMBOL} @ \$${PRICE} (${TIME})"
            fi
        done
        
        if [ -z "$LATEST_TRADES" ]; then
            LATEST_TRADES="None"
        fi
        
        SUMMARY+="Recent Trades: ${TRADE_COUNT} total\n"
        SUMMARY+="Latest: ${LATEST_TRADES}\n"
        
        # Check if daily trade limit is reached
        if [ "$TRADE_COUNT" -ge "$MAX_TRADES" ]; then
            ALERT="DAILY TRADE LIMIT REACHED: ${TRADE_COUNT}/${MAX_TRADES} trades executed"
            ALERTS+="$ALERT\n"
            echo "$(date): $ALERT" >> "$ALERT_LOG_FILE"
        fi
    fi
    
    # Check if server is running
    if [ "$CURRENT_STATUS" != "running" ]; then
        ALERT="TRADING SERVER NOT RUNNING: Status is '${CURRENT_STATUS}'"
        ALERTS+="$ALERT\n"
        echo "$(date): $ALERT" >> "$ALERT_LOG_FILE"
    fi
    
    # Check if analysis is recent (within last 2 hours)
    if [ "$LAST_ANALYSIS" != "N/A" ]; then
        LAST_TS=$(date -j -f "%Y-%m-%dT%H:%M:%S" "${LAST_ANALYSIS:0:19}" "+%s" 2>/dev/null || echo 0)
        NOW_TS=$(date "+%s")
        HOURS_DIFF=$(( (NOW_TS - LAST_TS) / 3600 ))
        
        if [ "$HOURS_DIFF" -gt 2 ]; then
            ALERT="NO RECENT ANALYSIS: Last analysis was ${HOURS_DIFF} hours ago"
            ALERTS+="$ALERT\n"
            echo "$(date): $ALERT" >> "$ALERT_LOG_FILE"
        fi
    fi
    
else
    # Fallback for non-JSON data or if jq is not available
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
