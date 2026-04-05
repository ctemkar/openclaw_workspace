#!/usr/bin/env python3
"""Check recent Binance orders"""

import ccxt
import os
import json
from datetime import datetime, timedelta

print("="*60)
print("🔍 CHECKING RECENT BINANCE ORDERS")
print("="*60)

try:
    # Load API keys
    key_path = 'secure_keys/.binance_key'
    secret_path = 'secure_keys/.binance_secret'
    
    if not os.path.exists(key_path):
        print("❌ Binance key not found")
        exit(1)
    
    with open(key_path, 'r') as f:
        api_key = f.read().strip()
    with open(secret_path, 'r') as f:
        api_secret = f.read().strip()
    
    # Initialize Binance
    binance = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
    
    print("✅ Connected to Binance")
    
    # Check open orders
    print("\n📋 Checking open orders...")
    try:
        open_orders = binance.fetch_open_orders('YFI/USDT')
        if open_orders:
            print(f"   Found {len(open_orders)} open orders:")
            for order in open_orders:
                print(f"   • {order['symbol']}: {order['side']} {order['amount']} @ ${order['price']}")
        else:
            print("   ✅ No open orders")
    except Exception as e:
        print(f"   ⚠️ Could not fetch open orders: {e}")
    
    # Check recent closed orders (last 24 hours)
    print("\n📋 Checking recent closed orders...")
    try:
        since = int((datetime.now() - timedelta(hours=24)).timestamp() * 1000)
        closed_orders = binance.fetch_my_trades('YFI/USDT', since=since, limit=10)
        
        if closed_orders:
            print(f"   Found {len(closed_orders)} recent trades:")
            for trade in closed_orders:
                time_str = datetime.fromtimestamp(trade['timestamp']/1000).strftime('%H:%M:%S')
                print(f"   • {time_str}: {trade['side']} {trade['amount']} YFI @ ${trade['price']}")
                print(f"     Cost: ${trade['cost']:.2f}, Fee: ${trade['fee']['cost'] if trade['fee'] else 0}")
        else:
            print("   ✅ No recent trades found")
    except Exception as e:
        print(f"   ⚠️ Could not fetch recent trades: {e}")
    
    # Check balance again
    print("\n💰 Checking current balance...")
    try:
        balance = binance.fetch_balance()
        usdt_free = balance.get('USDT', {}).get('free', 0)
        usdt_total = balance.get('USDT', {}).get('total', 0)
        usdt_used = balance.get('USDT', {}).get('used', 0)
        
        print(f"   Free USDT: ${usdt_free:.2f}")
        print(f"   Total USDT: ${usdt_total:.2f}")
        print(f"   Used USDT: ${usdt_used:.2f}")
        
        # Check YFI balance
        yfi_free = balance.get('YFI', {}).get('free', 0)
        yfi_total = balance.get('YFI', {}).get('total', 0)
        if yfi_total > 0:
            print(f"   YFI Balance: {yfi_total:.6f} YFI")
            
    except Exception as e:
        print(f"   ❌ Error checking balance: {e}")
    
    print("\n" + "="*60)
    print("🎯 ANALYSIS:")
    print(f"   Previous balance (21:32): $56.77")
    print(f"   Current balance: ${usdt_free if 'usdt_free' in locals() else 'UNKNOWN'}")
    print(f"   Difference: ${56.77 - usdt_free if 'usdt_free' in locals() else 'UNKNOWN'}")
    print(f"   Trade size: $28.50")
    print("="*60)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()