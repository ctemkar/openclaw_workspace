#!/bin/zsh
PORT_FILE="/Users/chetantemkar/.openclaw/workspace/app/.active_port"
LOG_FILE="/Users/chetantemkar/.openclaw/workspace/app/trading_bot_clean.log"

if [ -f "$LOG_FILE" ]; then
    tail -n 100 "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE"
fi

echo "--- Progress Monitor: $(date) ---"

if [ -f "$PORT_FILE" ]; then
    CURRENT_PORT=$(cat "$PORT_FILE")
    echo "Click to open REAL-TIME Dashboard:"
    echo "http://127.0.0.1:$CURRENT_PORT"
    echo "(Auto-refreshes every 10 seconds)"
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

# Check for current 26-crypto bot (FIXED VERSION)
if ps aux | grep -v grep | grep "real_26_crypto_trader_fixed.py" > /dev/null; then
    BOTS_RUNNING=$((BOTS_RUNNING + 1))
    BOT_LIST="$BOT_LIST real_26_crypto_trader_fixed.py"
fi

# Check for old bots (should not be running)
if ps aux | grep -v grep | grep -E "(fixed_bot_common|full_capital_bot|simple_real_trader|real_futures_trading_bot|fixed_futures_bot|enhanced_26_crypto)" > /dev/null; then
    BOTS_RUNNING=$((BOTS_RUNNING + 1))
    BOT_LIST="$BOT_LIST (OLD_BOT_STILL_RUNNING)"
fi

if [ $BOTS_RUNNING -eq 0 ]; then
    echo "BOT: [CRITICAL] NO TRADING BOTS RUNNING"
elif [ $BOTS_RUNNING -eq 1 ] && [[ "$BOT_LIST" == *"real_26_crypto_trader_fixed.py"* ]]; then
    echo "BOT: [OK] 1 BOT RUNNING:${BOT_LIST}"
    echo "   Strategy: 26-CRYPTO AGGRESSIVE (Gemini LONG, Binance SHORT)"
    echo "   Mode: AGGRESSIVE - 5% position size (reduced due to margin)"
    echo "   Capital: $393 Gemini LONG, $262 Binance SHORT"
    echo "   Status: FIXED VERSION - Prevents simultaneous LONG/SHORT"
    echo "   Hedge prevention: Active (skipping BTC, ETH, SOL, XRP, LINK)"
elif [[ "$BOT_LIST" == *"OLD_BOT_STILL_RUNNING"* ]]; then
    echo "BOT: [WARN] $BOTS_RUNNING BOTS RUNNING:${BOT_LIST}"
    echo "   Old bots still running - may conflict"
else
    echo "BOT: [UNKNOWN] $BOTS_RUNNING BOTS:${BOT_LIST}"
fi
