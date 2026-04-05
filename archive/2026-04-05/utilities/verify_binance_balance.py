#!/usr/bin/env python3
"""
Verify Binance balance
"""

import ccxt

with open('secure_keys/.binance_key', 'r') as f:
    b_key = f.read().strip()
with open('secure_keys/.binance_secret', 'r') as f:
    b_secret = f.read().strip()

exchange = ccxt.binance({'apiKey': b_key, 'secret': b_secret})
balance = exchange.fetch_balance()
usdt = balance['free'].get('USDT', 0)

print("💰 BINANCE BALANCE VERIFICATION:")
print(f"   USDT Balance: ${usdt:.2f}")
if usdt >= 50:
    extra = usdt - 50
    print(f"   ✅ SUFFICIENT for $50 shorts (${extra:.2f} extra)")
else:
    needed = 50 - usdt
    print(f"   ❌ INSUFFICIENT for $50 shorts (need ${needed:.2f} more)")