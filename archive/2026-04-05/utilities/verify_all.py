#!/usr/bin/env python3
"""
Verify both exchanges
"""

import ccxt

print("🔍 VERIFYING BOTH EXCHANGES:")
print("="*50)

# Test Gemini
try:
    with open('secure_keys/.gemini_key', 'r') as f:
        g_key = f.read().strip()
    with open('secure_keys/.gemini_secret', 'r') as f:
        g_secret = f.read().strip()
    
    exchange = ccxt.gemini({'apiKey': g_key, 'secret': g_secret})
    balance = exchange.fetch_balance()
    usd = balance['free'].get('USD', 0)
    print(f"📈 GEMINI: ${usd:.2f} USD ✅")
except Exception as e:
    print(f"📈 GEMINI: ❌ {e}")

# Test Binance  
try:
    with open('secure_keys/.binance_key', 'r') as f:
        b_key = f.read().strip()
    with open('secure_keys/.binance_secret', 'r') as f:
        b_secret = f.read().strip()
    
    exchange = ccxt.binance({'apiKey': b_key, 'secret': b_secret})
    balance = exchange.fetch_balance()
    usdt = balance['free'].get('USDT', 0)
    print(f"📉 BINANCE: ${usdt:.2f} USDT ✅")
except Exception as e:
    print(f"📉 BINANCE: ❌ {e}")

print("="*50)