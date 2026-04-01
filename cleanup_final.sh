#!/bin/bash

echo "🚨 FINAL CLEANUP: Disabling ALL cron jobs..."
echo "We'll keep only: Progress Report, auto_save, progress_monitor, Crypto Trading LLM Bot"

# First, disable ALL jobs
echo ""
echo "Step 1: Disabling ALL jobs..."
openclaw cron list --json | jq -r '.jobs[] | select(.enabled==true) | .id' | while read JOB_ID; do
    echo "  Disabling: $JOB_ID"
    openclaw cron disable "$JOB_ID"
done

echo ""
echo "✅ All jobs have been disabled!"
echo ""
echo "Step 2: Re-enabling essential jobs..."

# List of essential job names to keep
ESSENTIAL_JOBS=("Progress Report" "auto_save" "progress_monitor" "Crypto Trading LLM Bot")

# Get all jobs (including disabled ones)
ALL_JOBS=$(openclaw cron list --json)

for ESSENTIAL_JOB in "${ESSENTIAL_JOBS[@]}"; do
    echo "  Looking for: $ESSENTIAL_JOB"
    JOB_ID=$(echo "$ALL_JOBS" | jq -r ".jobs[] | select(.name | contains(\"$ESSENTIAL_JOB\")) | .id" | head -1)
    
    if [ ! -z "$JOB_ID" ]; then
        echo "    Found: $JOB_ID - Re-enabling..."
        openclaw cron enable "$JOB_ID"
    else
        echo "    Not found: $ESSENTIAL_JOB"
    fi
done

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📋 Final enabled jobs:"
openclaw cron list --json | jq -r '.jobs[] | select(.enabled==true) | "  - \(.name) (\(.id))"'