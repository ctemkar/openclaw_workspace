#!/usr/bin/env python3
"""
Check current MANA spread
"""

import ccxt
from datetime import datetime

print(f"📊 CURRENT MANA SPREAD CHECK - {datetime.now().strftime('%H:%M:%S')}")
print("=" * 50)

# Initialize exchanges
binance = ccxt.binance({'enableRateLimit': True})
gemini = ccxt.gemini({'enableRateLimit': True})

try:
    # Get MANA prices
    b_mana = binance.fetch_ticker('MANA/USDT')['last']
    g_mana = gemini.fetch_ticker('MANA/USD')['last']
    
    # Calculate spread
    spread = ((g_mana - b_mana) / b_mana) * 100
    
    print(f"💰 MANA PRICES:")
    print(f"   Binance: ${b_mana:.4f}")
    print(f"   Gemini:  ${g_mana:.4f}")
    print(f"   Spread:  {spread:.2f}%")
    
    print(f"\n🎯 TRADING STATUS:")
    if abs(spread) >= 0.5:
        print(f"   ✅ TRADABLE: {abs(spread):.2f}% ≥ 0.5% threshold")
        if spread > 0:
            print(f"   🚀 Action: Buy Binance, Sell Gemini")
            print(f"   💰 Profit: ${abs(spread):.2f} per $100 traded")
        else:
            print(f"   🚀 Action: Buy Gemini, Sell Binance")
            print(f"   💰 Profit: ${abs(spread):.2f} per $100 traded")
    else:
        print(f"   ⏳ MONITORING: {abs(spread):.2f}% < 0.5% threshold")
        print(f"   📈 Need spread ≥ 0.5% to trade")
    
    print(f"\n📈 ACCOUNT STATUS (from your test):")
    print(f"   MANA Balance: 118.661 (needs >119 to trade)")
    print(f"   USDT Balance: $1.7375")
    print(f"   Binance API: ✅ WORKING")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 50)
print(f"⏰ Check completed at {datetime.now().strftime('%H:%M:%S')}")