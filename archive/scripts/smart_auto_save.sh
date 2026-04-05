#!/bin/bash

# SMART AUTO-SAVE SCRIPT
# Hourly commits + immediate commits for major changes

cd /Users/chetantemkar/.openclaw/workspace/app

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== SMART AUTO-SAVE ===${NC}"
echo "Time: $(date)"
echo "Directory: $(pwd)"

# Check if git repository
if [ ! -d .git ]; then
    echo -e "${RED}❌ Not a git repository${NC}"
    exit 1
fi

# Check for changes
CHANGES=$(git status --porcelain)
if [ -z "$CHANGES" ]; then
    echo -e "${GREEN}✅ No changes to commit${NC}"
    exit 0
fi

# Show what changed
echo -e "${YELLOW}📊 Changes detected:${NC}"
git status --short

# Check for MAJOR changes (immediate commit triggers)
MAJOR_CHANGE=false
MAJOR_REASON=""

# 1. New Python files (bots, scripts)
NEW_PYTHON_FILES=$(echo "$CHANGES" | grep '^??' | grep '\.py$' | wc -l)
if [ "$NEW_PYTHON_FILES" -gt 0 ]; then
    MAJOR_CHANGE=true
    MAJOR_REASON="$MAJOR_REASON +$NEW_PYTHON_FILES new Python files"
fi

# 2. Modified critical files
CRITICAL_FILES="llm_consensus_bot.py real_26_crypto_trader.py HEARTBEAT.md MEMORY.md SOUL.md AGENTS.md TOOLS.md"
for file in $CRITICAL_FILES; do
    if echo "$CHANGES" | grep -q "$file"; then
        MAJOR_CHANGE=true
        MAJOR_REASON="$MAJOR_REASON $file modified"
    fi
done

# 3. New or modified config files
CONFIG_FILES=$(echo "$CHANGES" | grep -E '\.(json|yaml|yml|toml|cfg|conf|ini)$' | wc -l)
if [ "$CONFIG_FILES" -gt 0 ]; then
    MAJOR_CHANGE=true
    MAJOR_REASON="$MAJOR_REASON +$CONFIG_FILES config files"
fi

# 4. Large number of changes (>10 files)
TOTAL_CHANGES=$(echo "$CHANGES" | wc -l)
if [ "$TOTAL_CHANGES" -gt 10 ]; then
    MAJOR_CHANGE=true
    MAJOR_REASON="$MAJOR_REASON $TOTAL_CHANGES total changes"
fi

# Determine commit type and message
if [ "$MAJOR_CHANGE" = true ]; then
    COMMIT_TYPE="🚨 MAJOR"
    COMMIT_MSG="🚨 MAJOR UPDATE: $(date) - $MAJOR_REASON"
    echo -e "${RED}⚠️ MAJOR CHANGE DETECTED: $MAJOR_REASON${NC}"
    echo -e "${RED}🚨 Immediate commit triggered${NC}"
else
    COMMIT_TYPE="🔄 REGULAR"
    COMMIT_MSG="🔄 Automated Update: $(date) - $TOTAL_CHANGES changes"
    echo -e "${GREEN}📝 Regular hourly commit${NC}"
fi

# Add all changes
echo -e "${YELLOW}📦 Staging changes...${NC}"
git add .

# Commit
echo -e "${YELLOW}💾 Committing: $COMMIT_MSG${NC}"
git commit -m "$COMMIT_MSG"

# Push
echo -e "${YELLOW}🚀 Pushing to remote...${NC}"
if git push; then
    echo -e "${GREEN}✅ Successfully pushed to remote${NC}"
    echo -e "${GREEN}📊 Commit Type: $COMMIT_TYPE${NC}"
    echo -e "${GREEN}📝 Message: $COMMIT_MSG${NC}"
    
    # Log to file
    echo "$(date) - $COMMIT_TYPE - $COMMIT_MSG" >> auto_save.log
else
    echo -e "${RED}❌ Failed to push to remote${NC}"
    echo -e "${YELLOW}⚠️ Changes committed locally but not pushed${NC}"
fi

echo -e "${BLUE}=== AUTO-SAVE COMPLETE ===${NC}"