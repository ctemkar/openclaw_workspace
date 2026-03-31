#!/usr/bin/env python3
"""
Helper function to calculate actual Gemini P&L
"""

import json
import requests

def calculate_gemini_pnl():
    """Calculate actual Gemini P&L from gemini_trades.json"""
    try:
        with open('gemini_trades.json', 'r') as f:
            trades = json.load(f)
    except:
        return 0.0
    
    if not trades:
        return 0.0
    
    # Get current SOL price from Binance
    try:
        response = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=SOLUSDT', timeout=3)
        sol_price = float(response.json()['price'])
    except:
        sol_price = 82.65  # Fallback price
    
    total_pnl = 0
    for trade in trades:
        if trade.get('symbol') == 'SOL/USD':
            entry_price = trade.get('price', 0)
            amount = trade.get('amount', 0)
            value = trade.get('value', 0)
            current_value = amount * sol_price
            total_pnl += current_value - value
    
    return round(total_pnl, 2)

if __name__ == '__main__':
    pnl = calculate_gemini_pnl()
    print(f"Actual Gemini P&L: ${pnl:+.2f}")