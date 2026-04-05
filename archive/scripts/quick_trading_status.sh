#!/bin/bash
# Quick Trading Status Check

echo "=== QUICK TRADING STATUS ==="
echo "Time: $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo ""

# Check if trading server is running
echo "1. Trading Server Status:"
if curl -s http://localhost:5001/status > /dev/null 2>&1; then
    echo "   ✅ Server is running on port 5001"
else
    echo "   ❌ Server is not responding"
fi

# Check running bots
echo ""
echo "2. Running Trading Bots:"
bot_count=$(ps aux | grep -E "(trading|python.*bot)" | grep -v grep | wc -l)
echo "   Total bots running: $bot_count"

# Check latest report
echo ""
echo "3. Latest Report:"
if [ -f "latest_trading_analysis.txt" ]; then
    echo "   ✅ Latest analysis available"
    # Extract key info
    grep -A5 "SYSTEM HEALTH SUMMARY" latest_trading_analysis.txt | tail -5
else
    echo "   ❌ No latest analysis found"
fi

# Check critical alerts
echo ""
echo "4. Critical Alerts:"
if [ -f "critical_alerts.log" ]; then
    alert_count=$(grep -c "ALERT [0-9]:" critical_alerts.log)
    echo "   Active alerts: $alert_count"
    if [ $alert_count -gt 0 ]; then
        echo "   ⚠️  Check critical_alerts.log for details"
    fi
else
    echo "   No critical alerts file found"
fi

# Market status
echo ""
echo "5. Market Status:"
if command -v python3 &> /dev/null; then
    python3 -c "
import requests
try:
    r = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd', timeout=5)
    data = r.json()
    btc = data.get('bitcoin', {}).get('usd', 'N/A')
    eth = data.get('ethereum', {}).get('usd', 'N/A')
    print(f'   BTC/USD: \${btc:,}' if isinstance(btc, (int, float)) else f'   BTC/USD: {btc}')
    print(f'   ETH/USD: \${eth:,}' if isinstance(eth, (int, float)) else f'   ETH/USD: {eth}')
except:
    print('   Market data unavailable')
"
else
    echo "   Python not available for market check"
fi

echo ""
echo "=== RECOMMENDED NEXT STEPS ==="
echo "1. Review comprehensive_trading_report_20260331_052727.txt"
echo "2. Check critical_alerts.log for urgent issues"
echo "3. Address ETH positions exceeding stop-loss"
echo "4. Fix bot configuration errors"

echo ""
echo "For detailed analysis, run: python3 process_all_trading_data.py"