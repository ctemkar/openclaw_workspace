#!/usr/bin/env python3
import json
import subprocess
import datetime

# Current prices from the summary
btc_price = 70177.95
eth_price = 2173.18

# Get trades data
result = subprocess.run(['curl', '-s', 'http://localhost:5001/trades'], capture_output=True, text=True)
trades_data = json.loads(result.stdout)

# Analyze BTC trades
btc_trades = []
eth_trades = []

for trade in trades_data['trades']:
    if 'symbol' in trade:
        if trade['symbol'] == 'BTC/USD':
            btc_trades.append(trade)
        elif trade['symbol'] == 'ETH/USD':
            eth_trades.append(trade)
    elif 'model' in trade and 'BTC' in trade['model']:
        btc_trades.append(trade)
    elif 'model' in trade and 'ETH' in trade['model']:
        eth_trades.append(trade)

print('=== CURRENT MARKET ANALYSIS ===')
print(f'Current BTC Price: ${btc_price:,.2f}')
print(f'Current ETH Price: ${eth_price:,.2f}')
print()

print('=== BTC POSITIONS ANALYSIS ===')
for i, trade in enumerate(btc_trades[:5], 1):
    price = trade.get('price', trade.get('quantity', 0))
    if price:
        drawdown = ((btc_price - price) / price) * 100
        status = 'STOP-LOSS TRIGGERED' if drawdown < -5 else 'WARNING' if drawdown < -4 else 'OK'
        print(f'{i}. Entry: ${price:,.2f} | Current: ${btc_price:,.2f} | Drawdown: {drawdown:.2f}% | {status}')

print()
print('=== ETH POSITIONS ANALYSIS ===')
for i, trade in enumerate(eth_trades[:5], 1):
    price = trade.get('price', trade.get('quantity', 0))
    if price:
        drawdown = ((eth_price - price) / price) * 100
        status = 'STOP-LOSS TRIGGERED' if drawdown < -5 else 'WARNING' if drawdown < -4 else 'OK'
        print(f'{i}. Entry: ${price:,.2f} | Current: ${eth_price:,.2f} | Drawdown: {drawdown:.2f}% | {status}')

print()
print('=== RISK SUMMARY ===')
btc_triggers = sum(1 for trade in btc_trades[:5] if trade.get('price', 0) and ((btc_price - trade['price']) / trade['price']) * 100 < -5)
eth_triggers = sum(1 for trade in eth_trades[:5] if trade.get('price', 0) and ((eth_price - trade['price']) / trade['price']) * 100 < -5)
print(f'BTC Positions with stop-loss triggered: {btc_triggers}/{len(btc_trades[:5])}')
print(f'ETH Positions with stop-loss triggered: {eth_triggers}/{len(eth_trades[:5])}')
print(f'Total positions at risk: {btc_triggers + eth_triggers}/{len(btc_trades[:5]) + len(eth_trades[:5])}')