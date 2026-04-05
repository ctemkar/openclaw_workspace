#!/bin/bash

echo "🚨 CRITICAL CLEANUP: Disabling ALL duplicate cron jobs..."
echo "This will keep only essential jobs (Progress Report, auto_save, progress_monitor)"

# Get all job IDs
ALL_JOBS=$(openclaw cron list --json | jq -r '.jobs[] | .id')

ESSENTIAL_COUNT=0
DISABLED_COUNT=0

for JOB_ID in $ALL_JOBS; do
    # Get job details
    JOB_DETAILS=$(openclaw cron list --json | jq -r ".jobs[] | select(.id==\"$JOB_ID\")")
    NAME=$(echo "$JOB_DETAILS" | jq -r '.name')
    ENABLED=$(echo "$JOB_DETAILS" | jq -r '.enabled')
    
    # Check if it's an essential job
    if [[ "$NAME" == *"Progress Report"* ]] || \
       [[ "$NAME" == *"auto_save"* ]] || \
       [[ "$NAME" == *"progress_monitor"* ]] || \
       [[ "$NAME" == *"Crypto Trading LLM Bot"* ]]; then
        echo "✅ Keeping essential job: $NAME"
        ((ESSENTIAL_COUNT++))
    else
        if [[ "$ENABLED" == "true" ]]; then
            echo "❌ Disabling duplicate job: $NAME"
            openclaw cron update "$JOB_ID" --enabled false
            ((DISABLED_COUNT++))
        else
            echo "⚠️  Already disabled: $NAME"
        fi
    fi
done

echo ""
echo "📊 CLEANUP SUMMARY:"
echo "✅ Kept $ESSENTIAL_COUNT essential jobs"
echo "❌ Disabled $DISABLED_COUNT duplicate jobs"
echo ""
echo "Remaining enabled jobs:"
openclaw cron list --json | jq -r '.jobs[] | select(.enabled==true) | "  - \(.name) (\(.id))"'