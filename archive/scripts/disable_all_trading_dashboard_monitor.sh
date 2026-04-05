#!/bin/bash

echo "🚨 NUCLEAR OPTION: Disabling ALL 'trading_dashboard_monitor' jobs..."

# Count them
COUNT=$(openclaw cron list --json | jq '[.jobs[] | select(.enabled==true) | select(.name == "trading_dashboard_monitor")] | length')
echo "Found $COUNT 'trading_dashboard_monitor' jobs to disable"

# Get ALL their IDs
JOB_IDS=$(openclaw cron list --json | jq -r '.jobs[] | select(.enabled==true) | select(.name == "trading_dashboard_monitor") | .id')

# Disable them ALL
echo ""
echo "Disabling ALL $COUNT 'trading_dashboard_monitor' jobs..."
echo "$JOB_IDS" | while read JOB_ID; do
    echo "  Disabling: $JOB_ID"
    openclaw cron disable "$JOB_ID"
done

echo ""
echo "✅ Nuclear cleanup complete!"

# Check remaining
echo ""
echo "📋 Checking remaining enabled jobs..."
TOTAL_ENABLED=$(openclaw cron list --json | jq '[.jobs[] | select(.enabled==true)] | length')
TRADING_DASHBOARD_ENABLED=$(openclaw cron list --json | jq '[.jobs[] | select(.enabled==true) | select(.name == "trading_dashboard_monitor")] | length')

echo "Total enabled jobs remaining: $TOTAL_ENABLED"
echo "'trading_dashboard_monitor' jobs remaining: $TRADING_DASHBOARD_ENABLED"