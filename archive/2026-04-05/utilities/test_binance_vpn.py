#!/usr/bin/env python3
"""
Test Binance API access with VPN (Singapore)
"""
import ccxt
import time

print("🔍 TESTING BINANCE ACCESS WITH SINGAPORE VPN")
print("=" * 70)

try:
    # Initialize Binance with VPN connection
    binance = ccxt.binance({
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot'
        }
    })
    
    print("✅ Binance exchange object created")
    
    # Test 1: Ping API
    print("\n🔗 Testing API ping...")
    try:
        result = binance.ping()
        print(f"   ✅ Ping successful: {result}")
    except Exception as e:
        print(f"   ❌ Ping failed: {e}")
    
    # Test 2: Fetch MANA price (what bot trades)
    print("\n💰 Testing MANA/USDT price fetch...")
    try:
        ticker = binance.fetch_ticker('MANA/USDT')
        print(f"   ✅ Price fetched successfully!")
        print(f"   📊 MANA/USDT:")
        print(f"      Bid: ${ticker['bid']:.4f}")
        print(f"      Ask: ${ticker['ask']:.4f}")
        print(f"      Last: ${ticker['last']:.4f}")
        print(f"      Spread: ${ticker['ask'] - ticker['bid']:.4f}")
    except Exception as e:
        print(f"   ❌ Price fetch failed: {e}")
    
    # Test 3: Check if we can get balance (if API keys available)
    print("\n👛 Testing account access...")
    try:
        # Try to load API keys from environment
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('BINANCE_API_KEY')
        api_secret = os.getenv('BINANCE_API_SECRET')
        
        if api_key and api_secret:
            binance_with_auth = ccxt.binance({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True
            })
            
            balance = binance_with_auth.fetch_balance()
            print(f"   ✅ Account access successful!")
            print(f"   💰 Total balance: {balance['total']}")
        else:
            print(f"   ⚠️  No API keys found in .env (public access only)")
    except Exception as e:
        print(f"   ❌ Account access failed: {e}")
    
    # Test 4: Check server time
    print("\n⏰ Testing server time...")
    try:
        server_time = binance.fetch_time()
        from datetime import datetime
        dt = datetime.fromtimestamp(server_time / 1000)
        print(f"   ✅ Server time: {dt}")
        print(f"   📡 Server responding from Singapore VPN")
    except Exception as e:
        print(f"   ❌ Server time failed: {e}")
    
    print("\n" + "="*70)
    print("🎯 VPN TEST RESULTS:")
    print("1. If ALL tests pass → VPN working perfectly!")
    print("2. If ping/price work but account fails → Need API keys")
    print("3. If ALL fail → VPN not working or Binance still blocked")
    print("\n🚀 NEXT: Restart trading bot with VPN connection")
    
except Exception as e:
    print(f"\n❌ CRITICAL ERROR: {e}")
    print("   VPN may not be working or Binance still detecting Thailand")