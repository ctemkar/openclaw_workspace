#!/usr/bin/env python3
"""
Test Binance API keys using ccxt (same library the bots use)
"""

import os
import ccxt
from dotenv import load_dotenv

load_dotenv()

key = os.getenv('BINANCE_API_KEY')
secret = os.getenv('BINANCE_API_SECRET')

print("🔍 TESTING BINANCE API KEYS WITH CCXT")
print("=" * 50)
print(f"📋 Key loaded: {'Yes' if key else 'No'}")
print(f"📋 Secret loaded: {'Yes' if secret else 'No'}")

if not key or not secret:
    print("❌ ERROR: Missing API key or secret in .env file")
    exit(1)

print(f"🔑 Key: {key[:10]}...{key[-4:] if len(key) > 14 else ''}")
print(f"🔑 Secret: {secret[:10]}...{secret[-4:] if len(secret) > 14 else ''}")

try:
    print("\n🔄 Creating Binance exchange object...")
    
    # Create Binance exchange object (same as bots)
    exchange = ccxt.binance({
        'apiKey': key,
        'secret': secret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot',  # Spot trading
        }
    })
    
    print("✅ Exchange object created")
    
    # Test 1: Fetch balance
    print("\n1️⃣ Testing balance fetch...")
    try:
        balance = exchange.fetch_balance()
        print("✅ Balance fetch SUCCESS!")
        print(f"   Total assets: {len(balance.get('total', {}))}")
        
        # Show non-zero balances
        total = balance.get('total', {})
        non_zero = {k: v for k, v in total.items() if v > 0}
        
        print(f"   Non-zero balances: {len(non_zero)}")
        for asset, amount in list(non_zero.items())[:5]:
            print(f"     • {asset}: {amount:.8f}")
        
        if len(non_zero) > 5:
            print(f"     ... and {len(non_zero) - 5} more")
            
    except Exception as e:
        print(f"❌ Balance error: {type(e).__name__}: {e}")
        if hasattr(e, 'args') and len(e.args) > 0:
            error_msg = str(e.args[0])
            if "Invalid API-key" in error_msg or "invalid api-key" in error_msg.lower():
                print("   🔍 This confirms the API key is invalid!")
            elif "permissions" in error_msg.lower():
                print("   🔍 Check IP whitelist on Binance")
    
    # Test 2: Fetch ticker
    print("\n2️⃣ Testing market data...")
    try:
        ticker = exchange.fetch_ticker('BTC/USDT')
        print("✅ Market data SUCCESS!")
        print(f"   BTC/USDT: ${ticker['last']}")
    except Exception as e:
        print(f"❌ Market data error: {type(e).__name__}: {e}")
    
    # Test 3: Check if we can place orders (just check permissions)
    print("\n3️⃣ Checking order permissions...")
    try:
        # Just fetch open orders to test permissions
        orders = exchange.fetch_open_orders(symbol='BTC/USDT', limit=1)
        print(f"✅ Order permissions OK (found {len(orders)} open orders)")
    except Exception as e:
        error_msg = str(e)
        if "permissions" in error_msg.lower() or "not allowed" in error_msg.lower():
            print(f"❌ Order permissions error: {type(e).__name__}")
            print("   🔍 This suggests IP restrictions or trading disabled")
        else:
            print(f"ℹ️  Order check: {type(e).__name__}: {e}")
            print("   (This is normal if you have no open orders)")
    
except Exception as e:
    print(f"❌ General error: {type(e).__name__}: {e}")

print("\n" + "=" * 50)
print("💡 If balance fetch failed with 'Invalid API-key', you need to:")
print("   1. Log into Binance.com")
print("   2. Go to API Management")
print("   3. Create new API key")
print("   4. Update .env file")
print("   5. Restart bots")
print("=" * 50)