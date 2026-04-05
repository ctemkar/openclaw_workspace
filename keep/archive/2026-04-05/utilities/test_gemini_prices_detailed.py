#!/usr/bin/env python3
"""
Test what prices the bot actually sees on Gemini
"""

import ccxt
import json

# Load API keys
try:
    with open('secure_keys/gemini_keys.json', 'r') as f:
        gemini_keys = json.load(f)
except:
    print("⚠️ Could not load Gemini keys")
    gemini_keys = {'api_key': '', 'api_secret': ''}

GEMINI_CRYPTOS = ['BTC', 'ETH', 'SOL', 'XRP', 'DOT', 'DOGE', 'AVAX', 'LINK', 'UNI',
                  'LTC', 'ATOM', 'FIL', 'XTZ', 'AAVE', 'COMP', 'YFI']

def test_gemini_prices():
    print("🔍 TESTING WHAT BOT SEES ON GEMINI")
    print("==================================")
    
    try:
        exchange = ccxt.gemini({
            'apiKey': gemini_keys.get('api_key', ''),
            'secret': gemini_keys.get('api_secret', ''),
            'enableRateLimit': True,
        })
        
        print(f"Checking {len(GEMINI_CRYPTOS)} cryptos...")
        print("")
        print(f"{'Crypto':6} | {'Price':10} | {'24h %':8} | {'Signal':15} | {'Reason'}")
        print("-" * 70)
        
        for crypto in GEMINI_CRYPTOS:
            symbol = f"{crypto}/USD"
            try:
                ticker = exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                change_percent = ticker.get('percentage')
                
                # Calculate manually if needed (like bot does)
                if change_percent is None:
                    open_price = ticker.get('open')
                    if open_price and open_price > 0:
                        change_percent = ((current_price - open_price) / open_price) * 100
                
                # Check bot logic
                signal = None
                reason = ""
                
                if change_percent is not None:
                    if change_percent <= -1.0:
                        signal = "LONG (DIP)"
                        reason = f"Down {abs(change_percent):.2f}%"
                    elif change_percent >= 1.0:
                        signal = "LONG (MOMENTUM)"
                        reason = f"Up {change_percent:.2f}%"
                    else:
                        signal = "NO SIGNAL"
                        reason = f"Change: {change_percent:.2f}% (<1%)"
                else:
                    signal = "NO DATA"
                    reason = "No 24h change data"
                
                change_str = f"{change_percent:+.2f}%" if change_percent else "N/A"
                print(f"{crypto:6} | ${current_price:8.2f} | {change_str:>8} | {signal:15} | {reason}")
                
            except Exception as e:
                print(f"{crypto:6} | Error: {str(e)[:30]}...")
        
        print("")
        print("💡 ANALYSIS:")
        print("   - Bot looks for: change_percent <= -1.0 (DIP) OR change_percent >= +1.0 (MOMENTUM)")
        print("   - If no 24h% data, calculates from open price")
        print("   - Current issue: Markets might be too flat (<1% movement)")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_gemini_prices()
