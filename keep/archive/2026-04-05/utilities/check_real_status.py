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

try:
    print('🔍 CHECKING REAL GEMINI STATUS')
    print('='*50)
    
    # Check balance
    balance = exchange.fetch_balance()
    usd = balance['free'].get('USD', 0)
    btc = balance['free'].get('BTC', 0)
    total_usd = balance['total'].get('USD', 0)
    total_btc = balance['total'].get('BTC', 0)
    
    print(f'💰 Free USD: ${usd:.2f}')
    print(f'💰 Free BTC: {btc:.6f}')
    print(f'💰 Total USD: ${total_usd:.2f}')
    print(f'💰 Total BTC: {total_btc:.6f}')
    
    # Calculate BTC value
    ticker = exchange.fetch_ticker('BTC/USD')
    btc_price = ticker['last']
    btc_value = total_btc * btc_price
    total_portfolio = total_usd + btc_value
    
    print(f'📈 Current BTC price: ${btc_price:.2f}')
    print(f'💰 BTC value: ${btc_value:.2f}')
    print(f'💰 Total portfolio: ${total_portfolio:.2f}')
    
    # Check open orders
    print()
    print('📋 Checking open orders...')
    try:
        open_orders = exchange.fetch_open_orders('BTC/USD')
        print(f'Open BTC orders: {len(open_orders)}')
        for order in open_orders[:3]:
            print(f'  {order["side"]} {order["amount"]:.6f} BTC @ ${order["price"]:.2f}')
    except:
        print('  Could not fetch open orders')
    
    # Check recent trades
    print()
    print('📊 Checking recent trades...')
    try:
        trades = exchange.fetch_my_trades('BTC/USD', limit=10)
        print(f'Recent BTC trades: {len(trades)}')
        for trade in trades[-5:]:
            time_str = datetime.fromtimestamp(trade['timestamp']/1000).strftime('%H:%M:%S')
            print(f'  {time_str} {trade["side"]} {trade["amount"]:.6f} BTC @ ${trade["price"]:.2f} (${trade["cost"]:.2f})')
    except:
        print('  Could not fetch trades')
    
    print()
    print('⚠️  DISCREPANCY ALERT')
    print('='*50)
    print('Daily trades.json shows 2 BTC buys totaling $406')
    print(f'But system shows capital: $175.53')
    print(f'And Gemini shows: ${total_portfolio:.2f} total')
    print()
    print('🚨 ACTION REQUIRED:')
    print('1. Stop all trading bots')
    print('2. Audit actual vs reported positions')
    print('3. Fix logging system')
    print('4. Reconcile capital')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()