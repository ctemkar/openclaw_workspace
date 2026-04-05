#!/bin/bash

echo "========================================================"
echo "🚨 ULTIMATE CRON JOB CLEANUP SCRIPT"
echo "========================================================"
echo ""
echo "This script will DISABLE all trading_dashboard_monitor jobs"
echo "that are causing OpenRouter billing errors."
echo ""
echo "IMPORTANT: Run this in your TERMINAL, not through OpenClaw!"
echo ""
echo "Steps:"
echo "1. Open Terminal app"
echo "2. Copy the commands below"
echo "3. Paste and run in Terminal"
echo ""
echo "========================================================"
echo "📋 COPY THESE COMMANDS:"
echo "========================================================"
echo ""
echo "# Create cleanup script"
cat << 'EOF'
#!/bin/bash

echo "🚨 MASS DISABLE OF TRADING DASHBOARD JOBS"
echo "========================================"

# Get all trading dashboard job IDs
echo "Fetching job IDs..."
JOB_IDS=$(openclaw cron list --json | jq -r '.jobs[] | select(.name | test("trading_dashboard_monitor"; "i")) | .id')

COUNT=$(echo "$JOB_IDS" | wc -l | tr -d ' ')
echo "Found $COUNT trading_dashboard_monitor jobs"

if [ "$COUNT" -eq 0 ]; then
    echo "✅ No trading dashboard jobs found!"
    exit 0
fi

echo ""
echo "⚠️  WARNING: About to disable $COUNT cron jobs"
echo "This will stop all billing attempts to OpenRouter"
echo ""
read -p "Press Enter to continue, or Ctrl+C to cancel..."

echo ""
echo "Starting cleanup (this may take a few minutes)..."
DISABLED=0
ERRORS=0

# Create a temporary file with job IDs
TEMP_FILE=$(mktemp)
echo "$JOB_IDS" > "$TEMP_FILE"
TOTAL_LINES=$(wc -l < "$TEMP_FILE" | tr -d ' ')

echo "Processing $TOTAL_LINES jobs..."

# Process jobs in batches
BATCH_SIZE=20
BATCH_NUM=1

while read -r JOB_ID; do
    # Process batch
    if [ $(((DISABLED + ERRORS) % BATCH_SIZE)) -eq 0 ] && [ $((DISABLED + ERRORS)) -ne 0 ]; then
        echo "  Batch $BATCH_NUM complete: $((DISABLED + ERRORS))/$TOTAL_LINES"
        BATCH_NUM=$((BATCH_NUM + 1))
        sleep 1
    fi
    
    # Try to disable
    if openclaw cron disable "$JOB_ID" > /dev/null 2>&1; then
        DISABLED=$((DISABLED + 1))
        echo -n "."
    else
        ERRORS=$((ERRORS + 1))
        echo -n "X"
    fi
    
    # Small delay
    sleep 0.3
    
done < "$TEMP_FILE"

# Clean up temp file
rm "$TEMP_FILE"

echo ""
echo ""
echo "========================================"
echo "✅ CLEANUP COMPLETE!"
echo "========================================"
echo ""
echo "Results:"
echo "  Total jobs found: $COUNT"
echo "  Successfully disabled: $DISABLED"
echo "  Errors: $ERRORS"
echo ""
echo "Final status:"
echo "  Remaining enabled jobs:"
openclaw cron list --json | jq '[.jobs[] | select(.enabled == true)] | length'
echo ""
echo "🎉 Billing to OpenRouter should STOP immediately!"
echo ""
echo "Next steps:"
echo "1. Check OpenRouter billing dashboard"
echo "2. Request refund if applicable"
echo "3. Monitor that no new duplicate jobs appear"
EOF
echo ""
echo "========================================================"
echo "📝 INSTRUCTIONS:"
echo "========================================================"
echo ""
echo "1. Open Terminal app"
echo "2. Copy ALL the code above (from # Create cleanup script to EOF)"
echo "3. In Terminal, type: nano cleanup.sh"
echo "4. Paste the code, press Ctrl+O, Enter, then Ctrl+X"
echo "5. Run: chmod +x cleanup.sh"
echo "6. Run: ./cleanup.sh"
echo ""
echo "OR run this one-liner in Terminal:"
echo ""
echo 'openclaw cron list --json | jq -r '\''.jobs[] | select(.name | test("trading_dashboard_monitor"; "i")) | .id'\'' | while read JOB_ID; do echo "Disabling $JOB_ID"; openclaw cron disable "$JOB_ID"; sleep 0.5; done'
echo ""
echo "========================================================"
echo "⚠️  REMINDER: Run in TERMINAL, not through OpenClaw!"
echo "========================================================"