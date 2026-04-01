#!/bin/bash

echo "🔄 RESTARTING TRADING BOT WITH .env SUPPORT"
echo "=========================================="

# Kill existing bots
echo "Stopping existing trading bots..."
pkill -f "simple_26_crypto_bot.py" 2>/dev/null && echo "✅ Stopped running bots" || echo "⚠️  No bots running or couldn't stop"

# Wait a moment
sleep 2

# Start new bot with .env support
echo ""
echo "Starting updated bot with .env support..."
cd /Users/chetantemkar/.openclaw/workspace/app
nohup python3 simple_26_crypto_bot.py > bot_with_env.log 2>&1 &

# Check if started
sleep 3
if ps aux | grep -q "simple_26_crypto_bot.py" | grep -v grep; then
    echo "✅ Bot restarted with .env support"
    echo "📄 Logs: bot_with_env.log"
    
    # Show bot info
    echo ""
    echo "🔍 Bot process info:"
    ps aux | grep "simple_26_crypto_bot.py" | grep -v grep | tail -1 | awk '{print "PID: "$2", Started: "$9}'
    
    # Check log for .env message
    echo ""
    echo "📋 Checking log for .env confirmation..."
    if grep -q ".env SECURE VERSION" bot_with_env.log 2>/dev/null; then
        echo "✅ Bot running with .env secure version"
    else
        echo "⚠️  Could not confirm .env version in logs"
    fi
else
    echo "❌ Failed to start bot"
    echo "Check bot_with_env.log for errors"
fi

echo ""
echo "🎯 VERIFICATION STEPS:"
echo "1. Check bot_with_env.log for any errors"
echo "2. Verify trading is working normally"
echo "3. Monitor for any API key issues"
echo ""
echo "⚠️  IMPORTANT: The bot now uses .env file instead of secure_keys/"
echo "   Make sure .env has correct API keys"
echo "   Backup: simple_26_crypto_bot.py.backup (original version)"