#!/usr/bin/env python3
"""
Check Gemini exchange transactions and compare with logs
"""

import ccxt
import json
from datetime import datetime, timedelta

print("🔍 CHECKING GEMINI TRANSACTION HISTORY")
print("="*60)

try:
    # Load Gemini keys
    with open('secure_keys/.gemini_key', 'r') as f:
        g_key = f.read().strip()
    with open('secure_keys/.gemini_secret', 'r') as f:
        g_secret = f.read().strip()
    
    # Initialize exchange
    exchange = ccxt.gemini({
        'apiKey': g_key,
        'secret': g_secret,
        'enableRateLimit': True
    })
    
    print("✅ Gemini connection established")
    
    # Get balance
    balance = exchange.fetch_balance()
    usd_balance = balance['free'].get('USD', 0)
    print(f"💰 Current Gemini Balance: ${usd_balance:.2f} USD")
    
    # Try to fetch recent trades (last 24 hours)
    print("\n📊 Attempting to fetch recent trades...")
    
    # Check for BTC/USD trades
    try:
        since_time = exchange.milliseconds() - 86400000  # 24 hours ago
        trades = exchange.fetch_my_trades('BTC/USD', since=since_time)
        print(f"   BTC/USD trades found: {len(trades)}")
        for i, trade in enumerate(trades[:5]):  # Show first 5
            trade_time = exchange.iso8601(trade['timestamp'])
            print(f"   Trade {i+1}: {trade_time} - {trade['side']} {trade['amount']} BTC @ ${trade['price']:.2f}")
    except Exception as e:
        print(f"   ❌ Could not fetch BTC/USD trades: {e}")
    
    # Check for ETH/USD trades
    try:
        since_time = exchange.milliseconds() - 86400000
        trades = exchange.fetch_my_trades('ETH/USD', since=since_time)
        print(f"   ETH/USD trades found: {len(trades)}")
        for i, trade in enumerate(trades[:5]):
            trade_time = exchange.iso8601(trade['timestamp'])
            print(f"   Trade {i+1}: {trade_time} - {trade['side']} {trade['amount']} ETH @ ${trade['price']:.2f}")
    except Exception as e:
        print(f"   ❌ Could not fetch ETH/USD trades: {e}")
    
    # Get order history
    print("\n📋 Checking order history...")
    try:
        since_time = exchange.milliseconds() - 86400000
        orders = exchange.fetch_orders(since=since_time)
        print(f"   Total orders (last 24h): {len(orders)}")
        
        # Filter for today's orders
        today_orders = []
        for order in orders:
            order_time = exchange.iso8601(order['timestamp'])
            if '2026-03-31' in order_time:
                today_orders.append(order)
        
        print(f"   Today's orders (Mar 31): {len(today_orders)}")
        for order in today_orders[:5]:
            order_time = exchange.iso8601(order['timestamp'])
            print(f"   - {order_time}: {order['symbol']} - {order['side']} {order['status']} ({order.get('filled', 0)} filled)")
            
    except Exception as e:
        print(f"   ❌ Could not fetch orders: {e}")
    
    # Check open positions
    print("\n📈 Checking open positions...")
    try:
        open_orders = exchange.fetch_open_orders()
        print(f"   Open orders: {len(open_orders)}")
        for order in open_orders[:3]:
            print(f"   - {order['symbol']}: {order['side']} {order['amount']} @ ${order['price']}")
    except Exception as e:
        print(f"   ❌ Could not fetch open orders: {e}")
    
except Exception as e:
    print(f"❌ Error checking Gemini: {e}")
    import traceback
    traceback.print_exc()

print("="*60)