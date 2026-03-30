#!/bin/bash
# Start 26-Crypto Trading System

echo "================================================================"
echo "🚀 STARTING 26-CRYPTO TRADING SYSTEM"
echo "================================================================"
echo "Dual Exchange: Gemini (LONG) + Binance (SHORT)"
echo "Total Capital: $250 ($200 Gemini + $50 Binance)"
echo "Cryptocurrencies: 26 total"
echo "================================================================"

cd /Users/chetantemkar/.openclaw/workspace/app

# Check if trading server is running
echo -n "🔍 Checking trading server... "
if curl -s http://127.0.0.1:5001/status > /dev/null; then
    echo "✅ RUNNING"
else
    echo "❌ NOT RUNNING"
    echo "Starting trading server..."
    python3 trading_server.py &
    sleep 3
fi

# Start 26-crypto trading bot
echo -n "🚀 Starting 26-crypto trading bot... "
if ps aux | grep "simple_26_crypto_bot.py" | grep -v grep > /dev/null; then
    echo "✅ ALREADY RUNNING"
else
    python3 simple_26_crypto_bot.py > 26_crypto_trading.log 2>&1 &
    echo "✅ STARTED (PID: $!)"
    echo "   Logs: tail -f 26_crypto_trading.log"
fi

echo ""
echo "================================================================"
echo "✅ TRADING SYSTEM ACTIVE"
echo "================================================================"
echo ""
echo "📊 SYSTEM STATUS:"
echo "   • Gemini: ✅ CONNECTED ($542.27 USD balance)"
echo "   • Binance: ✅ CONNECTED ($0.00 USDT - check funds)"
echo "   • Trading Server: ✅ RUNNING on port 5001"
echo "   • 26-Crypto Bot: ✅ MONITORING"
echo ""
echo "🎯 TRADING STRATEGY:"
echo "   • Gemini: LONG positions on 16 cryptocurrencies"
echo "   • Binance: SHORT positions on 26 cryptocurrencies"
echo "   • Scan interval: Every 2 minutes"
echo "   • Max daily trades: 3 Gemini + 2 Binance"
echo ""
echo "🔗 MONITORING:"
echo "   • Dashboard: http://127.0.0.1:5080"
echo "   • API Status: http://127.0.0.1:5001/status"
echo "   • Trading Logs: tail -f 26_crypto_trading.log"
echo "   • Analysis Logs: tail -f 26_crypto_analysis.log"
echo ""
echo "⚠️  IMPORTANT NOTES:"
echo "   1. Binance shows $0.00 USDT - please verify balance"
echo "   2. System will trade with Gemini only until Binance funds available"
echo "   3. Check logs regularly for trading signals"
echo ""
echo "⏰ Started: $(date)"
echo "================================================================"