#!/bin/bash

# Smart Auto-Save Script
# Commits and pushes all changes, checks for major changes

set -e

cd /Users/chetantemkar/.openclaw/workspace/app

echo "=== Smart Auto-Save - $(date) ==="

# Check git status
echo "Checking git status..."
git status --porcelain > /tmp/git_changes.txt
CHANGES_COUNT=$(wc -l < /tmp/git_changes.txt)

if [ "$CHANGES_COUNT" -eq 0 ]; then
    echo "No changes to commit."
    echo "=== Auto-Save Complete ==="
    exit 0
fi

# Analyze changes
echo "Analyzing $CHANGES_COUNT changes..."

# Count file types
PYTHON_FILES=$(grep -c "\.py$" /tmp/git_changes.txt || true)
CONFIG_FILES=$(grep -c "\.json$\|\.yml$\|\.yaml$\|\.env$\|\.toml$" /tmp/git_changes.txt || true)
MD_FILES=$(grep -c "\.md$" /tmp/git_changes.txt || true)
SH_FILES=$(grep -c "\.sh$" /tmp/git_changes.txt || true)
LOG_FILES=$(grep -c "\.log$" /tmp/git_changes.txt || true)

# Check for major changes (based on previous pattern)
MAJOR_CHANGE=false
if [ "$PYTHON_FILES" -ge 3 ] || [ "$CONFIG_FILES" -ge 2 ] || [ "$MD_FILES" -ge 1 ]; then
    MAJOR_CHANGE=true
    echo "🚨 MAJOR CHANGE DETECTED:"
    echo "  - Python files: $PYTHON_FILES"
    echo "  - Config files: $CONFIG_FILES"
    echo "  - Markdown files: $MD_FILES"
    echo "  - Shell scripts: $SH_FILES"
    echo "  - Log files: $LOG_FILES"
else
    echo "Minor changes detected:"
    echo "  - Total changes: $CHANGES_COUNT"
fi

# Add all changes
echo "Adding changes to git..."
git add -A

# Create commit message
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S %z')
if [ "$MAJOR_CHANGE" = true ]; then
    COMMIT_MSG="🚨 MAJOR UPDATE: $TIMESTAMP - + $PYTHON_FILES new Python files + $CONFIG_FILES config files + $MD_FILES docs"
else
    COMMIT_MSG="Auto-save: $TIMESTAMP - $CHANGES_COUNT changes"
fi

echo "Committing: $COMMIT_MSG"
git commit -m "$COMMIT_MSG"

# Push to remote
echo "Pushing to remote..."
git push origin main

# Log the auto-save
if [ "$MAJOR_CHANGE" = true ]; then
    echo "$(date) - 🚨 MAJOR - $COMMIT_MSG $CHANGES_COUNT total changes" >> auto_save.log
else
    echo "$(date) - Auto-save: $CHANGES_COUNT changes" >> auto_save.log
fi

echo "=== Auto-Save Complete ==="
echo "Summary:"
echo "  - Changes committed: $CHANGES_COUNT"
echo "  - Python files: $PYTHON_FILES"
echo "  - Config files: $CONFIG_FILES"
echo "  - Major change: $MAJOR_CHANGE"

if [ "$MAJOR_CHANGE" = true ]; then
    echo ""
    echo "⚠️  MAJOR CHANGES NEED ATTENTION!"
    echo "Recent significant updates to Python code, configs, or documentation."
    echo "Please review the changes when possible."
fi