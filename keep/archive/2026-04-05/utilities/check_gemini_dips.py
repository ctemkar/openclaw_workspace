#!/usr/bin/env python3
"""
Check which Gemini cryptos are down 1.5%+ (LONG threshold)
"""

import ccxt
import time

def check_gemini_dips():
    """Check Gemini cryptos for dips"""
    
    print("🔍 CHECKING GEMINI FOR 1.5%+ DIPS")
    print("=" * 60)
    
    # Load API keys
    try:
        with open("secure_keys/.gemini_key", "r") as f:
            api_key = f.read().strip()
        with open("secure_keys/.gemini_secret", "r") as f:
            api_secret = f.read().strip()
    except:
        print("❌ Gemini API keys not found")
        return
    
    # Initialize Gemini
    exchange = ccxt.gemini({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
    })
    
    # Gemini available cryptos
    gemini_cryptos = [
        'BTC', 'ETH', 'SOL', 'XRP', 'DOT', 'DOGE', 'AVAX', 'LINK', 'UNI',
        'LTC', 'ATOM', 'FIL', 'XTZ', 'AAVE', 'COMP', 'YFI'
    ]
    
    print(f"Checking {len(gemini_cryptos)} cryptos on Gemini...")
    print()
    
    dips_found = 0
    
    for crypto in gemini_cryptos:
        try:
            symbol = f"{crypto}/USD"
            ticker = exchange.fetch_ticker(symbol)
            
            current_price = ticker['last']
            change_percent = ticker['percentage']
            
            if change_percent is None:
                # Calculate manually
                open_price = ticker['open']
                if open_price and open_price > 0:
                    change_percent = ((current_price - open_price) / open_price) * 100
            
            if change_percent and change_percent <= -1.5:  # 1.5% threshold
                dips_found += 1
                print(f"🎯 {crypto}: {change_percent:.2f}% DOWN (would BUY)")
                print(f"   Price: ${current_price:.2f}")
                print(f"   Position size: ${531.65 * 0.10:.2f} (10% of Gemini capital)")
                print()
            elif change_percent:
                # Show all for context
                if change_percent < 0:
                    print(f"   {crypto}: {change_percent:.2f}% down")
                else:
                    print(f"   {crypto}: +{change_percent:.2f}% up")
            
            time.sleep(0.1)  # Rate limiting
            
        except Exception as e:
            print(f"❌ Error checking {crypto}: {e}")
    
    print("=" * 60)
    if dips_found > 0:
        print(f"✅ Found {dips_found} cryptos down 1.5%+ (would trigger LONG buys)")
    else:
        print("❌ No cryptos down 1.5%+ on Gemini right now")
        print("   Market may be bullish (prices going up)")
        print("   Bot is waiting for dips to buy")

if __name__ == "__main__":
    check_gemini_dips()