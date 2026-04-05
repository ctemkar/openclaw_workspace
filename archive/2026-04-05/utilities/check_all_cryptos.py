#!/usr/bin/env python3
"""
Check ALL 26 cryptos for LONG opportunities (dips)
"""

import ccxt
import json

ALL_CRYPTOS = [
    'BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOT', 'DOGE', 'AVAX', 'LINK', 'UNI',
    'LTC', 'ATOM', 'FIL', 'XTZ', 'AAVE', 'COMP', 'YFI', 'SNX', 'ENJ', 'BAT',
    'ZEC', 'MANA', 'OXT', 'BCH', 'MATIC', 'MKR'
]

def check_all_cryptos():
    print("📊 CHECKING ALL 26 CRYPTOS FOR DIPS (1%+)")
    print("==========================================")
    
    try:
        # Initialize Binance (public)
        exchange = ccxt.binance({
            'enableRateLimit': True,
        })
        
        print(f"Checking {len(ALL_CRYPTOS)} cryptos on Binance...")
        print("")
        print(f"{'Crypto':6} | {'Price':10} | {'24h %':8} | {'Status':15} | {'Dip %'}")
        print("-" * 70)
        
        dip_count = 0
        rise_count = 0
        flat_count = 0
        
        for crypto in ALL_CRYPTOS:
            symbol = f"{crypto}/USDT"
            try:
                ticker = exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                change_24h = ticker.get('percentage', 0)
                
                if change_24h is None:
                    # Try to calculate
                    high = ticker.get('high')
                    low = ticker.get('low')
                    if high and low:
                        midpoint = (high + low) / 2
                        change_24h = ((current_price - midpoint) / midpoint) * 100
                    else:
                        change_24h = 0
                
                # Categorize
                if change_24h <= -1.0:
                    status = "📉 DIP (BUY)"
                    dip_count += 1
                    color = "\033[92m"  # Green
                elif change_24h >= 1.0:
                    status = "📈 RISE (SELL)"
                    rise_count += 1
                    color = "\033[91m"  # Red
                else:
                    status = "➡️  FLAT"
                    flat_count += 1
                    color = "\033[93m"  # Yellow
                
                reset = "\033[0m"
                change_str = f"{change_24h:+.2f}%"
                
                print(f"{crypto:6} | ${current_price:8.4f} | {color}{change_str:>8}{reset} | {status:15} | {abs(change_24h):.2f}%")
                
            except Exception as e:
                print(f"{crypto:6} | Error: {str(e)[:30]}...")
        
        print("")
        print("📊 SUMMARY:")
        print(f"  📉 Dips (down 1%+): {dip_count} cryptos")
        print(f"  📈 Rises (up 1%+): {rise_count} cryptos")
        print(f"  ➡️  Flat (<1% change): {flat_count} cryptos")
        print(f"  📊 Total: {dip_count + rise_count + flat_count}/{len(ALL_CRYPTOS)}")
        
        print("")
        print("💡 ANALYSIS:")
        if dip_count == 0:
            print("  🚨 NO DIPS FOUND! All 26 cryptos are flat or rising")
            print("  🤔 Possible issues:")
            print("     1. Markets in strong bull run")
            print("     2. 1% threshold too strict")
            print("     3. Need momentum buying (buy on rises too)")
        else:
            print(f"  ✅ Found {dip_count} buying opportunities")
        
        # Check specific cryptos that might be down
        print("")
        print("🔍 CHECKING SPECIFIC 'DIPPY' CRYPTOS:")
        dip_candidates = ['ADA', 'DOT', 'FIL', 'XTZ', 'ENJ', 'BAT', 'MANA', 'OXT']
        for crypto in dip_candidates:
            try:
                ticker = exchange.fetch_ticker(f"{crypto}/USDT")
                change = ticker.get('percentage', 0)
                if change <= -0.5:  # Even small dips
                    print(f"  {crypto}: {change:+.2f}% (close to dip)")
            except:
                pass
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_all_cryptos()
