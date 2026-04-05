#!/usr/bin/env python3
"""
EMERGENCY SELL SCRIPT - Sell stuck YFI positions
The bot bought YFI but never sold it. This script sells it NOW.
"""

import ccxt
import json
import time
from datetime import datetime

print("🚨 EMERGENCY YFI SELL SCRIPT")
print("=" * 60)
print("The trading bot bought YFI but never sold it.")
print("This script will SELL all YFI holdings NOW.")
print("=" * 60)

# Load API keys (same as bot)
def load_binance_keys():
    """Load Binance API keys from secure_keys"""
    try:
        with open('secure_keys/.binance_key', 'r') as f:
            api_key = f.read().strip()
        with open('secure_keys/.binance_secret', 'r') as f:
            api_secret = f.read().strip()
        
        print(f"🔑 Using API key: {api_key[:10]}...")
        return api_key, api_secret
    except Exception as e:
        print(f"❌ Error loading API keys: {e}")
        return "", ""

def main():
    # Initialize Binance
    api_key, api_secret = load_binance_keys()
    
    binance = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
    
    print("\n🔍 Checking current holdings...")
    
    try:
        # Get balance
        balance = binance.fetch_balance()
        
        # Check YFI holdings
        yfi_balance = balance.get('YFI', {}).get('free', 0)
        usdt_balance = balance.get('USDT', {}).get('free', 0)
        
        print(f"💰 Current balances:")
        print(f"   YFI: {yfi_balance:.6f}")
        print(f"   USDT: ${usdt_balance:.2f}")
        
        if yfi_balance <= 0:
            print("❌ No YFI to sell. Exiting.")
            return
        
        # Get current YFI price
        ticker = binance.fetch_ticker('YFI/USDT')
        current_price = ticker['last']
        
        print(f"\n📊 Current YFI price: ${current_price:.2f}")
        print(f"💵 YFI value: ${yfi_balance * current_price:.2f}")
        
        # Auto-confirm in non-interactive environment
        print(f"\n🚀 READY TO SELL {yfi_balance:.6f} YFI")
        print(f"   Expected proceeds: ~${yfi_balance * current_price:.2f}")
        
        # Auto-confirm for emergency
        print("\n⚠️  AUTO-CONFIRMING SELL (emergency mode)...")
        confirm = 'yes'
        
        if confirm != 'yes':
            print("❌ Sale cancelled.")
            return
        
        # Execute SELL
        print(f"\n🔄 Selling {yfi_balance:.6f} YFI at market price...")
        
        sell_order = binance.create_market_sell_order(
            'YFI/USDT',
            yfi_balance
        )
        
        print(f"✅ SELL EXECUTED!")
        print(f"   Order ID: {sell_order['id']}")
        print(f"   Amount: {sell_order['filled']:.6f} YFI")
        print(f"   Average Price: ${sell_order['average']:.2f}")
        print(f"   Total: ${sell_order['cost']:.2f}")
        
        # Check new balance
        time.sleep(2)  # Wait for balance update
        new_balance = binance.fetch_balance()
        new_usdt = new_balance.get('USDT', {}).get('free', 0)
        
        print(f"\n💰 NEW BALANCE:")
        print(f"   USDT: ${new_usdt:.2f}")
        print(f"   Increase: ${new_usdt - usdt_balance:.2f}")
        
        # Log the sale
        with open('EMERGENCY_SALE.log', 'a') as f:
            f.write(f"{datetime.now().isoformat()} | EMERGENCY YFI SALE | ")
            f.write(f"Amount: {yfi_balance:.6f} | Price: ${sell_order['average']:.2f} | ")
            f.write(f"Total: ${sell_order['cost']:.2f} | New USDT: ${new_usdt:.2f}\n")
        
        print(f"\n📝 Log saved to EMERGENCY_SALE.log")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("\n💡 TROUBLESHOOTING:")
        print("   1. Check API keys are correct")
        print("   2. Check internet connection")
        print("   3. Check Binance account status")

if __name__ == "__main__":
    main()