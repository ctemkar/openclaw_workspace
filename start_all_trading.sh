#!/bin/bash
echo "=== STARTING ALL TRADING SYSTEMS ==="
echo ""

echo "1. Stopping any existing systems..."
pkill -f "forex_bot_with_schwab.py" 2>/dev/null
pkill -f "simple_trading_dashboard.py" 2>/dev/null
sleep 2

echo ""
echo "2. Starting Forex Trading Bot..."
echo "   Account: Schwab #13086459 ($220)"
echo "   Mode: Real trading (ultra-conservative)"
nohup python3 forex_bot_with_schwab.py --real-trading > real_forex_trading.log 2>&1 &
FOREX_PID=$!
sleep 2

if ps -p $FOREX_PID > /dev/null 2>&1; then
    echo "   ✅ Forex bot started (PID: $FOREX_PID)"
    echo "   📝 Log: real_forex_trading.log"
else
    echo "   ❌ Failed to start Forex bot"
fi

echo ""
echo "3. Starting Comprehensive Dashboard..."
nohup python3 simple_trading_dashboard.py > dashboard.log 2>&1 &
DASH_PID=$!
sleep 2

if ps -p $DASH_PID > /dev/null 2>&1; then
    echo "   ✅ Dashboard started (PID: $DASH_PID)"
    echo "   📊 Open: http://localhost:5010"
    echo "   📝 Log: dashboard.log"
else
    echo "   ❌ Failed to start dashboard"
fi

echo ""
echo "4. Creating trade files if they don't exist..."
if [ ! -f "real_forex_trades.json" ]; then
    echo '[]' > real_forex_trades.json
    echo "   ✅ Created real_forex_trades.json"
fi

echo ""
echo "5. System Status:"
echo "   ============="
echo "   • Forex Bot: $(ps -p $FOREX_PID >/dev/null 2>&1 && echo '✅ RUNNING' || echo '❌ STOPPED')"
echo "   • Dashboard: $(ps -p $DASH_PID >/dev/null 2>&1 && echo '✅ RUNNING' || echo '❌ STOPPED')"
echo "   • Dashboard URL: http://localhost:5010"
echo "   • Forex Log: real_forex_trading.log"
echo "   • Trades File: real_forex_trades.json"

echo ""
echo "6. Monitoring commands:"
echo "   ==================="
echo "   • Check status: ./monitor_all_trading.sh"
echo "   • View logs: tail -f real_forex_trading.log"
echo "   • Open dashboard: http://localhost:5010"
echo "   • Stop all: pkill -f \"forex_bot_with_schwab.py\" && pkill -f \"simple_trading_dashboard.py\""

echo ""
echo "🎉 ALL SYSTEMS STARTED!"
echo "   Your $220 Forex account is now actively trading"
echo "   Dashboard shows all systems at http://localhost:5010"
echo "   Bot is ultra-conservative (good for small account)"