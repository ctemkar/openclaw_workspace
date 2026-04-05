#!/usr/bin/env python3
import ccxt
import time

print("🔍 CHECKING CURRENT BALANCE - 18:17")
print("=" * 50)

# Load keys
with open('secure_keys/.binance_key', 'r') as f:
    api_key = f.read().strip()
with open('secure_keys/.binance_secret', 'r') as f:
    api_secret = f.read().strip()

binance = ccxt.binance({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True
})

try:
    balance = binance.fetch_balance()
    
    print("💰 CURRENT BALANCES:")
    usdt_free = balance.get('USDT', {}).get('free', 0)
    usdt_total = balance.get('USDT', {}).get('total', 0)
    yfi_free = balance.get('YFI', {}).get('free', 0)
    yfi_total = balance.get('YFI', {}).get('total', 0)
    
    print(f"  USDT free: ${usdt_free:.2f}")
    print(f"  USDT total: ${usdt_total:.2f}")
    print(f"  YFI free: {yfi_free:.6f}")
    print(f"  YFI total: {yfi_total:.6f}")
    
    # Get YFI price
    ticker = binance.fetch_ticker('YFI/USDT')
    yfi_price = ticker['last']
    
    print(f"\\n📊 CURRENT YFI PRICE: ${yfi_price:.2f}")
    print(f"💵 YFI VALUE: ${yfi_total * yfi_price:.2f}")
    print(f"💰 TOTAL PORTFOLIO: ${usdt_free + (yfi_total * yfi_price):.2f}")
    
    print(f"\\n⏰ Time: {time.strftime('%H:%M:%S')}")
    
except Exception as e:
    print(f"❌ Error: {e}")