#!/usr/bin/env python3
"""
Full Binance balance check
"""

import ccxt

with open('secure_keys/.binance_key', 'r') as f:
    b_key = f.read().strip()
with open('secure_keys/.binance_secret', 'r') as f:
    b_secret = f.read().strip()

exchange = ccxt.binance({'apiKey': b_key, 'secret': b_secret})
balance = exchange.fetch_balance()

print("🔍 FULL BINANCE BALANCE CHECK:")
print("="*40)
for currency, amount in balance['total'].items():
    if amount > 0:
        print(f"{currency}: {amount}")
print("="*40)

usdt = balance['total'].get('USDT', 0)
print(f"Total USDT: ${usdt:.2f}")

# Check if deposit might be pending
print("\n📊 Balance Details:")
print(f"Free USDT: ${balance['free'].get('USDT', 0):.2f}")
print(f"Used USDT: ${balance['used'].get('USDT', 0):.2f}")
print(f"Total USDT: ${balance['total'].get('USDT', 0):.2f}")