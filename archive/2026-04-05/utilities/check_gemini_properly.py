#!/usr/bin/env python3
"""
Check Gemini PROPERLY using ccxt like the trading bot does
"""

import ccxt
import os
import json
from datetime import datetime

print("🔍 CHECKING GEMINI PROPERLY (using ccxt)")
print("="*60)

# Load API keys
try:
    with open("secure_keys/.gemini_key", "r") as f:
        GEMINI_KEY = f.read().strip()
    with open("secure_keys/.gemini_secret", "r") as f:
        GEMINI_SECRET = f.read().strip()
    print("✅ Gemini API keys loaded")
except Exception as e:
    print(f"❌ Failed to load API keys: {e}")
    exit(1)

# Initialize exchange EXACTLY like the trading bot
exchange = ccxt.gemini({
    'apiKey': GEMINI_KEY,
    'secret': GEMINI_SECRET,
    'enableRateLimit': True,
})

print("\n💰 CHECKING BALANCES...")
try:
    balance = exchange.fetch_balance()
    print("✅ Balance retrieved successfully")
    
    total_usd = balance['total'].get('USD', 0)
    free_usd = balance['free'].get('USD', 0)
    used_usd = balance['used'].get('USD', 0)
    
    total_btc = balance['total'].get('BTC', 0)
    free_btc = balance['free'].get('BTC', 0)
    used_btc = balance['used'].get('BTC', 0)
    
    print(f"  USD: {total_usd:.2f} (Free: {free_usd:.2f}, Used: {used_usd:.2f})")
    print(f"  BTC: {total_btc:.8f} (Free: {free_btc:.8f}, Used: {used_btc:.8f})")
    
    # Calculate portfolio value
    ticker = exchange.fetch_ticker('BTC/USD')
    btc_price = ticker['last']
    print(f"  Current BTC price: ${btc_price:,.2f}")
    
    portfolio_value = total_usd + (total_btc * btc_price)
    print(f"  Portfolio value: ${portfolio_value:,.2f}")
    
except Exception as e:
    print(f"❌ Failed to get balance: {e}")

print("\n📊 CHECKING TRADE HISTORY...")
try:
    # Get trades for today
    since = exchange.parse8601(datetime.now().strftime('%Y-%m-%dT00:00:00Z'))
    trades = exchange.fetch_my_trades('BTC/USD', since=since, limit=50)
    
    print(f"✅ Found {len(trades)} BTC/USD trades today")
    
    if trades:
        total_buys = 0
        total_sells = 0
        btc_bought = 0
        btc_sold = 0
        
        print("  Recent trades:")
        for trade in trades[-10:]:  # Last 10 trades
            time_str = exchange.iso8601(trade['timestamp'])
            side = trade['side'].upper()
            price = trade['price']
            amount = trade['amount']
            cost = trade['cost']
            
            print(f"    {time_str[11:19]} - {side} {amount:.6f} BTC @ ${price:,.2f} (${cost:,.2f})")
            
            if side == 'BUY':
                total_buys += cost
                btc_bought += amount
            else:
                total_sells += cost
                btc_sold += amount
        
        print(f"\n  📈 Today's summary:")
        print(f"    BTC bought: {btc_bought:.6f} (${total_buys:,.2f})")
        print(f"    BTC sold: {btc_sold:.6f} (${total_sells:,.2f})")
        print(f"    Net BTC: {btc_bought - btc_sold:.6f}")
        print(f"    Net USD: ${total_sells - total_buys:,.2f}")
        
except Exception as e:
    print(f"❌ Failed to get trades: {e}")

print("\n📋 CHECKING OPEN ORDERS...")
try:
    open_orders = exchange.fetch_open_orders('BTC/USD')
    print(f"✅ Found {len(open_orders)} open BTC/USD orders")
    
    for order in open_orders[:5]:
        side = order['side'].upper()
        price = order['price']
        amount = order['amount']
        remaining = order['remaining']
        print(f"  {side} {remaining:.6f}/{amount:.6f} BTC @ ${price:,.2f}")
        
except Exception as e:
    print(f"❌ Failed to get open orders: {e}")

print("\n" + "="*60)
print("🎯 ACTION PLAN BASED ON REAL DATA:")
print("1. Know EXACT balance and positions")
print("2. Fix broken logging/tracking system")
print("3. Resume trading with PROPER monitoring")
print("4. Grow the money (mission!)")
print("="*60)