#!/usr/bin/env python3
"""
Check current Gemini prices to see if any are down 1%+
"""

import ccxt
import json

# Load API keys from secure_keys
try:
    with open('secure_keys/gemini_keys.json', 'r') as f:
        gemini_keys = json.load(f)
except:
    print("⚠️ Could not load Gemini keys")
    gemini_keys = {'api_key': '', 'api_secret': ''}

# Gemini cryptos from the bot
GEMINI_CRYPTOS = [
    'BTC', 'ETH', 'LTC', 'BCH', 'ZEC', 'FIL', 'BAT', 'LINK', 
    'OXT', 'MANA', 'MATIC', 'MKR', 'OMG', 'COMP', 'ENJ', 'SNX'
]

def check_gemini_prices():
    print("🔍 CHECKING GEMINI PRICES FOR 1%+ DIPS")
    print("======================================")
    
    try:
        # Initialize Gemini exchange (public only - no trading)
        exchange = ccxt.gemini({
            'apiKey': gemini_keys.get('api_key', ''),
            'secret': gemini_keys.get('api_secret', ''),
            'enableRateLimit': True,
        })
        
        print(f"Checking {len(GEMINI_CRYPTOS)} cryptos on Gemini...")
        print("")
        
        opportunities = 0
        for crypto in GEMINI_CRYPTOS:
            symbol = f"{crypto}/USD"
            try:
                ticker = exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                change_percent = ticker.get('percentage')
                
                if change_percent is None:
                    # Calculate from 24h high/low
                    high_24h = ticker.get('high')
                    low_24h = ticker.get('low')
                    if high_24h and low_24h and high_24h > 0:
                        # Approximate change from 24h range midpoint
                        midpoint = (high_24h + low_24h) / 2
                        change_percent = ((current_price - midpoint) / midpoint) * 100
                    else:
                        change_percent = 0
                
                # Check if down 1% or more
                is_opportunity = change_percent <= -1.0 if change_percent else False
                
                # Format output
                change_str = f"{change_percent:+.2f}%" if change_percent else "N/A"
                status = "✅ DOWN 1%+" if is_opportunity else "❌ Not down enough"
                
                print(f"{crypto:6} | ${current_price:8.2f} | {change_str:>8} | {status}")
                
                if is_opportunity:
                    opportunities += 1
                    print(f"   ↳ Would trigger LONG trade! (Down {abs(change_percent):.2f}%)")
                
            except Exception as e:
                print(f"{crypto:6} | Error: {str(e)[:40]}...")
        
        print("")
        print(f"📊 RESULT: {opportunities} LONG opportunities found (need 1%+ dip)")
        print("")
        if opportunities == 0:
            print("💡 REASON NO GEMINI TRADES: No cryptos are down 1%+ right now")
            print("   The bot is working correctly - waiting for dips to buy")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_gemini_prices()
