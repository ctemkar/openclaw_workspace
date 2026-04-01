#!/bin/bash

echo "🗑️  DELETE DUPLICATE CRON JOBS"
echo "=============================="

# Get ALL job IDs first
echo "Getting all job IDs..."
ALL_IDS=$(openclaw cron list --json | jq -r '.jobs[].id')
TOTAL=$(echo "$ALL_IDS" | wc -l | tr -d ' ')
echo "Total jobs: $TOTAL"

# Get trading dashboard job IDs
echo "Finding trading dashboard jobs..."
TRADING_IDS=$(openclaw cron list --json | jq -r '.jobs[] | select(.name | test("trading_dashboard_monitor"; "i")) | .id')
COUNT=$(echo "$TRADING_IDS" | wc -l | tr -d ' ')
echo "Found $COUNT trading_dashboard_monitor jobs"

if [ "$COUNT" -eq 0 ]; then
    echo "No trading dashboard jobs found!"
    exit 0
fi

echo ""
echo "⚠️  WARNING: This will DELETE $COUNT cron jobs!"
echo "Press Ctrl+C in the next 5 seconds to cancel..."
sleep 5

echo ""
echo "Starting deletion..."
DELETED=0

# Delete them one by one
for JOB_ID in $TRADING_IDS; do
    echo -n "Deleting $JOB_ID... "
    
    # Use timeout to prevent hanging
    if timeout 5 openclaw cron rm "$JOB_ID" > /dev/null 2>&1; then
        echo "✅"
        DELETED=$((DELETED + 1))
    else
        echo "❌ (timeout or error)"
    fi
    
    # Tiny delay every 10 jobs
    if [ $((DELETED % 10)) -eq 0 ] && [ "$DELETED" -ne 0 ]; then
        sleep 0.1
    fi
done

echo ""
echo "=============================="
echo "✅ Deleted $DELETED/$COUNT trading dashboard jobs"

# Final count
REMAINING=$(openclaw cron list --json | jq '.jobs | length')
echo "Remaining total jobs: $REMAINING"

# List remaining job types
echo ""
echo "📋 Remaining job types:"
openclaw cron list --json | jq -r '.jobs[].name' | sort | uniq -c | sort -rn