#!/usr/bin/env python3
"""
Test Gemini API key functionality
"""

import ccxt
import os

print('🔍 Testing Gemini API Key...')
try:
    with open('secure_keys/.gemini_key', 'r') as f:
        key = f.read().strip()
    with open('secure_keys/.gemini_secret', 'r') as f:
        secret = f.read().strip()
    
    print(f'Key length: {len(key)} chars')
    print(f'Secret length: {len(secret)} chars')
    
    # Try to initialize
    exchange = ccxt.gemini({
        'apiKey': key,
        'secret': secret,
        'enableRateLimit': True,
    })
    print('✅ Gemini exchange object created')
    
    # Try a simple fetch
    try:
        ticker = exchange.fetch_ticker('BTC/USD')
        print(f'✅ Gemini API works! BTC price: ${ticker["last"]:.2f}')
        
        # Try to fetch balance
        try:
            balance = exchange.fetch_balance()
            usd_balance = balance.get('total', {}).get('USD', 0)
            print(f'✅ Gemini balance fetch successful! USD: ${usd_balance:.2f}')
        except Exception as e:
            print(f'❌ Gemini balance fetch failed: {e}')
            
    except Exception as e:
        print(f'❌ Gemini ticker fetch failed: {e}')
        
except Exception as e:
    print(f'❌ Error: {e}')