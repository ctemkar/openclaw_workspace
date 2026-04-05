#!/usr/bin/env python3
import os
import ccxt

print("=== CURRENT BALANCES AFTER SOL SALE ===")
print()

# Load environment
env_data = {}
try:
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if line and '=' in line and not line.startswith('#'):
                key, val = line.split('=', 1)
                env_data[key.strip()] = val.strip()
except Exception as e:
    print(f"Error loading .env: {e}")

total = 0

# Gemini
try:
    g = ccxt.gemini({
        'apiKey': env_data.get('GEMINI_API_KEY'),
        'secret': env_data.get('GEMINI_API_SECRET'),
    })
    g_bal = g.fetch_balance()
    g_usd = g_bal.get('USD', {}).get('free', 0)
    print(f"Gemini Free USD: ${g_usd:.2f}")
    total += g_usd
except Exception as e:
    print(f"Gemini error: {str(e)[:80]}")

# Binance Spot
try:
    bs = ccxt.binance({
        'apiKey': env_data.get('BINANCE_API_KEY'),
        'secret': env_data.get('BINANCE_API_SECRET'),
        'options': {'defaultType': 'spot'}
    })
    bs_bal = bs.fetch_balance()
    bs_usdt = bs_bal.get('USDT', {}).get('free', 0)
    print(f"Binance Spot Free USDT: ${bs_usdt:.2f}")
    total += bs_usdt
except Exception as e:
    print(f"Binance Spot error: {str(e)[:80]}")

# Binance Futures
try:
    bf = ccxt.binance({
        'apiKey': env_data.get('BINANCE_API_KEY'),
        'secret': env_data.get('BINANCE_API_SECRET'),
        'options': {'defaultType': 'future'}
    })
    bf_bal = bf.fetch_balance()
    bf_usdt = bf_bal.get('USDT', {}).get('free', 0)
    print(f"Binance Futures Free USDT: ${bf_usdt:.2f}")
    total += bf_usdt
except Exception as e:
    print(f"Binance Futures error: {str(e)[:80]}")

print(f"\n💰 TOTAL FREE CAPITAL: ${total:.2f}")
print(f"📈 20% Position Size: ${total * 0.20:.2f}")

if total >= 400:
    print("🎯 STATUS: EXCELLENT ($400+ available)")
elif total >= 200:
    print("🎯 STATUS: GOOD ($200+ available)")
elif total >= 100:
    print("🎯 STATUS: ADEQUATE ($100+ available)")
elif total >= 10:
    print("🎯 STATUS: MINIMAL ($10+ available)")
else:
    print("❌ STATUS: INSUFFICIENT (need $10 minimum)")