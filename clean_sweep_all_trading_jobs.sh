#!/bin/bash

echo "🚨 CLEAN SWEEP: Disabling ALL remaining trading-related jobs..."

# Define trading-related keywords
TRADING_KEYWORDS="trading Trading TRADING crypto Crypto CRYPTO dashboard Dashboard DASHBOARD monitor Monitor MONITOR log Log LOG"

# Get ALL enabled jobs
echo "Getting all enabled jobs..."
openclaw cron list --json > all_jobs.json

# Count total enabled
TOTAL_ENABLED=$(jq '[.jobs[] | select(.enabled==true)] | length' all_jobs.json)
echo "Total enabled jobs: $TOTAL_ENABLED"

# Identify trading jobs to disable
echo ""
echo "Identifying trading-related jobs to disable..."
TRADING_JOBS=$(jq -r '.jobs[] | select(.enabled==true) | select(
    (.name | test("trading|Trading|TRADING|crypto|Crypto|CRYPTO|dashboard|Dashboard|DASHBOARD|monitor|Monitor|MONITOR|log|Log|LOG")) or
    (.payload.message? // "" | test("trading|Trading|TRADING|crypto|Crypto|CRYPTO|dashboard|Dashboard|DASHBOARD|monitor|Monitor|MONITOR|log|Log|LOG"))
) | "\(.name) - \(.id)"' all_jobs.json)

# Count trading jobs
TRADING_COUNT=$(echo "$TRADING_JOBS" | wc -l | tr -d ' ')
echo "Found $TRADING_COUNT trading-related jobs to disable"

# List them
echo ""
echo "Trading jobs to disable:"
echo "$TRADING_JOBS" | head -20
if [ $TRADING_COUNT -gt 20 ]; then
    echo "... and $((TRADING_COUNT - 20)) more"
fi

# Get job IDs for trading jobs
TRADING_JOB_IDS=$(jq -r '.jobs[] | select(.enabled==true) | select(
    (.name | test("trading|Trading|TRADING|crypto|Crypto|CRYPTO|dashboard|Dashboard|DASHBOARD|monitor|Monitor|MONITOR|log|Log|LOG")) or
    (.payload.message? // "" | test("trading|Trading|TRADING|crypto|Crypto|CRYPTO|dashboard|Dashboard|DASHBOARD|monitor|Monitor|MONITOR|log|Log|LOG"))
) | .id' all_jobs.json)

# Save to file
echo "$TRADING_JOB_IDS" > trading_job_ids.txt
echo "Saved $TRADING_COUNT job IDs to trading_job_ids.txt"

# Disable them in batches
echo ""
echo "Disabling ALL $TRADING_COUNT trading-related jobs..."
BATCH_SIZE=20
BATCH_COUNT=0
TOTAL_DISABLED=0

while read JOB_ID; do
    if [ -n "$JOB_ID" ]; then
        echo "Disabling job ID: $JOB_ID"
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
done < trading_job_ids.txt

# Wait for any remaining jobs
wait

echo ""
echo "✅ Clean sweep complete! Disabled $TOTAL_DISABLED trading-related jobs."

# Clean up
rm -f all_jobs.json trading_job_ids.txt

# Final verification
echo ""
echo "📋 FINAL VERIFICATION:"

# Get remaining enabled jobs
openclaw cron list --json > remaining_jobs.json

# Count remaining
REMAINING_TOTAL=$(jq '[.jobs[] | select(.enabled==true)] | length' remaining_jobs.json)
echo "Total enabled jobs remaining: $REMAINING_TOTAL"

# List remaining jobs
echo ""
echo "Remaining enabled jobs:"
jq -r '.jobs[] | select(.enabled==true) | "  - \(.name)"' remaining_jobs.json | sort | uniq -c | sort -nr

# Clean up
rm -f remaining_jobs.json

echo ""
echo "🎯 Only essential monitoring jobs should remain (Progress Report, etc.)"