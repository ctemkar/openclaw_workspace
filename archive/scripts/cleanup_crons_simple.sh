#!/bin/bash

echo "🚨 MASSIVE CLEANUP: Disabling ALL duplicate cron jobs..."

# First, let's see how many jobs we have
TOTAL_JOBS=$(openclaw cron list --json | jq '.jobs | length')
echo "Total cron jobs found: $TOTAL_JOBS"

# Disable ALL jobs first (we'll re-enable essentials later)
echo "Disabling ALL jobs..."
openclaw cron list --json | jq -r '.jobs[].id' | while read JOB_ID; do
    echo "Disabling job: $JOB_ID"
    openclaw cron disable "$JOB_ID"
done

echo ""
echo "✅ ALL cron jobs have been disabled"
echo ""
echo "Now let's check what we have left..."
openclaw cron list --json | jq -r '.jobs[] | "\(.name) - \(.id) - Enabled: \(.enabled)"' | head -20