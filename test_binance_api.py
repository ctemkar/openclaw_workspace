#!/usr/bin/env python3
"""
Test Binance API key
"""

import ccxt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API keys from environment
api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')

print("🔍 TESTING BINANCE API KEY")
print(f"API Key (first 8 chars): {api_key[:8]}...")
print(f"Secret (first 8 chars): {api_secret[:8]}...")
print()

if not api_key or not api_secret:
    print("❌ ERROR: API key or secret not found in .env file")
    print("Make sure .env file exists in current directory")
    exit(1)

try:
    # Initialize Binance with API keys
    binance = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot'
        }
    })
    
    print("✅ Binance exchange initialized")
    
    # Test 1: Fetch account balance (requires valid API key)
    print("📊 Testing: fetch_balance()...")
    balance = binance.fetch_balance()
    
    print(f"✅ SUCCESS! API key is VALID")
    print(f"💰 Account has {len(balance['total'])} assets")
    
    # Show MANA balance if available
    if 'MANA' in balance['total'] and balance['total']['MANA'] > 0:
        print(f"🎯 MANA Balance: {balance['total']['MANA']}")
    else:
        print("⚠️ MANA balance: 0.00 (or not found)")
    
    # Show USDT balance
    if 'USDT' in balance['total']:
        print(f"💵 USDT Balance: {balance['total']['USDT']}")
    
    # Test 2: Fetch ticker (public, should always work)
    print("\n📈 Testing: fetch_ticker('MANA/USDT')...")
    ticker = binance.fetch_ticker('MANA/USDT')
    print(f"✅ MANA Price: ${ticker['last']:.4f}")
    
    print("\n🎉 ALL TESTS PASSED! API KEY IS WORKING!")
    
except ccxt.AuthenticationError as e:
    print(f"❌ AUTHENTICATION ERROR: {e}")
    print("This means the API key or secret is INVALID")
    print("Please regenerate API key on Binance")
    
except ccxt.ExchangeError as e:
    print(f"❌ EXCHANGE ERROR: {e}")
    print("Possible issues:")
    print("1. Thailand IP blocked (try VPN)")
    print("2. API key permissions incorrect")
    print("3. Exchange maintenance")
    
except Exception as e:
    print(f"❌ UNEXPECTED ERROR: {e}")
    print("Check internet connection and try again")