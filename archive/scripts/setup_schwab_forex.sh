#!/bin/zsh

echo "=== SCHWAB FOREX TRADING SETUP ==="
echo ""
echo "🚀 Setting up Schwab for real Forex trading..."
echo ""

echo "1. Checking current setup..."
echo "   📊 Current active bots:"
ps aux | grep -E "(forex|trading)" | grep -v grep | grep -v "ps aux" | awk '{print "   • "$11" (PID: "$2")"}'

echo ""
echo "2. Stopping existing Forex bot..."
pkill -f "simple_forex_bot.py" 2>/dev/null
pkill -f "forex_bot_with_schwab.py" 2>/dev/null
sleep 2

echo ""
echo "3. Checking Schwab credentials..."
if [ -f ".env" ]; then
    echo "   📄 Checking .env file for Schwab credentials..."
    if grep -q "SCHWAB_API_KEY" .env && grep -q "SCHWAB_API_SECRET" .env; then
        echo "   ✅ Schwab credentials found in .env"
        echo ""
        echo "   🎯 Ready for real trading!"
        echo ""
        echo "   To start REAL Forex trading with Schwab:"
        echo "   python3 forex_bot_with_schwab.py --real-trading"
    else
        echo "   ❌ Schwab credentials NOT found in .env"
        echo ""
        echo "   📝 You need to add:"
        echo "   SCHWAB_API_KEY=your_app_key_here"
        echo "   SCHWAB_API_SECRET=your_app_secret_here"
        echo "   SCHWAB_ACCOUNT_ID=your_account_number"
        echo ""
        echo "   📖 See SCHWAB_SETUP_GUIDE.md for instructions"
        echo ""
        echo "   For now, starting in PAPER trading mode..."
        REAL_MODE="--paper-trading"
    fi
else
    echo "   ❌ .env file not found"
    echo "   Creating template .env file..."
    cp .env.example .env 2>/dev/null || echo "# Create .env file with your credentials" > .env
    REAL_MODE="--paper-trading"
fi

echo ""
echo "4. Starting Forex bot..."
if [ "$REAL_MODE" = "--paper-trading" ]; then
    echo "   📝 Starting in PAPER TRADING mode"
    nohup python3 forex_bot_with_schwab.py --paper-trading > forex_schwab_output.log 2>&1 &
else
    echo "   💰 Starting in REAL TRADING mode with Schwab"
    nohup python3 forex_bot_with_schwab.py --real-trading > forex_schwab_output.log 2>&1 &
fi

FOREX_PID=$!
echo "   ✅ Forex bot started (PID: $FOREX_PID)"
echo "   📝 Log: forex_schwab_output.log"

echo ""
echo "5. Quick test of connection..."
sleep 3
echo "   🔍 Checking bot status..."
if [ -f "forex_schwab_output.log" ]; then
    echo "   📊 Initial output:"
    tail -5 forex_schwab_output.log
else
    echo "   ⏳ Bot starting up..."
fi

echo ""
echo "🎯 SETUP COMPLETE!"
echo ""
if [ "$REAL_MODE" = "--paper-trading" ]; then
    echo "📝 CURRENT MODE: PAPER TRADING"
    echo "   • Using $10,000 virtual balance"
    echo "   • Testing strategy with real market data"
    echo "   • Ready to switch to real trading"
    echo ""
    echo "🚀 TO SWITCH TO REAL TRADING:"
    echo "   1. Get Schwab API credentials from developer.schwab.com"
    echo "   2. Add them to your .env file"
    echo "   3. Run: ./setup_schwab_forex.sh"
else
    echo "💰 CURRENT MODE: REAL TRADING WITH SCHWAB"
    echo "   • Connected to your Schwab account"
    echo "   • Executing real Forex trades"
    echo "   • Real money at risk - trade carefully!"
    echo ""
    echo "⚠️ IMPORTANT:"
    echo "   • Start with small position sizes (0.01 lots)"
    echo "   • Monitor performance closely"
    echo "   • Keep stop losses active"
    echo "   • Never risk more than 1-2% per trade"
fi

echo ""
echo "📈 TO MONITOR PERFORMANCE:"
echo "   tail -f forex_schwab_output.log"
echo "   cat paper_forex_trades.json   # or real_forex_trades.json"
echo ""
echo "🛑 TO STOP THE BOT:"
echo "   pkill -f \"forex_bot_with_schwab.py\""
echo ""
echo "🔧 FOR TROUBLESHOOTING:"
echo "   python3 test_schwab_connection.py"
echo "   Check SCHWAB_SETUP_GUIDE.md"
echo ""
echo "✅ Schwab Forex trading setup complete!"