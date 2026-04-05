#!/bin/bash

# Auto Git Commit Script
# This script automatically commits workspace changes with descriptive messages

echo "=== Auto Git Commit ==="
echo "Current time: $(date)"
echo ""

# Check git status first
echo "Checking git status..."
git status --short

# Add all changes
echo ""
echo "Adding all changes..."
git add -A

# Create descriptive commit message based on file types
echo ""
echo "Creating commit message..."

# Analyze what types of files were changed
MEMORY_FILES=""
PERSONALITY_FILES=""
SCRIPT_FILES=""
DOC_FILES=""
OTHER_FILES=""

# Check for memory-related files
if git status --porcelain | grep -E "(AGENTS\.md|SOUL\.md|USER\.md|IDENTITY\.md|HEARTBEAT\.md)" > /dev/null; then
    MEMORY_FILES="memory/personality"
fi

# Check for script files
if git status --porcelain | grep -E "\.(sh|py|js|ts)$" > /dev/null; then
    SCRIPT_FILES="scripts"
fi

# Check for documentation files
if git status --porcelain | grep -E "\.(md|txt|json)$" > /dev/null; then
    DOC_FILES="documentation"
fi

# Check for log files
if git status --porcelain | grep -E "\.log$" > /dev/null; then
    OTHER_FILES="logs"
fi

# Build commit message components
COMPONENTS=()
[ -n "$MEMORY_FILES" ] && COMPONENTS+=("$MEMORY_FILES")
[ -n "$SCRIPT_FILES" ] && COMPONENTS+=("$SCRIPT_FILES")
[ -n "$DOC_FILES" ] && COMPONENTS+=("$DOC_FILES")
[ -n "$OTHER_FILES" ] && COMPONENTS+=("$OTHER_FILES")

if [ ${#COMPONENTS[@]} -eq 0 ]; then
    # If no specific types detected, check for any changes
    if git status --porcelain | grep -q "^"; then
        COMPONENTS=("various files")
    else
        echo "No changes to commit."
        exit 0
    fi
fi

COMMIT_MESSAGE="Auto-commit: Updated $(IFS=,; echo "${COMPONENTS[*]}") - $(date '+%Y-%m-%d %H:%M:%S')"

echo "Commit message: $COMMIT_MESSAGE"
echo ""

# Commit changes
echo "Committing changes..."
git commit -m "$COMMIT_MESSAGE"

# Show commit result
echo ""
echo "Commit completed:"
git log --oneline -1

# Optional: push to remote
# echo ""
# echo "Pushing to remote..."
# git push

echo ""
echo "=== Auto Git Commit Complete ==="