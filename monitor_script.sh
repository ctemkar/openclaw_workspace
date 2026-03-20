#!/bin/bash
API_URL="http://localhost:5001/"
LOG_FILE="./trading_monitoring.log"
CRITICAL_LOG_FILE="./critical_alerts.log"

# Fetch data, log all of it, then process for critical alerts
curl -s "$API_URL" | tee >(jq -c . >> "$LOG_FILE") |
jq -r '
  (.stopLossTriggered) as $stopLossTriggered |
  (.takeProfitTriggered) as $takeProfitTriggered |
  (.drawdownIndicatorsCritical) as $drawdownIndicatorsCritical |
  if $stopLossTriggered then "STOP LOSS TRIGGERED: \(.)"
  elif $takeProfitTriggered then "TAKE PROFIT TRIGGERED: \(.)"
  elif $drawdownIndicatorsCritical then "CRITICAL DRAWDOWN INDICATORS: \(.)"
  else "Monitoring OK"
  end
' > >(grep -v "Monitoring OK" | tee -a "$CRITICAL_LOG_FILE") | tee >(grep "Monitoring OK" >> "$LOG_FILE")

# Generate a plain text summary (this part might need adjustment based on actual jq output)
# For now, we'll assume the last line of the combined output is a reasonable summary.
# A more sophisticated approach would parse the jq output more specifically.
SUMMARY=$(tail -n 1 "$LOG_FILE")
echo "Monitoring Summary: $SUMMARY"
