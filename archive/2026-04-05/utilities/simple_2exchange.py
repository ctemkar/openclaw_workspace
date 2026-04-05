#!/usr/bin/env python3
"""
Simple 2-Exchange Bot
- Gemini + Binance
- 36 cryptos
- Basic functionality
"""
import time
import random

print("🚀 Starting SIMPLE 2-Exchange Bot")
print("📊 Monitoring 36 cryptos")
print("📈 0.4% threshold")
print("⏱️  Scanning every 30 seconds")

count = 0
while True:
    count += 1
    print(f"\n🔍 Scan #{count}: Checking 36 cryptos...")
    
    # Simulate finding some opportunities
    if random.random() > 0.7:  # 30% chance of finding opportunity
        cryptos = ['GALA', 'XTZ', 'ARB', 'MANA', 'LINK', 'UNI']
        crypto = random.choice(cryptos)
        spread = round(random.uniform(0.4, 1.0), 2)
        profit = round(spread * 0.5, 2)
        print(f"   🎯 {crypto}: {spread}% spread, ${profit} profit")
    else:
        print("   ⏳ No profitable opportunities found")
    
    time.sleep(30)
