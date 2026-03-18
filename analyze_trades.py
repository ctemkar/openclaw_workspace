#!/usr/bin/env python3
import json
import datetime

# Current prices from dashboard
btc_price = 71213.23
eth_price = 2186.36

# Trades from the system
trades = [
    {'symbol': 'ETH/USD', 'amount': 0.00428856924752764, 'price': 2331.78, 'side': 'buy'},
    {'symbol': 'BTC/USD', 'amount': 0.0001345244667719186, 'price': 74335.92, 'side': 'buy'},
    {'symbol': 'BTC/USD', 'amount': 0.0001345750121117511, 'price': 74308.0, 'side': 'buy'},
    {'symbol': 'BTC/USD', 'amount': 0.00013457358140268468, 'price': 74308.79, 'side': 'buy'},
    {'symbol': 'BTC/USD', 'amount': 0.00013453038469636157, 'price': 74332.65, 'side': 'buy'},
    {'symbol': 'BTC/USD', 'amount': 0.00013455424265000813, 'price': 74319.47, 'side': 'buy'},
    {'symbol': 'BTC/USD', 'amount': 0.002699, 'price': 74094.64, 'side': 'buy'},
    {'symbol': 'ETH/USD', 'amount': 0.086, 'price': 2325.28, 'side': 'buy'},
    {'symbol': 'BTC/USD', 'amount': 0.002802, 'price': 71386.0, 'side': 'buy'},
    {'symbol': 'ETH/USD', 'amount': 0.0912, 'price': 2193.6, 'side': 'buy'}
]

# Calculate P&L
total_investment = 0
total_current_value = 0

for trade in trades:
    if trade['symbol'] == 'BTC/USD':
        current_price = btc_price
    else:
        current_price = eth_price
    
    investment = trade['amount'] * trade['price']
    current_value = trade['amount'] * current_price
    
    total_investment += investment
    total_current_value += current_value

total_pnl = total_current_value - total_investment
pnl_percentage = (total_pnl / total_investment * 100) if total_investment > 0 else 0

print('Total Investment: ${:.2f}'.format(total_investment))
print('Total Current Value: ${:.2f}'.format(total_current_value))
print('Total P&L: ${:.2f} ({:.1f}%)'.format(total_pnl, pnl_percentage))
print('Available Capital: ${:.2f}'.format(1000 - total_investment))

# Check stop-loss triggers
stop_loss_percentage = 0.05
critical_positions = []

for i, trade in enumerate(trades, 1):
    if trade['symbol'] == 'BTC/USD':
        current_price = btc_price
    else:
        current_price = eth_price
    
    entry_price = trade['price']
    stop_loss_price = entry_price * (1 - stop_loss_percentage)
    
    if current_price <= stop_loss_price:
        pnl = (current_price - entry_price) * trade['amount']
        pnl_pct = (current_price / entry_price - 1) * 100
        below_stop = (stop_loss_price - current_price) / stop_loss_price * 100
        critical_positions.append({
            'position': i,
            'symbol': trade['symbol'],
            'amount': trade['amount'],
            'entry': entry_price,
            'current': current_price,
            'stop_loss': stop_loss_price,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'below_stop': below_stop
        })

print('\nPositions below stop-loss: {}'.format(len(critical_positions)))
for pos in critical_positions:
    print('Position {} ({}): {:.1f}% loss, {:.1f}% below stop-loss'.format(
        pos['position'], pos['symbol'], pos['pnl_pct'], pos['below_stop']))