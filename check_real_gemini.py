#!/usr/bin/env python3
import ccxt
import os

print('🔍 CHECKING REAL GEMINI BALANCE')
print('='*50)

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
    # Get REAL balance
    balance = exchange.fetch_balance()
    print('💰 REAL GEMINI BALANCE:')
    for currency, amount in balance['total'].items():
        if amount > 0:
            print(f'  {currency}: {amount}')
    
    # Calculate total USD value
    usd = balance['total'].get('USD', 0)
    btc = balance['total'].get('BTC', 0)
    eth = balance['total'].get('ETH', 0)
    sol = balance['total'].get('SOL', 0)
    
    # Get current prices
    if btc > 0:
        btc_ticker = exchange.fetch_ticker('BTC/USD')
        btc_value = btc * btc_ticker['last']
    else:
        btc_value = 0
    
    if eth > 0:
        eth_ticker = exchange.fetch_ticker('ETH/USD')
        eth_value = eth * eth_ticker['last']
    else:
        eth_value = 0
    
    if sol > 0:
        sol_ticker = exchange.fetch_ticker('SOL/USD')
        sol_value = sol * sol_ticker['last']
    else:
        sol_value = 0
    
    total_value = usd + btc_value + eth_value + sol_value
    
    print(f'\n📊 TOTAL PORTFOLIO VALUE: ${total_value:.2f}')
    print(f'  USD: ${usd:.2f}')
    if btc > 0:
        print(f'  BTC: {btc:.8f} (${btc_value:.2f})')
    if eth > 0:
        print(f'  ETH: {eth:.8f} (${eth_value:.2f})')
    if sol > 0:
        print(f'  SOL: {sol:.8f} (${sol_value:.2f})')
    
    print(f'\n🎯 Your screenshot shows:')
    print(f'  USD: $563.07')
    print(f'  ETH: 0.0023499 ETH (~$4.80)')
    print(f'  SOL: 0.05986488 SOL (~$4.73)')
    print(f'  Total: ~$572.60')
    
    print(f'\n🚨 DISCREPANCY ANALYSIS:')
    print(f'  If system shows 22 trades but Gemini shows minimal holdings...')
    print(f'  The trading bot might be:')
    print(f'  1. Trading in simulation mode')
    print(f'  2. Using wrong API keys')
    print(f'  3. Logging but not executing trades')
    print(f'  4. Reading from stale database')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()