
#!/bin/bash

URL="http://localhost:5001/"
TRADING_LOG="/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_LOG="/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
SUMMARY_LOG="/Users/chetantemkar/.openclaw/workspace/app/trading_summary.txt"

# Fetch data
response=$(curl -s "$URL")

# Log all data
echo "$(date): $response" >> "$TRADING_LOG"

# Detect critical alerts (example: simple keyword detection)
if echo "$response" | grep -qi "stop-loss triggered"; then
  echo "$(date): STOP-LOSS TRIGGERED - $response" >> "$CRITICAL_LOG"
  echo "ALERT: Stop-loss triggered at $(date)." >> "$SUMMARY_LOG"
fi

if echo "$response" | grep -qi "take-profit triggered"; then
  echo "$(date): TAKE-PROFIT TRIGGERED - $response" >> "$CRITICAL_LOG"
  echo "ALERT: Take-profit triggered at $(date)." >> "$SUMMARY_LOG"
fi

if echo "$response" | grep -qi "critical drawdown"; then
  echo "$(date): CRITICAL DRAWDOWN - $response" >> "$CRITICAL_LOG"
  echo "ALERT: Critical drawdown detected at $(date)." >> "$SUMMARY_LOG"
fi

# Generate summary if no critical alerts were explicitly logged in this run,
# otherwise the alerts above have already added to SUMMARY_LOG.
# More sophisticated analysis would go here.
if [ ! -s "$SUMMARY_LOG" ] || ! tail -n 1 "$SUMMARY_LOG" | grep -q "ALERT:"; then
  echo "$(date): Analysis complete. No critical alerts detected in this cycle." >> "$SUMMARY_LOG"
fi

echo "Monitoring complete."
