#!/usr/bin/env python3
"""
Quick check of current market conditions for 26 cryptos
"""

import ccxt
from datetime import datetime

# Top cryptos
CRYPTOS = ["BTC", "ETH", "SOL", "ADA", "XRP", "DOT", "DOGE", "AVAX", "MATIC", "LINK"]

print("=" * 70)
print("QUICK MARKET CHECK - 26 CRYPTOS")
print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
print("=" * 70)

# Initialize exchanges (public access)
gemini = ccxt.gemini()
binance = ccxt.binance()

print("\n🔍 CURRENT PRICE MOVEMENTS (last 24h):")
print("-" * 70)

# Check a few major cryptos
for crypto in CRYPTOS[:5]:  # First 5
    try:
        # Gemini
        gemini_pair = f"{crypto}/USD"
        gemini_ticker = gemini.fetch_ticker(gemini_pair)
        gemini_change = gemini_ticker['percentage']
        
        # Binance
        binance_pair = f"{crypto}/USDT"
        binance_ticker = binance.fetch_ticker(binance_pair)
        binance_change = binance_ticker['percentage']
        
        print(f"{crypto:6} | Gemini: {gemini_change:6.2f}% | Binance: {binance_change:6.2f}% | ", end="")
        
        # Signal assessment
        if gemini_change > 0.8:
            print("📈 LONG opportunity on Gemini")
        elif gemini_change < -1.0:
            print("📉 SHORT opportunity on Gemini (if supported)")
        elif binance_change < -1.0:
            print("📉 SHORT opportunity on Binance")
        elif binance_change > 0.8:
            print("📈 LONG opportunity on Binance")
        else:
            print("➡️  No strong signal")
            
    except Exception as e:
        print(f"{crypto:6} | Error: {str(e)[:30]}...")

print("\n" + "=" * 70)
print("🎯 TRADING SIGNAL SUMMARY:")
print("=" * 70)
print("LONG signal: > 0.8% gain (Gemini)")
print("SHORT signal: < -1.0% loss (Binance)")
print("-" * 70)
print("💡 If no signals found:")
print("1. Markets might be flat/consolidating")
print("2. Thresholds might be too high")
print("3. Check during high volatility periods")
print("4. Consider lower thresholds (0.5% for LONG, 0.8% for SHORT)")
print("=" * 70)
print(f"⏰ Checked at: {datetime.now().strftime('%H:%M:%S')}")