#!/usr/bin/env python3
"""
Check what should have happened in the last 2 hours
"""

import ccxt
from datetime import datetime, timedelta

print("=" * 70)
print("2-HOUR TRADING PERFORMANCE CHECK")
print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
print("Bot running since: ~00:15 (2 hours 17 minutes ago)")
print("=" * 70)

# Current market check
print("\n🔍 CURRENT MARKET CONDITIONS:")
print("-" * 70)

try:
    gemini = ccxt.gemini()
    binance = ccxt.binance()
    
    # Check major pairs
    pairs_to_check = [
        ("BTC/USD", "BTC/USDT"),
        ("ETH/USD", "ETH/USDT"), 
        ("SOL/USD", "SOL/USDT"),
        ("ADA/USD", "ADA/USDT"),
        ("XRP/USD", "XRP/USDT")
    ]
    
    opportunities_found = 0
    
    for gemini_pair, binance_pair in pairs_to_check:
        try:
            # Gemini (LONG opportunities)
            g_ticker = gemini.fetch_ticker(gemini_pair)
            g_price = g_ticker['last']
            g_change = g_ticker.get('percentage', 0)
            
            # Binance (SHORT opportunities)
            b_ticker = binance.fetch_ticker(binance_pair)
            b_price = b_ticker['last']
            b_change = b_ticker.get('percentage', 0)
            
            crypto = gemini_pair.split('/')[0]
            print(f"\n{crypto}:")
            print(f"  Gemini:   ${g_price:8.2f} ({g_change:6.2f}%)", end="")
            if g_change > 0.8:
                print(" ⚡ LONG SIGNAL!")
                opportunities_found += 1
            else:
                print("")
            
            print(f"  Binance:  ${b_price:8.2f} ({b_change:6.2f}%)", end="")
            if b_change < -1.0:
                print(" ⚡ SHORT SIGNAL!")
                opportunities_found += 1
            else:
                print("")
                
        except Exception as e:
            print(f"\nError checking {gemini_pair}: {str(e)[:30]}...")
    
    print("\n" + "=" * 70)
    print("📊 2-HOUR SUMMARY:")
    print("=" * 70)
    
    if opportunities_found > 0:
        print(f"✅ {opportunities_found} trading opportunities found in current market")
        print("   The bot SHOULD have detected these if markets moved similarly")
    else:
        print("❌ No strong signals in current market")
        print("   Markets might be too calm for our thresholds")
    
    print("\n🎯 OUR TRADING THRESHOLDS:")
    print("   • LONG (Gemini): > 0.8% gain")
    print("   • SHORT (Binance): < -1.0% loss")
    
    print("\n💡 WHY NO TRADES YET:")
    print("   1. Markets might not have moved enough")
    print("   2. Bot checks pairs in batches (6 Gemini + 8 Binance per cycle)")
    print("   3. Might have missed brief opportunities")
    print("   4. Conservative thresholds reduce false signals")
    
    print("\n🚀 RECOMMENDATIONS:")
    print("   1. Lower thresholds: 0.5% LONG, 0.8% SHORT")
    print("   2. Check ALL pairs every cycle")
    print("   3. Add volume filter (require volume surge)")
    print("   4. Monitor during high volatility periods")
    
except Exception as e:
    print(f"❌ Error checking markets: {e}")

print(f"\n⏰ Analysis time: {datetime.now().strftime('%H:%M:%S')}")
print("=" * 70)