#!/bin/zsh
# Check if 26-crypto trading bot is running and alert if stopped

BOT_PID=$(ps aux | grep "real_26_crypto_trader.py" | grep -v grep | awk '{print $2}')

if [ -z "$BOT_PID" ]; then
    echo "🚨 ALERT: TRADING BOT STOPPED"
    echo "Time: $(date)"
    echo "Bot: real_26_crypto_trader.py"
    echo "Status: NOT RUNNING"
    echo "Action needed: Restart bot immediately"
    
    # Check when it last ran
    if [ -f "bot_common.log" ]; then
        LAST_LOG=$(tail -1 bot_common.log | cut -d' ' -f1-3)
        echo "Last activity in logs: $LAST_LOG"
    fi
    
    # Check for crash logs
    if [ -f "26_crypto_bot.log" ]; then
        LAST_ERROR=$(grep -i "error\|exception\|crash" 26_crypto_bot.log | tail -1)
        if [ ! -z "$LAST_ERROR" ]; then
            echo "Last error detected: $LAST_ERROR"
        fi
    fi
    
    exit 1
else
    echo "✅ Trading bot running (PID: $BOT_PID)"
    echo "Time: $(date)"
    echo "Bot: real_26_crypto_trader.py"
    
    # Check bot uptime
    START_TIME=$(ps -o lstart= -p $BOT_PID)
    echo "Started: $START_TIME"
    
    # Check recent logs
    if [ -f "bot_common.log" ]; then
        LAST_ACTIVITY=$(tail -5 bot_common.log | grep -E "CYCLE|opportunit|ERROR" | tail -1)
        if [ ! -z "$LAST_ACTIVITY" ]; then
            echo "Last activity: $LAST_ACTIVITY"
        fi
    fi
    
    exit 0
fi