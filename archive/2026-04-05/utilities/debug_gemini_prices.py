#!/usr/bin/env python3
"""
Debug: Check what prices the bot is actually seeing
"""

import ccxt
import time

def debug_gemini_prices():
    """Debug Gemini price data"""
    
    print("🔍 DEBUG: What Gemini Prices Bot Sees")
    print("=" * 60)
    
    # Initialize Gemini (same as bot)
    exchange = ccxt.gemini({
        'enableRateLimit': True,
    })
    
    cryptos = ['BTC', 'ETH', 'SOL', 'XRP', 'DOT']
    
    for crypto in cryptos:
        try:
            symbol = f"{crypto}/USD"
            ticker = exchange.fetch_ticker(symbol)
            
            print(f"\n📊 {symbol}:")
            print(f"   Last: ${ticker['last']:.2f}")
            print(f"   Close: ${ticker.get('close', 'N/A')}")
            print(f"   High: ${ticker.get('high', 'N/A')}")
            print(f"   Low: ${ticker.get('low', 'N/A')}")
            
            # Calculate like the bot does now
            reference_price = None
            
            if ticker.get('close') and ticker['close'] > 0:
                reference_price = ticker['close']
                print(f"   Using CLOSE as reference: ${reference_price:.2f}")
            elif ticker.get('high') and ticker.get('low') and ticker['high'] > 0 and ticker['low'] > 0:
                reference_price = (ticker['high'] + ticker['low']) / 2
                print(f"   Using HIGH/LOW avg as reference: ${reference_price:.2f}")
            else:
                reference_price = ticker['last']
                print(f"   Using LAST as reference: ${reference_price:.2f}")
            
            # Calculate 24h change
            change_percent = ((ticker['last'] - reference_price) / reference_price) * 100
            
            print(f"   Calculated change: {change_percent:.2f}%")
            
            # Check against threshold
            if change_percent <= -1.5:
                print(f"   🎯 WOULD BUY! (down {abs(change_percent):.2f}%)")
            elif change_percent < 0:
                print(f"   Down {abs(change_percent):.2f}% (need 1.5%+)")
            else:
                print(f"   Up {change_percent:.2f}%")
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_gemini_prices()