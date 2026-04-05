#!/bin/bash

# Auto-Save Script
# Wrapper for smart_auto_save.sh with memory updates

set -e

cd /Users/chetantemkar/.openclaw/workspace/app

echo "=== Auto-Save with Memory Updates - $(date) ==="

# First run the smart auto-save
./smart_auto_save.sh

# Update memory files if they exist
echo ""
echo "=== Updating Memory Files ==="

# Update HEARTBEAT.md with current timestamp
if [ -f "HEARTBEAT.md" ]; then
    echo "Updating HEARTBEAT.md..."
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S %z')
    echo "Last auto-save: $TIMESTAMP" > HEARTBEAT.md
    echo "System is running and auto-saving changes." >> HEARTBEAT.md
    echo "Next auto-save scheduled for every hour." >> HEARTBEAT.md
    echo "" >> HEARTBEAT.md
    echo "Recent auto-save log:" >> HEARTBEAT.md
    tail -5 auto_save.log 2>/dev/null | sed 's/^/  /' >> HEARTBEAT.md || true
fi

# Update MEMORY.md if it exists
if [ -f "MEMORY.md" ]; then
    echo "Updating MEMORY.md..."
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S %z')
    # Check if MEMORY.md has a timestamp section
    if grep -q "Last updated:" MEMORY.md; then
        sed -i '' "s/Last updated:.*/Last updated: $TIMESTAMP/" MEMORY.md
    else
        echo "" >> MEMORY.md
        echo "---" >> MEMORY.md
        echo "Last updated: $TIMESTAMP" >> MEMORY.md
    fi
fi

echo ""
echo "=== Memory Update Complete ==="
echo "Auto-save with memory updates completed at $(date)"