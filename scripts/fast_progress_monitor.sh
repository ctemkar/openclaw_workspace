#!/bin/bash
echo "=== FAST PROGRESS MONITOR - $(date '+%Y-%m-%d %H:%M:%S %Z') ==="
echo ""

# Check if practical monitor bot is running
if ps aux | grep -v grep | grep -q "practical_monitor_bot.py"; then
    BOT_PID=$(ps aux | grep "practical_monitor_bot.py" | grep -v grep | awk '{print $2}')
    echo "[OK] PRACTICAL MONITOR BOT RUNNING (PID: $BOT_PID)"
    
    # Get the VERY LAST trade from the log
    if [ -f "practical_profits.log" ]; then
        LAST_TRADE=$(tail -1 practical_profits.log 2>/dev/null)
        if [ -n "$LAST_TRADE" ]; then
            LAST_PROFIT=$(echo "$LAST_TRADE" | awk -F'Profit: \\$' '{print $2}' | awk '{print $1}')
            LAST_TOTAL=$(echo "$LAST_TRADE" | awk -F'Total: \\$' '{print $2}')
            LAST_TIME=$(echo "$LAST_TRADE" | awk '{print $1" "$2}')
            
            echo "[CHART] LATEST TRADE:"
            echo "   Time: $LAST_TIME"
            echo "   Profit: \$$LAST_PROFIT"
            echo "   Total: \$$LAST_TOTAL"
            
            # Count trades TODAY (April 5) - REAL count
            TODAY=$(date '+%Y-%m-%d')
            TODAY_TRADES=$(grep "^$TODAY" practical_profits.log 2>/dev/null | wc -l)
            if [ "$TODAY_TRADES" -gt 0 ]; then
                # Get actual trade count from last entry
                LAST_TRADE_COUNT=$(echo "$LAST_TRADE" | awk -F'Trades: ' '{print $2}' | awk '{print $1}')
                echo "   Trades today: $LAST_TRADE_COUNT (REAL count from log)"
                echo "   Profit today: \$$LAST_TOTAL"
            else
                echo "   No trades today yet"
            fi
        else
            echo "   No trades in log"
        fi
    fi
    
    # Get latest monitor status
    if [ -f "practical_monitor.log" ]; then
        LAST_CHECK=$(tail -5 practical_monitor.log 2>/dev/null | grep "MARKET CHECK" | tail -1)
        if [ -n "$LAST_CHECK" ]; then
            LAST_TIME=$(echo "$LAST_CHECK" | awk '{print $1" "$2}')
            BINANCE_PRICE=$(tail -10 practical_monitor.log 2>/dev/null | grep "Binance MANA/USDT" | tail -1 | awk -F': \\$' '{print $2}')
            GEMINI_PRICE=$(tail -10 practical_monitor.log 2>/dev/null | grep "Gemini MANA/USD" | tail -1 | awk -F': \\$' '{print $2}')
            SPREAD=$(tail -10 practical_monitor.log 2>/dev/null | grep "Spread:" | tail -1 | awk '{print $2}')
            
            echo "[MONITOR] LATEST CHECK:"
            echo "   Time: $LAST_TIME"
            echo "   Binance: \$$BINANCE_PRICE"
            echo "   Gemini: \$$GEMINI_PRICE"
            echo "   Spread: $SPREAD%"
            
            # Check if spread is profitable
            SPREAD_NUM=$(echo "$SPREAD" | sed 's/%//')
            if (( $(echo "$SPREAD_NUM >= 0.5" | bc -l) )); then
                echo "   🎯 PROFITABLE OPPORTUNITY DETECTED!"
            else
                echo "   ⏳ Spread too small for arbitrage"
            fi
        fi
    fi
else
    echo "[ERROR] PRACTICAL MONITOR BOT NOT RUNNING"
fi

echo ""
echo "[SEARCH] CURRENT MARKET STATUS (from arbitrage bot):"

# Check arbitrage bot status and get latest spreads
ARBITRAGE_LOG="real_26_crypto_arbitrage.log"
if [ -f "$ARBITRAGE_LOG" ]; then
    # Get last scan time
    LAST_SCAN=$(tail -50 "$ARBITRAGE_LOG" 2>/dev/null | grep "CYCLE" | tail -1 | awk '{print $NF}' || echo "UNKNOWN")
    
    # Get top 3 spreads from latest scan
    echo "   Last arbitrage scan: $LAST_SCAN"
    echo ""
    
    # Extract top spreads from log
    TOP_SPREADS=$(tail -50 "$ARBITRAGE_LOG" 2>/dev/null | grep -A15 "TOP 10 CRYPTO SPREADS" | head -16)
    
    if [ -n "$TOP_SPREADS" ]; then
        echo "   📊 TOP 3 SPREADS (from last scan):"
        
        # Parse and show top 3
        COUNT=0
        echo "$TOP_SPREADS" | while read line; do
            # Match spread lines: "   1 | XTZ    | $      0.3444 | $      0.3480 |      -0.89% | $     0.89 | B→G"
            if [[ $line =~ ([[:space:]]*[0-9]+[[:space:]]*\|[[:space:]]*)([A-Z]+)(.*) ]]; then
                if [ $COUNT -lt 3 ]; then
                    # Extract crypto and spread
                    CRYPTO=$(echo "$line" | awk -F'|' '{print $2}' | xargs)
                    BINANCE_PRICE=$(echo "$line" | awk -F'|' '{print $3}' | tr -d '$ ' | xargs)
                    GEMINI_PRICE=$(echo "$line" | awk -F'|' '{print $4}' | tr -d '$ ' | xargs)
                    SPREAD=$(echo "$line" | awk -F'|' '{print $5}' | xargs)
                    DIRECTION=$(echo "$line" | awk -F'|' '{print $7}' | xargs)
                    
                    # Clean up direction
                    DIRECTION=${DIRECTION//G→B/"Gemini↑"}
                    DIRECTION=${DIRECTION//B→G/"Binance↑"}
                    
                    echo "     $((COUNT+1)). $CRYPTO: $SPREAD ($DIRECTION)"
                    echo "        Binance: \$$BINANCE_PRICE, Gemini: \$$GEMINI_PRICE"
                    
                    COUNT=$((COUNT+1))
                fi
            fi
        done
        
        # Get best opportunity
        BEST_OPP=$(tail -50 "$ARBITRAGE_LOG" 2>/dev/null | grep -A1 "Best opportunity:" | head -2)
        if [ -n "$BEST_OPP" ]; then
            echo ""
            echo "   🎯 $(echo "$BEST_OPP" | grep "Best opportunity:" | sed 's/.*INFO - //')"
            echo "   🚀 $(echo "$BEST_OPP" | grep "Action:" | sed 's/.*INFO - //')"
            
            # Check if tradable
            TRADABLE=$(tail -50 "$ARBITRAGE_LOG" 2>/dev/null | grep "TRADABLE:" | tail -1 | sed 's/.*INFO - //')
            if [ -n "$TRADABLE" ]; then
                echo "   ✅ $TRADABLE"
            fi
        fi
        
        # Get average spread
        AVG_SPREAD=$(tail -50 "$ARBITRAGE_LOG" 2>/dev/null | grep "Average spread:" | tail -1 | sed 's/.*INFO - //')
        if [ -n "$AVG_SPREAD" ]; then
            echo "   📊 $AVG_SPREAD"
        fi
    else
        echo "   ⏳ Waiting for arbitrage bot data..."
        echo "   Next scan in 5 minutes (300 seconds)"
    fi
else
    echo "   ❌ Arbitrage bot log not found"
fi

echo ""
echo "[BOT] 26-CRYPTO ARBITRAGE BOT STATUS:"
if ps aux | grep -v grep | grep -q "real_26_crypto_arbitrage_bot.py"; then
    BOT_PID=$(ps aux | grep "real_26_crypto_arbitrage_bot.py" | grep -v grep | awk '{print $2}')
    echo "   Status: ✅ RUNNING (PID: $BOT_PID)"
    
    # Check last activity
    if [ -f "$ARBITRAGE_LOG" ]; then
        LAST_ACTIVITY=$(tail -1 "$ARBITRAGE_LOG" 2>/dev/null | cut -d' ' -f1-3)
        if [ -n "$LAST_ACTIVITY" ]; then
            echo "   Last activity: $LAST_ACTIVITY"
        fi
        
        # Count cycles
        CYCLE_COUNT=$(grep -c "CYCLE.*STARTING" "$ARBITRAGE_LOG" 2>/dev/null)
        echo "   Cycles completed: $CYCLE_COUNT"
    fi
else
    echo "   Status: ❌ STOPPED"
    echo "   Action: Restart with: python3 real_26_crypto_arbitrage_bot.py"
fi

echo ""
echo "[OK] FAST MONITOR COMPLETED AT $(date '+%H:%M:%S')"
echo "   Data source: real_26_crypto_arbitrage.log"
echo "   No API calls - avoids rate limits"