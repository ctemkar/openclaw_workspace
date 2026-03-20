#!/bin/bash

URL="http://localhost:5001/"
MONITOR_LOG="/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
ALERTS_LOG="/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"

# Fetch data
DATA=$(curl --max-time 10 -s "$URL")

if [ $? -ne 0 ]; then
  echo "$(date): ERROR: Failed to fetch data from $URL. Curl exited with status $?." >> "$MONITOR_LOG"
  echo "$(date): ERROR: Failed to fetch data from $URL. Check connectivity and server status."
  exit 1
fi

# Log all extracted data
echo "$(date): --- Trading Data ---" >> "$MONITOR_LOG"
echo "$DATA" >> "$MONITOR_LOG"
echo "" >> "$MONITOR_LOG"

# Detect and log critical alerts
echo "$(date): --- Critical Alerts ---" >> "$ALERTS_LOG"
ALERT_FOUND=false

# Detect stop-loss/take-profit (adjust keywords as needed based on actual output)
if echo "$DATA" | grep -q -i -e "STOP_LOSS_TRIGGERED" -e "TAKE_PROFIT_HIT"; then
  ALERT_MESSAGE="ORDER_TRIGGERED: Stop-loss or Take-profit order triggered."
  echo "$(date): $ALERT_MESSAGE" >> "$ALERTS_LOG"
  ALERT_FOUND=true
fi

# Detect critical drawdown (adjust threshold/keywords as needed)
if echo "$DATA" | grep -q -i "CRITICAL_DRAWDOWN"; then
  ALERT_MESSAGE="DRAWDOWN_ALERT: Critical drawdown detected."
  echo "$(date): $ALERT_MESSAGE" >> "$ALERTS_LOG"
  ALERT_FOUND=true
fi

if [ "$ALERT_FOUND" = false ]; then
  echo "No critical alerts detected." >> "$ALERTS_LOG"
fi
echo "" >> "$ALERTS_LOG"

# Generate summary
SUMMARY="Trading Monitoring Summary (as of $(date)):\n"
SUMMARY+="  - Monitored URL: $URL\n"
SUMMARY+="  - Trading data logged to: $MONITOR_LOG\n"
SUMMARY+="  - Alerts logged to: $ALERTS_LOG\n"

if [ "$ALERT_FOUND" = true ]; then
  SUMMARY+="  - CRITICAL ALERTS DETECTED. Review $ALERTS_LOG for details.\n"
else
  SUMMARY+="  - No critical alerts detected.\n"
fi

echo -e "$SUMMARY"

exit 0
