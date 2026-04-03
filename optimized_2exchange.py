#!/usr/bin/env python3
"""
Optimized 2-Exchange Bot
- Gemini + Binance
- 36 cryptos from config
- Efficient scanning
"""
import ccxt
import time
import json

with open('arbitrage_config.json', 'r') as f:
    config = json.load(f)

cryptos = config.get('supported_cryptos', [])

gemini = ccxt.gemini()
binance = ccxt.binance()

scan_count = 0
opportunities_found = 0

while True:
    scan_count += 1
    print(f"🔍 2-Exchange Scan #{scan_count}: {len(cryptos)} cryptos")
    
    current_opportunities = 0
    
    for crypto in cryptos:
        try:
            g_price = gemini.fetch_ticker(f"{crypto}/USD")['last']
            b_price = binance.fetch_ticker(f"{crypto}/USDT")['last']
            
            spread = ((g_price - b_price) / b_price) * 100
            
            if abs(spread) > 0.4:
                current_opportunities += 1
                print(f"   💰 {crypto}: {spread:.2f}%")
        except:
            continue
    
    if current_opportunities > 0:
        opportunities_found += current_opportunities
        print(f"🎯 Found {current_opportunities} opportunities!")
    else:
        print("⏳ No opportunities found")
    
    if scan_count % 10 == 0:
        print(f"📊 SUMMARY: {scan_count} scans, {opportunities_found} total opportunities")
    
    time.sleep(30)
