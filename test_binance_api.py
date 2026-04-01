#!/usr/bin/env python3
"""
Test Binance API key functionality
"""

import ccxt
import os

print('🔍 Testing Binance API Key...')
try:
    with open('secure_keys/.binance_key', 'r') as f:
        key = f.read().strip()
    with open('secure_keys/.binance_secret', 'r') as f:
        secret = f.read().strip()
    
    print(f'Key length: {len(key)} chars')
    print(f'Secret length: {len(secret)} chars')
    
    # Try to initialize
    exchange = ccxt.binance({
        'apiKey': key,
        'secret': secret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future',
        }
    })
    print('✅ Binance Futures exchange object created')
    
    # Try a simple fetch
    try:
        ticker = exchange.fetch_ticker('BTC/USDT')
        print(f'✅ Binance API works! BTC price: ${ticker["last"]:.2f}')
        
        # Try to fetch balance
        try:
            balance = exchange.fetch_balance()
            usdt_balance = balance.get('total', {}).get('USDT', 0)
            print(f'✅ Binance balance fetch successful! USDT: ${usdt_balance:.2f}')
        except Exception as e:
            print(f'❌ Binance balance fetch failed: {e}')
            
    except Exception as e:
        print(f'❌ Binance ticker fetch failed: {e}')
        
except Exception as e:
    print(f'❌ Error: {e}')