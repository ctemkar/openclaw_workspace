#!/usr/bin/env python3
"""
Test the NEW Binance API keys that were just regenerated
"""

import os
import sys
from dotenv import load_dotenv

print("🔍 TESTING NEW BINANCE API KEYS")
print("=" * 60)

# Load environment variables
load_dotenv()

binance_key = os.getenv('BINANCE_API_KEY')
binance_secret = os.getenv('BINANCE_API_SECRET')

print(f"📋 Key loaded from .env: {'✅ YES' if binance_key else '❌ NO'}")
print(f"📋 Secret loaded from .env: {'✅ YES' if binance_secret else '❌ NO'}")

if not binance_key or not binance_secret:
    print("\n🚨 ERROR: Missing API key or secret in .env file")
    print("   Make sure BINANCE_API_KEY and BINANCE_API_SECRET are set")
    sys.exit(1)

print(f"\n🔑 Key (first/last 8 chars): {binance_key[:8]}...{binance_key[-8:]}")
print(f"🔑 Secret (first/last 8 chars): {binance_secret[:8]}...{binance_secret[-8:]}")
print(f"📏 Key length: {len(binance_key)} characters")
print(f"📏 Secret length: {len(binance_secret)} characters")

print("\n🔄 Testing connection with ccxt...")

try:
    import ccxt
    print(f"✅ ccxt version: {ccxt.__version__}")
    
    # Create exchange object (same as bots)
    exchange = ccxt.binance({
        'apiKey': binance_key,
        'secret': binance_secret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot',
        }
    })
    
    print("✅ Exchange object created successfully")
    
    # Test 1: Market data (public, doesn't need auth)
    print("\n1️⃣ Testing market data (public API)...")
    try:
        ticker = exchange.fetch_ticker('BTC/USDT')
        print(f"   ✅ Market data OK")
        print(f"   📊 BTC/USDT: ${ticker['last']}")
        print(f"   📈 24h change: {ticker['percentage']:.2f}%")
    except Exception as e:
        print(f"   ❌ Market data failed: {type(e).__name__}: {e}")
        print("   ⚠️  Even public data failed - check network/VPN")
    
    # Test 2: Account balance (private, needs valid keys)
    print("\n2️⃣ Testing account access (private API)...")
    try:
        balance = exchange.fetch_balance()
        print("   ✅ Account access SUCCESSFUL!")
        print(f"   📊 Account type: {balance.get('info', {}).get('accountType', 'spot')}")
        
        # Show balances
        total = balance.get('total', {})
        non_zero = {k: v for k, v in total.items() if v > 0}
        
        print(f"   💰 Non-zero balances: {len(non_zero)}")
        
        if non_zero:
            print("   📋 Balances:")
            for asset, amount in list(non_zero.items())[:10]:  # Show first 10
                print(f"     • {asset}: {amount:.8f}")
            if len(non_zero) > 10:
                print(f"     ... and {len(non_zero) - 10} more")
        else:
            print("   ℹ️  No balances found (account might be empty)")
            
        # Check for MANA specifically (for the arbitrage bot)
        if 'MANA' in total:
            mana_balance = total['MANA']
            print(f"\n   🎯 MANA balance: {mana_balance:.2f}")
            if mana_balance >= 50:
                print(f"   ✅ Sufficient MANA for trading (≥50)")
            else:
                print(f"   ⚠️  Insufficient MANA for trading (need ≥50, have {mana_balance:.2f})")
        else:
            print(f"\n   ⚠️  No MANA balance found")
            
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ Account access failed: {type(e).__name__}")
        print(f"   📝 Error: {error_msg[:200]}")
        
        # Common error analysis
        if "Invalid API-key" in error_msg or "invalid api-key" in error_msg.lower():
            print("\n   🚨 KEY ISSUE: API key is INVALID")
            print("   Possible reasons:")
            print("   • Key was just created and needs time to activate")
            print("   • Key/secret copied incorrectly")
            print("   • Key doesn't exist on Binance")
        elif "permissions" in error_msg.lower():
            print("\n   🚨 PERMISSIONS ISSUE: Check IP whitelist")
            print("   • Add your current IP to Binance API whitelist")
            print("   • Enable trading permissions")
        elif "IP" in error_msg.upper():
            print("\n   🚨 IP RESTRICTION: Your IP isn't whitelisted")
            print("   • Check Binance API settings")
            print("   • Add your IP to whitelist")
        else:
            print(f"\n   🔍 Unknown error type")
    
    # Test 3: Server time (simple API call)
    print("\n3️⃣ Testing server connectivity...")
    try:
        server_time = exchange.fetch_time()
        print(f"   ✅ Server time: {server_time}")
        print("   ✅ Full API connectivity confirmed")
    except Exception as e:
        print(f"   ❌ Server time failed: {type(e).__name__}: {e}")
    
except ImportError:
    print("❌ ERROR: ccxt library not installed")
    print("   Install with: pip install ccxt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {type(e).__name__}: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("🎯 TEST COMPLETE")
print("=" * 60)
print("\n💡 Next steps based on results:")
print("1. If ALL TESTS PASSED: Restart trading bots")
print("2. If ACCOUNT ACCESS FAILED: Check Binance API settings")
print("3. If MARKET DATA FAILED: Check network/VPN connection")
print("4. Update HEARTBEAT.md with new status")
print("\nReady to proceed when you are!")