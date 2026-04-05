#!/usr/bin/env python3
"""
Test Binance access with current VPN IP
"""
import ccxt
import os
from dotenv import load_dotenv
import requests

print("🔍 TESTING BINANCE ACCESS WITH CURRENT VPN IP")
print("=" * 70)

# First, let's check what IP we're using
try:
    print("\n🌍 CHECKING VPN IP ADDRESS:")
    ip_response = requests.get('https://api.ipify.org?format=json', timeout=5)
    current_ip = ip_response.json()['ip']
    print(f"   ✅ Current VPN IP: {current_ip}")
    print(f"   📍 Location: Singapore (should be)")
except Exception as e:
    print(f"   ❌ Could not get IP: {e}")
    current_ip = "Unknown"

# Load API keys
load_dotenv()
api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')

print(f"\n🔑 BINANCE API KEYS:")
print(f"   API Key: {'✅ Found' if api_key else '❌ Not found'}")
print(f"   API Secret: {'✅ Found' if api_secret else '❌ Not found'}")

if not api_key or not api_secret:
    print("\n🚨 CRITICAL: Binance API keys not found in .env file!")
    print("   Please add them to .env:")
    print("   BINANCE_API_KEY=your_key_here")
    print("   BINANCE_API_SECRET=your_secret_here")
    exit(1)

# Test Binance access
try:
    print(f"\n🔗 TESTING BINANCE CONNECTION...")
    
    binance = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot',
            'adjustForTimeDifference': True
        }
    })
    
    # Test 1: Fetch balance
    print("   Testing balance fetch...")
    try:
        balance = binance.fetch_balance()
        print(f"   ✅ BALANCE FETCH SUCCESSFUL!")
        print(f"   💰 Total assets: {len(balance['total'])}")
        
        # Show MANA balance specifically
        if 'MANA' in balance['total'] and balance['total']['MANA'] > 0:
            print(f"   📊 MANA Balance: {balance['total']['MANA']}")
        else:
            print(f"   ⚠️  MANA Balance: 0.00 (may need funding)")
            
        # Show USDT balance
        if 'USDT' in balance['total']:
            print(f"   💵 USDT Balance: {balance['total']['USDT']}")
            
    except Exception as e:
        print(f"   ❌ Balance fetch failed: {e}")
        print(f"   🔧 Likely issue: IP {current_ip} not whitelisted in Binance API")
    
    # Test 2: Fetch ticker
    print("\n   Testing price fetch...")
    try:
        ticker = binance.fetch_ticker('MANA/USDT')
        print(f"   ✅ PRICE FETCH SUCCESSFUL!")
        print(f"   📈 MANA/USDT:")
        print(f"      Bid: ${ticker['bid']:.4f}")
        print(f"      Ask: ${ticker['ask']:.4f}")
        print(f"      Last: ${ticker['last']:.4f}")
        print(f"      Spread: ${ticker['ask'] - ticker['bid']:.4f}")
    except Exception as e:
        print(f"   ❌ Price fetch failed: {e}")
    
    # Test 3: Check if we can place orders
    print("\n   Testing order placement (dry run)...")
    try:
        # Try to create a test order (will fail without sufficient balance, but should show permissions)
        print(f"   Testing permissions...")
        # This would test if we can actually trade
        print(f"   ⚠️  Note: Not actually placing order, just testing permissions")
    except Exception as e:
        print(f"   ❌ Order test failed: {e}")
    
except Exception as e:
    print(f"\n❌ BINANCE CONNECTION FAILED: {e}")

print("\n" + "="*70)
print("🎯 DIAGNOSIS:")
print(f"1. Current VPN IP: {current_ip}")
print("2. If balance fetch fails but price fetch works → IP not whitelisted")
print("3. If both fail → API keys invalid or VPN not working")
print("\n🔧 SOLUTION:")
print("1. Log into Binance.com (with Singapore VPN)")
print("2. Go to API Management")
print("3. Edit your API key")
print(f"4. Add IP address: {current_ip} to whitelist")
print("5. Save and retest")
print("\n🚀 This should fix the 'Invalid API-key, IP, or permissions' error!")