#!/usr/bin/env python3
"""
Detailed API key test to understand what's happening
"""

import ccxt
import os

def test_exchange(name, key_file, secret_file, exchange_class, test_symbol, main_currency, extra_config):
    print(f'\n{"="*60}')
    print(f'Testing {name}')
    print(f'{"="*60}')
    
    try:
        with open(key_file, 'r') as f:
            key = f.read().strip()
        with open(secret_file, 'r') as f:
            secret = f.read().strip()
        
        print(f'Key: {key[:6]}...{key[-6:] if len(key) > 12 else ""}')
        print(f'Key length: {len(key)}')
        
        # Create exchange
        exchange_config = {
            'apiKey': key,
            'secret': secret,
            'enableRateLimit': True,
        }
        exchange_config.update(extra_config)
        
        exchange = getattr(ccxt, exchange_class)(exchange_config)
        
        # Test 1: Public endpoint
        print('\n1. Testing public endpoint...')
        try:
            ticker = exchange.fetch_ticker(test_symbol)
            print(f'   ✅ Public OK: {test_symbol} = ${ticker["last"]:.2f}')
        except Exception as e:
            print(f'   ❌ Public failed: {e}')
            return False
        
        # Test 2: Private endpoint - different methods
        print('\n2. Testing private endpoints...')
        
        # Method A: fetch_balance
        print('   A. fetch_balance()...')
        try:
            balance = exchange.fetch_balance()
            total_dict = balance.get('total', {})
            free_dict = balance.get('free', {})
            used_dict = balance.get('used', {})
            
            asset_count = len([k for k, v in total_dict.items() if float(v) > 0])
            print(f'      ✅ Balance fetched')
            print(f'      Total assets: {len(total_dict)}')
            print(f'      Assets with balance > 0: {asset_count}')
            
            # Show actual balances
            # main_currency is already a parameter
            if main_currency in total_dict:
                print(f'      {main_currency} total: ${float(total_dict[main_currency]):.2f}')
                print(f'      {main_currency} free: ${float(free_dict.get(main_currency, 0)):.2f}')
                print(f'      {main_currency} used: ${float(used_dict.get(main_currency, 0)):.2f}')
            
            # Show top 5 non-zero balances
            non_zero = [(k, float(v)) for k, v in total_dict.items() if float(v) > 0 and k != main_currency]
            if non_zero:
                print(f'      Non-zero balances (top 5):')
                for asset, amount in sorted(non_zero, key=lambda x: x[1], reverse=True)[:5]:
                    print(f'        {asset}: {amount:.8f}')
            
            return True
            
        except Exception as e:
            print(f'      ❌ fetch_balance failed: {e}')
            
            # Try alternative: fetch_accounts or fetch_wallets
            print('   B. Trying alternative methods...')
            try:
                if hasattr(exchange, 'fetch_accounts'):
                    accounts = exchange.fetch_accounts()
                    print(f'      fetch_accounts: {len(accounts)} accounts')
                if hasattr(exchange, 'fetch_wallets'):
                    wallets = exchange.fetch_wallets()
                    print(f'      fetch_wallets: {len(wallets)} wallets')
            except Exception as e2:
                print(f'      ❌ Alternative methods also failed: {e2}')
            
            return False
            
    except Exception as e:
        print(f'❌ Setup failed: {e}')
        return False

# Test configurations
tests = [
    {
        'name': 'Binance Futures',
        'key_file': '.binance_key',
        'secret_file': '.binance_secret',
        'exchange_class': 'binance',
        'test_symbol': 'BTC/USDT',
        'main_currency': 'USDT',
        'extra_config': {'options': {'defaultType': 'future'}}
    },
    {
        'name': 'Binance Spot',
        'key_file': '.binance_key',
        'secret_file': '.binance_secret',
        'exchange_class': 'binance',
        'test_symbol': 'BTC/USDT',
        'main_currency': 'USDT',
        'extra_config': {'options': {'defaultType': 'spot'}}
    },
    {
        'name': 'Gemini',
        'key_file': '.gemini_key',
        'secret_file': '.gemini_secret',
        'exchange_class': 'gemini',
        'test_symbol': 'BTC/USD',
        'main_currency': 'USD',
        'extra_config': {}
    }
]

print('🔍 DETAILED API KEY DIAGNOSTIC')
print('='*60)

results = {}
for test in tests:
    results[test['name']] = test_exchange(
        name=test['name'],
        key_file=test['key_file'],
        secret_file=test['secret_file'],
        exchange_class=test['exchange_class'],
        test_symbol=test['test_symbol'],
        main_currency=test['main_currency'],
        extra_config=test['extra_config']
    )

print('\n' + '='*60)
print('SUMMARY')
print('='*60)

for name, success in results.items():
    status = '✅ PASS' if success else '❌ FAIL'
    print(f'{name}: {status}')

print('\n' + '='*60)
print('ANALYSIS')
print('='*60)

if not any(results.values()):
    print('All private endpoint tests failed. Possible issues:')
    print('1. API keys have restricted permissions (no balance access)')
    print('2. IP restrictions (API keys locked to specific IPs)')
    print('3. Keys expired or revoked')
    print('4. Exchange API issues')
elif results['Binance Spot'] and not results['Binance Futures']:
    print('Binance keys work for Spot but not Futures. Check Futures permissions.')
elif results['Binance Futures'] and not results['Binance Spot']:
    print('Binance keys work for Futures but not Spot. Unusual but possible.')
else:
    print('Mixed results. Check specific error messages above.')