#!/usr/bin/env python3
"""
Simple Binance balance check using ccxt
"""

import ccxt
import os

print("🔍 Checking Binance Balance with CCXT")
print("="*60)

# Read API keys
try:
    with open('secure_keys/.binance_key', 'r') as f:
        api_key = f.read().strip()
    with open('secure_keys/.binance_secret', 'r') as f:
        api_secret = f.read().strip()
except FileNotFoundError as e:
    print(f"❌ Error reading API keys: {e}")
    exit(1)

try:
    # Initialize Binance Futures
    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'options': {
            'defaultType': 'future',
        },
        'enableRateLimit': True,
    })
    
    print("✅ Connected to Binance Futures")
    
    # Fetch balance
    balance = exchange.fetch_balance()
    
    print(f"\n💰 Total Balance: ${float(balance['total']['USDT']):.2f}")
    print(f"💵 Free Balance: ${float(balance['free']['USDT']):.2f}")
    print(f"📊 Used Balance: ${float(balance['used']['USDT']):.2f}")
    
    # Check if we have any open positions
    positions = exchange.fetch_positions()
    open_positions = [p for p in positions if float(p['contracts']) > 0]
    
    print(f"\n📈 Open Positions: {len(open_positions)}")
    for pos in open_positions:
        print(f"   {pos['symbol']}: {pos['contracts']} contracts")
        print(f"     Entry: ${pos['entryPrice']}, Current: ${pos['markPrice']}")
        print(f"     P&L: ${pos['unrealizedPnl']}")
    
    # Check margin requirements
    free_usdt = float(balance['free']['USDT'])
    required = 13.43  # What the bot is trying to trade
    
    print(f"\n🔍 Can we trade ${required:.2f}?")
    print(f"   Free USDT: ${free_usdt:.2f}")
    
    if free_usdt >= required:
        print(f"   ✅ YES - Sufficient funds")
    else:
        print(f"   ❌ NO - Need ${required - free_usdt:.2f} more")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)