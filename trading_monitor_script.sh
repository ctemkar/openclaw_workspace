#!/bin/bash
URL="http://localhost:5001/"
MONITOR_LOG="/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
ALERT_LOG="/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
SUMMARY_FILE="/Users/chetantemkar/.openclaw/workspace/app/trading_summary.txt"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

echo "--- Monitoring started at $TIMESTAMP ---" >> "$MONITOR_LOG"

# Using curl to fetch. Ensure curl is installed on the system where cron runs.
# If not, this part will fail. The prompt implies a shell environment.
curl -s "$URL" >> "$MONITOR_LOG"
CURL_EXIT_CODE=$?

if [ $CURL_EXIT_CODE -ne 0 ]; then
    echo "Error: curl failed with exit code $CURL_EXIT_CODE at $(date)" >> "$ALERT_LOG"
    echo "CRITICAL: Trading dashboard at $URL is unreachable." >> "$ALERT_LOG"
    echo "CRITICAL: Trading dashboard at $URL is unreachable. (Timestamp: $TIMESTAMP)" > "$SUMMARY_FILE"
    exit 1
fi

# --- Alert Detection Logic ---
# This is a placeholder. Real logic would depend on the content fetched (e.g., JSON parsing, regex)
# Example: Detect if "stop_loss_triggered": true in JSON output
ALERT_DETECTED=false
if grep -q '"stop_loss_triggered": true' "$MONITOR_LOG"; then
    echo "ALERT: Stop-loss triggered at $(date)" >> "$ALERT_LOG"
    ALERT_DETECTED=true
fi
if grep -q '"take_profit_triggered": true' "$MONITOR_LOG"; then
    echo "ALERT: Take-profit triggered at $(date)" >> "$ALERT_LOG"
    ALERT_DETECTED=true
fi
# Critical drawdown detection (example: if current balance drops below a threshold)
# A simpler check could be looking for a specific "drawdown_critical: true" flag.
if grep -q '"drawdown_critical": true' "$MONITOR_LOG"; then
    echo "ALERT: Critical drawdown detected at $(date)" >> "$ALERT_LOG"
    ALERT_DETECTED=true
fi

# --- Generate Summary ---
echo "Trading Dashboard Analysis Summary ($TIMESTAMP)" > "$SUMMARY_FILE"
echo "============================================" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"

# Append last few lines of monitoring log (e.g., last 10 lines)
echo "Recent Monitoring Data:" >> "$SUMMARY_FILE"
tail -n 10 "$MONITOR_LOG" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"

if [ "$ALERT_DETECTED" = true ]; then
    echo "CRITICAL ALERTS DETECTED:" >> "$SUMMARY_FILE"
    # Append last few lines of alert log
    tail -n 10 "$ALERT_LOG" >> "$SUMMARY_FILE"
else
    echo "No critical alerts detected." >> "$SUMMARY_FILE"
fi

echo "--- Monitoring finished at $(date) ---" >> "$MONITOR_LOG"
echo "Monitoring task completed."