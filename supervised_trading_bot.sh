#!/bin/bash
# SUPERVISED TRADING BOT - AUTO-RESTART ON FAILURE

cd /Users/chetantemkar/.openclaw/workspace/app

echo "🚀 SUPERVISED TRADING BOT STARTING AT $(date)"
echo "=============================================="

# Create restart log
RESTART_LOG="trading_bot_restart.log"
echo "Supervised bot started at $(date)" >> "$RESTART_LOG"

# Counter for restarts
RESTART_COUNT=0
MAX_RESTARTS=100

while [ $RESTART_COUNT -lt $MAX_RESTARTS ]; do
    RESTART_COUNT=$((RESTART_COUNT + 1))
    
    echo ""
    echo "🔄 STARTING TRADING BOT (Attempt $RESTART_COUNT) at $(date)"
    echo "=============================================="
    
    # Start the bot and capture output
    python3 real_26_crypto_trader.py 2>&1 | tee -a "trading_bot_run_$(date +%Y%m%d_%H%M%S).log"
    
    EXIT_CODE=$?
    echo ""
    echo "⚠️ TRADING BOT STOPPED with exit code: $EXIT_CODE at $(date)"
    echo "Restarting in 10 seconds..."
    
    # Log the restart
    echo "Restart $RESTART_COUNT at $(date) - Exit code: $EXIT_CODE" >> "$RESTART_LOG"
    
    # Wait before restarting
    sleep 10
    
    # Check if we should continue
    if [ $RESTART_COUNT -ge $MAX_RESTARTS ]; then
        echo "❌ MAXIMUM RESTARTS REACHED ($MAX_RESTARTS)"
        echo "Please check the bot configuration."
        break
    fi
done

echo ""
echo "🛑 SUPERVISED BOT STOPPED AT $(date)"
echo "Total restarts: $RESTART_COUNT"