#!/bin/bash

# Define log files
TRADING_LOG="/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_LOG="/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
URL="http://localhost:5001/"

# Fetch data from the URL
# Use curl with a timeout and handle potential errors
data=$(curl --silent --max-time 10 "$URL")
exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo "$(date): Error fetching data from $URL. curl exited with code $exit_code." >> "$TRADING_LOG"
    echo "Summary: Failed to fetch trading data due to connection error." >&2 # Output summary to stderr for cron delivery
    exit 1
fi

# Log general data
echo "$(date): Fetched data:" >> "$TRADING_LOG"
echo "$data" >> "$TRADING_LOG"
echo "" >> "$TRADING_LOG"

ALERT_FOUND=false

# --- Analysis for Critical Alerts ---
# This is a placeholder. You'll need to define specific patterns/conditions.

# Example: Detect stop-loss/take-profit orders (assuming they are keywords in the logs)
if echo "$data" | grep -qiE "stop-loss|take-profit"; then
    echo "$(date): CRITICAL ALERT - Stop-loss or Take-profit order detected." >> "$CRITICAL_LOG"
    echo "$(date): CRITICAL ALERT - Stop-loss or Take-profit order detected." >> "$TRADING_LOG"
    ALERT_FOUND=true
fi

# Example: Detect critical drawdown (assuming a numerical value in logs)
# This example assumes a line like "drawdown: 15%" or "drawdown: -0.15"
# It looks for values directly after "drawdown: " (with optional spaces), extracts them,
# converts percentages to decimals if present, and checks if the absolute value is > 10.
if echo "$data" | grep -Eoi "drawdown: *([0-9]+(\.[0-9]+)?%?|-[0-9]+(\.[0-9]+)?)" | sed -E 's/drawdown: *//; s/%//' | awk \
    '{ 
        val = $0; 
        if (val ~ /%/) { 
            sub(/%/, "", val); 
            val = val / 100; 
        } 
        if (val > 0.10 || val < -0.10) { 
            print "CRITICAL_DRAWDOWN_DETECTED"; # Output a marker string
        } 
    }' | grep -q "CRITICAL_DRAWDOWN_DETECTED"; then
    echo "$(date): CRITICAL ALERT - Critical drawdown detected." >> "$CRITICAL_LOG"
    echo "$(date): CRITICAL ALERT - Critical drawdown detected." >> "$TRADING_LOG"
    ALERT_FOUND=true
fi

# --- Generate Summary ---
SUMMARY="Trading Monitoring Summary: $(date)\n"

if [ "$ALERT_FOUND" = true ]; then
    SUMMARY+="CRITICAL ALERTS DETECTED. Please check detailed logs.\n"
    SUMMARY+="Critical alerts logged to: $CRITICAL_LOG\n"
    SUMMARY+="Detailed logs available at: $TRADING_LOG\n"
else
    SUMMARY+="No critical alerts detected.\n"
fi

# Output the summary to standard output (which cron will capture)
echo -e "$SUMMARY"

exit 0
