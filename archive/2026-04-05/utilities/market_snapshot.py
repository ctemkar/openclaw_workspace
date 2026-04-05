#!/usr/bin/env python3
"""
Quick market snapshot for momentum analysis
"""

import requests
import json
from datetime import datetime

print('=== CURRENT MARKET SNAPSHOT ===')
print(f'Time: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC')

# Get simple price data
url = 'https://api.coingecko.com/api/v3/simple/price'
params = {
    'ids': 'bitcoin,ethereum,solana',
    'vs_currencies': 'usd',
    'include_24hr_change': 'true',
    'include_24hr_vol': 'true'
}

try:
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    
    print('\nCurrent Prices:')
    for coin, info in data.items():
        price = info.get('usd', 0)
        change = info.get('usd_24h_change', 0)
        print(f'{coin.upper()}: ${price:,.2f} ({change:+.2f}% 24h)')
    
    # Check for momentum conditions
    print('\nMomentum Analysis:')
    for coin, info in data.items():
        change = info.get('usd_24h_change', 0)
        if change >= 5:
            print(f'🚀 {coin.upper()}: Strong momentum (+{change:.2f}% in 24h)')
        elif change >= 2.5:
            print(f'📈 {coin.upper()}: Moderate momentum (+{change:.2f}% in 24h)')
        elif change <= -5:
            print(f'📉 {coin.upper()}: Strong downtrend ({change:.2f}% in 24h)')
        else:
            print(f'⚖️  {coin.upper()}: Consolidating ({change:+.2f}% in 24h)')
            
except Exception as e:
    print(f'Error: {e}')