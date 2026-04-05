#!/usr/bin/env python3
import ccxt
import os

with open('secure_keys/.gemini_key', 'r') as f:
    key = f.read().strip()
with open('secure_keys/.gemini_secret', 'r') as f:
    secret = f.read().strip()

exchange = ccxt.gemini({
    'apiKey': key,
    'secret': secret,
    'enableRateLimit': True
})

try:
    print('Testing Gemini API...')
    ticker = exchange.fetch_ticker('BTC/USD')
    print(f'BTC Price: ${ticker["last"]:.2f}')
    
    balance = exchange.fetch_balance()
    usd = balance['free'].get('USD', 0)
    print(f'USD Balance: ${usd:.2f}')
    
    # Test order book
    orderbook = exchange.fetch_order_book('BTC/USD')
    print(f'Bid: ${orderbook["bids"][0][0]:.2f}, Ask: ${orderbook["asks"][0][0]:.2f}')
    
    print('✅ API working!')
except Exception as e:
    print(f'❌ API error: {e}')
    import traceback
    traceback.print_exc()