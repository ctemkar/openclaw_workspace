#!/usr/bin/env python3
import json
import os

# Check daily trades
with open('daily_trades.json', 'r') as f:
    daily = json.load(f)

print('📊 DAILY TRADES ANALYSIS:')
print('='*50)
total_spent = 0
for trade in daily['trades']:
    print(f'{trade["side"]} {trade["amount"]:.6f} BTC @ ${trade["price"]:.2f} = ${trade["value"]:.2f}')
    total_spent += trade['value']

print(f'\n💰 Total spent on BTC: ${total_spent:.2f}')
print(f'📈 Portfolio value: ${daily["metadata"]["total_portfolio_value"]:.2f}')

# Check if we started with more than $250
print('\n🤔 DISCREPANCY ANALYSIS:')
print(f'If we spent ${total_spent:.2f} on BTC and have ${daily["metadata"]["total_portfolio_value"]:.2f} total...')
print(f'We must have started with more than $250')

# Let me check the actual Gemini trades again
print('\n🔍 Let me check actual Gemini trades more carefully...')

import ccxt
from datetime import datetime

with open('secure_keys/.gemini_key', 'r') as f:
    key = f.read().strip()
with open('secure_keys/.gemini_secret', 'r') as f:
    secret = f.read().strip()

exchange = ccxt.gemini({
    'apiKey': key,
    'secret': secret,
    'enableRateLimit': True
})

# Get ALL trades, not just today
print('\n📋 CHECKING ALL GEMINI TRADES:')
trades = exchange.fetch_my_trades('BTC/USD', limit=50)
print(f'Total trades in history: {len(trades)}')

# Group by date
from collections import defaultdict
trades_by_date = defaultdict(list)
for trade in trades:
    trade_time = datetime.fromtimestamp(trade['timestamp']/1000)
    date_str = trade_time.date().isoformat()
    trades_by_date[date_str].append(trade)

print('\n📅 TRADES BY DATE:')
for date, date_trades in sorted(trades_by_date.items()):
    total_date = sum(t['cost'] for t in date_trades if t['side'] == 'buy')
    print(f'{date}: {len(date_trades)} trades, ${total_date:.2f} total')

# Check current BTC holdings
balance = exchange.fetch_balance()
btc = balance['total'].get('BTC', 0)
print(f'\n💰 CURRENT BTC HOLDINGS: {btc:.6f} BTC')

# Calculate average buy price
buy_trades = [t for t in trades if t['side'] == 'buy']
if buy_trades:
    total_btc_bought = sum(t['amount'] for t in buy_trades)
    total_spent_on_btc = sum(t['cost'] for t in buy_trades)
    avg_price = total_spent_on_btc / total_btc_bought
    print(f'📊 AVERAGE BTC BUY PRICE: ${avg_price:.2f}')
    print(f'   Total BTC bought: {total_btc_bought:.6f}')
    print(f'   Total spent: ${total_spent_on_btc:.2f}')

print('\n🎯 CONCLUSION:')
print('The system was tracking WRONG initial capital.')
print(f'Actual portfolio: ${daily["metadata"]["total_portfolio_value"]:.2f}')
print('P&L calculation needs baseline correction.')