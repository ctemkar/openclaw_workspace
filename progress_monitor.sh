#!/bin/zsh
PORT_FILE="/Users/chetantemkar/.openclaw/workspace/app/.active_port"
LOG_FILE="/Users/chetantemkar/.openclaw/workspace/app/trading_bot_clean.log"

if [ -f "$LOG_FILE" ]; then
    tail -n 100 "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE"
fi

echo "--- Progress Monitor: $(date) ---"

if [ -f "$PORT_FILE" ]; then
    CURRENT_PORT=$(cat "$PORT_FILE")
    echo "Click to open Dashboard:"
    echo "http://127.0.0.1:$CURRENT_PORT"
    echo ""
    
    if ! curl -s "http://127.0.0.1:$CURRENT_PORT" > /dev/null; then
        echo "STATUS: [WARN] API is DOWN"
    else
        echo "STATUS: [OK] API is UP"
    fi
else
    echo "STATUS: [ERROR] Port file missing"
fi

# Check for actual running trading bots
BOTS_RUNNING=0
BOT_LIST=""

if ps aux | grep -v grep | grep -E "(simple_real_trader|real_futures_trading_bot|fixed_futures_bot)" > /dev/null; then
    BOTS_RUNNING=$((BOTS_RUNNING + 1))
    BOT_LIST="$BOT_LIST simple_real_trader.py"
fi

if ps aux | grep -v grep | grep "real_futures_trading_bot.py" > /dev/null; then
    BOTS_RUNNING=$((BOTS_RUNNING + 1))
    BOT_LIST="$BOT_LIST real_futures_trading_bot.py"
fi

if ps aux | grep -v grep | grep "fixed_futures_bot.py" > /dev/null; then
    BOTS_RUNNING=$((BOTS_RUNNING + 1))
    BOT_LIST="$BOT_LIST fixed_futures_bot.py"
fi

if [ $BOTS_RUNNING -eq 0 ]; then
    echo "BOT: [CRITICAL] NO TRADING BOTS RUNNING"
elif [ $BOTS_RUNNING -eq 1 ]; then
    echo "BOT: [WARN] ONLY 1 BOT RUNNING:${BOT_LIST}"
else
    echo "BOT: [OK] $BOTS_RUNNING BOTS RUNNING:${BOT_LIST}"
fi
