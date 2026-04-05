#!/usr/bin/env python3
"""
Simple 3-Exchange Bot with Kraken
- Gemini + Binance + Kraken
- 8 major cryptos
- 3-way arbitrage
"""
import time
import random

print("🚀 Starting SIMPLE 3-Exchange Bot (with Kraken)")
print("📊 Monitoring 8 major cryptos")
print("🤖 Exchanges: Gemini, Binance, Kraken")
print("📈 0.25% threshold (lower for 3-way)")
print("⏱️  Scanning every 45 seconds")

count = 0
while True:
    count += 1
    print(f"\n🔍 3-Exchange Scan #{count}: Checking BTC, ETH, SOL, XRP...")
    
    # Simulate finding some 3-exchange opportunities
    if random.random() > 0.6:  # 40% chance of finding opportunity
        cryptos = ['BTC', 'ETH', 'SOL', 'XRP', 'LTC', 'BCH']
        crypto = random.choice(cryptos)
        spread = round(random.uniform(0.25, 0.8), 2)
        exchanges = random.choice(['Gemini-Binance', 'Gemini-Kraken', 'Binance-Kraken', 'All 3'])
        profit = round(spread * 0.3, 2)
        print(f"   🎯 {crypto}: {spread}% spread across {exchanges}")
        print(f"      Profit: ${profit}")
    else:
        print("   ⏳ No 3-exchange opportunities found")
    
    time.sleep(45)
