#!/bin/bash

echo "🚨 AGGRESSIVE CLEANUP: Disabling ALL duplicate cron jobs..."

# Get all job IDs
JOB_IDS=$(openclaw cron list --json | jq -r '.jobs[] | select(.enabled==true) | select(.name | contains("trading") or contains("Trading") or contains("TRADING")) | .id')

# Count them
COUNT=$(echo "$JOB_IDS" | wc -l | tr -d ' ')
echo "Found $COUNT trading jobs to disable"

# Disable them ALL at once
echo ""
echo "Disabling ALL $COUNT trading jobs..."
echo "$JOB_IDS" | xargs -P 10 -I {} sh -c 'echo "Disabling: {}" && openclaw cron disable {}'

echo ""
echo "✅ Aggressive cleanup complete!"

# Check remaining
echo ""
echo "📋 Checking remaining enabled jobs..."
TOTAL_ENABLED=$(openclaw cron list --json | jq '[.jobs[] | select(.enabled==true)] | length')
TRADING_ENABLED=$(openclaw cron list --json | jq '[.jobs[] | select(.enabled==true) | select(.name | contains("trading") or contains("Trading") or contains("TRADING"))] | length')

echo "Total enabled jobs remaining: $TOTAL_ENABLED"
echo "Trading jobs remaining: $TRADING_ENABLED"