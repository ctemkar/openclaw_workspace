#!/bin/bash
echo "=== PROGRESS MONITOR - $(date '+%Y-%m-%d %H:%M:%S %Z') ==="
echo ""

# Check if practical profit bot is running
if ps aux | grep -v grep | grep -q "practical_profit_bot.py"; then
    BOT_PID=$(ps aux | grep "practical_profit_bot.py" | grep -v grep | awk '{print $2}')
    echo "[OK] PRACTICAL PROFIT BOT RUNNING (PID: $BOT_PID)"
    
    # Check for API errors in logs
    if tail -5 practical_profit_output.log 2>/dev/null | grep -q "Invalid API-key"; then
        echo "[ERROR] BINANCE API ERROR: Invalid API key/permissions"
        echo "   Status: BOT RUNNING BUT NOT TRADING"
        echo "   Last trade: $(tail -1 practical_profits.log 2>/dev/null | cut -d' ' -f1-2 || echo 'NO TRADES TODAY')"
        echo "   Today's profit: $0.00 (NO TRADES)"
    else
        # Check TODAY'S profits only
        if [ -f "practical_profits.log" ]; then
            echo ""
            echo "[CHART] TODAY'S PROFITS (April 5):"
            # Get today's date in log format
            TODAY="2026-04-05"
            
            # Get today's trades only
            TODAYS_TRADES=$(grep "^$TODAY" practical_profits.log 2>/dev/null)
            
            if [ -n "$TODAYS_TRADES" ]; then
                # Count today's trades
                TODAY_TRADE_COUNT=$(echo "$TODAYS_TRADES" | wc -l)
                
                # Get today's profit from last trade entry
                TODAY_PROFIT=$(echo "$TODAYS_TRADES" | tail -1 | awk -F'Total: \\$' '{print $2}' || echo "0.00")
                
                echo "   Trades today: $TODAY_TRADE_COUNT"
                echo "   Profit today: \$$TODAY_PROFIT"
                echo "   Last trade: $(echo "$TODAYS_TRADES" | tail -1 | cut -d' ' -f1-3 || echo 'NONE')"
                
                # Show last 3 trades today
                if [ "$TODAY_TRADE_COUNT" -gt 0 ]; then
                    echo "   Recent trades:"
                    echo "$TODAYS_TRADES" | tail -3 | while read line; do
                        echo "     • $line"
                    done
                fi
            else
                echo "   No trades today yet"
                echo "   Last trade: $(tail -1 practical_profits.log 2>/dev/null | cut -d' ' -f1-3 || echo 'NONE')"
            fi
        fi
    fi
else
    echo "[ERROR] PRACTICAL PROFIT BOT NOT RUNNING"
fi

# Check current MANA spread and top 3 spreads
echo ""
echo "[SEARCH] CURRENT MARKET STATUS:"
python3 << 'PYEOF'
import ccxt
from datetime import datetime

try:
    # Initialize exchanges
    binance = ccxt.binance({'enableRateLimit': True})
    gemini = ccxt.gemini({'enableRateLimit': True})
    
    # Check MANA first
    binance_mana = binance.fetch_ticker('MANA/USDT')['last']
    gemini_mana = gemini.fetch_ticker('MANA/USD')['last']
    
    mana_spread = ((gemini_mana - binance_mana) / binance_mana) * 100
    
    # Show MANA spread
    if mana_spread >= 0:
        print(f"MANA Spread: +{mana_spread:.2f}% (Gemini HIGHER)")
    else:
        print(f"MANA Spread: {mana_spread:.2f}% (Gemini LOWER)")
    
    print(f"Binance: ${binance_mana:.4f}")
    print(f"Gemini: ${gemini_mana:.4f}")
    
    if abs(mana_spread) >= 0.5:
        profit_30 = 30 * (abs(mana_spread)/100) - 0.06
        print(f"[MONEY] Potential profit (if Gemini worked): ${profit_30:.2f}")
    else:
        print("[CLOCK] MANA spread too small for arbitrage")
    
    print("")
    print("[CHART] TOP 3 SPREADS (Binance vs Gemini):")
    
    # Check top cryptos for spreads
    cryptos = ['XTZ', 'AAVE', 'UNI', 'FIL', 'YFI', 'LTC', 'DOT', 'COMP', 'ATOM', 'LINK']
    spreads = []
    
    for crypto in cryptos:
        try:
            binance_price = binance.fetch_ticker(f'{crypto}/USDT')['last']
            gemini_price = gemini.fetch_ticker(f'{crypto}/USD')['last']
            
            if gemini_price > 0:
                spread = ((binance_price - gemini_price) / gemini_price) * 100
                spreads.append({
                    'crypto': crypto,
                    'binance': binance_price,
                    'gemini': gemini_price,
                    'spread': spread,
                    'abs_spread': abs(spread)
                })
        except:
            continue
    
    # Sort by absolute spread (highest first)
    spreads.sort(key=lambda x: x['abs_spread'], reverse=True)
    
    # Show top 3
    for i, s in enumerate(spreads[:3], 1):
        direction = "Gemini↑" if s['spread'] > 0 else "Binance↑"
        print(f"  {i}. {s['crypto']}: {s['spread']:.2f}% ({direction})")
        print(f"     Binance: ${s['binance']:.4f}, Gemini: ${s['gemini']:.4f}")
    
    if spreads:
        avg_spread = sum(s['abs_spread'] for s in spreads) / len(spreads)
        print(f"  📊 Average spread: {avg_spread:.2f}%")
        
        # Show best opportunity
        best = spreads[0]
        if best['abs_spread'] >= 0.3:  # 0.3% threshold
            print(f"  🎯 Best opportunity: {best['crypto']} ({best['spread']:.2f}%)")
            if best['spread'] > 0:
                print(f"     Action: Buy on Gemini, sell on Binance")
            else:
                print(f"     Action: Buy on Binance, sell on Gemini")
        
except Exception as e:
    print(f"Error checking spreads: {e}")
PYEOF

# Check system resources
echo ""
echo "[COMPUTER] SYSTEM RESOURCES:"
ps aux | grep "practical_profit" | grep -v grep | awk '{print "   CPU: "$3"%, MEM: "$4"%, PID: "$2}'

# Check sorted spread dashboard and arbitrage bot
echo ""
echo "[CHART] SPREAD MONITORING:"
echo "   • Sorted Spread Dashboard: http://localhost:5025"
echo "   • 26-Crypto Arbitrage Bot: $(ps aux | grep -q 'real_26_crypto_arbitrage_bot' && echo 'RUNNING' || echo 'STOPPED')"

# Show top spreads from arbitrage bot log if available
if [ -f "real_26_crypto_arbitrage.log" ]; then
    echo "   • Top spreads from arbitrage bot:"
    # Get the latest spread data
    LATEST_SPREADS=$(tail -50 real_26_crypto_arbitrage.log 2>/dev/null | grep -A15 "TOP 10 CRYPTO SPREADS" | head -16)
    
    if [ -n "$LATEST_SPREADS" ]; then
        echo "$LATEST_SPREADS" | grep -E "^    [0-9]+" | head -3 | while read line; do
            # Clean up the line
            CLEAN_LINE=$(echo "$line" | sed 's/^[[:space:]]*//')
            echo "     $CLEAN_LINE"
        done
        
        # Show best opportunity
        BEST_OPP=$(tail -50 real_26_crypto_arbitrage.log 2>/dev/null | grep -A2 "Best opportunity:" | head -3)
        if [ -n "$BEST_OPP" ]; then
            echo "     $(echo "$BEST_OPP" | grep "Best opportunity:")"
            echo "     $(echo "$BEST_OPP" | grep "Action:")"
        fi
    else
        echo "     (Waiting for first scan...)"
    fi
fi

echo ""
echo "[OK] PROGRESS MONITOR COMPLETED AT $(date '+%H:%M:%S')"
