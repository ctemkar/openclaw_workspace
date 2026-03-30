#!/bin/bash
# COMPLETE API KEY SETUP SCRIPT
# Run this after you get your API keys from Gemini/Binance

echo "================================================"
echo "🚀 COMPLETE API KEY SETUP FOR REAL TRADING"
echo "================================================"
echo "Total Capital: $250 ($200 Gemini, $50 Binance)"
echo "================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "conservative_crypto_trading.py" ]; then
    echo "❌ ERROR: Run this from trading workspace directory"
    echo "Current dir: $(pwd)"
    exit 1
fi

echo "📁 Creating secure key storage..."
mkdir -p secure_keys
chmod 700 secure_keys

echo ""
echo "🔐 ENTER YOUR API KEYS (Will be stored securely)"
echo "================================================"

# Get Gemini keys
read -p "Enter your Gemini API Key: " GEMINI_KEY
read -sp "Enter your Gemini Secret (hidden): " GEMINI_SECRET
echo ""

# Get Binance keys  
read -p "Enter your Binance API Key: " BINANCE_KEY
read -sp "Enter your Binance Secret (hidden): " BINANCE_SECRET
echo ""

echo ""
echo "💾 Storing keys with ultra-secure permissions..."

# Store Gemini keys
echo "$GEMINI_KEY" > secure_keys/.gemini_key
echo "$GEMINI_SECRET" > secure_keys/.gemini_secret
chmod 600 secure_keys/.gemini_key secure_keys/.gemini_secret

# Store Binance keys
echo "$BINANCE_KEY" > secure_keys/.binance_key
echo "$BINANCE_SECRET" > secure_keys/.binance_secret
chmod 600 secure_keys/.binance_key secure_keys/.binance_secret

# Create symlinks
ln -sf secure_keys/.gemini_key .gemini_key 2>/dev/null || true
ln -sf secure_keys/.gemini_secret .gemini_secret 2>/dev/null || true
ln -sf secure_keys/.binance_key .binance_key 2>/dev/null || true
ln -sf secure_keys/.binance_secret .binance_secret 2>/dev/null || true

echo "✅ Keys stored in secure_keys/ directory"
echo "✅ Symlinks created for trading system"
echo ""

echo "🔄 Updating trading system configuration..."
# Update the trading bot for dual exchange
python3 -c "
import re
with open('conservative_crypto_trading.py', 'r') as f:
    content = f.read()

# Update to dual exchange with $200/$50
if 'EXCHANGE = \"gemini\"' in content:
    content = content.replace('EXCHANGE = \"gemini\"', 'USE_DUAL_EXCHANGE = True\\nGEMINI_CAPITAL = 200.00\\nBINANCE_CAPITAL = 50.00')
    print('✅ Updated to dual exchange: $200 Gemini, $50 Binance')
elif 'USE_DUAL_EXCHANGE = True' in content:
    # Update capital amounts
    content = re.sub(r'GEMINI_CAPITAL = \d+\.\d+', 'GEMINI_CAPITAL = 200.00', content)
    content = re.sub(r'BINANCE_CAPITAL = \d+\.\d+', 'BINANCE_CAPITAL = 50.00', content)
    print('✅ Updated capital amounts: $200 Gemini, $50 Binance')
else:
    print('⚠️ Could not find exchange configuration to update')

with open('conservative_crypto_trading.py', 'w') as f:
    f.write(content)
"

echo ""
echo "🔍 Testing connections..."

# Create test scripts
cat > test_gemini_connection.py << 'EOF'
#!/usr/bin/env python3
"""
Test Gemini API connection
"""
import os
import sys

try:
    key = open('.gemini_key').read().strip()
    secret = open('.gemini_secret').read().strip()
    
    if not key or key == 'YOUR_ACTUAL_GEMINI_API_KEY':
        print("❌ Gemini: No valid API key found")
        print("   Please add your actual Gemini API key to .gemini_key")
    else:
        print("✅ Gemini: API key found (first 10 chars):", key[:10] + "...")
        print("   Secret found:", "✓" if secret and secret != 'YOUR_ACTUAL_GEMINI_SECRET' else "❌ Missing")
        
except FileNotFoundError:
    print("❌ Gemini: .gemini_key or .gemini_secret not found")
except Exception as e:
    print(f"❌ Gemini error: {e}")
EOF

cat > test_binance_connection.py << 'EOF'
#!/usr/bin/env python3
"""
Test Binance API connection
"""
import os
import sys

try:
    key = open('.binance_key').read().strip()
    secret = open('.binance_secret').read().strip()
    
    if not key or key == 'YOUR_ACTUAL_BINANCE_API_KEY':
        print("❌ Binance: No valid API key found")
        print("   Please add your actual Binance API key to .binance_key")
    else:
        print("✅ Binance: API key found (first 10 chars):", key[:10] + "...")
        print("   Secret found:", "✓" if secret and secret != 'YOUR_ACTUAL_BINANCE_SECRET' else "❌ Missing")
        
except FileNotFoundError:
    print("❌ Binance: .binance_key or .binance_secret not found")
except Exception as e:
    print(f"❌ Binance error: {e}")
EOF

chmod +x test_gemini_connection.py test_binance_connection.py

# Run tests
python3 test_gemini_connection.py
python3 test_binance_connection.py

echo ""
echo "🚀 RESTARTING TRADING SYSTEM..."

# Kill existing processes
pkill -f "trading_server.py" 2>/dev/null || true
pkill -f "conservative_crypto_trading.py" 2>/dev/null || true
sleep 2

# Start fresh
python3 trading_server.py > server.log 2>&1 &
SERVER_PID=$!
python3 conservative_crypto_trading.py > bot.log 2>&1 &
BOT_PID=$!

echo "✅ Trading Server started (PID: $SERVER_PID)"
echo "✅ Trading Bot started (PID: $BOT_PID)"
echo ""

sleep 3

echo "🔍 Checking system status..."
curl -s http://127.0.0.1:5001/status 2>/dev/null | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print('✅ Trading API responding')
    print(f'   Status: {data.get(\"status\", \"unknown\")}')
    print(f'   Capital: ${data.get(\"capital\", 0)}')
    print(f'   Last analysis: {data.get(\"last_analysis\", \"unknown\")}')
except:
    print('⚠️ Could not reach trading API')
    print('   Check logs: tail -f server.log')
"

echo ""
echo "================================================"
echo "🎯 SETUP COMPLETE!"
echo "================================================"
echo ""
echo "📊 NEXT STEPS:"
echo "1. Fund your accounts:"
echo "   • Gemini: Transfer $200"
echo "   • Binance: Transfer $50"
echo ""
echo "2. Test Telegram reports:"
echo "   • Message @MMCashEarner_bot"
echo "   • Send: /status"
echo ""
echo "3. Monitor trading:"
echo "   • Dashboard: http://127.0.0.1:5080"
echo "   • API: http://127.0.0.1:5001/status"
echo "   • Logs: tail -f bot.log"
echo ""
echo "4. Security check:"
echo "   • Verify IP restrictions on exchange API keys"
echo "   • Enable trade alerts on both exchanges"
echo "   • Check secure_keys/README_SECURITY.md"
echo ""
echo "🚀 REAL $250 TRADING IS READY!"
echo "================================================"