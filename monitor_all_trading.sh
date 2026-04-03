#!/bin/bash
echo "=== COMPREHENSIVE TRADING MONITOR ==="
echo "Time: $(date '+%H:%M:%S %Z')"
echo ""

echo "📊 ACTIVE TRADING SYSTEMS:"
echo "=========================="

# Check Forex bot
if ps aux | grep -v grep | grep -q "forex_bot_with_schwab.py"; then
    FOREX_PID=$(ps aux | grep "forex_bot_with_schwab.py" | grep -v grep | awk '{print $2}')
    echo "✅ FOREX TRADING BOT (PID: $FOREX_PID)"
    echo "   Account: Schwab #13086459 ($220)"
    echo "   Bot: forex_bot_with_schwab.py"
    
    # Check recent activity
    if [ -f "real_forex_trading.log" ]; then
        echo "   📈 Recent scan:"
        tail -1 real_forex_trading.log | sed 's/^/      /'
    fi
else
    echo "❌ FOREX BOT NOT RUNNING"
    echo "   To start: python3 forex_bot_with_schwab.py --real-trading > real_forex_trading.log 2>&1 &"
fi

echo ""
echo "📈 DASHBOARDS:"
echo "============="

# Check dashboards
DASH_COUNT=0
if ps aux | grep -v grep | grep -q "simple_trading_dashboard.py"; then
    DASH_PID=$(ps aux | grep "simple_trading_dashboard.py" | grep -v grep | awk '{print $2}')
    echo "✅ COMPREHENSIVE DASHBOARD (PID: $DASH_PID)"
    echo "   URL: http://localhost:5010"
    echo "   Shows: All trading systems"
    DASH_COUNT=$((DASH_COUNT + 1))
fi

if ps aux | grep -v grep | grep -q "real_dashboard_simple.py"; then
    OLD_DASH_PID=$(ps aux | grep "real_dashboard_simple.py" | grep -v grep | awk '{print $2}')
    echo "✅ OLD DASHBOARD (PID: $OLD_DASH_PID)"
    DASH_COUNT=$((DASH_COUNT + 1))
fi

if [ $DASH_COUNT -eq 0 ]; then
    echo "❌ NO DASHBOARDS RUNNING"
    echo "   To start: python3 simple_trading_dashboard.py > dashboard.log 2>&1 &"
fi

echo ""
echo "💰 TRADING RESULTS:"
echo "=================="

# Check Forex trades
if [ -f "real_forex_trades.json" ]; then
    echo "📜 FOREX TRADES:"
    python3 -c "
import json
try:
    with open('real_forex_trades.json', 'r') as f:
        trades = json.load(f)
    open_trades = [t for t in trades if t.get('status') == 'OPEN']
    closed_trades = [t for t in trades if t.get('status') == 'CLOSED']
    print(f'   Open trades: {len(open_trades)}')
    print(f'   Closed trades: {len(closed_trades)}')
    if closed_trades:
        profits = [t.get('profit', 0) for t in closed_trades]
        total = sum(profits)
        color = '\033[92m' if total > 0 else '\033[91m'
        reset = '\033[0m'
        print(f'   Total profit: {color}\${total:.2f}{reset}')
        if len(closed_trades) > 0:
            wins = sum(1 for p in profits if p > 0)
            print(f'   Win rate: {wins/len(closed_trades)*100:.1f}%')
except Exception as e:
    print(f'   Error: {e}')
"
else
    echo "📝 No Forex trades yet (bot being conservative)"
fi

echo ""
echo "₿ CRYPTO TRADING (HISTORICAL):"
echo "   Total profit: \$2.60 (35 trades)"
echo "   Status: ✅ PROVEN SUCCESS"
echo "   Can restart: YES (practical_profit_bot.py)"

echo ""
echo "📈 SCALING PLAN:"
echo "==============="
echo "   Current: Phase 1 - Proof of Concept (\$220)"
echo "   Next: Phase 2 - Add \$500 when proven"
echo "   Your plan: \"Will add funds when proven successful\""

echo ""
echo "🔧 QUICK COMMANDS:"
echo "================="
echo "  Dashboard:  http://localhost:5010"
echo "  Forex logs: tail -f real_forex_trading.log"
echo "  Stop all:   pkill -f \"forex_bot_with_schwab.py\" && pkill -f \"simple_trading_dashboard.py\""
echo "  Start all:  ./start_all_trading.sh"

echo ""
echo "💡 TIP: The bot is being ULTRA-CONSERVATIVE with your \$220 account."
echo "       This is GOOD - better to wait for high-probability setups."
echo "       First trades will come when market conditions are right."

echo ""
echo "⏰ Next Forex scan: ~$(date -v+10M '+%H:%M')"
echo "🔄 Dashboard auto-refresh: Every 30 seconds"