#!/usr/bin/env python3
"""
Check REAL Gemini holdings including SOL
"""

import ccxt
import os
import json

print("🔍 CHECKING REAL GEMINI HOLDINGS")
print("="*60)

# Read Gemini API keys
try:
    with open('secure_keys/.gemini_key', 'r') as f:
        api_key = f.read().strip()
    with open('secure_keys/.gemini_secret', 'r') as f:
        api_secret = f.read().strip()
except FileNotFoundError as e:
    print(f"❌ Error reading API keys: {e}")
    exit(1)

# Initialize Gemini
exchange = ccxt.gemini({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
})

print("✅ Connected to Gemini")

try:
    # Fetch complete balance
    balance = exchange.fetch_balance()
    
    print(f"\n💰 TOTAL BALANCE:")
    print(f"   USD Total: ${float(balance['total']['USD']):.2f}")
    print(f"   USD Free: ${float(balance['free']['USD']):.2f}")
    print(f"   USD Used: ${float(balance['used']['USD']):.2f}")
    
    print(f"\n📊 CRYPTO HOLDINGS:")
    
    # Check all cryptocurrencies with non-zero balances
    crypto_holdings = []
    total_crypto_value = 0
    
    for currency, amount in balance['total'].items():
        if currency != 'USD' and float(amount) > 0:
            # Get current price
            try:
                symbol = f"{currency}/USD"
                ticker = exchange.fetch_ticker(symbol)
                price = float(ticker['last'])
                value = float(amount) * price
                
                crypto_holdings.append({
                    'currency': currency,
                    'amount': float(amount),
                    'price': price,
                    'value': value
                })
                
                total_crypto_value += value
                
                print(f"   {currency}: {amount} coins")
                print(f"     Price: ${price:.2f}, Value: ${value:.2f}")
                
            except Exception as e:
                print(f"   {currency}: {amount} coins (price unavailable)")
    
    print(f"\n📈 SUMMARY:")
    print(f"   Total USD: ${float(balance['total']['USD']):.2f}")
    print(f"   Crypto Value: ${total_crypto_value:.2f}")
    print(f"   Cash USD: ${float(balance['total']['USD']) - total_crypto_value:.2f}")
    
    # Check specifically for SOL
    print(f"\n🔍 SPECIFICALLY CHECKING SOL:")
    try:
        sol_balance = float(balance['total'].get('SOL', 0))
        if sol_balance > 0:
            sol_ticker = exchange.fetch_ticker('SOL/USD')
            sol_price = float(sol_ticker['last'])
            sol_value = sol_balance * sol_price
            
            print(f"   SOL Balance: {sol_balance} SOL")
            print(f"   SOL Price: ${sol_price:.2f}")
            print(f"   SOL Value: ${sol_value:.2f}")
        else:
            print(f"   No SOL holdings found")
            
    except Exception as e:
        print(f"   Error checking SOL: {e}")
    
    # Update dashboard data with correct holdings
    print(f"\n🔄 UPDATING DASHBOARD DATA...")
    
    # Read existing capital data
    try:
        with open('trading_data/capital.json', 'r') as f:
            capital_data = json.load(f)
    except FileNotFoundError:
        capital_data = {}
    
    # Update with real Gemini data
    capital_data['gemini_total'] = float(balance['total']['USD'])
    capital_data['gemini_crypto_value'] = total_crypto_value
    capital_data['gemini_cash'] = float(balance['total']['USD']) - total_crypto_value
    capital_data['gemini_holdings'] = crypto_holdings
    
    if sol_balance > 0:
        capital_data['has_sol'] = True
        capital_data['sol_balance'] = sol_balance
        capital_data['sol_value'] = sol_value
    else:
        capital_data['has_sol'] = False
    
    # Write updated data
    with open('trading_data/capital.json', 'w') as f:
        json.dump(capital_data, f, indent=2)
    
    print(f"✅ Updated trading_data/capital.json with real Gemini holdings")
    
    # Also update system_status.json
    try:
        with open('system_status.json', 'r') as f:
            system_data = json.load(f)
    except FileNotFoundError:
        system_data = {'api': {}}
    
    if 'capital_allocation' not in system_data['api']:
        system_data['api']['capital_allocation'] = {}
    
    system_data['api']['capital_allocation']['gemini'] = float(balance['total']['USD'])
    system_data['api']['capital_allocation']['gemini_holdings'] = crypto_holdings
    
    with open('system_status.json', 'w') as f:
        json.dump(system_data, f, indent=2)
    
    print(f"✅ Updated system_status.json with Gemini holdings")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)