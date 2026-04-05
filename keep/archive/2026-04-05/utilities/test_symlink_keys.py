#!/usr/bin/env python3
"""
Test API keys using symbolic links (same as trading bot)
"""

import ccxt
import os

print('🔍 Testing API Keys via Symbolic Links (like trading bot)')
print('='*60)

# Test Gemini
print('\n=== Gemini Test ===')
try:
    with open('.gemini_key', 'r') as f:
        key = f.read().strip()
    with open('.gemini_secret', 'r') as f:
        secret = f.read().strip()
    
    print(f'API Key: {key[:4]}...{key[-4:] if len(key) > 8 else ""}')
    
    exchange = ccxt.gemini({
        'apiKey': key,
        'secret': secret,
        'enableRateLimit': True,
    })
    
    # Public test
    ticker = exchange.fetch_ticker('BTC/USD')
    print(f'✅ Public API OK (BTC/USD last: ${ticker["last"]:.2f})')
    
    # Private test
    balance = exchange.fetch_balance()
    usd_balance = balance.get('total', {}).get('USD', 0)
    asset_count = len([k for k, v in balance.get('total', {}).items() if v > 0])
    print(f'✅ Private API OK (asset entries: {asset_count}, USD: ${usd_balance:.2f})')
    
except Exception as e:
    print(f'❌ Gemini test failed: {e}')

# Test Binance
print('\n=== Binance Test ===')
try:
    with open('.binance_key', 'r') as f:
        key = f.read().strip()
    with open('.binance_secret', 'r') as f:
        secret = f.read().strip()
    
    print(f'API Key: {key[:4]}...{key[-4:] if len(key) > 8 else ""}')
    
    exchange = ccxt.binance({
        'apiKey': key,
        'secret': secret,
        'enableRateLimit': True,
        'options': {'defaultType': 'future'},
    })
    
    # Public test
    ticker = exchange.fetch_ticker('BTC/USDT')
    print(f'✅ Public API OK (BTC/USDT last: ${ticker["last"]:.2f})')
    
    # Private test
    balance = exchange.fetch_balance()
    usdt_balance = balance.get('total', {}).get('USDT', 0)
    asset_count = len([k for k, v in balance.get('total', {}).items() if v > 0])
    print(f'✅ Private API OK (asset entries: {asset_count}, USDT: ${usdt_balance:.2f})')
    
except Exception as e:
    print(f'❌ Binance test failed: {e}')

print('\n=== Summary ===')
print('Testing complete using symbolic links (same path as trading bot)')