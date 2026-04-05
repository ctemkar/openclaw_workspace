#!/bin/bash

echo "🚨 DISABLING ALL OPENROUTER CRON JOBS"
echo "======================================"

# Get all cron jobs
JOBS=$(openclaw cron list --json | jq -r '.jobs[] | select(.payload.model | contains("openrouter") or contains("gemini")) | .id')

COUNT=0
for JOB_ID in $JOBS; do
    echo "Disabling job: $JOB_ID"
    openclaw cron update "$JOB_ID" --enabled false
    ((COUNT++))
done

echo "======================================"
echo "✅ Disabled $COUNT OpenRouter cron jobs"
echo ""
echo "💰 ESTIMATED MONTHLY SAVINGS:"
echo "   Assuming 100 jobs × 12 runs/hour = 1,200 runs/hour"
echo "   ~$0.18-$0.36 PER HOUR"
echo "   ~$4.32-$8.64 PER DAY"
echo "   ~$129.60-$259.20 PER MONTH"
echo ""
echo "🎯 NEXT: Check OpenRouter billing dashboard"