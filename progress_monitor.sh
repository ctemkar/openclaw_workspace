#!/bin/bash

echo "=== TRADING BOT PROGRESS MONITOR ==="
echo "Time: $(date '+%Y-%m-%d %H:%M:%S') (Asia/Bangkok)"
echo ""

# Check profit summary
if [ -f "profit_summary.log" ]; then
    echo "📊 Profit Summary:"
    tail -5 profit_summary.log | while read line; do
        echo "  $line"
    done
    echo ""
else
    echo "📊 Profit Summary: File not found"
    echo ""
fi

# Check real money trades
if [ -f "real_money_trades.log" ]; then
    echo "💰 Real Money Trading Status:"
    success_count=$(grep -c "✅ Trade executed successfully" real_money_trades.log || echo "0")
    error_count=$(grep -c "❌ Cannot trade\|❌ Insufficient balance" real_money_trades.log || echo "0")
    echo "  Successful trades: $success_count"
    echo "  Errors: $error_count"
    
    echo ""
    echo "📈 Recent Activity:"
    tail -3 real_money_trades.log | while read line; do
        echo "  $line"
    done
    echo ""
else
    echo "💰 Real Money Trades: File not found"
    echo ""
fi

# Check next gen trading results
if [ -f "next_gen_trading_results.json" ]; then
    echo "🚀 Next Gen Trading System:"
    python3 -c "
import json
try:
    with open('next_gen_trading_results.json', 'r') as f:
        data = json.load(f)
    print('  Status:', data.get('status', 'Unknown'))
    print('  Total Profit: $' + str(data.get('total_profit', 0)))
    print('  Total Trades:', data.get('total_trades', 0))
    print('  Win Rate:', str(data.get('win_rate', 0)) + '%')
except Exception as e:
    print('  Error reading file:', str(e))
"
    echo ""
else
    echo "🚀 Next Gen Trading System: File not found"
    echo ""
fi

# Check active trading processes
echo "🔄 Active Trading Processes:"
ps aux | grep -E "(python.*trading|python.*arbitrage|python.*bot)" | grep -v grep | head -5 | while read line; do
    pid=$(echo $line | awk '{print $2}')
    cmd=$(echo $line | awk '{for(i=11;i<=NF;i++) printf $i" "; print ""}')
    echo "  PID $pid: $cmd"
done

echo ""
echo "=== MARKET CONDITIONS ==="
# Check if we can get market data
echo "📈 Checking market conditions..."
python3 -c "
import requests
import time
try:
    # Try to get BTC price as market indicator
    response = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT', timeout=5)
    if response.status_code == 200:
        data = response.json()
        print('  BTC/USDT: \$' + data['price'])
    else:
        print('  Market data: API unavailable')
except Exception as e:
    print('  Market data: Error fetching -', str(e))
"

echo ""
echo "=== SYSTEM STATUS ==="
# Check disk space
df -h . | tail -1 | awk '{print "  Disk usage: " $5 " used (" $3 "/" $2 ")"}'

# Check memory usage
free -h 2>/dev/null || vm_stat 2>/dev/null || echo "  Memory: Check not available on macOS"

echo ""
echo "=== END OF REPORT ==="