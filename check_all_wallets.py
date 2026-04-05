#!/usr/bin/env python3
"""Check all Binance wallets"""

import ccxt
import os

print("="*60)
print("🔍 CHECKING ALL BINANCE WALLETS")
print("="*60)

try:
    # Load API keys
    with open('secure_keys/.binance_key', 'r') as f:
        api_key = f.read().strip()
    with open('secure_keys/.binance_secret', 'r') as f:
        api_secret = f.read().strip()
    
    # Initialize Binance with different account types
    configs = {
        'spot': {'options': {'defaultType': 'spot'}},
        'margin': {'options': {'defaultType': 'margin'}},
        'futures': {'options': {'defaultType': 'future'}},
    }
    
    for acc_type, config in configs.items():
        print(f"\n📋 Checking {acc_type.upper()} account...")
        try:
            exchange = ccxt.binance({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
                **config
            })
            
            balance = exchange.fetch_balance()
            
            # Check USDT
            usdt_free = balance.get('USDT', {}).get('free', 0)
            usdt_total = balance.get('USDT', {}).get('total', 0)
            usdt_used = balance.get('USDT', {}).get('used', 0)
            
            if usdt_total > 0 or usdt_used > 0:
                print(f"   USDT Free: ${usdt_free:.2f}")
                print(f"   USDT Total: ${usdt_total:.2f}")
                print(f"   USDT Used: ${usdt_used:.2f}")
            
            # Check other currencies with balance
            print(f"   Other balances:")
            has_other = False
            for currency, data in balance.items():
                if isinstance(data, dict) and data.get('total', 0) > 0:
                    if currency not in ['USDT', 'info', 'free', 'used', 'total']:
                        print(f"     {currency}: {data.get('total', 0):.8f}")
                        has_other = True
            
            if not has_other:
                print("     None")
                
        except Exception as e:
            print(f"   ⚠️ Error checking {acc_type}: {e}")
    
    print("\n" + "="*60)
    print("🎯 POSSIBLE EXPLANATIONS:")
    print("   1. Funds in different account type (margin/futures)")
    print("   2. Open orders reserving funds")
    print("   3. API caching issue earlier")
    print("   4. Cross-margin or isolated position")
    print("="*60)
    
except Exception as e:
    print(f"❌ Error: {e}")