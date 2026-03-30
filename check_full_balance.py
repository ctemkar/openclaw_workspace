#!/usr/bin/env python3
"""
Check full Binance balance
"""

import ccxt

with open('secure_keys/.binance_key', 'r') as f:
    b_key = f.read().strip()
with open('secure_keys/.binance_secret', 'r') as f:
    b_secret = f.read().strip()

exchange = ccxt.binance({'apiKey': b_key, 'secret': b_secret})
balance = exchange.fetch_balance()

print("💰 FULL BINANCE BALANCE CHECK:")
print("="*40)

# Check all currencies with balance > 0
for currency, amount in balance['total'].items():
    if amount > 0:
        print(f"{currency}: {amount}")

print("="*40)
print(f"Free USDT: ${balance['free'].get('USDT', 0):.2f}")
print(f"Used USDT: ${balance['used'].get('USDT', 0):.2f}")
print(f"Total USDT: ${balance['total'].get('USDT', 0):.2f}")

# Check if deposit might be pending
print("\n🔍 If you see $0.00 but expect $77:")
print("   1. Deposit might still be processing")
print("   2. Check Binance app/website")
print("   3. USDT might be in 'Funding' account")
print("   4. Might need to transfer from Spot to Funding")