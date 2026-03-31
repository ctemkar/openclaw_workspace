#!/usr/bin/env python3
"""
Check FULL Gemini balance to use for trading
"""

import ccxt
import json

print("💰 CHECKING FULL GEMINI BALANCE")
print("="*60)

try:
    with open("secure_keys/.gemini_key", "r") as f:
        GEMINI_KEY = f.read().strip()
    with open("secure_keys/.gemini_secret", "r") as f:
        GEMINI_SECRET = f.read().strip()
    
    exchange = ccxt.gemini({
        'apiKey': GEMINI_KEY,
        'secret': GEMINI_SECRET,
        'enableRateLimit': True,
    })
    
    print("✅ Gemini API keys loaded")
    
    # Get full balance
    balance = exchange.fetch_balance()
    
    print("\n📊 FULL GEMINI BALANCE:")
    for currency, amount in balance['total'].items():
        if amount > 0:
            free = balance['free'].get(currency, 0)
            used = balance['used'].get(currency, 0)
            print(f"  {currency}: {amount:.8f} (Free: {free:.8f}, Used: {used:.8f})")
    
    # Get USD cash
    usd_cash = balance['free'].get('USD', 0)
    print(f"\n💵 AVAILABLE CASH (USD): ${usd_cash:.2f}")
    
    # Get BTC value
    btc_amount = balance['free'].get('BTC', 0)
    if btc_amount > 0:
        ticker = exchange.fetch_ticker('BTC/USD')
        btc_price = ticker['last']
        btc_value = btc_amount * btc_price
        print(f"💰 BTC HOLDINGS: {btc_amount:.6f} BTC (${btc_value:.2f} @ ${btc_price:.2f})")
    
    total_portfolio = usd_cash + btc_value if 'btc_value' in locals() else usd_cash
    print(f"\n🎯 TOTAL PORTFOLIO VALUE: ${total_portfolio:.2f}")
    
    # Calculate trading capital (use 80% of cash for trading)
    trading_capital = usd_cash * 0.8
    print(f"\n🚀 RECOMMENDED TRADING CAPITAL (80% of cash): ${trading_capital:.2f}")
    print(f"   (Keeps 20% as buffer for withdrawals/fees)")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("🎯 Update bot to use FULL balance instead of just $100!")
print("="*60)