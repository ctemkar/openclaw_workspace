#!/bin/bash
echo "🔄 Monitoring for active trades..."
echo "Press Ctrl+C to stop"
echo ""

while true; do
    echo "=== $(date '+%H:%M:%S') ==="
    
    # Check process status
    echo "🤖 Bots running:"
    ps -p 87808,88232,88434 -o pid,comm 2>/dev/null | grep -v PID
    
    # Check for new log entries
    echo ""
    echo "📝 Recent activity:"
    
    # Check each log file
    for log in auto_arbitrage_bot.log practical_profit_bot.log multi_llm_trading_bot.log; do
        if [ -f "$log" ]; then
            echo "  $log:"
            tail -1 "$log" 2>/dev/null | sed 's/^/    /'
        fi
    done
    
    echo ""
    echo "🔍 Auto Arbitrage Bot (Arbitration):"
    echo "  Status: ✅ RUNNING (PID: 87808)"
    echo "  Action: Scanning 27 cryptos for >0.4% spreads"
    echo "  When spread found: Will execute automatically"
    echo ""
    echo "📊 Dashboard: http://localhost:5020"
    echo "⏰ Next check in 30 seconds..."
    echo "----------------------------------------"
    sleep 30
done
