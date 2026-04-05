#!/usr/bin/env python3
"""Calculate total portfolio value"""

import ccxt
import os

print("="*60)
print("💰 CALCULATING TOTAL PORTFOLIO VALUE")
print("="*60)

try:
    # Load API keys
    with open('secure_keys/.binance_key', 'r') as f:
        api_key = f.read().strip()
    with open('secure_keys/.binance_secret', 'r') as f:
        api_secret = f.read().strip()
    
    # Initialize Binance
    binance = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
    
    # Get balance
    balance = binance.fetch_balance()
    
    # Portfolio
    portfolio = {
        'USDT': balance.get('USDT', {}).get('total', 0),
        'YFI': balance.get('YFI', {}).get('total', 0),
        'ETH': balance.get('ETH', {}).get('total', 0),
        'MANA': balance.get('MANA', {}).get('total', 0),
        'ADA': balance.get('ADA', {}).get('total', 0),
        'USDC': balance.get('USDC', {}).get('total', 0),
        'DOGE': balance.get('DOGE', {}).get('total', 0),
        'SOL': balance.get('SOL', {}).get('total', 0),
        'DOT': balance.get('DOT', {}).get('total', 0),
        'UNI': balance.get('UNI', {}).get('total', 0),
    }
    
    print("📊 PORTFOLIO HOLDINGS:")
    total_value = 0
    
    for coin, amount in portfolio.items():
        if amount > 0:
            if coin == 'USDT' or coin == 'USDC':
                value = amount  # Stablecoins
                print(f"   {coin}: {amount:.8f} = ${value:.2f}")
                total_value += value
            else:
                # Get current price
                try:
                    if coin == 'YFI':
                        ticker = binance.fetch_ticker('YFI/USDT')
                    else:
                        ticker = binance.fetch_ticker(f'{coin}/USDT')
                    
                    price = ticker['last']
                    value = amount * price
                    print(f"   {coin}: {amount:.8f} @ ${price:.2f} = ${value:.2f}")
                    total_value += value
                except Exception as e:
                    print(f"   {coin}: {amount:.8f} (price unavailable)")
    
    print("\n" + "="*60)
    print(f"💰 TOTAL PORTFOLIO VALUE: ${total_value:.2f}")
    print(f"📈 USDT Only: ${portfolio['USDT']:.2f}")
    print(f"📊 Crypto Value: ${total_value - portfolio['USDT']:.2f}")
    print("="*60)
    
    # Check if earlier $56.77 could have been TOTAL portfolio
    print("\n🎯 ANALYSIS:")
    print(f"   Earlier reported: $56.77 (21:32)")
    print(f"   Current total: ${total_value:.2f}")
    print(f"   USDT only: ${portfolio['USDT']:.2f}")
    print(f"   Difference: ${abs(56.77 - total_value):.2f}")
    
    if abs(56.77 - total_value) < 5:
        print("   ✅ $56.77 was likely TOTAL portfolio value (not just USDT)")
    else:
        print("   ❓ Still unexplained difference")
    
except Exception as e:
    print(f"❌ Error: {e}")