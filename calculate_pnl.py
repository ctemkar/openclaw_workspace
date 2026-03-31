#!/usr/bin/env python3
"""
Calculate total P&L for Gemini and Binance
"""

import json
import requests
from datetime import datetime

def get_current_price(symbol):
    """Get current price for a symbol"""
    # For now, use approximate prices
    prices = {
        'SOL/USD': 82.50,
        'BTC/USD': 66500.00,
        'ETH/USD': 3500.00,
        'XRP/USD': 0.52,
        'ADA/USD': 0.45,
        'DOT/USD': 7.20,
        'DOGE/USD': 0.15,
        'AVAX/USD': 36.00,
        'LINK/USD': 18.50,
        'UNI/USD': 10.20,
        'LTC/USD': 82.00,
        'ATOM/USD': 10.50,
        'FIL/USD': 5.80,
        'XTZ/USD': 1.05,
        'AAVE/USD': 100.00,
        'COMP/USD': 60.00,
        'YFI/USD': 8500.00
    }
    return prices.get(symbol, 0)

def main():
    print('📊 TOTAL P&L SUMMARY')
    print('=' * 60)
    
    try:
        # Get data from dashboard API
        response = requests.get('http://localhost:5007/api/data', timeout=5)
        data = response.json()
    except:
        print('❌ Could not fetch dashboard data')
        return
    
    # Calculate total P&L from positions
    total_pnl = 0
    total_value = 0
    gemini_pnl = 0
    gemini_value = 0
    binance_pnl = 0
    binance_value = 0
    
    print('🔍 CURRENT POSITIONS:')
    positions = data.get('positions', [])
    
    for pos in positions:
        exchange = pos.get('exchange', 'unknown')
        symbol = pos.get('symbol', 'unknown')
        entry_price = pos.get('price', 0)
        amount = pos.get('amount', 0)
        
        # Get current price
        current_price = get_current_price(symbol)
        
        position_value = amount * current_price
        entry_value = amount * entry_price
        pnl = position_value - entry_value
        pnl_percent = (pnl / entry_value * 100) if entry_value > 0 else 0
        
        total_pnl += pnl
        total_value += position_value
        
        if exchange == 'gemini':
            gemini_pnl += pnl
            gemini_value += position_value
            exchange_symbol = '♊'
        elif exchange == 'binance':
            binance_pnl += pnl
            binance_value += position_value
            exchange_symbol = '₿'
        else:
            exchange_symbol = '❓'
        
        print(f'  {exchange_symbol} {exchange.upper():8} {symbol:10} Entry: ${entry_price:.2f} Current: ${current_price:.2f} P&L: ${pnl:+.2f} ({pnl_percent:+.2f}%)')
    
    print()
    print('💰 CAPITAL BREAKDOWN:')
    capital = data.get('capital', {})
    print(f'  Total Capital: ${capital.get("total_capital", 0):.2f}')
    print(f'  Gemini Total: ${capital.get("gemini_total", 0):.2f}')
    print(f'  Binance Total: ${capital.get("binance_total", 0):.2f}')
    print(f'  Deployed: ${capital.get("deployed", 0):.2f}')
    print(f'  Available Gemini: ${capital.get("available_gemini", 0):.2f}')
    print(f'  Available Binance: ${capital.get("available_binance", 0):.2f}')
    
    print()
    print('📈 P&L SUMMARY:')
    print(f'  Gemini P&L: ${gemini_pnl:+.2f} ({gemini_value:.2f} value)')
    print(f'  Binance P&L: ${binance_pnl:+.2f} ({binance_value:.2f} value)')
    print(f'  Total P&L: ${total_pnl:+.2f} ({total_value:.2f} total value)')
    
    # Calculate percentages
    total_capital = capital.get('total_capital', 1)
    total_pnl_percent = (total_pnl / total_capital * 100) if total_capital > 0 else 0
    
    print()
    print('📊 POSITION COUNT:')
    gemini_count = len([p for p in positions if p.get('exchange') == 'gemini'])
    binance_count = len([p for p in positions if p.get('exchange') == 'binance'])
    print(f'  Gemini positions: {gemini_count}')
    print(f'  Binance positions: {binance_count}')
    print(f'  Total positions: {len(positions)}')
    
    print()
    print('📊 OVERALL PERFORMANCE:')
    print(f'  Total P&L %: {total_pnl_percent:+.2f}%')
    print(f'  Gemini P&L %: {(gemini_pnl / capital.get("gemini_total", 1) * 100) if capital.get("gemini_total", 0) > 0 else 0:+.2f}%')
    print(f'  Binance P&L %: {(binance_pnl / capital.get("binance_total", 1) * 100) if capital.get("binance_total", 0) > 0 else 0:+.2f}%')
    
    print()
    print('📅 Last updated:', data.get('timestamp', 'unknown'))

if __name__ == '__main__':
    main()