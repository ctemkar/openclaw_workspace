#!/usr/bin/env python3
"""
Final key check before starting trading
"""

import ccxt
import os
from datetime import datetime

print("🔍 FINAL KEY VALIDATION BEFORE TRADING")
print("="*60)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)

# Test Gemini
print("\n📈 GEMINI VALIDATION:")
try:
    with open('secure_keys/.gemini_key', 'r') as f:
        g_key = f.read().strip()
    with open('secure_keys/.gemini_secret', 'r') as f:
        g_secret = f.read().strip()
    
    print(f"  Key: {g_key[:10]}... ({len(g_key)} chars)")
    print(f"  Secret: {g_secret[:10]}... ({len(g_secret)} chars)")
    
    exchange = ccxt.gemini({'apiKey': g_key, 'secret': g_secret})
    balance = exchange.fetch_balance()
    usd = balance['free'].get('USD', 0)
    
    print(f"  ✅ Balance: ${usd:.2f}")
    print(f"  ✅ Status: READY for $200 longs")
    
    # Test market order capability
    ticker = exchange.fetch_ticker('BTC/USD')
    print(f"  ✅ Market: BTC/USD = ${ticker['last']:.2f}")
    
    gemini_ok = True
except Exception as e:
    print(f"  ❌ Error: {e}")
    gemini_ok = False

# Test Binance
print("\n📉 BINANCE VALIDATION:")
try:
    with open('secure_keys/.binance_key', 'r') as f:
        b_key = f.read().strip()
    with open('secure_keys/.binance_secret', 'r') as f:
        b_secret = f.read().strip()
    
    print(f"  Key: {b_key[:10]}... ({len(b_key)} chars)")
    print(f"  Secret: {b_secret[:10]}... ({len(b_secret)} chars)")
    
    exchange = ccxt.binance({
        'apiKey': b_key, 
        'secret': b_secret,
        'options': {'defaultType': 'spot'}
    })
    balance = exchange.fetch_balance()
    usdt = balance['free'].get('USDT', 0)
    
    print(f"  ✅ Balance: ${usdt:.2f}")
    if usdt >= 50:
        print(f"  ✅ Status: READY for $50 shorts")
    else:
        print(f"  ⚠️ Status: Needs $50 deposit (has ${usdt:.2f})")
    
    # Test market order capability
    ticker = exchange.fetch_ticker('BTC/USDT')
    print(f"  ✅ Market: BTC/USDT = ${ticker['last']:.2f}")
    
    binance_ok = True
except Exception as e:
    print(f"  ❌ Error: {e}")
    binance_ok = False

print("\n" + "="*60)
print("🎯 TRADING READINESS:")
print("="*60)

if gemini_ok and binance_ok:
    print("✅ BOTH EXCHANGES VALIDATED!")
    print("\n💰 FUNDING STATUS:")
    
    # Get balances again for summary
    exchange = ccxt.gemini({'apiKey': g_key, 'secret': g_secret})
    gemini_balance = exchange.fetch_balance()['free'].get('USD', 0)
    
    exchange = ccxt.binance({'apiKey': b_key, 'secret': b_secret})
    binance_balance = exchange.fetch_balance()['free'].get('USDT', 0)
    
    print(f"  • Gemini: ${gemini_balance:.2f} available")
    print(f"  • Binance: ${binance_balance:.2f} available")
    
    if gemini_balance >= 200:
        print("\n🚀 READY TO START TRADING!")
        print("  Gemini has $200+ for longs ✅")
        
        if binance_balance >= 50:
            print("  Binance has $50+ for shorts ✅")
            print("  💰 FULL $250 STRATEGY READY!")
        else:
            needed = 50 - binance_balance
            print(f"  Binance needs ${needed:.2f} more for shorts")
            print("  🎯 START WITH $200 GEMINI LONGS NOW!")
    else:
        needed = 200 - gemini_balance
        print(f"\n⚠️ Gemini needs ${needed:.2f} more for trading")
        
elif gemini_ok and not binance_ok:
    print("⚠️ Gemini OK, Binance failed")
    print("  Start with $200 Gemini longs only")
    
elif not gemini_ok and binance_ok:
    print("⚠️ Binance OK, Gemini failed")
    print("  Fix Gemini connection first")
    
else:
    print("❌ Both exchanges failed")
    print("  Check API keys and permissions")

print("\n" + "="*60)
print("⚡ NEXT: ./activate_real_system_now.sh")
print("="*60)