#!/bin/bash

echo "🚨 QUICK DISABLE - Trading Dashboard Monitor Jobs"
echo "================================================"

# Get list of trading dashboard job IDs
echo "Fetching job IDs..."
JOB_IDS=$(openclaw cron list --json | jq -r '.jobs[] | select(.name | test("trading_dashboard_monitor"; "i")) | .id')

COUNT=$(echo "$JOB_IDS" | wc -l | tr -d ' ')
echo "Found $COUNT trading_dashboard_monitor jobs"

# Disable them one by one
DISABLED=0
for JOB_ID in $JOB_IDS; do
    echo -n "Disabling $JOB_ID... "
    if openclaw cron disable "$JOB_ID" > /dev/null 2>&1; then
        echo "✅"
        DISABLED=$((DISABLED + 1))
    else
        echo "❌"
    fi
    
    # Small delay to avoid getting killed
    sleep 0.5
done

echo ""
echo "================================================"
echo "✅ Disabled $DISABLED/$COUNT trading_dashboard_monitor jobs"
echo ""
echo "📊 Remaining enabled jobs:"
openclaw cron list --json | jq '[.jobs[] | select(.enabled == true)] | length'