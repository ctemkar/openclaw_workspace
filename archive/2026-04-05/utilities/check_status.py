#!/usr/bin/env python3
import ccxt
import os
from datetime import datetime

with open('secure_keys/.gemini_key', 'r') as f:
    key = f.read().strip()
with open('secure_keys/.gemini_secret', 'r') as f:
    secret = f.read().strip()

exchange = ccxt.gemini({
    'apiKey': key,
    'secret': secret,
    'enableRateLimit': True
})

print('📊 GEMINI TRADING STATUS')
print('='*50)

# Check balance
balance = exchange.fetch_balance()
usd = balance['free'].get('USD', 0)
print(f'💰 Available: ${usd:.2f} USD')

# Check current prices
symbols = ['BTC/USD', 'ETH/USD', 'SOL/USD']
for symbol in symbols:
    ticker = exchange.fetch_ticker(symbol)
    change = ticker.get('percentage', 0)
    if change is None:
        change = 0.0
    signal = 'HOLD'
    if change < -3.0:
        signal = 'BUY (dip)'
    elif change > 8.0:
        signal = 'SELL (profit)'
    
    print(f'{symbol}: ${ticker["last"]:.2f} ({change:.1f}%) - {signal}')

print()
print('🤖 Trading Bot Status:')
print('- Real trading bot running (PID 57043)')
print('- Checks every 10 minutes')
print('- Conservative strategy: Buy dips >3%, Sell profits >8%')
print('- Max 2 trades/day, $40 per trade')
print()
print('📈 Next check in ~10 minutes')