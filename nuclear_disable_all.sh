#!/bin/bash

echo "🚨 NUCLEAR OPTION ACTIVATED: Disabling ALL 166 trading_dashboard_monitor jobs..."

# Get ALL job IDs for trading_dashboard_monitor
JOB_IDS=$(openclaw cron list --json | jq -r '.jobs[] | select(.enabled==true) | select(.name == "trading_dashboard_monitor") | .id')

# Count them
COUNT=$(echo "$JOB_IDS" | wc -l | tr -d ' ')
echo "Found $COUNT 'trading_dashboard_monitor' jobs to disable"

# Create a batch file
echo "$JOB_IDS" > job_ids.txt
echo "Job IDs saved to job_ids.txt"

# Disable them in batches of 20 to avoid overwhelming the system
BATCH_SIZE=20
BATCH_COUNT=0
TOTAL_DISABLED=0

echo ""
echo "Disabling in batches of $BATCH_SIZE..."

while read JOB_ID; do
    if [ -n "$JOB_ID" ]; then
        echo "Disabling: $JOB_ID"
        openclaw cron disable "$JOB_ID" > /dev/null 2>&1 &
        
        BATCH_COUNT=$((BATCH_COUNT + 1))
        TOTAL_DISABLED=$((TOTAL_DISABLED + 1))
        
        # Wait after each batch
        if [ $BATCH_COUNT -ge $BATCH_SIZE ]; then
            echo "  Waiting for batch to complete..."
            wait
            BATCH_COUNT=0
            echo "  Batch complete. Disabled $TOTAL_DISABLED so far..."
        fi
    fi
done < job_ids.txt

# Wait for any remaining jobs
wait

echo ""
echo "✅ Nuclear cleanup complete! Disabled $TOTAL_DISABLED jobs."

# Clean up
rm -f job_ids.txt

# Final verification
echo ""
echo "📋 FINAL VERIFICATION:"
REMAINING=$(openclaw cron list --json | jq '[.jobs[] | select(.enabled==true) | select(.name == "trading_dashboard_monitor")] | length')
echo "'trading_dashboard_monitor' jobs remaining: $REMAINING"

TOTAL_ENABLED=$(openclaw cron list --json | jq '[.jobs[] | select(.enabled==true)] | length')
echo "Total enabled jobs remaining: $TOTAL_ENABLED"