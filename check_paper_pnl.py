#!/usr/bin/env python3
"""
Check P&L for existing paper trades
"""

import json

# Current prices from latest execution
current_prices = {
    'BTCUSD': 67683.00,
    'ETHUSD': 2099.43,
    'SOLUSD': 82.66
}

# Load existing paper trades
with open('aggressive_paper_trades_executed.json', 'r') as f:
    data = json.load(f)

print('📊 EXISTING PAPER TRADES - CURRENT STATUS')
print('=' * 60)

total_pnl = 0
trade_count = len(data['trades_executed'])

for trade in data['trades_executed']:
    symbol = trade['symbol']
    entry = trade['entry_price']
    current = current_prices.get(symbol, entry)
    position_size = trade['position_size']
    action = trade['action']
    
    if action == 'BUY':
        pnl = (current - entry) * position_size
        pnl_percent = ((current - entry) / entry) * 100
    else:  # SELL
        pnl = (entry - current) * position_size
        pnl_percent = ((entry - current) / entry) * 100
    
    total_pnl += pnl
    
    status = '✅ PROFIT' if pnl > 0 else '❌ LOSS' if pnl < 0 else '⚖️  BREAKEVEN'
    
    print(f'{symbol} {action}:')
    print(f'  Entry: ${entry:,.2f}')
    print(f'  Current: ${current:,.2f}')
    print(f'  Position: {position_size:.6f}')
    print(f'  P&L: ${pnl:,.2f} ({pnl_percent:.2f}%) {status}')
    print(f'  Stop Loss: ${trade["stop_loss"]:,.2f}')
    print(f'  Take Profit: ${trade["take_profit"]:,.2f}')
    print()

print('=' * 60)
print(f'💰 TOTAL PAPER P&L: ${total_pnl:,.2f}')
avg_return = total_pnl / data['summary']['total_position_value'] * 100 if data['summary']['total_position_value'] > 0 else 0
print(f'📈 AVERAGE RETURN: {avg_return:.2f}%')
print(f'🏦 PAPER BALANCE: ${25000 + total_pnl:,.2f}')
print(f'⚡ LEVERAGE EXPOSURE: ${data["summary"]["total_position_value"]:,.2f} ({data["summary"]["total_position_value"]/25000:.1f}x)')