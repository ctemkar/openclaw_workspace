#!/usr/bin/env python3
"""
Check current arbitrage opportunities
"""

import ccxt
from datetime import datetime

print("=" * 70)
print(f"📊 REAL-TIME ARBITRAGE CHECK - {datetime.now().strftime('%H:%M:%S')}")
print("=" * 70)

# Initialize exchanges (public data only)
binance = ccxt.binance({'enableRateLimit': True})
gemini = ccxt.gemini({'enableRateLimit': True})

# Check MANA first
print("\n🔍 CHECKING MANA (our main trading pair):")
try:
    binance_mana = binance.fetch_ticker('MANA/USDT')['last']
    gemini_mana = gemini.fetch_ticker('MANA/USD')['last']
    
    mana_spread = ((gemini_mana - binance_mana) / binance_mana) * 100
    
    print(f"   Binance: ${binance_mana:.4f}")
    print(f"   Gemini: ${gemini_mana:.4f}")
    print(f"   Spread: {mana_spread:.2f}%")
    
    if abs(mana_spread) >= 0.5:
        print(f"   ✅ TRADABLE: {abs(mana_spread):.2f}% ≥ 0.5%")
        if mana_spread > 0:
            print(f"   🚀 Action: Buy Binance, Sell Gemini")
        else:
            print(f"   🚀 Action: Buy Gemini, Sell Binance")
    else:
        print(f"   ⏳ MONITORING: {abs(mana_spread):.2f}% < 0.5%")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

# Check top arbitrage opportunities
print("\n🔍 CHECKING TOP ARBITRAGE OPPORTUNITIES:")
cryptos = ['YFI', 'FIL', 'COMP', 'LTC', 'DOT', 'ATOM', 'XTZ', 'AVAX', 'UNI', 'ETH']
spreads = []

for crypto in cryptos:
    try:
        binance_price = binance.fetch_ticker(f'{crypto}/USDT')['last']
        gemini_price = gemini.fetch_ticker(f'{crypto}/USD')['last']
        
        if gemini_price > 0:
            spread = ((binance_price - gemini_price) / gemini_price) * 100
            spreads.append({
                'crypto': crypto,
                'binance': binance_price,
                'gemini': gemini_price,
                'spread': spread,
                'abs_spread': abs(spread)
            })
    except Exception as e:
        # Some cryptos may not be available on both exchanges
        continue

# Sort by absolute spread
spreads.sort(key=lambda x: x['abs_spread'], reverse=True)

print(f"\n📈 TOP 5 ARBITRAGE OPPORTUNITIES:")
for i, s in enumerate(spreads[:5], 1):
    direction = "Gemini↑" if s['spread'] > 0 else "Binance↑"
    tradable = "✅" if s['abs_spread'] >= 0.5 else "⏳"
    
    print(f"  {i}. {s['crypto']}: {s['spread']:.2f}% ({direction}) {tradable}")
    print(f"     Binance: ${s['binance']:.4f}, Gemini: ${s['gemini']:.4f}")
    
    if s['abs_spread'] >= 0.5:
        if s['spread'] > 0:
            print(f"     🚀 Action: Buy Gemini, Sell Binance")
        else:
            print(f"     🚀 Action: Buy Binance, Sell Gemini")

if spreads:
    best = spreads[0]
    print(f"\n🎯 BEST OPPORTUNITY: {best['crypto']} ({best['spread']:.2f}%)")
    
    if best['abs_spread'] >= 0.5:
        print(f"   ✅ READY TO TRADE (≥0.5% spread)")
        if best['spread'] > 0:
            print(f"   🚀 Buy on Gemini at ${best['gemini']:.2f}")
            print(f"   🚀 Sell on Binance at ${best['binance']:.2f}")
        else:
            print(f"   🚀 Buy on Binance at ${best['binance']:.2f}")
            print(f"   🚀 Sell on Gemini at ${best['gemini']:.2f}")
    else:
        print(f"   ⏳ MONITORING (<0.5% spread)")
    
    # Calculate average spread
    avg_spread = sum(s['abs_spread'] for s in spreads) / len(spreads)
    print(f"\n📊 MARKET SUMMARY:")
    print(f"   • Cryptos analyzed: {len(spreads)}")
    print(f"   • Average spread: {avg_spread:.2f}%")
    print(f"   • Tradable opportunities: {sum(1 for s in spreads if s['abs_spread'] >= 0.5)}")

print("\n" + "=" * 70)
print(f"⏰ Check completed at {datetime.now().strftime('%H:%M:%S')}")
print("=" * 70)