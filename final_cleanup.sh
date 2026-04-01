#!/bin/bash

echo "🚨 FINAL CLEANUP: Disabling ALL cron jobs except essential ones..."
echo "Essential jobs: Progress Report, auto_save, progress_monitor, Crypto Trading LLM Bot"

# First, disable ALL jobs
echo ""
echo "Step 1: Disabling ALL jobs..."
openclaw cron list --json | jq -r '.jobs[] | select(.enabled==true) | .id' | while read JOB_ID; do
    echo "  Disabling job ID: $JOB_ID"
    openclaw cron disable "$JOB_ID"
done

echo ""
echo "Step 2: Re-enabling essential jobs..."

# Re-enable Progress Report
echo "  Looking for Progress Report job..."
PROGRESS_JOB=$(openclaw cron list --json | jq -r '.jobs[] | select(.name | contains("Progress Report")) | .id' | head -1)
if [ ! -z "$PROGRESS_JOB" ]; then
    echo "  Re-enabling Progress Report: $PROGRESS_JOB"
    openclaw cron enable "$PROGRESS_JOB"
fi

# Re-enable auto_save
echo "  Looking for auto_save job..."
AUTO_SAVE_JOB=$(openclaw cron list --json | jq -r '.jobs[] | select(.name | contains("auto_save")) | .id' | head -1)
if [ ! -z "$AUTO_SAVE_JOB" ]; then
    echo "  Re-enabling auto_save: $AUTO_SAVE_JOB"
    openclaw cron enable "$AUTO_SAVE_JOB"
fi

# Re-enable progress_monitor
echo "  Looking for progress_monitor job..."
PROGRESS_MONITOR_JOB=$(openclaw cron list --json | jq -r '.jobs[] | select(.name | contains("progress_monitor")) | .id' | head -1)
if [ ! -z "$PROGRESS_MONITOR_JOB" ]; then
    echo "  Re-enabling progress_monitor: $PROGRESS_MONITOR_JOB"
    openclaw cron enable "$PROGRESS_MONITOR_JOB"
fi

# Re-enable Crypto Trading LLM Bot
echo "  Looking for Crypto Trading LLM Bot job..."
CRYPTO_BOT_JOB=$(openclaw cron list --json | jq -r '.jobs[] | select(.name | contains("Crypto Trading LLM Bot")) | .id' | head -1)
if [ ! -z "$CRYPTO_BOT_JOB" ]; then
    echo "  Re-enabling Crypto Trading LLM Bot: $CRYPTO_BOT_JOB"
    openclaw cron enable "$CRYPTO_BOT_JOB"
fi

echo ""
echo "✅ CLEANUP COMPLETE!"
echo ""
echo "📋 Final enabled jobs:"
openclaw cron list --json | jq -r '.jobs[] | select(.enabled==true) | "  - \(.name) (\(.id))"'