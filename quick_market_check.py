#!/usr/bin/env python3
"""
Quick market check for crypto momentum trading
"""

import requests
from datetime import datetime

print('=== REAL-TIME MARKET CHECK ===')
print(f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} UTC')
print()

# Get current prices
try:
    url = 'https://api.coingecko.com/api/v3/simple/price'
    params = {
        'ids': 'bitcoin,ethereum,solana',
        'vs_currencies': 'usd',
        'include_24hr_change': 'true',
        'include_24hr_vol': 'true'
    }
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    
    print('Current Market Prices:')
    print('-' * 40)
    
    coins = {
        'bitcoin': 'BTC',
        'ethereum': 'ETH', 
        'solana': 'SOL'
    }
    
    for coin_id, symbol in coins.items():
        info = data.get(coin_id, {})
        price = info.get('usd', 0)
        change_24h = info.get('usd_24h_change', 0)
        print(f'{symbol}: ${price:,.2f} ({change_24h:+.2f}% 24h)')
    
    print()
    print('Market Analysis:')
    print('-' * 40)
    
    # Check for momentum
    btc_change = data.get('bitcoin', {}).get('usd_24h_change', 0)
    eth_change = data.get('ethereum', {}).get('usd_24h_change', 0)
    sol_change = data.get('solana', {}).get('usd_24h_change', 0)
    
    if any(abs(x) >= 5 for x in [btc_change, eth_change, sol_change]):
        print('⚠️  Significant 24h moves detected (>5%)')
    else:
        print('📊 Markets relatively stable (<5% 24h moves)')
    
    # Check if any are positive
    positive_moves = sum(1 for x in [btc_change, eth_change, sol_change] if x > 0)
    if positive_moves >= 2:
        print('📈 Majority of markets in positive territory')
    elif positive_moves == 1:
        print('⚖️  Mixed market sentiment')
    else:
        print('📉 Majority of markets in negative territory')
    
    print()
    print('Momentum Trading Assessment:')
    print('-' * 40)
    
    # Check for aggressive momentum criteria
    print('For aggressive momentum trading (5%+ hourly moves):')
    if any(abs(x) >= 2 for x in [btc_change, eth_change, sol_change]):
        print('⚠️  Some volatility present, but not extreme')
    else:
        print('⏸️  Low volatility - markets in consolidation')
    
    print()
    print('Paper Trading Status:')
    print('-' * 40)
    print('✅ $25,000 paper balance available')
    print('✅ 2x leverage enabled (paper trading only)')
    print('✅ 8% stop-loss, 15% take-profit parameters')
    print('✅ Max 5 trades per day limit')
    
except Exception as e:
    print(f'Error fetching market data: {e}')