#!/usr/bin/env python3
import requests
import json

# Check Binance prices
try:
    binance_url = 'https://api.binance.com/api/v3/ticker/price?symbol=MANAUSDT'
    binance_response = requests.get(binance_url, timeout=10)
    binance_data = binance_response.json()
    binance_price = float(binance_data['price'])
    print(f'Binance MANA/USDT: ${binance_price:.4f}')
except Exception as e:
    print(f'Binance error: {e}')

# Check Gemini prices  
try:
    gemini_url = 'https://api.gemini.com/v1/pubticker/manausd'
    gemini_response = requests.get(gemini_url, timeout=10)
    gemini_data = gemini_response.json()
    gemini_price = float(gemini_data['last'])
    print(f'Gemini MANA/USD: ${gemini_price:.4f}')
    
    # Calculate spread
    if 'binance_price' in locals():
        spread = ((gemini_price - binance_price) / binance_price) * 100
        print(f'Spread: {spread:.2f}%')
        if spread > 1.0:
            print(f'💰 ARBITRAGE OPPORTUNITY DETECTED!')
            print(f'   Buy Binance: ${binance_price:.4f}')
            print(f'   Sell Gemini: ${gemini_price:.4f}')
            print(f'   Potential profit: ${gemini_price - binance_price:.4f} per MANA')
except Exception as e:
    print(f'Gemini error: {e}')