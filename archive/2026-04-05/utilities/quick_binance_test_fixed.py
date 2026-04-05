#!/usr/bin/env python3
import ccxt
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')

print('🔍 QUICK BINANCE TEST AFTER IP WHITELIST')
print('='*50)

if not api_key or not api_secret:
    print('❌ API keys not found')
    exit()

try:
    binance = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True
    })
    
    # Test 1: Balance
    try:
        balance = binance.fetch_balance()
        print('✅ BALANCE ACCESS WORKS!')
        print(f'   Total assets: {len(balance["total"])}')
        if 'MANA' in balance['total']:
            print(f'   MANA: {balance["total"]["MANA"]}')
        if 'USDT' in balance['total']:
            print(f'   USDT: {balance["total"]["USDT"]}')
    except Exception as e:
        print(f'❌ Balance failed: {e}')
    
    # Test 2: Price
    try:
        ticker = binance.fetch_ticker('MANA/USDT')
        print('✅ PRICE ACCESS WORKS!')
        print(f'   MANA: ${ticker["bid"]:.4f} - ${ticker["ask"]:.4f}')
    except Exception as e:
        print(f'❌ Price failed: {e}')
        
except Exception as e:
    print(f'❌ Connection failed: {e}')