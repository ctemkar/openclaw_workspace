#!/usr/bin/env python3
import ccxt
import os
import json

with open('.gemini_key', 'r') as f:
    key = f.read().strip()
with open('.gemini_secret', 'r') as f:
    secret = f.read().strip()

exchange = ccxt.gemini({
    'apiKey': key,
    'secret': secret,
    'enableRateLimit': True
})

# Check balance
balance = exchange.fetch_balance()
print('Updated Balance:')
print(f"USD: ${balance['free'].get('USD', 0):,.2f}")
print(f"BTC: {balance['free'].get('BTC', 0):.6f}")

# Check open orders
print('\nChecking for open orders...')
try:
    open_orders = exchange.fetch_open_orders('BTC/USD')
    print(f'Open orders: {len(open_orders)}')
    for order in open_orders:
        print(f"  ID: {order['id']}, Status: {order['status']}, Amount: {order['amount']}")
except Exception as e:
    print(f'Error checking orders: {e}')

# Check trade history
print('\nRecent trades:')
try:
    trades = exchange.fetch_my_trades('BTC/USD', limit=5)
    for trade in trades:
        print(f"  {trade['datetime']}: {trade['side']} {trade['amount']} BTC @ ${trade['price']:.2f}")
except Exception as e:
    print(f'Error fetching trades: {e}')

# Check current price
print('\nCurrent Market:')
try:
    ticker = exchange.fetch_ticker('BTC/USD')
    print(f"BTC Price: ${ticker['last']:.2f}")
    print(f"24h Change: {ticker['percentage']:.2f}%")
except Exception as e:
    print(f'Error fetching ticker: {e}')