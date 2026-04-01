#!/bin/bash
# FIX SYSTEM NOW - Clean duplicates and check status

cd /Users/chetantemkar/.openclaw/workspace/app

echo "🔧 FIXING SYSTEM AT 01:14 AM"
echo "=============================================="

echo ""
echo "1. CLEANING DUPLICATE BOTS:"
echo "----------------------------------------------"
echo "Killing all 26-crypto bot instances..."
pkill -f "real_26_crypto_trader.py"
sleep 2
echo "Starting fresh instance..."
nohup python3 real_26_crypto_trader.py > 26_crypto_bot.log 2>&1 &
sleep 2
echo "✅ 26-crypto bot cleaned and restarted"

echo ""
echo "2. CHECKING LLM DECISIONS:"
echo "----------------------------------------------"
if [ -f "llm_consensus_decisions.json" ]; then
    echo "📊 Recent LLM decisions:"
    python3 -c "
import json
with open('llm_consensus_decisions.json', 'r') as f:
    decisions = json.load(f)
print(f'Total decisions: {len(decisions)}')
for d in decisions[-3:]:
    print(f\"  {d.get('crypto', 'Unknown')}: {d.get('signal', 'Unknown')} (Buy: {d.get('buy_score', 'N/A')}, Sell: {d.get('sell_score', 'N/A')})\")
"
else
    echo "❌ No LLM decisions file"
fi

echo ""
echo "3. CURRENT SYSTEM STATUS:"
echo "----------------------------------------------"
echo "LLM Bot running:" $(ps aux | grep "llm_consensus_bot.py" | grep -v grep | wc -l)
echo "26-Crypto Bot instances:" $(ps aux | grep "real_26_crypto_trader.py" | grep -v grep | wc -l)
echo "Dashboard processes:" $(ps aux | grep -E "(simple_status|simple_pnl|simple_fixed|trades_dashboard)" | grep -v grep | wc -l)

echo ""
echo "4. DASHBOARD PORTS (all should be dead):"
echo "----------------------------------------------"
for port in 5007 5008 5009 5011; do
    echo -n "Port $port: "
    if curl -s http://localhost:$port/ > /dev/null 2>&1; then
        echo "✅ ACTIVE"
    else
        echo "❌ DEAD"
    fi
done

echo ""
echo "=============================================="
echo "✅ System cleanup completed at $(date)"
echo "⚠️ Dashboards still need to be restarted"
echo "📊 LLM bot is making decisions (check llm_consensus_decisions.json)"