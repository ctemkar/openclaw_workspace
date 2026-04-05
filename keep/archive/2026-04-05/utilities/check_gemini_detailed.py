#!/usr/bin/env python3
"""
Check Gemini in detail - all accounts and endpoints
"""

import ccxt
import os
import json
from datetime import datetime

print("🔍 DETAILED GEMINI CHECK")
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

# Initialize Gemini with different options
exchange = ccxt.gemini({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
    'options': {
        'fetchBalance': 'all',  # Try to get all account types
    }
})

print("✅ Connected to Gemini")

try:
    print(f"\n1️⃣ STANDARD BALANCE FETCH:")
    print("-" * 40)
    
    balance = exchange.fetch_balance()
    
    # Print all balance info
    print(f"Timestamp: {balance.get('timestamp', 'N/A')}")
    print(f"Datetime: {balance.get('datetime', 'N/A')}")
    
    print(f"\n💰 BALANCE TOTALS:")
    for currency in ['USD', 'BTC', 'ETH', 'SOL']:
        if currency in balance['total']:
            total = float(balance['total'][currency])
            free = float(balance['free'][currency])
            used = float(balance['used'][currency])
            
            if total > 0 or free > 0 or used > 0:
                print(f"   {currency}:")
                print(f"     Total: {total}")
                print(f"     Free: {free}")
                print(f"     Used: {used}")
    
    print(f"\n2️⃣ ALL CURRENCIES WITH BALANCES:")
    print("-" * 40)
    
    for currency, amount in balance['total'].items():
        amount_float = float(amount)
        if amount_float > 0.0001:  # More than tiny dust
            free = float(balance['free'].get(currency, 0))
            used = float(balance['used'].get(currency, 0))
            
            print(f"   {currency}:")
            print(f"     Total: {amount_float}")
            print(f"     Free: {free}")
            print(f"     Used: {used}")
            
            # Try to get price if it's a crypto
            if currency != 'USD':
                try:
                    symbol = f"{currency}/USD"
                    ticker = exchange.fetch_ticker(symbol)
                    price = float(ticker['last'])
                    value = amount_float * price
                    print(f"     Price: ${price:.2f}")
                    print(f"     Value: ${value:.2f}")
                except:
                    print(f"     Price: N/A")
    
    print(f"\n3️⃣ CHECK SPECIFIC ENDPOINTS:")
    print("-" * 40)
    
    # Try private endpoint
    print("Trying private API endpoint...")
    try:
        # Some exchanges have additional endpoints
        accounts = exchange.private_get_accounts()
        print(f"   Accounts found: {len(accounts)}")
        for acc in accounts:
            print(f"   Account: {acc.get('account', 'N/A')}, Name: {acc.get('name', 'N/A')}")
    except Exception as e:
        print(f"   Private accounts endpoint not available: {e}")
    
    print(f"\n4️⃣ TRADE HISTORY (last 10):")
    print("-" * 40)
    
    try:
        trades = exchange.fetch_my_trades(symbol='SOL/USD', limit=10)
        if trades:
            print(f"   Last {len(trades)} SOL trades:")
            for trade in trades:
                print(f"   {trade['datetime']}: {trade['side']} {trade['amount']} SOL @ ${trade['price']}")
        else:
            print(f"   No recent SOL trades found")
    except Exception as e:
        print(f"   Error fetching trades: {e}")
    
    print(f"\n5️⃣ ORDERS (open):")
    print("-" * 40)
    
    try:
        orders = exchange.fetch_open_orders(symbol='SOL/USD')
        if orders:
            print(f"   Open SOL orders: {len(orders)}")
            for order in orders:
                print(f"   {order['side']} {order['amount']} SOL @ ${order['price']} ({order['status']})")
        else:
            print(f"   No open SOL orders")
    except Exception as e:
        print(f"   Error fetching orders: {e}")
    
    print(f"\n🎯 CONCLUSION:")
    print("-" * 40)
    
    total_usd = float(balance['total'].get('USD', 0))
    print(f"   Total USD: ${total_usd:.2f}")
    
    # Calculate crypto value
    crypto_value = 0
    for currency, amount in balance['total'].items():
        if currency != 'USD' and float(amount) > 0.001:  # > 0.001 to filter dust
            try:
                symbol = f"{currency}/USD"
                ticker = exchange.fetch_ticker(symbol)
                price = float(ticker['last'])
                crypto_value += float(amount) * price
            except:
                pass
    
    print(f"   Crypto Value: ${crypto_value:.2f}")
    print(f"   Cash (USD - Crypto): ${total_usd - crypto_value:.2f}")
    
    if total_usd - crypto_value > total_usd * 0.9:
        print(f"   💡 NOTE: Most value is in CASH, not crypto")
    else:
        print(f"   💡 NOTE: Significant crypto holdings")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)