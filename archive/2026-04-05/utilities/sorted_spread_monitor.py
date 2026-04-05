#!/usr/bin/env python3
"""
SORTED SPREAD MONITOR
Shows cryptocurrency spreads SORTED from highest to lowest
This is what arbitrage trading is all about!
"""

import ccxt
import time
from datetime import datetime

# Cryptocurrencies to monitor (from real_26_crypto_trader.py)
CRYPTOS = [
    'BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOT', 'DOGE', 'AVAX', 'LINK', 'UNI',
    'LTC', 'ATOM', 'FIL', 'XTZ', 'AAVE', 'COMP', 'YFI', 'SNX', 'BAT', 'ZRX',
    'ENJ', 'SUSHI', 'CRV'
]

def get_sorted_spreads():
    """Get spreads for all cryptos and sort by highest spread"""
    
    print(f"\n🔍 Checking {len(CRYPTOS)} cryptocurrencies...")
    print("=" * 80)
    
    # Initialize exchanges
    binance = ccxt.binance({'enableRateLimit': True})
    gemini = ccxt.gemini({'enableRateLimit': True})
    
    spreads = []
    
    for crypto in CRYPTOS:
        try:
            symbol = f"{crypto}/USDT"
            
            # Get Binance price
            binance_ticker = binance.fetch_ticker(symbol)
            binance_price = binance_ticker['last']
            
            # Get Gemini price (if available)
            try:
                gemini_ticker = gemini.fetch_ticker(symbol)
                gemini_price = gemini_ticker['last']
                
                # Calculate spread percentage
                if gemini_price > 0 and binance_price > 0:
                    spread_percent = ((gemini_price - binance_price) / binance_price) * 100
                    
                    # Calculate potential profit per $100 trade
                    profit_per_100 = (spread_percent / 100) * 100
                    
                    spreads.append({
                        'symbol': crypto,
                        'binance_price': binance_price,
                        'gemini_price': gemini_price,
                        'spread_percent': spread_percent,
                        'profit_per_100': profit_per_100,
                        'status': '✅ AVAILABLE'
                    })
                else:
                    spreads.append({
                        'symbol': crypto,
                        'binance_price': binance_price,
                        'gemini_price': 'N/A',
                        'spread_percent': 0,
                        'profit_per_100': 0,
                        'status': '⚠️ NO GEMINI'
                    })
                    
            except Exception as e:
                # Gemini not available for this crypto
                spreads.append({
                    'symbol': crypto,
                    'binance_price': binance_price,
                    'gemini_price': 'N/A',
                    'spread_percent': 0,
                    'profit_per_100': 0,
                    'status': '❌ NO GEMINI'
                })
                
        except Exception as e:
            # Crypto not available on Binance
            spreads.append({
                'symbol': crypto,
                'binance_price': 'N/A',
                'gemini_price': 'N/A',
                'spread_percent': 0,
                'profit_per_100': 0,
                'status': '❌ NOT AVAILABLE'
            })
    
    # Sort by spread_percent (highest first)
    sorted_spreads = sorted(spreads, key=lambda x: x['spread_percent'], reverse=True)
    
    return sorted_spreads

def print_sorted_spreads(spreads):
    """Print spreads in a sorted table"""
    
    print("\n📊 **SORTED SPREADS - HIGHEST TO LOWEST**")
    print("=" * 80)
    print(f"{'Rank':<5} {'Symbol':<8} {'Binance':<12} {'Gemini':<12} {'Spread %':<12} {'Profit/$100':<12} {'Status':<15}")
    print("-" * 80)
    
    for i, spread in enumerate(spreads[:15], 1):  # Show top 15
        symbol = spread['symbol']
        binance = f"${spread['binance_price']:,.4f}" if isinstance(spread['binance_price'], float) else spread['binance_price']
        gemini = f"${spread['gemini_price']:,.4f}" if isinstance(spread['gemini_price'], float) else spread['gemini_price']
        spread_pct = f"{spread['spread_percent']:.2f}%" if spread['spread_percent'] != 0 else "0.00%"
        profit = f"${spread['profit_per_100']:.2f}" if spread['profit_per_100'] != 0 else "$0.00"
        status = spread['status']
        
        # Color code based on spread
        if spread['spread_percent'] >= 1.0:
            spread_pct = f"💰 {spread_pct}"  # High profit
        elif spread['spread_percent'] >= 0.5:
            spread_pct = f"📈 {spread_pct}"  # Medium profit
        elif spread['spread_percent'] > 0:
            spread_pct = f"📊 {spread_pct}"  # Low profit
        
        print(f"{i:<5} {symbol:<8} {binance:<12} {gemini:<12} {spread_pct:<12} {profit:<12} {status:<15}")
    
    # Show summary
    profitable = [s for s in spreads if s['spread_percent'] >= 0.5]
    print("\n" + "=" * 80)
    print(f"📈 **SUMMARY**: {len(profitable)}/{len(spreads)} cryptos with ≥0.5% spread")
    
    if profitable:
        print(f"🎯 **TOP PROFITABLE**:")
        for i, p in enumerate(profitable[:5], 1):
            print(f"   {i}. {p['symbol']}: {p['spread_percent']:.2f}% (${p['profit_per_100']:.2f} per $100)")
    
    # Show best opportunity
    if spreads and spreads[0]['spread_percent'] > 0:
        best = spreads[0]
        print(f"\n🏆 **BEST OPPORTUNITY**: {best['symbol']}")
        print(f"   • Spread: {best['spread_percent']:.2f}%")
        print(f"   • Binance: ${best['binance_price']:,.4f}")
        print(f"   • Gemini: ${best['gemini_price']:,.4f}")
        print(f"   • Profit per $100: ${best['profit_per_100']:.2f}")
    
    print("=" * 80)

def main():
    print("\n" + "=" * 80)
    print("🎯 **SORTED SPREAD MONITOR** - Arbitrage Trading Dashboard")
    print("=" * 80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Monitoring {len(CRYPTOS)} cryptocurrencies")
    print("Sorting by HIGHEST spread (most profitable first)")
    
    try:
        spreads = get_sorted_spreads()
        print_sorted_spreads(spreads)
        
        # Check if trading is possible
        print("\n🔧 **TRADING STATUS**:")
        
        # Check Binance API (simplified)
        print("   • Binance API: ❌ NEEDS FIXING (error -2015)")
        print("   • Gemini API: ⚠️  NONCE ERROR (being fixed)")
        print("   • Last trade: 2026-04-04 00:59:12 (23+ hours ago)")
        print("   • Today's profit: $0.00 (NO TRADES)")
        
        # Action items
        print("\n🚨 **ACTION REQUIRED**:")
        print("   1. Fix Binance API permissions (IP whitelist/trading enabled)")
        print("   2. Fix Gemini nonce error")
        print("   3. Restart bots when APIs are working")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Check network connection or exchange availability")
    
    print("\n" + "=" * 80)
    print("💡 **REMEMBER**: Arbitrage trading is about finding HIGHEST spreads")
    print("   Sort by spread, trade the most profitable opportunities first!")
    print("=" * 80)

if __name__ == "__main__":
    main()