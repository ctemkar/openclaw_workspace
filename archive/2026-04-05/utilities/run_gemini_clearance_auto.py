#!/usr/bin/env python3
"""
Run Gemini clearance with auto-confirm
"""

import subprocess
import time

print("🚀 RUNNING GEMINI CLEARANCE WITH AUTO-CONFIRM")
print("="*60)

# Create a modified version that auto-confirms
script_content = '''
import ccxt
import json
import time
from datetime import datetime

print("💰 GEMINI CLEARANCE - AUTO CONFIRM")
print("="*60)

try:
    # Load Gemini keys
    with open("secure_keys/.gemini_key", "r") as f:
        GEMINI_KEY = f.read().strip()
    with open("secure_keys/.gemini_secret", "r") as f:
        GEMINI_SECRET = f.read().strip()
    
    print("✅ Gemini API keys loaded")
    
    # Initialize Gemini
    exchange = ccxt.gemini({
        'apiKey': GEMINI_KEY,
        'secret': GEMINI_SECRET,
        'enableRateLimit': True,
    })
    
    # Load markets
    exchange.load_markets()
    
    # Get balance
    balance = exchange.fetch_balance()
    
    print("\\n📊 HOLDINGS FOUND:")
    
    # Check BTC specifically
    btc_amount = balance['total'].get('BTC', 0)
    if btc_amount > 0:
        print(f"  BTC: {btc_amount:.8f}")
        
        # Check if we can sell BTC
        market = exchange.market('BTC/USD')
        min_amount = market['limits']['amount']['min']
        
        if btc_amount >= min_amount:
            ticker = exchange.fetch_ticker('BTC/USD')
            price = ticker['last']
            value = btc_amount * price
            
            print(f"    Min required: {min_amount:.8f}")
            print(f"    Current price: ${price:.2f}")
            print(f"    Value: ${value:.2f}")
            
            print("\\n" + "="*60)
            print("🚀 AUTO-SELLING BTC")
            print("="*60)
            
            try:
                print(f"\\n📤 Selling {btc_amount:.8f} BTC...")
                order = exchange.create_order(
                    symbol='BTC/USD',
                    type='market',
                    side='sell',
                    amount=btc_amount
                )
                
                print(f"✅ SOLD! Order ID: {order['id']}")
                print(f"   Sold {btc_amount:.8f} BTC for ~${value:.2f}")
                
                # Save record
                record = {
                    'timestamp': datetime.now().isoformat(),
                    'currency': 'BTC',
                    'amount': btc_amount,
                    'order_id': order['id'],
                    'estimated_value': value
                }
                
                with open("gemini_btc_sale.json", "w") as f:
                    json.dump(record, f, indent=2)
                
                print("\\n📝 Sale record saved: gemini_btc_sale.json")
                
            except Exception as e:
                print(f"❌ Failed to sell BTC: {e}")
        else:
            print(f"❌ BTC amount too small (min: {min_amount:.8f})")
    else:
        print("  No BTC holdings")
    
    # Check new balance
    print("\\n🔄 Checking new balance...")
    new_balance = exchange.fetch_balance()
    new_cash = new_balance['total'].get('USD', 0)
    new_btc = new_balance['total'].get('BTC', 0)
    
    print(f"💰 New USD cash: ${new_cash:.2f}")
    print(f"💰 New BTC: {new_btc:.8f}")
    
    print("\\n" + "="*60)
    print("✅ AUTO-CLEARANCE COMPLETE")
    print("="*60)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
'''

# Write and run the script
with open("auto_clearance.py", "w") as f:
    f.write(script_content)

print("📝 Created auto-clearance script")
print("⚡ Running...")

result = subprocess.run(["python3", "auto_clearance.py"], capture_output=True, text=True)

print(result.stdout)
if result.stderr:
    print("❌ Errors:", result.stderr)

print("="*60)
print("✅ Execution complete")
print("="*60)