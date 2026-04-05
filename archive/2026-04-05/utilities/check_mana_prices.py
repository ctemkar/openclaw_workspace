import requests
import json
import time

# Get MANA price from Binance
try:
    binance_response = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=MANAUSDT', timeout=5)
    binance_price = float(binance_response.json()['price'])
    print(f'Binance MANA price: ${binance_price:.4f}')
except Exception as e:
    print(f'Binance API error: {e}')

# Get MANA price from Gemini
try:
    gemini_response = requests.get('https://api.gemini.com/v1/pubticker/manausd', timeout=5)
    gemini_price = float(gemini_response.json()['last'])
    print(f'Gemini MANA price: ${gemini_price:.4f}')
    
    # Calculate spread
    spread = ((gemini_price - binance_price) / binance_price) * 100
    print(f'Spread: {spread:.2f}%')
    
    # Calculate potential profit per 1000 MANA
    profit_per_1000 = (gemini_price - binance_price) * 1000
    print(f'Potential profit per 1000 MANA: ${profit_per_1000:.2f}')
except Exception as e:
    print(f'Gemini API error: {e}')