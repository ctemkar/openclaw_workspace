#!/usr/bin/env python3
"""
Conservative Crypto Market Analysis
"""

import requests
import json
from datetime import datetime

print('📊 MARKET ANALYSIS - Conservative Crypto Trading')
print('='*60)
print(f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} (UTC+7)')
print()

try:
    # Get BTC and ETH prices
    btc_data = requests.get('https://api.gemini.com/v1/pubticker/btcusd', timeout=10).json()
    eth_data = requests.get('https://api.gemini.com/v1/pubticker/ethusd', timeout=10).json()
    
    btc_price = float(btc_data['last'])
    eth_price = float(eth_data['last'])
    
    print(f'BTC/USD: ${btc_price:,.2f}')
    print(f'  Bid: ${float(btc_data["bid"]):,.2f}')
    print(f'  Ask: ${float(btc_data["ask"]):,.2f}')
    print(f'  Volume (24h): {float(btc_data["volume"]["BTC"]):,.2f} BTC')
    print()
    print(f'ETH/USD: ${eth_price:,.2f}')
    print(f'  Bid: ${float(eth_data["bid"]):,.2f}')
    print(f'  Ask: ${float(eth_data["ask"]):,.2f}')
    print(f'  Volume (24h): {float(eth_data["volume"]["ETH"]):,.2f} ETH')
    print()
    
    # Calculate bid/ask spread
    btc_bid = float(btc_data['bid'])
    btc_ask = float(btc_data['ask'])
    btc_spread = btc_ask - btc_bid
    btc_spread_percent = (btc_spread / btc_price) * 100
    
    eth_bid = float(eth_data['bid'])
    eth_ask = float(eth_data['ask'])
    eth_spread = eth_ask - eth_bid
    eth_spread_percent = (eth_spread / eth_price) * 100
    
    print(f'📈 Market Spread Analysis:')
    print(f'  BTC Spread: ${btc_spread:.2f} ({btc_spread_percent:.3f}%)')
    print(f'  ETH Spread: ${eth_spread:.2f} ({eth_spread_percent:.3f}%)')
    
    # Get order book depth
    btc_book = requests.get('https://api.gemini.com/v1/book/btcusd', timeout=10).json()
    print(f'  BTC Order Book Depth: {len(btc_book["bids"])} bids, {len(btc_book["asks"])} asks')
    
    # Simple sentiment based on price action (using bid/ask midpoint)
    btc_mid = (btc_bid + btc_ask) / 2
    # For demo, we'll use a simple heuristic
    if btc_spread_percent < 0.02:  # Tight spread suggests liquidity
        sentiment = 'NEUTRAL ↔️ (Good liquidity)'
    elif btc_spread_percent > 0.05:  # Wide spread suggests volatility
        sentiment = 'VOLATILE ⚡ (Wide spreads)'
    else:
        sentiment = 'STABLE 🔒 (Normal market conditions)'
    
    print(f'  Market Condition: {sentiment}')
    
    # Support/Resistance levels (simplified)
    print(f'\n📊 Support/Resistance Levels (simplified):')
    print(f'  Current: ${btc_price:,.2f}')
    print(f'  Near Support: ${btc_price * 0.98:,.2f} (-2%)')
    print(f'  Near Resistance: ${btc_price * 1.02:,.2f} (+2%)')
    
except Exception as e:
    print(f'Error fetching market data: {e}')