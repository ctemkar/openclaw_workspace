#!/usr/bin/env python3
"""
Check current Gemini prices to see if any are down 1%+
"""

import ccxt
import os
from dotenv import load_dotenv

load_dotenv()

# Gemini cryptos from the bot
GEMINI_CRYPTOS = [
    'BTC', 'ETH', 'LTC', 'BCH', 'ZEC', 'FIL', 'BAT', 'LINK', 
    'OXT', 'MANA', 'MATIC', 'MKR', 'OMG', 'COMP', 'ENJ', 'SNX'
]

def check_gemini_prices():
    print("🔍 CHECKING GEMINI PRICES FOR 1%+ DIPS")
    print("======================================")
    
    try:
        # Initialize Gemini exchange
        exchange = ccxt.gemini({
            'apiKey': os.getenv('GEMINI_API_KEY'),
            'secret': os.getenv('GEMINI_API_SECRET'),
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
                change_percent = ticker['percentage']
                
                if change_percent is None:
                    # Calculate manually
                    open_price = ticker['open']
                    if open_price and open_price > 0:
                        change_percent = ((current_price - open_price) / open_price) * 100
                
                if change_percent:
                    status = "✅ DOWN 1%+" if change_percent <= -1.0 else "❌ Not down enough"
                    color = "\033[92m" if change_percent <= -1.0 else "\033[91m" if change_percent > 0 else "\033[93m"
                    reset = "\033[0m"
                    
                    print(f"{crypto:6} | ${current_price:8.4f} | {color}{change_percent:7.2f}%{reset} | {status}")
                    
                    if change_percent <= -1.0:
                        opportunities += 1
                        print(f"   ↳ Would trigger LONG trade!")
                
            except Exception as e:
                print(f"{crypto:6} | Error: {str(e)[:50]}...")
        
        print("")
        print(f"📊 RESULT: {opportunities} LONG opportunities found (need 1%+ dip)")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_gemini_prices()
