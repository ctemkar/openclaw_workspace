#!/usr/bin/env python3
import requests
import json
from datetime import datetime

def get_real_prices():
    """Get real-time prices from CoinGecko"""
    try:
        url = 'https://api.coingecko.com/api/v3/simple/price'
        params = {
            'ids': 'bitcoin,ethereum,solana',
            'vs_currencies': 'usd'
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        btc_price = data.get('bitcoin', {}).get('usd', 67975.67)
        eth_price = data.get('ethereum', {}).get('usd', 2074.92)
        sol_price = data.get('solana', {}).get('usd', 83.85)
        
        print('REAL-TIME MARKET DATA:')
        print(f'BTC/USD: ${btc_price:,.2f}')
        print(f'ETH/USD: ${eth_price:,.2f}')
        print(f'SOL/USD: ${sol_price:,.2f}')
        
        return {
            'BTCUSD': btc_price,
            'ETHUSD': eth_price,
            'SOLUSD': sol_price
        }
        
    except Exception as e:
        print(f'API Error: {e}')
        print('Using simulated prices from trading script')
        return {
            'BTCUSD': 67975.67,
            'ETHUSD': 2074.92,
            'SOLUSD': 83.85
        }

if __name__ == '__main__':
    get_real_prices()