#!/bin/bash
echo "🧹 FINAL CLEANUP - Keeping only essential files"
echo "================================================"

# Create essential files list
ESSENTIAL_FILES=(
    # Core identity files
    "SOUL.md"
    "USER.md" 
    "IDENTITY.md"
    "AGENTS.md"
    "TOOLS.md"
    "MEMORY.md"
    "HEARTBEAT.md"
    
    # Active bots
    "real_26_crypto_arbitrage_bot.py"
    "fast_progress_monitor.sh"
    
    # Security
    ".gitignore"
    ".env.example"
    "secure_keys/"
    
    # Memory system
    "memory/"
    
    # Cleanup script itself
    "final_cleanup.sh"
)

# Create keep directory
mkdir -p keep

echo "📁 Moving essential files to keep/ directory..."
for file in "${ESSENTIAL_FILES[@]}"; do
    if [ -e "$file" ]; then
        echo "  Keeping: $file"
        # For directories, copy contents
        if [ -d "$file" ]; then
            mkdir -p "keep/$file"
            cp -r "$file"/* "keep/$file/" 2>/dev/null || true
        else
            cp "$file" "keep/" 2>/dev/null || true
        fi
    fi
done

# Also keep the archive directory
if [ -d "archive" ]; then
    echo "  Keeping: archive/"
    cp -r "archive" "keep/" 2>/dev/null || true
fi

# Also keep logs directory
if [ -d "logs" ]; then
    echo "  Keeping: logs/"
    cp -r "logs" "keep/" 2>/dev/null || true
fi

echo ""
echo "📊 Summary:"
echo "  Essential files kept in: keep/"
echo "  Original files remain in project root"
echo ""
echo "To complete cleanup:"
echo "  1. Review keep/ directory"
echo "  2. Delete unnecessary files from project root"
echo "  3. Move essential files back if needed"
echo "================================================"