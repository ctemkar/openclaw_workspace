#!/usr/bin/env python3
"""
Analyze the REAL trades found in daily_trades.json
"""

import json
from datetime import datetime

print("🔍 ANALYZING REAL TRADES FROM daily_trades.json")
print("="*60)

with open('daily_trades.json', 'r') as f:
    data = json.load(f)

trades = data.get('trades', [])
date = data.get('date', 'Unknown')

print(f"📅 Date: {date}")
print(f"📊 Total trades: {len(trades)}")
print()

total_buy_value = 0
total_sell_value = 0
open_trades = 0
closed_trades = 0

for i, trade in enumerate(trades, 1):
    symbol = trade['symbol']
    side = trade['side']
    price = trade['price']
    amount = trade['amount']
    value = trade['value']
    status = trade['status']
    timestamp = trade['timestamp']
    
    time_str = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).strftime('%H:%M:%S')
    
    print(f"Trade #{i}:")
    print(f"  Time: {time_str}")
    print(f"  {symbol} {side.upper()} {amount:.6f} @ ${price:,.2f}")
    print(f"  Value: ${value:,.2f}")
    print(f"  Status: {status}")
    
    if side == 'buy':
        total_buy_value += value
    elif side == 'sell':
        total_sell_value += value
    
    if status == 'open':
        open_trades += 1
    elif status == 'closed':
        closed_trades += 1
    
    print()

print("="*60)
print("📈 SUMMARY:")
print(f"  Total buy value: ${total_buy_value:,.2f}")
print(f"  Total sell value: ${total_sell_value:,.2f}")
print(f"  Net: ${total_sell_value - total_buy_value:,.2f}")
print(f"  Open trades: {open_trades}")
print(f"  Closed trades: {closed_trades}")

# Check against capital
initial_capital = 250
current_capital = 175.53
loss = initial_capital - current_capital

print(f"\n💰 CAPITAL ANALYSIS:")
print(f"  Initial: ${initial_capital:,.2f}")
print(f"  Current: ${current_capital:,.2f}")
print(f"  Loss: ${loss:,.2f} ({loss/initial_capital*100:.1f}%)")

print("\n" + "="*60)
print("🚨 DISCREPANCY ALERT:")
print(f"  Trades show ${total_buy_value:,.2f} in BUYS")
print(f"  But we only had ${initial_capital:,.2f} capital!")
print(f"  Where did the extra ${total_buy_value - initial_capital:,.2f} come from?")
print("="*60)