#!/usr/bin/env python3
import requests
import json
import time

# Get Binance price
try:
    binance_url = 'https://api.binance.com/api/v3/ticker/price?symbol=MANAUSDT'
    binance_response = requests.get(binance_url, timeout=5)
    binance_data = binance_response.json()
    binance_price = float(binance_data['price'])
except Exception as e:
    print(f"Binance error: {e}")
    binance_price = 0.0

# Get Gemini price
try:
    gemini_url = 'https://api.gemini.com/v1/pubticker/manausd'
    gemini_response = requests.get(gemini_url, timeout=5)
    gemini_data = gemini_response.json()
    gemini_price = float(gemini_data['last'])
except Exception as e:
    print(f"Gemini error: {e}")
    gemini_price = 0.0

if binance_price > 0 and gemini_price > 0:
    spread = ((binance_price - gemini_price) / gemini_price) * 100
    print(f'Binance: ${binance_price:.4f}')
    print(f'Gemini: ${gemini_price:.4f}')
    print(f'Spread: {spread:.2f}%')
    print(f'Potential profit per $30 trade: ${30 * spread/100:.2f}')
else:
    print('Error fetching prices')