#!/usr/bin/env python3
"""
CANCEL GEMINI LIMIT ORDERS
Cancel all open limit orders on Gemini since they're not filled
"""

import ccxt
import os
import json
from datetime import datetime

print("="*70)
print("🛑 CANCELING GEMINI LIMIT ORDERS")
print("="*70)

# Load API keys from .env
def load_env():
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
        return env_vars
    except Exception as e:
        print(f"❌ Error loading .env: {e}")
        return {}

env = load_env()
gemini_key = env.get('GEMINI_API_KEY')
gemini_secret = env.get('GEMINI_API_SECRET')

if not gemini_key or not gemini_secret:
    print("❌ Gemini API keys not found in .env")
    exit(1)

# Initialize Gemini
exchange = ccxt.gemini({
    'apiKey': gemini_key,
    'secret': gemini_secret,
    'enableRateLimit': True,
})

print("✅ Gemini exchange connected")

# Fetch open orders
try:
    print("\n🔍 Fetching open orders...")
    open_orders = exchange.fetch_open_orders()
    
    if not open_orders:
        print("✅ No open orders found on Gemini")
        exit(0)
    
    print(f"Found {len(open_orders)} open orders:")
    
    for order in open_orders:
        print(f"\n  Symbol: {order['symbol']}")
        print(f"  Side: {order['side'].upper()}")
        print(f"  Amount: {order['amount']:.6f}")
        print(f"  Price: ${order['price']:.2f}")
        print(f"  Order ID: {order['id']}")
        print(f"  Status: {order['status']}")
    
    print("\n" + "="*70)
    print("⚠️  These orders are NOT filled (still open)")
    print("   Need to cancel them to free up funds")
    print("="*70)
    
    # Cancel all orders
    print("\n🛑 Cancelling all open orders...")
    cancelled = []
    failed = []
    
    for order in open_orders:
        try:
            result = exchange.cancel_order(order['id'], order['symbol'])
            cancelled.append({
                'order_id': order['id'],
                'symbol': order['symbol'],
                'side': order['side'],
                'amount': order['amount'],
                'price': order['price']
            })
            print(f"✅ Cancelled: {order['symbol']} {order['side']} {order['amount']:.6f}")
        except Exception as e:
            failed.append({
                'order_id': order['id'],
                'symbol': order['symbol'],
                'error': str(e)
            })
            print(f"❌ Failed to cancel {order['id']}: {e}")
    
    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'cancelled': cancelled,
        'failed': failed,
        'total_cancelled': len(cancelled),
        'total_failed': len(failed)
    }
    
    results_file = "trading_data/gemini_cancellations.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: {results_file}")
    
    if cancelled:
        print(f"\n✅ Successfully cancelled {len(cancelled)} orders")
        print("💰 Funds should now be available for trading")
    
    if failed:
        print(f"\n⚠️  Failed to cancel {len(failed)} orders")
        print("   May need to cancel manually in Gemini UI")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*70)
print("💡 NEXT STEPS:")
print("1. Check Gemini balance - funds should be available")
print("2. Start fresh with accurate positions")
print("3. Verify dashboard shows reality, not fiction")
print("="*70)