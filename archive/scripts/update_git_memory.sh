#!/bin/bash
# Git commit with memory context

echo "="
echo "📝 GIT COMMIT WITH MEMORY CONTEXT"
echo "="

# Get current timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Create commit message with context
COMMIT_MESSAGE="[MEMORY] Update memory system and current state - $TIMESTAMP

CRITICAL CONTEXT:
- System reset to reality after dashboard showed fictional data
- P&L now calculated correctly using actual entry prices
- Gemini-only bot running with $563 cash
- All dashboards showing accurate data with real P&L
- Total P&L: -$14.29 (ETH -$12.31, SOL -$1.98)

CHANGES:
- Created memory system for context retention
- Fixed dashboard P&L calculations
- Updated trades.json with real entry prices
- Added memory.json for persistent context

LESSONS:
- Always verify dashboard data against exchange APIs
- Store important memories in git for context
- P&L requires actual entry prices, not current prices
- User wants proactive problem identification"

# Add all files
git add .

# Commit with context
git commit -m "$COMMIT_MESSAGE"

# Push to remote
git push origin main

echo ""
echo "✅ Git commit completed with memory context"
echo "📄 Commit includes memory.json for persistence"