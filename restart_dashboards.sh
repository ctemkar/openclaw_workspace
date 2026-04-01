#!/bin/bash
# RESTART ALL DASHBOARDS

cd /Users/chetantemkar/.openclaw/workspace/app

echo "🚀 RESTARTING ALL DASHBOARDS"
echo "=============================================="

# Kill all existing dashboards
echo "1. Killing old dashboard processes..."
pkill -f "simple_status_dashboard.py" 2>/dev/null
pkill -f "simple_pnl_fixed.py" 2>/dev/null
pkill -f "simple_fixed_dashboard.py" 2>/dev/null
pkill -f "trades_dashboard_fixed.py" 2>/dev/null
pkill -f "http.server" 2>/dev/null
echo "✅ Old dashboards killed"

# Start Simple Status Dashboard (Port 5007)
echo ""
echo "2. Starting Simple Status Dashboard (Port 5007)..."
python3 simple_status_dashboard.py > dashboard_5007.log 2>&1 &
sleep 3
echo -n "   Status: "
if curl -s http://localhost:5007/ > /dev/null 2>&1; then
    echo "✅ RUNNING"
else
    echo "❌ FAILED"
fi

# Start P&L Dashboard (Port 5008)
echo ""
echo "3. Starting P&L Dashboard (Port 5008)..."
python3 simple_pnl_fixed.py --port 5008 > dashboard_5008.log 2>&1 &
sleep 2
echo -n "   Status: "
if curl -s http://localhost:5008/ > /dev/null 2>&1; then
    echo "✅ RUNNING"
else
    echo "❌ FAILED"
fi

# Start Fixed Dashboard (Port 5009)
echo ""
echo "4. Starting Fixed Dashboard (Port 5009)..."
python3 simple_fixed_dashboard.py --port 5009 > dashboard_5009.log 2>&1 &
sleep 2
echo -n "   Status: "
if curl -s http://localhost:5009/ > /dev/null 2>&1; then
    echo "✅ RUNNING"
else
    echo "❌ FAILED"
fi

# Start Real-Time Trades Dashboard (Port 5011)
echo ""
echo "5. Starting Real-Time Trades Dashboard (Port 5011)..."
python3 trades_dashboard_fixed.py --port 5011 > dashboard_5011.log 2>&1 &
sleep 2
echo -n "   Status: "
if curl -s http://localhost:5011/ > /dev/null 2>&1; then
    echo "✅ RUNNING"
else
    echo "❌ FAILED"
fi

echo ""
echo "=============================================="
echo "📊 FINAL DASHBOARD STATUS:"
echo "----------------------------------------------"
for port in 5007 5008 5009 5011; do
    echo -n "Port $port: "
    if curl -s http://localhost:$port/ > /dev/null 2>&1; then
        echo "✅ ACTIVE"
    else
        echo "❌ INACTIVE"
    fi
done

echo ""
echo "🤖 TRADING BOT STATUS:"
echo "----------------------------------------------"
ps aux | grep -E "(real_26_crypto|llm_consensus)" | grep -v grep | grep -v "restart_dashboards" | wc -l | xargs echo "Active trading bots:"

echo ""
echo "🎯 DASHBOARD LINKS:"
echo "----------------------------------------------"
echo "• Port 5007: http://localhost:5007/ (Simple Status)"
echo "• Port 5008: http://localhost:5008/ (P&L Dashboard)"
echo "• Port 5009: http://localhost:5009/ (Fixed Dashboard)"
echo "• Port 5011: http://localhost:5011/ (Real-Time Trades)"

echo ""
echo "✅ Dashboard restart completed at $(date)"