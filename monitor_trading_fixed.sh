#!/bin/bash

URL="http://localhost:5001/status"
GENERAL_LOG="./trading_monitoring.log"
CRITICAL_LOG="./critical_alerts.log"
SUMMARY_FILE="/tmp/trading_summary.txt"

# Fetch data from the URL
response=$(curl -s "$URL")

# Check if the response is empty or indicates an error
if [[ -z "$response" ]]; then
  echo "$(date): ERROR - No response from $URL" >> "$GENERAL_LOG"
  echo "There was an error retrieving data from the trading dashboard." > "$SUMMARY_FILE"
  exit 1
fi

# Log the response
echo "$(date): $response" >> "$GENERAL_LOG"

# Parse JSON response
status=$(echo "$response" | jq -r '.status // "unknown"')
capital=$(echo "$response" | jq -r '.capital // 0')
last_analysis=$(echo "$response" | jq -r '.last_analysis // "unknown"')

# Check for critical conditions
# For now, we'll check if system is running and log basic status
# In a real system, we would check for specific alert conditions

ALERT_FOUND=false

# Check if system is not running
if [[ "$status" != "running" ]]; then
  echo "$(date): ALERT - System status is '$status', expected 'running'." >> "$CRITICAL_LOG"
  echo "System status alert: status is '$status'" >> "$SUMMARY_FILE"
  ALERT_FOUND=true
fi

# Check if capital is below threshold (e.g., less than 90% of initial $1000)
if (( $(echo "$capital < 900" | bc -l) )); then
  echo "$(date): ALERT - Capital has dropped below $900 (current: \$$capital)." >> "$CRITICAL_LOG"
  echo "Capital alert: \$$capital (below \$900 threshold)" >> "$SUMMARY_FILE"
  ALERT_FOUND=true
fi

# Check if last analysis is too old (more than 2 hours ago)
current_time=$(date -u +%s)
last_analysis_time=$(date -u -d "$last_analysis" +%s 2>/dev/null || echo "0")
if [[ "$last_analysis_time" != "0" ]]; then
  time_diff=$((current_time - last_analysis_time))
  if (( time_diff > 7200 )); then  # 2 hours in seconds
    echo "$(date): ALERT - Last analysis was $((time_diff/3600)) hours ago." >> "$CRITICAL_LOG"
    echo "Analysis alert: Last analysis was $((time_diff/3600)) hours ago" >> "$SUMMARY_FILE"
    ALERT_FOUND=true
  fi
fi

# If no alerts, state that
if [[ "$ALERT_FOUND" == "false" ]]; then
  echo "No critical alerts detected." > "$SUMMARY_FILE"
  echo "System status: $status" >> "$SUMMARY_FILE"
  echo "Capital: \$$capital" >> "$SUMMARY_FILE"
  echo "Last analysis: $last_analysis" >> "$SUMMARY_FILE"
fi

# The summary will be read from SUMMARY_FILE by the cron job delivery