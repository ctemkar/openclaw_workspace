#!/bin/bash

echo "🚨 CLEANING UP DUPLICATE TRADING CRON JOBS..."
echo "This will disable ALL jobs with 'trading' in the name or monitoring localhost:5001"

# Count total jobs
TOTAL_JOBS=$(openclaw cron list --json | jq '.jobs | length')
echo "Total cron jobs found: $TOTAL_JOBS"

# Count enabled trading jobs
ENABLED_TRADING_JOBS=$(openclaw cron list --json | jq '[.jobs[] | select(.enabled==true) | select(.name | contains("trading") or contains("Trading") or contains("TRADING") or (.payload.message // "") | contains("localhost:5001") or (.payload.text // "") | contains("localhost:5001"))] | length')
echo "Enabled trading jobs to disable: $ENABLED_TRADING_JOBS"

# Disable them
echo ""
echo "Disabling trading jobs..."
openclaw cron list --json | jq -r '.jobs[] | select(.enabled==true) | select(.name | contains("trading") or contains("Trading") or contains("TRADING") or (.payload.message // "") | contains("localhost:5001") or (.payload.text // "") | contains("localhost:5001")) | .id' | while read JOB_ID; do
    echo "  Disabling: $JOB_ID"
    openclaw cron disable "$JOB_ID"
done

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "Remaining enabled jobs:"
openclaw cron list --json | jq -r '.jobs[] | select(.enabled==true) | "  - \(.name) (\(.id))"'