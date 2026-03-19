#!/bin/bash
# Trading Dashboard Monitor Script
# Run by cron job to monitor trading system

cd /Users/chetantemkar/.openclaw/workspace/app

# Run the monitoring script
python3 trading_monitor.py

# Check if critical alerts were generated
if [ $? -eq 1 ]; then
    echo "CRITICAL ALERTS DETECTED - Check critical_alerts.log"
    # In a real implementation, you could send notifications here
    # e.g., send telegram message, email, etc.
fi

echo "Monitoring completed at $(date)"