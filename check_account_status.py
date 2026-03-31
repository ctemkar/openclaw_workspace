#!/usr/bin/env python3
"""
Check current account status and portfolio value
"""

import ccxt
import os
import json
from datetime import datetime

def main():
    # Setup Gemini
    with open('.gemini_key', 'r') as f:
        api_key = f.read().strip()
    with open('.gemini_secret', 'r') as f:
        api_secret = f.read().strip()
    
    exchange = ccxt.gemini({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
    
    # Get balance
    balance = exchange.fetch_balance()
    usd_balance = balance['free'].get('USD', 0)
    btc_balance = balance['free'].get('BTC', 0)
    eth_balance = balance['free'].get('ETH', 0)
    
    # Get current prices
    btc_ticker = exchange.fetch_ticker('BTC/USD')
    eth_ticker = exchange.fetch_ticker('ETH/USD')
    btc_price = btc_ticker['last']
    eth_price = eth_ticker['last']
    
    # Calculate portfolio value
    btc_value = btc_balance * btc_price
    eth_value = eth_balance * eth_price
    total_value = usd_balance + btc_value + eth_value
    
    print('💰 REAL-TIME ACCOUNT STATUS')
    print('=' * 50)
    print(f'USD Balance: ${usd_balance:,.2f}')
    print(f'BTC Balance: {btc_balance:.6f} (${btc_value:,.2f})')
    print(f'ETH Balance: {eth_balance:.6f} (${eth_value:,.2f})')
    print(f'Total Portfolio Value: ${total_value:,.2f}')
    print(f'Current BTC Price: ${btc_price:,.2f}')
    print(f'Current ETH Price: ${eth_price:,.2f}')
    print(f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} (UTC+7)')
    
    return {
        'usd_balance': usd_balance,
        'btc_balance': btc_balance,
        'eth_balance': eth_balance,
        'btc_value': btc_value,
        'eth_value': eth_value,
        'total_value': total_value,
        'btc_price': btc_price,
        'eth_price': eth_price,
        'timestamp': datetime.now().isoformat()
    }

if __name__ == "__main__":
    main()