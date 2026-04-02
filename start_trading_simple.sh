#!/bin/bash
# Simple startup for trading bot and dashboard

echo "=================================================="
echo "🚀 STARTING TRADING BOT & DASHBOARD"
echo "=================================================="

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASE_DIR"

# Kill any existing processes
echo "🛑 Stopping any existing processes..."
pkill -f "real_26_crypto_trader.py" 2>/dev/null
pkill -f "simple_dashboard.py" 2>/dev/null
sleep 2

# Start trading bot
echo "🚀 Starting trading bot..."
nohup python3 real_26_crypto_trader.py > trader.log 2>&1 &
TRADER_PID=$!
sleep 3

# Start dashboard
echo "🚀 Starting dashboard..."
nohup python3 simple_dashboard.py > dashboard.log 2>&1 &
DASHBOARD_PID=$!
sleep 3

# Check if processes are running
echo "🔍 Checking processes..."
if ps -p $TRADER_PID > /dev/null; then
    echo "✅ Trading bot started (PID: $TRADER_PID)"
else
    echo "❌ Trading bot failed to start"
    exit 1
fi

if ps -p $DASHBOARD_PID > /dev/null; then
    echo "✅ Dashboard started (PID: $DASHBOARD_PID)"
else
    echo "❌ Dashboard failed to start"
    exit 1
fi

echo ""
echo "=================================================="
echo "🎯 SYSTEM STARTED SUCCESSFULLY"
echo "=================================================="
echo ""
echo "📊 Dashboard: http://localhost:5007"
echo "🤖 Trading bot PID: $TRADER_PID"
echo "📈 Dashboard PID: $DASHBOARD_PID"
echo ""
echo "📋 Monitoring commands:"
echo "   tail -f trader.log"
echo "   tail -f dashboard.log"
echo "   curl http://localhost:5007"
echo ""
echo "🛑 To stop:"
echo "   pkill -f 'real_26_crypto_trader.py'"
echo "   pkill -f 'simple_dashboard.py'"
echo ""
echo "=================================================="