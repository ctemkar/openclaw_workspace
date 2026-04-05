#!/usr/bin/env python3
"""
Test Alpaca API connection to verify account type
"""
import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

print("🔍 TESTING ALPACA API CONNECTION")
print("=" * 60)

# Load environment variables
load_dotenv()

# Get Alpaca keys
api_key = os.getenv('ALPACA_API_KEY')
api_secret = os.getenv('ALPACA_API_SECRET')

if not api_key or not api_secret:
    print("❌ ERROR: Alpaca API keys not found in .env file")
    exit(1)

print(f"✅ API Key found: {api_key[:10]}...")
print(f"✅ API Secret found: {api_secret[:10]}...")

# Try to connect to Alpaca
try:
    # First try LIVE trading endpoint
    print("\n🔗 Testing LIVE trading endpoint...")
    api = tradeapi.REST(
        api_key,
        api_secret,
        'https://api.alpaca.markets',  # LIVE trading
        api_version='v2'
    )
    
    account = api.get_account()
    print(f"✅ LIVE ACCOUNT CONNECTED!")
    print(f"   Account ID: {account.id}")
    print(f"   Status: {account.status}")
    print(f"   Buying Power: ${account.buying_power}")
    print(f"   Cash: ${account.cash}")
    print(f"   Portfolio Value: ${account.portfolio_value}")
    print(f"   Account Type: {'LIVE TRADING' if account.trading_blocked == False else 'RESTRICTED'}")
    
except Exception as e:
    print(f"❌ LIVE endpoint failed: {e}")
    
    # Try PAPER trading endpoint
    try:
        print("\n🔗 Testing PAPER trading endpoint...")
        api = tradeapi.REST(
            api_key,
            api_secret,
            'https://paper-api.alpaca.markets',  # PAPER trading
            api_version='v2'
        )
        
        account = api.get_account()
        print(f"✅ PAPER ACCOUNT CONNECTED!")
        print(f"   Account ID: {account.id}")
        print(f"   Status: {account.status}")
        print(f"   Buying Power: ${account.buying_power}")
        print(f"   Cash: ${account.cash}")
        print(f"   Portfolio Value: ${account.portfolio_value}")
        print(f"   Account Type: PAPER TRADING (Not real money)")
        
    except Exception as e2:
        print(f"❌ PAPER endpoint also failed: {e2}")
        print("\n🚨 CRITICAL: Cannot connect to Alpaca with provided keys")
        print("   Possible issues:")
        print("   1. Invalid API keys")
        print("   2. Account not activated")
        print("   3. Network/access issues")
        print("   4. Keys expired/revoked")

print("\n🎯 NEXT STEPS:")
print("1. Verify account type (LIVE vs PAPER)")
print("2. Check available balance for trading")
print("3. Build REAL arbitration trading bot")
print("4. Integrate with dashboard (REAL profits only)")