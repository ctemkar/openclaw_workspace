#!/usr/bin/env python3
"""
Real-time price updater for trading system
Runs every 60 seconds to update prices
"""

import json
import time
import ccxt
from datetime import datetime
import os

def update_prices():
    """Update all prices in trading data"""
    try:
        # Load current data
        with open('trading_data/trades.json', 'r') as f:
            trades = json.load(f)
        
        with open('trading_data/capital.json', 'r') as f:
            capital = json.load(f)
        
        # Get current SOL price from Gemini
        exchange = ccxt.gemini({'enableRateLimit': True})
        ticker = exchange.fetch_ticker('SOL/USD')
        sol_price = ticker['last']
        
        # Update trades
        total_pl = 0
        for trade in trades:
            if isinstance(trade, dict) and trade.get('symbol', '').startswith('SOL/'):
                entry_price = trade.get('price', 0)
                amount = trade.get('amount', 0)
                
                # Calculate P&L
                pl = (sol_price - entry_price) * amount
                total_pl += pl
                
                # Update trade
                trade['current_price'] = sol_price
                trade['current_value'] = amount * sol_price
                trade['unrealized_pl'] = pl
                trade['unrealized_pl_percent'] = ((sol_price / entry_price) - 1) * 100
                trade['last_price_update'] = datetime.now().isoformat()
        
        # Save updated trades
        with open('trading_data/trades.json', 'w') as f:
            json.dump(trades, f, indent=2)
        
        # Update capital
        capital['last_updated'] = datetime.now().isoformat()
        
        # Update Gemini total with live P&L
        if 'gemini_total' in capital:
            cash = capital.get('available_gemini', 0)
            deployed = capital.get('deployed', 0)
            capital['gemini_total'] = cash + deployed + total_pl
            capital['total_capital'] = capital['gemini_total'] + capital.get('binance_total', 0)
        
        with open('trading_data/capital.json', 'w') as f:
            json.dump(capital, f, indent=2)
        
        print(f'[{datetime.now().strftime("%H:%M:%S")}] Updated: SOL=${sol_price:.4f}, P&L=${total_pl:.4f}')
        return True
        
    except Exception as e:
        print(f'[{datetime.now().strftime("%H:%M:%S")}] Error updating: {e}')
        return False

if __name__ == '__main__':
    print('🚀 STARTING REAL-TIME PRICE UPDATER')
    print('   • Updates every 60 seconds')
    print('   • Updates SOL price and P&L')
    print('   • Logs to price_updater.log')
    print()
    
    while True:
        update_prices()
        time.sleep(60)  # Update every 60 seconds

