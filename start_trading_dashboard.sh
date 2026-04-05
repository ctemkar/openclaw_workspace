#!/bin/bash

echo "============================================================"
echo "🚀 STARTING REAL TRADING DASHBOARD SYSTEM"
echo "============================================================"

# Start real trading data generator
echo "1. Starting real trading data generator..."
python3 real_trading_data_generator.py > real_data_generator.log 2>&1 &
DATA_GEN_PID=$!
sleep 3
echo "   Generator PID: $DATA_GEN_PID"

# Check if data is being generated
echo ""
echo "2. Checking data generation..."
if [ -d "real_trading_data" ]; then
    echo "   ✅ Data directory exists"
    ls -la real_trading_data/*.json 2>/dev/null | head -3
else
    echo "   ⚠️ Data directory not created yet"
fi

# Start web server
echo ""
echo "3. Starting web server on port 8081..."
python3 -m http.server 8081 > dashboard_server.log 2>&1 &
SERVER_PID=$!
sleep 2
echo "   Server PID: $SERVER_PID"

echo ""
echo "============================================================"
echo "✅ SYSTEM STARTED SUCCESSFULLY"
echo "============================================================"
echo ""
echo "🔗 DASHBOARD LINKS:"
echo "• Main Dashboard: http://localhost:8081/actual_trading_dashboard_with_real_data.html"
echo "• Simple Dashboard: http://localhost:8081/actual_trading_dashboard.html"
echo ""
echo "📊 WHAT YOU'LL SEE:"
echo "• Real trading metrics with LLM scores (1-10)"
echo "• Spread % between Binance and Gemini exchanges"
echo "• Market sentiment (Bullish/Bearish/Neutral)"
echo "• Recent trades with decision reasons"
echo "• Active positions and strategy performance"
echo ""
echo "🔄 DATA FLOW:"
echo "Paper Trading → Data Generator → Dashboard → Your Browser"
echo ""
echo "📝 MONITORING:"
echo "• Data generator logs: tail -f real_data_generator.log"
echo "• Server logs: tail -f dashboard_server.log"
echo "• Paper trading: tail -f fixed_simulated_trades_audit.json"
echo ""
echo "🎯 PAPER TRADING STATUS:"
ps aux | grep "fixed_paper_trading" | grep -v grep || echo "   ⚠️ Paper trading not found"
echo ""
echo "Press Ctrl+C to stop all processes"
echo "============================================================"

# Wait for user interrupt
wait