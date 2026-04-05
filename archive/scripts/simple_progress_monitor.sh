#!/bin/bash
echo "=== REAL-TIME PROGRESS MONITOR - $(date '+%Y-%m-%d %H:%M:%S %Z') ==="
echo ""

# Check if practical profit bot is running
if ps aux | grep -v grep | grep -q "practical_profit_bot.py"; then
    BOT_PID=$(ps aux | grep "practical_profit_bot.py" | grep -v grep | awk '{print $2}')
    echo "[OK] PRACTICAL PROFIT BOT RUNNING (PID: $BOT_PID)"
    
    # Get the VERY LAST trade from the log
    if [ -f "practical_profits.log" ]; then
        LAST_TRADE=$(tail -1 practical_profits.log)
        LAST_PROFIT=$(echo "$LAST_TRADE" | awk -F'Profit: \\$' '{print $2}' | awk '{print $1}')
        LAST_TOTAL=$(echo "$LAST_TRADE" | awk -F'Total: \\$' '{print $2}')
        LAST_TIME=$(echo "$LAST_TRADE" | awk '{print $1" "$2}')
        
        echo "[CHART] LATEST TRADE:"
        echo "   Time: $LAST_TIME"
        echo "   Profit: \$$LAST_PROFIT"
        echo "   Total: \$$LAST_TOTAL"
        
        # Count trades TODAY (April 5)
        TODAY_TRADES=$(grep "^2026-04-05" practical_profits.log 2>/dev/null | wc -l)
        if [ "$TODAY_TRADES" -gt 0 ]; then
            TODAY_PROFIT=$(grep "^2026-04-05" practical_profits.log 2>/dev/null | tail -1 | awk -F'Total: \\$' '{print $2}')
            echo "   Trades today: $TODAY_TRADES"
            echo "   Profit today: \$$TODAY_PROFIT"
        else
            echo "   No trades today yet"
        fi
    fi
else
    echo "[ERROR] PRACTICAL PROFIT BOT NOT RUNNING"
fi

echo ""
echo "[SEARCH] CURRENT MARKET STATUS:"
python3 << 'PYEOF'
import ccxt
from datetime import datetime

try:
    # Initialize exchanges
    binance = ccxt.binance({'enableRateLimit': True})
    gemini = ccxt.gemini({'enableRateLimit': True})
    
    # Check MANA
    binance_mana = binance.fetch_ticker('MANA/USDT')['last']
    gemini_mana = gemini.fetch_ticker('MANA/USD')['last']
    
    mana_spread = ((gemini_mana - binance_mana) / binance_mana) * 100
    
    print(f"MANA Spread: {mana_spread:.2f}%")
    print(f"Binance: ${binance_mana:.4f}")
    print(f"Gemini: ${gemini_mana:.4f}")
    
    if abs(mana_spread) >= 0.5:
        print(f"[MONEY] Tradable spread: {abs(mana_spread):.2f}%")
    else:
        print(f"[CLOCK] Spread too small: {abs(mana_spread):.2f}%")
    
    print("")
    print("[CHART] TOP ARBITRAGE OPPORTUNITIES:")
    
    # Check top cryptos
    cryptos = ['FIL', 'YFI', 'COMP', 'LTC', 'DOT', 'ATOM', 'XTZ', 'AVAX', 'UNI', 'ETH']
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
    
    # Sort by absolute spread
    spreads.sort(key=lambda x: x['abs_spread'], reverse=True)
    
    # Show top 3
    for i, s in enumerate(spreads[:3], 1):
        direction = "Gemini↑" if s['spread'] > 0 else "Binance↑"
        print(f"  {i}. {s['crypto']}: {s['spread']:.2f}% ({direction})")
        print(f"     Binance: ${s['binance']:.4f}, Gemini: ${s['gemini']:.4f}")
    
    if spreads:
        best = spreads[0]
        print(f"  🎯 Best: {best['crypto']} ({best['spread']:.2f}%)")
        if best['abs_spread'] >= 0.5:
            print(f"  ✅ TRADABLE: ≥0.5% spread")
        else:
            print(f"  ⏳ MONITORING: <0.5% spread")
        
except Exception as e:
    print(f"Error: {e}")
PYEOF

# Check arbitrage bot status
echo ""
echo "[BOT] 26-CRYPTO ARBITRAGE BOT:"
if ps aux | grep -v grep | grep -q "real_26_crypto_arbitrage_bot.py"; then
    echo "   Status: ✅ RUNNING"
    echo "   Last scan: $(tail -5 real_26_crypto_arbitrage.log 2>/dev/null | grep 'CYCLE' | tail -1 | awk '{print $NF}' || echo 'N/A')"
    
    # Show best opportunity from arbitrage bot
    BEST_OPP=$(tail -30 real_26_crypto_arbitrage.log 2>/dev/null | grep -A1 "Best opportunity:" | head -2)
    if [ -n "$BEST_OPP" ]; then
        echo "   $(echo "$BEST_OPP" | grep "Best opportunity:")"
        echo "   $(echo "$BEST_OPP" | grep "Action:")"
    fi
else
    echo "   Status: ❌ STOPPED"
fi

echo ""
echo "[OK] REAL-TIME MONITOR COMPLETED AT $(date '+%H:%M:%S')"