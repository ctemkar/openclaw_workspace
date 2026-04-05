#!/bin/bash
echo "=== FOREX BOT MONITOR ==="
echo "Time: $(date '+%H:%M:%S')"
echo ""

# Check if bot is running
if ps aux | grep -v grep | grep -q "ultra_safe_forex_bot.py"; then
    PID=$(ps aux | grep "ultra_safe_forex_bot.py" | grep -v grep | awk '{print $2}')
    echo "✅ Bot Running (PID: $PID)"
    
    # Check recent activity
    if [ -f "ultra_safe_forex_output.log" ]; then
        echo "📊 Recent logs:"
        tail -3 ultra_safe_forex_output.log
    fi
    
    # Check trades
    if [ -f "ultra_safe_trades.json" ]; then
        echo "💰 Trades:"
        python3 -c "
import json
try:
    with open('ultra_safe_trades.json', 'r') as f:
        trades = json.load(f)
    open_trades = [t for t in trades if t.get('status') == 'OPEN']
    closed_trades = [t for t in trades if t.get('status') == 'CLOSED']
    print(f'  Open: {len(open_trades)}, Closed: {len(closed_trades)}')
    if closed_trades:
        profits = [t.get('profit', 0) for t in closed_trades]
        print(f'  Total profit: ${sum(profits):.2f}')
except:
    print('  No trades yet')
"
    fi
else
    echo "❌ Bot Not Running"
    echo "   To start: python3 ultra_safe_forex_bot.py > ultra_safe_forex_output.log 2>&1 &"
fi

echo ""
echo "📈 RESOURCE USAGE:"
ps aux | grep "ultra_safe_forex_bot.py" | grep -v grep | awk '{print "  CPU: "$3"%, MEM: "$4"%, PID: "$2}'

echo ""
echo "🔧 COMMANDS:"
echo "  Monitor: tail -f ultra_safe_forex_output.log"
echo "  Trades: cat ultra_safe_trades.json"
echo "  Stop: pkill -f ultra_safe_forex_bot.py"
echo "  Start: ./monitor_forex.sh"
