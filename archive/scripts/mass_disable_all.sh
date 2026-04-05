#!/bin/bash

echo "🚨 NUCLEAR OPTION: Disabling ALL cron jobs except essential ones..."
echo "This will keep only: Progress Report, auto_save, progress_monitor, Crypto Trading LLM Bot"

# Get all job IDs
ALL_JOBS=$(openclaw cron list --json | jq -r '.jobs[] | .id')

ESSENTIAL_COUNT=0
DISABLED_COUNT=0

for JOB_ID in $ALL_JOBS; do
    # Get job name
    JOB_NAME=$(openclaw cron list --json | jq -r ".jobs[] | select(.id==\"$JOB_ID\") | .name")
    
    # Check if it's an essential job
    if [[ "$JOB_NAME" == *"Progress Report"* ]] || \
       [[ "$JOB_NAME" == *"auto_save"* ]] || \
       [[ "$JOB_NAME" == *"progress_monitor"* ]] || \
       [[ "$JOB_NAME" == *"Crypto Trading LLM Bot"* ]]; then
        echo "✅ Keeping essential job: $JOB_NAME"
        ((ESSENTIAL_COUNT++))
    else
        echo "❌ Disabling: $JOB_NAME"
        openclaw cron disable "$JOB_ID"
        ((DISABLED_COUNT++))
    fi
done

echo ""
echo "📊 CLEANUP COMPLETE:"
echo "✅ Kept $ESSENTIAL_COUNT essential jobs"
echo "❌ Disabled $DISABLED_COUNT duplicate jobs"
echo ""
echo "Remaining enabled jobs:"
openclaw cron list --json | jq -r '.jobs[] | select(.enabled==true) | "  - \(.name)"'