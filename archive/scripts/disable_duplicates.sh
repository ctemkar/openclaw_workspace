#!/bin/bash

echo "Fetching cron jobs..."
JOBS=$(openclaw cron list --json | jq -r '.jobs[] | select(.enabled==true) | select(.payload.message | contains("localhost:5001") or .payload.text | contains("localhost:5001") or .name | contains("trading_dashboard") or .name | contains("trading-monitor")) | .id')

COUNT=0
for JOB_ID in $JOBS; do
    echo "Disabling job: $JOB_ID"
    openclaw cron update "$JOB_ID" --enabled false
    ((COUNT++))
done

echo "✅ Disabled $COUNT duplicate cron jobs"

# List remaining enabled jobs
echo -e "\nRemaining enabled jobs:"
openclaw cron list --json | jq -r '.jobs[] | select(.enabled==true) | "\(.name) - \(.id)"'