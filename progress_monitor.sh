#!/bin/bash
echo "=== PROGRESS MONITOR - $(date '+%Y-%m-%d %H:%M:%S %Z') ==="
echo ""

# Check if practical profit bot is running
if ps aux | grep -v grep | grep -q "practical_profit_bot.py"; then
    BOT_PID=$(ps aux | grep "practical_profit_bot.py" | grep -v grep | awk '{print $2}')
    echo "✅ PRACTICAL PROFIT BOT RUNNING (PID: $BOT_PID)"
    
    # Check for API errors in logs
    if tail -5 practical_profit_output.log 2>/dev/null | grep -q "Invalid API-key"; then
        echo "🚨 BINANCE API ERROR: Invalid API key/permissions"
        echo "   Status: BOT RUNNING BUT NOT TRADING"
        echo "   Last trade: $(tail -1 practical_profits.log 2>/dev/null | cut -d' ' -f1-2 || echo 'NO TRADES TODAY')"
        echo "   Today's profit: $0.00 (NO TRADES)"
    else
        # Check latest profits
        if [ -f "practical_profits.log" ]; then
            echo ""
            echo "📊 LATEST PROFITS:"
            tail -5 practical_profits.log
        fi
    fi
else
    echo "❌ PRACTICAL PROFIT BOT NOT RUNNING"
fi

# Check current MANA spread
echo ""
echo "🔍 CURRENT MARKET STATUS:"
python3 << 'PYEOF'
import ccxt
try:
    binance = ccxt.binance({'enableRateLimit': True})
    gemini = ccxt.gemini({'enableRateLimit': True})
    
    binance_price = binance.fetch_ticker('MANA/USDT')['last']
    gemini_price = gemini.fetch_ticker('MANA/USD')['last']
    
    spread = ((gemini_price - binance_price) / binance_price) * 100
    
    print(f"MANA Spread: {abs(spread):.2f}%")
    print(f"Binance: ${binance_price:.4f}")
    print(f"Gemini: ${gemini_price:.4f}")
    
    if abs(spread) >= 0.5:
        profit_30 = 30 * (abs(spread)/100) - 0.06
        print(f"💰 Potential profit (if Gemini worked): ${profit_30:.2f}")
    else:
        print("⏳ Spread too small for arbitrage")
        
except Exception as e:
    print(f"Error: {e}")
PYEOF

# Check system resources
echo ""
echo "💻 SYSTEM RESOURCES:"
ps aux | grep "practical_profit" | grep -v grep | awk '{print "   CPU: "$3"%, MEM: "$4"%, PID: "$2}'

echo ""
echo "✅ PROGRESS MONITOR COMPLETED AT $(date '+%H:%M:%S')"
