#!/usr/bin/env python3
"""
TOP 10 SPREADS REPORT
Fetches prices for ALL 23 cryptos from Binance & Gemini
Calculates spreads, sorts by highest, shows top 10
"""

import ccxt
import time
from datetime import datetime

# All 23 cryptos being monitored
ALL_CRYPTOS = [
    'BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOT', 'DOGE', 'AVAX', 'LINK', 'UNI',
    'LTC', 'ATOM', 'FIL', 'XTZ', 'AAVE', 'COMP', 'YFI', 'SNX', 'BAT', 'ZRX',
    'ENJ', 'SUSHI', 'CRV'
]

def get_top_spreads():
    """Fetch prices and calculate top 10 spreads"""
    print("=" * 70)
    print("TOP 10 SPREADS REPORT - " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)
    
    # Initialize exchanges
    try:
        binance = ccxt.binance({'enableRateLimit': True})
        gemini = ccxt.gemini({'enableRateLimit': True})
    except Exception as e:
        print(f"[ERROR] Failed to initialize exchanges: {e}")
        return
    
    spreads = []
    
    print(f"\n🔍 Checking {len(ALL_CRYPTOS)} cryptos...")
    
    for crypto in ALL_CRYPTOS:
        try:
            # Binance uses USDT pairs
            binance_symbol = f"{crypto}/USDT"
            binance_ticker = binance.fetch_ticker(binance_symbol)
            binance_price = binance_ticker['last']
            
            # Gemini uses USD pairs
            gemini_symbol = f"{crypto}/USD"
            gemini_ticker = gemini.fetch_ticker(gemini_symbol)
            gemini_price = gemini_ticker['last']
            
            # Calculate spread (Gemini - Binance)
            spread_percent = ((gemini_price - binance_price) / binance_price) * 100
            
            # Calculate profit per $100
            profit_per_100 = 100 * (abs(spread_percent) / 100) - 0.06  # 6 cents fee
            
            spreads.append({
                'crypto': crypto,
                'binance': binance_price,
                'gemini': gemini_price,
                'spread': spread_percent,
                'profit_100': profit_per_100,
                'direction': 'HIGHER' if spread_percent > 0 else 'LOWER'
            })
            
            print(f"  {crypto}: Binance=${binance_price:.4f}, Gemini=${gemini_price:.4f}, Spread={spread_percent:.2f}%")
            
            # Rate limiting
            time.sleep(0.1)
            
        except Exception as e:
            print(f"  {crypto}: ERROR - {str(e)[:50]}")
            continue
    
    # Sort by absolute spread (highest first)
    spreads_sorted = sorted(spreads, key=lambda x: abs(x['spread']), reverse=True)
    
    print("\n" + "=" * 70)
    print("🏆 TOP 10 SPREADS (Highest to Lowest)")
    print("=" * 70)
    print(f"{'Rank':<5} {'Crypto':<6} {'Binance':<10} {'Gemini':<10} {'Spread %':<10} {'Profit/$100':<12} {'Status':<15}")
    print("-" * 70)
    
    for i, spread in enumerate(spreads_sorted[:10], 1):
        crypto = spread['crypto']
        binance_price = spread['binance']
        gemini_price = spread['gemini']
        spread_pct = spread['spread']
        profit = spread['profit_100']
        direction = spread['direction']
        
        # Format based on spread value
        if abs(spread_pct) >= 0.5:
            status = "[PROFITABLE]"
            spread_str = f"{spread_pct:+.2f}%"
            profit_str = f"${profit:.2f}"
        else:
            status = "[TOO SMALL]"
            spread_str = f"{spread_pct:+.2f}%"
            profit_str = f"${profit:.2f}"
        
        print(f"{i:<5} {crypto:<6} ${binance_price:<9.4f} ${gemini_price:<9.4f} {spread_str:<10} {profit_str:<12} {status:<15}")
    
    # Show summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    profitable = [s for s in spreads_sorted if abs(s['spread']) >= 0.5]
    if profitable:
        print(f"✅ PROFITABLE OPPORTUNITIES: {len(profitable)} cryptos")
        for p in profitable[:3]:  # Top 3 profitable
            print(f"   • {p['crypto']}: {p['spread']:+.2f}% ({p['direction']}), Profit: ${p['profit_100']:.2f}/$100")
    else:
        print(f"⏳ NO PROFITABLE OPPORTUNITIES (all spreads < 0.5%)")
        print(f"   • Highest spread: {spreads_sorted[0]['crypto']} ({spreads_sorted[0]['spread']:+.2f}%)")
        print(f"   • Lowest spread: {spreads_sorted[-1]['crypto']} ({spreads_sorted[-1]['spread']:+.2f}%)")
    
    print(f"\n📈 TOTAL CRYPTOS CHECKED: {len(spreads)}/{len(ALL_CRYPTOS)}")
    print(f"💰 MINIMUM PROFITABLE SPREAD: 0.5% (${0.44:.2f} profit per $100 after fees)")
    print("=" * 70)

if __name__ == "__main__":
    get_top_spreads()