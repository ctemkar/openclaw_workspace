#!/usr/bin/env python3
"""
Simple 3-Exchange Bot with Kraken
- Gemini, Binance, Kraken
- 8 major cryptos
- Simple and reliable
"""
import ccxt
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

cryptos = ['BTC', 'ETH', 'SOL', 'XRP', 'LTC', 'BCH', 'LINK', 'UNI']

exchanges = {
    'gemini': ccxt.gemini(),
    'binance': ccxt.binance(),
    'kraken': ccxt.kraken()
}

scan_count = 0

while True:
    scan_count += 1
    print(f"🔍 3-Exchange Scan #{scan_count}")
    
    for crypto in cryptos:
        prices = {}
        
        for name, exchange in exchanges.items():
            try:
                if name == 'gemini':
                    symbol = f"{crypto}/USD"
                elif name == 'binance':
                    symbol = f"{crypto}/USDT"
                elif name == 'kraken':
                    if crypto == 'BTC':
                        symbol = 'XBT/USD'
                    else:
                        symbol = f"{crypto}/USD"
                
                ticker = exchange.fetch_ticker(symbol)
                prices[name] = ticker['last']
            except:
                continue
        
        if len(prices) >= 2:
            buy_exchange = min(prices, key=prices.get)
            sell_exchange = max(prices, key=prices.get)
            spread = ((prices[sell_exchange] - prices[buy_exchange]) / prices[buy_exchange]) * 100
            
            if abs(spread) > 0.2:
                print(f"   💰 {crypto}: {spread:.2f}%")
                print(f"      Buy {buy_exchange}: ${prices[buy_exchange]:.2f}")
                print(f"      Sell {sell_exchange}: ${prices[sell_exchange]:.2f}")
    
    time.sleep(45)
