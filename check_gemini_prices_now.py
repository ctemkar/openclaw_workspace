#!/usr/bin/env python3
"""
Check REAL Gemini prices right now to see why bot isn't buying
"""

import ccxt
import time
from datetime import datetime

def check_gemini_prices():
    """Check current Gemini prices and 24h changes"""
    
    print("🔍 REAL-TIME GEMINI PRICE CHECK")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    # Initialize Gemini (public API for ticker data)
    exchange = ccxt.gemini({
        'enableRateLimit': True,
        'timeout': 10000,
    })
    
    # Gemini available cryptos
    gemini_cryptos = [
        'BTC', 'ETH', 'SOL', 'XRP', 'DOT', 'DOGE', 'AVAX', 'LINK', 'UNI',
        'LTC', 'ATOM', 'FIL', 'XTZ', 'AAVE', 'COMP', 'YFI'
    ]
    
    print(f"Checking {len(gemini_cryptos)} cryptos on Gemini...")
    print("Threshold for BUY: 1.5%+ drop in 24h")
    print()
    
    results = []
    
    for crypto in gemini_cryptos:
        try:
            symbol = f"{crypto}/USD"
            ticker = exchange.fetch_ticker(symbol)
            
            current_price = ticker['last']
            change_percent = ticker.get('percentage')
            
            if change_percent is None:
                # Calculate from open/high/low/close
                open_price = ticker.get('open')
                if open_price and open_price > 0:
                    change_percent = ((current_price - open_price) / open_price) * 100
                else:
                    change_percent = 0
            
            results.append({
                'crypto': crypto,
                'price': current_price,
                'change': change_percent,
                'would_buy': change_percent <= -1.5 if change_percent else False
            })
            
            time.sleep(0.2)  # Rate limiting
            
        except Exception as e:
            print(f"❌ Error checking {crypto}: {e}")
            results.append({
                'crypto': crypto,
                'price': 0,
                'change': 0,
                'would_buy': False,
                'error': str(e)
            })
    
    # Sort by change (most negative first)
    results.sort(key=lambda x: x['change'] if x['change'] else 100)
    
    # Display results
    print("📊 GEMINI 24H PRICE CHANGES:")
    print("-" * 60)
    
    dips_found = 0
    for r in results:
        if r.get('error'):
            print(f"   {r['crypto']}: ERROR - {r['error'][:30]}")
        elif r['change'] is not None:
            if r['change'] <= -1.5:
                dips_found += 1
                print(f"🎯 {r['crypto']}: {r['change']:.2f}% DOWN - WOULD BUY!")
                print(f"   Price: ${r['price']:.2f}")
            elif r['change'] < 0:
                print(f"   {r['crypto']}: {r['change']:.2f}% down")
            else:
                print(f"   {r['crypto']}: +{r['change']:.2f}% up")
        else:
            print(f"   {r['crypto']}: No data")
    
    print()
    print("=" * 60)
    
    if dips_found > 0:
        print(f"✅ Found {dips_found} cryptos down 1.5%+")
        print(f"   Bot SHOULD be buying these!")
    else:
        print("❌ NO cryptos down 1.5%+ on Gemini")
        print("   Reason: Market is BULLISH (prices going UP)")
        print("   Bot is WAITING for dips to buy")
    
    # Check if bot might have issues
    print()
    print("🔧 POSSIBLE ISSUES TO CHECK:")
    print("1. API connection to Gemini")
    print("2. Rate limiting (too many requests)")
    print("3. Incorrect symbol format")
    print("4. Market data not updating")
    
    return results

if __name__ == "__main__":
    check_gemini_prices()