#!/bin/bash

echo "🔐 SIMPLE SECURITY FIX FOR EXPOSED API KEYS"
echo "=========================================="

# 1. First, let's see what we're dealing with
echo ""
echo "📊 SCANNING FOR EXPOSED KEYS..."
TOTAL_FILES=$(find . -name "*.py" -type f | xargs grep -l "api_key\|API_KEY\|secret\|SECRET" 2>/dev/null | wc -l)
echo "Found $TOTAL_FILES files with potential API key exposure"

echo ""
echo "🔍 SAMPLE OF EXPOSED KEYS (first 5 files):"
find . -name "*.py" -type f | xargs grep -l "api_key\|API_KEY\|secret\|SECRET" 2>/dev/null | head -5 | while read f; do
    echo "  File: $f"
    grep -n "api_key\|API_KEY\|secret\|SECRET" "$f" | head -2 | sed 's/^/    /'
done

echo ""
echo "🚨 CRITICAL ACTION PLAN:"
echo "1. CREATE SECURE .env FILE"
echo "2. MOVE ALL KEYS TO .env"
echo "3. UPDATE CODE TO USE os.getenv()"
echo "4. REMOVE HARDCODED KEYS"

echo ""
echo "📝 STEP 1: Check current .env file"
if [ -f .env ]; then
    echo "✅ .env file exists"
    echo "Current keys in .env:"
    grep -E "API|SECRET|KEY" .env | head -10
else
    echo "❌ No .env file found"
    echo "Creating .env template..."
    cat > .env.template << 'EOF'
# CRITICAL: API KEYS - DO NOT COMMIT TO GIT!
# Move your actual keys here and rename to .env

# Gemini Exchange
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_API_SECRET=your_actual_gemini_api_secret_here

# Binance Exchange  
BINANCE_API_KEY=your_actual_binance_api_key_here
BINANCE_API_SECRET=your_actual_binance_api_secret_here

# OpenRouter (if used)
OPENROUTER_API_KEY=your_actual_openrouter_api_key_here

# Trading Configuration
TRADING_CAPITAL=1000
STOP_LOSS_PERCENT=5
TAKE_PROFIT_PERCENT=10
EOF
    echo "✅ Created .env.template"
    echo "⚠️  IMPORTANT: Copy .env.template to .env and add your real keys"
fi

echo ""
echo "📝 STEP 2: Manual Fix Instructions"
echo "For EACH file with exposed keys, you need to:"
echo "1. Find the hardcoded key: grep -n 'api_key' filename.py"
echo "2. Replace with: api_key = os.getenv('GEMINI_API_KEY')"
echo "3. Add at top of file: import os"
echo ""
echo "📝 STEP 3: Quick Test Script"
cat > test_env_keys.py << 'EOF'
#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔐 Testing Environment Variables")
print("=" * 40)

keys_to_check = [
    'GEMINI_API_KEY',
    'GEMINI_API_SECRET', 
    'BINANCE_API_KEY',
    'BINANCE_API_SECRET',
    'OPENROUTER_API_KEY'
]

for key in keys_to_check:
    value = os.getenv(key)
    if value:
        print(f"✅ {key}: {value[:10]}... (length: {len(value)})")
    else:
        print(f"❌ {key}: NOT SET")

print("\n⚠️  If keys are missing, add them to .env file")
print("⚠️  If .env doesn't exist, create it from .env.template")
EOF

chmod +x test_env_keys.py
echo "✅ Created test script: python3 test_env_keys.py"

echo ""
echo "📝 STEP 4: Find Files That Need Fixing"
echo "Run this command to see all files with exposed keys:"
echo "  grep -r 'api_key\\|API_KEY\\|secret\\|SECRET' . --include='*.py' --include='*.sh' | grep -v '.env' | head -20"

echo ""
echo "📝 STEP 5: Create Backup Before Making Changes"
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "✅ Created backup directory: $BACKUP_DIR"
echo "   To backup: cp *.py \"$BACKUP_DIR/\""

echo ""
echo "🎯 RECOMMENDED APPROACH:"
echo "1. Run: python3 test_env_keys.py (check .env works)"
echo "2. Pick ONE important file to fix first"
echo "3. Test that file still works after fix"
echo "4. Repeat for other files"
echo ""
echo "⚠️  WARNING: Fixing 1,006 files will take time"
echo "    Start with the most critical trading bots first"