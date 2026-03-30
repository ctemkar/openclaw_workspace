#!/bin/bash

# Trading monitoring script
LOG_FILE="/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERTS_FILE="/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
DATA_URL="http://localhost:5001/"

echo "--- $(date) ---" >> $LOG_FILE

# 1. Fetch data from the URL using exec and curl
echo "Fetching data from $DATA_URL..." >> $LOG_FILE
FETCHED_DATA=$(curl -s $DATA_URL)

if [ $? -ne 0 ]; then
  echo "Error: Failed to fetch data from $DATA_URL" >> $LOG_FILE
  exit 1
fi

echo "Data fetched successfully." >> $LOG_FILE

# 3. Log all extracted data
echo "$FETCHED_DATA" >> $LOG_FILE

# --- Placeholder for 2. Parse data and 4. Implement alert conditions ---
# In a real-world scenario, you would use a more robust parsing method here,
# potentially invoking a Python script or using tools like `jq` if the data is JSON.
# For simplicity, we'll use basic grep for demonstration, assuming text-based data.

# Example: Check for critical conditions (this is highly dependent on the data format)
# Assumed format for demonstration:
# STOP_LOSS_HIT=true
# TAKE_PROFIT_HIT=false
# DRAWDOWN_CRITICAL=false
# CAPITAL=10000
# STOP_LOSS=9000
# TAKE_PROFIT=11000

STOP_LOSS_HIT=$(echo "$FETCHED_DATA" | grep "STOP_LOSS_HIT=true" > /dev/null && echo "true" || echo "false")
TAKE_PROFIT_HIT=$(echo "$FETCHED_DATA" | grep "TAKE_PROFIT_HIT=true" > /dev/null && echo "true" || echo "false")
DRAWDOWN_CRITICAL=$(echo "$FETCHED_DATA" | grep "DRAWDOWN_CRITICAL=true" > /dev/null && echo "true" || echo "false")

CAPITAL=$(echo "$FETCHED_DATA" | grep "CAPITAL=" | cut -d= -f2)
STOP_LOSS=$(echo "$FETCHED_DATA" | grep "STOP_LOSS=" | cut -d= -f2)
TAKE_PROFIT=$(echo "$FETCHED_DATA" | grep "TAKE_PROFIT=" | cut -d= -f2)

ALERT_TRIGGERED=false
ALERT_MESSAGE=""

if [ "$STOP_LOSS_HIT" == "true" ]; then
  ALERT_TRIGGERED=true
  ALERT_MESSAGE="STOP LOSS HIT. Capital: $CAPITAL, Stop Loss: $STOP_LOSS"
  echo "ALERT: Stop Loss Hit!" >> $LOG_FILE
elif [ "$TAKE_PROFIT_HIT" == "true" ]; then
  ALERT_TRIGGERED=true
  ALERT_MESSAGE="TAKE PROFIT HIT. Capital: $CAPITAL, Take Profit: $TAKE_PROFIT"
  echo "ALERT: Take Profit Hit!" >> $LOG_FILE
elif [ "$DRAWDOWN_CRITICAL" == "true" ]; then
  ALERT_TRIGGERED=true
  ALERT_MESSAGE="DRAWDOWN CRITICAL. Capital: $CAPITAL"
  echo "ALERT: Drawdown Critical!" >> $LOG_FILE
fi

# 5. If any alert condition is met, save critical data
if [ "$ALERT_TRIGGERED" == "true" ]; then
  echo "--- Critical Alert ---" >> $CRITICAL_ALERTS_FILE
  echo "Timestamp: $(date)" >> $CRITICAL_ALERTS_FILE
  echo "$ALERT_MESSAGE" >> $CRITICAL_ALERTS_FILE
  echo "Full Fetched Data Snippet:" >> $CRITICAL_ALERTS_FILE
  echo "$FETCHED_DATA" | head -n 10 >> $CRITICAL_ALERTS_FILE # Log snippet of data
  echo "----------------------" >> $CRITICAL_ALERTS_FILE
  echo "Critical alert logged to $CRITICAL_ALERTS_FILE" >> $LOG_FILE
fi

echo "Trading monitoring script finished." >> $LOG_FILE
