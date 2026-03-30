#!/usr/bin/env python3
"""
Real market check with error handling
"""

import ccxt
from datetime import datetime

print("=" * 70)
print("REAL MARKET CHECK")
print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
print("=" * 70)

try:
    # Test Gemini
    print("\n🔍 Testing Gemini API...")
    gemini = ccxt.gemini()
    
    # Test BTC
    try:
        btc = gemini.fetch_ticker('BTC/USD')
        print(f"✅ BTC/USD: ${btc['last']:.2f}")
        print(f"   24h Change: {btc.get('percentage', 0):.2f}%")
    except Exception as e:
        print(f"❌ Gemini BTC error: {e}")
    
    # Test ETH
    try:
        eth = gemini.fetch_ticker('ETH/USD')
        print(f"✅ ETH/USD: ${eth['last']:.2f}")
        print(f"   24h Change: {eth.get('percentage', 0):.2f}%")
    except Exception as e:
        print(f"❌ Gemini ETH error: {e}")

except Exception as e:
    print(f"❌ Gemini init error: {e}")

try:
    # Test Binance
    print("\n🔍 Testing Binance API...")
    binance = ccxt.binance()
    
    # Test BTC
    try:
        btc = binance.fetch_ticker('BTC/USDT')
        print(f"✅ BTC/USDT: ${btc['last']:.2f}")
        print(f"   24h Change: {btc.get('percentage', 0):.2f}%")
    except Exception as e:
        print(f"❌ Binance BTC error: {e}")
    
    # Test ETH
    try:
        eth = binance.fetch_ticker('ETH/USDT')
        print(f"✅ ETH/USDT: ${eth['last']:.2f}")
        print(f"   24h Change: {eth.get('percentage', 0):.2f}%")
    except Exception as e:
        print(f"❌ Binance ETH error: {e}")

except Exception as e:
    print(f"❌ Binance init error: {e}")

print("\n" + "=" * 70)
print("DIAGNOSIS:")
print("=" * 70)

print("If APIs are failing:")
print("1. Internet connection issue")
print("2. Exchange API rate limiting")
print("3. CCXT library issue")
print("4. Market data temporarily unavailable")

print("\n💡 QUICK FIX:")
print("1. Check internet: ping 8.8.8.8")
print("2. Restart bot with: python3 simple_26_crypto_bot.py")
print("3. Check logs for specific errors")

print(f"\n⏰ Checked at: {datetime.now().strftime('%H:%M:%S')}")
print("=" * 70)